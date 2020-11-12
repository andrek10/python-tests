import os
import matplotlib.pyplot as plt
from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np
plt.close("all")

compopt = 4
path = Path(f'C:\\Users\\andre\\Desktop\\PHMCompressed')

fig, axes = plt.subplots(4,5)
axes = axes.ravel()

for k, test in enumerate(['1_1', '1_2', '1_3', '1_4', '1_5', '1_6', '1_7', '2_1', '2_2', '2_3', '2_4', '2_5', '2_6', '2_7', '3_1', '3_2', '3_3']):
    ax = axes[k]
    files = list(path.glob(f'{test}_*.h5'))
    sizes = np.zeros(len(files))

    for i in range(0, len(sizes)):
        sizes[i] = os.stat(files[i]).st_size

    ax.plot(sizes, label=f'{test}')

ax.legend()
plt.show()