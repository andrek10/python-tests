"""Test random seed and reloading
"""

from importlib import reload

import numpy as np

import algorithms
import module

reload(algorithms)

if __name__ == "__main__":
    np.random.seed(43)
    algorithms.fun1()
    module.fun2()
