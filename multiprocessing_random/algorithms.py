"""Module
"""

import numpy as np

def fun1(seed):
    """Generate random numbers

    Parameters
    ----------
    seed : int
        Seed

    Returns
    -------
    array
        Random numbers
    """
    np.random.seed(seed)
    return np.random.randn(5)