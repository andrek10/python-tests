""" This example shows a full factorial variation

Based on https://github.com/CATIA-Systems/FMPy/blob/master/fmpy/examples/parameter_variation.py
"""

import dask
from dask import bag
from dask.diagnostics import ProgressBar
import numpy as np
import fmpy
from fmpy.fmi2 import FMU2Slave
from fmpy import read_model_description, platform
from fmpy.util import download_test_file
import shutil

FMU_FILENAME = 'fmu_test.fmu'

# define the parameter space for the variation
INITIAL_INPUTS = [1.0, 2.0, 3.0]  # AC voltage [V]
INITIAL_INTEGRATORS = [0.0, 0.5, 1.0]          # DC current [A]

SYNC = False  # synchronized execution (for debugging)

STOP_TIME = 0.1
STEP_TIME = 0.02

DLL_HANDLE = None

N_CHUNKS = 10  # number of chunks to divide the workload

# create the parameters
INITIAL_INPUTS_GRID, INITIAL_INTEGRATORS_GRID = np.meshgrid(INITIAL_INPUTS, INITIAL_INTEGRATORS, indexing='ij')


def simulate_fmu(*args):
    """ Worker function that simulates the FMU
    Parameters:
        args = [indices, fmu_args, start_vrs, result_vrs]
        indices     a list of indices into the parameter arrays
        fmu_args    FMU constructor arguments
    Returns:
        a list of tuples (i, [u_dc, losses]) that contain the index 'i' and the averaged results of the
        'uDC' and 'Losses' variables
    """

    indices, fmu_args, start_vrs, result_vrs = args

    zipped = []

    # global fmu_args, start_vrs, result_vrs, dll_handle

    fmu = FMU2Slave(**fmu_args)

    fmu.instantiate()

    # iterate over the all indices in this batch
    for i in indices:

        # get the start values for the current index
        start_values = [INITIAL_INPUTS_GRID[i], INITIAL_INTEGRATORS_GRID[i]]

        fmu.reset()

        fmu.setupExperiment()

        # set the start values
        fmu.setReal(vr=start_vrs, value=start_values)

        fmu.enterInitializationMode()
        fmu.exitInitializationMode()

        time = 0.0
        step_size = 0.02

        results = []

        # simulation loop
        while time < STOP_TIME:
            fmu.doStep(currentCommunicationPoint=time, communicationStepSize=step_size)
            time += step_size

            if time > 0.02:
                result = fmu.getReal(result_vrs)
                results.append(result)

        u_dc, losses = zip(*results)

        # store the index and the averaged signals
        zipped.append((i, [np.average(u_dc), np.average(losses)]))

    fmu.terminate()

    # call the FMI API directly to avoid unloading the share library
    fmu.fmi2FreeInstance(fmu.component)

    if SYNC:
        # remember the shared library handle so we can unload it later
        global DLL_HANDLE
        DLL_HANDLE = fmu.dll._handle
    else:
        # unload the shared library directly
        fmpy.freeLibrary(fmu.dll._handle)

    return zipped


def run_experiment(show_plot=True):

    if platform not in ['win32', 'win64']:
        raise Exception("Rectifier.fmu is only available for Windows")

    print("Parameter variation on %s:" % FMU_FILENAME)
    print("  u", INITIAL_INPUTS)
    print("  IDC", INITIAL_INTEGRATORS)

    if SYNC:
        dask.config.set(scheduler='synchronous')  # synchronized scheduler

    # read the model description
    model_description = read_model_description(FMU_FILENAME)

    # collect the value references for the variables to read / write
    vrs = {}
    for variable in model_description.modelVariables:
        vrs[variable.name] = variable.valueReference

    # extract the FMU
    unzipdir = fmpy.extract(FMU_FILENAME)

    fmu_args = {'guid': model_description.guid,
                'modelIdentifier': model_description.coSimulation.modelIdentifier,
                'unzipDirectory': unzipdir}

    # get the value references for the start and output values
    start_vrs = [vrs['u'], vrs['Integrator_InitialCondition']]
    result_vrs = [vrs['y']]

    indices = list(np.ndindex(INITIAL_INTEGRATORS_GRID.shape))

    print("Running %d simulations (%d chunks)..." % (INITIAL_INPUTS_GRID.size, N_CHUNKS))
    with ProgressBar():
        # calculate the losses for every chunk
        b = bag.from_sequence(indices, npartitions=N_CHUNKS)
        results = b.map_partitions(simulate_fmu, fmu_args, start_vrs, result_vrs).compute()

    LOSSES = np.zeros_like(INITIAL_INPUTS_GRID)

    # put the results together
    for i, res in results:
        LOSSES[i] = res[1]

    # unload the shared library
    if SYNC:
        while True:
            try:
                fmpy.freeLibrary(DLL_HANDLE)
            except:
                break

    # clean up
    shutil.rmtree(unzipdir, ignore_errors=True)

    if show_plot:
        print("Plotting results...")

        import matplotlib.pyplot as plt

        figure = plt.figure()
        figure.patch.set_facecolor('white')
        ax = figure.add_subplot(1, 1, 1)

        CS = plt.contourf(INITIAL_INPUTS_GRID, INITIAL_INTEGRATORS_GRID, LOSSES, 10)
        plt.colorbar(CS, aspect=30)

        CS = ax.contour(INITIAL_INPUTS_GRID, INITIAL_INTEGRATORS_GRID, LOSSES, 10, colors='k', linewidths=0.8)
        ax.clabel(CS=CS, fmt='%.0f', fontsize=9, inline=1)

        ax.set_title('Losses / W')
        ax.set_xlabel('AC Voltage / V')
        ax.set_ylabel('DC Current / A')

        plt.show()
    else:
        print("Plotting disabled")

    print("Done.")

    return LOSSES


if __name__ == '__main__':

    run_experiment()
