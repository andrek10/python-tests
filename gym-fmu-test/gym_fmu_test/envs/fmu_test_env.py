'''
Making a gym for FMU testing
Cartpole code: https://github.com/openai/gym/blob/master/gym/envs/classic_control/cartpole.py
Making a custom env: https://github.com/openai/gym/blob/master/docs/creating-environments.md
'''

import gym
from gym import error, spaces, utils
from gym.utils import seeding

from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from fmpy.util import plot_result, download_test_file
import numpy as np
import shutil

class FmuTestEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        # define the model name and simulation parameters
        fmu_filename = 'fmu_test.fmu'
        start_time = 0.0
        stop_time = 10.0
        self.step_size = 1e-5

        # read the model description
        model_description = read_model_description(fmu_filename)

        # collect the value references
        vrs = {}
        for variable in model_description.modelVariables:
            vrs[variable.name] = variable.valueReference

        # get the value references for the variables we want to get/set
        self.vr_inputs   = vrs['u']
        self.vr_output = vrs['Out1']

        # extract the FMU
        unzipdir = extract(fmu_filename)
        self.fmu = FMU2Slave(guid=model_description.guid,
                        unzipDirectory=unzipdir,
                        modelIdentifier=model_description.coSimulation.modelIdentifier,
                        instanceName='instance1')

        # initialize
        self.fmu.instantiate()
        self.fmu.setupExperiment(startTime=start_time)
        self.fmu.enterInitializationMode()
        self.fmu.exitInitializationMode()

        self.time = start_time

    def step(self, action):
        # set the input
        self.fmu.setReal([self.vr_inputs], [action])

        # perform one step
        self.fmu.doStep(currentCommunicationPoint=self.time, communicationStepSize=self.step_size)

        # get the current state after input
        self.state = self.fmu.getReal([self.vr_output])
    def reset(self):
        pass
    def render(self, mode='human'):
        pass
    def close(self):
        pass