from gym.envs.registration import register

register(
    id='fmu-test-v0',
    entry_point='gym_fmu_test.envs:FmuTestEnv',
)
