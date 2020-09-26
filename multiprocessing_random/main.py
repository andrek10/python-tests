"""Test multiprocessing and random generation seed
"""

from multiprocessing import Process

import algorithms

def node(seed_list):
    """Tasks for each node

    Parameters
    ----------
    seed_list : array
        Seeds to try
    """
    for seed in seed_list:
        print('Seed', seed, ':', algorithms.fun1(seed))

if __name__ == "__main__":
    PROCESS_LIST = []
    SEED_LIST = [10, 20, 30, 40]
    for i in range(0, 2):
        PROCESS_LIST.append(Process(target=node, args=(SEED_LIST,)))
        PROCESS_LIST[-1].start()
        print(f'Started process {i}')
    # Join the processing threads first
    for i, PROCESS in enumerate(PROCESS_LIST):
        PROCESS.join()
        print(f'Process {i} finished')
