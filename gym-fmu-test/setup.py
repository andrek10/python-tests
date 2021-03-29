'''
Add custom file to setup: https://stackoverflow.com/questions/1612733/including-non-python-files-with-setup-py
'''

from setuptools import setup

setup(name='gym-fmu-test',
      version='0.0.1',
      install_requires=['gym','fmpy','numpy'],  # And any other dependencies foo needs
      package_data={'': ['fmu_test.fmu']},
)