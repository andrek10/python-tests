# -*- coding: utf-8 -*-
"""
Created on Tue Mar 30 09:22:31 2021

@author: andre
"""

""" This example demonstrates how to use the FMU.get*() and FMU.set*() functions
to set custom input and control the simulation
This code is taken from FMPy's homepage with custom_input
https://github.com/CATIA-Systems/FMPy/blob/master/fmpy/examples/custom_input.py
"""

from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from fmpy.util import plot_result
import numpy as np
import shutil

# define the model name and simulation parameters
fmu_filename = 'fmu_test.fmu'
start_time = 0.0
threshold = 2.0
stop_time = 10.0
step_size = 1e-5

# download the FMU
#download_test_file('2.0', 'CoSimulation', 'MapleSim', '2016.2', 'CoupledClutches', fmu_filename)

# read the model description
model_description = read_model_description(fmu_filename)

# collect the value references
vrs = {}
for variable in model_description.modelVariables:
    vrs[variable.name] = variable.valueReference

# get the value references for the variables we want to get/set
vr_inputs   = vrs['u']
vr_outputs4 = vrs['Out1']

# extract the FMU
unzipdir = extract(fmu_filename)

fmu = FMU2Slave(guid=model_description.guid,
                unzipDirectory=unzipdir,
                modelIdentifier=model_description.coSimulation.modelIdentifier,
                instanceName='instance1')

# initialize
fmu.instantiate()
fmu.setupExperiment(startTime=start_time)
fmu.enterInitializationMode()
fmu.exitInitializationMode()

time = start_time

def fun1():
    fmu.terminate()
    fmu.instantiate()
    fmu.setupExperiment(startTime=time)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()
