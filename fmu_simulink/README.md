# fmu_simulink

Test opening an FMU that is exported from Simulink using (Simulix)[https://github.com/Kvixen/Simulix].

Open the FMU in Python using (FPMy)[https://github.com/CATIA-Systems/FMPy]

Make the following environment:
```
conda create -n rlgym -y anaconda=2020.11
conda install -n rlgym -y -c pytorch pytorch torchvision torchaudio cpuonly
conda install -n rlgym -y -c conda-forge fmpy
conda activate rlgym
pip install gym
pip install fmipp --prefer-binary
```
