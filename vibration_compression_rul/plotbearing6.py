import os
import matplotlib.pyplot as plt
from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np
plt.close("all")

compopt = 4
path = Path(f'C:\\Users\\andre\\Desktop\\bearing6Compressed')

fig, ax = plt.subplots()

for k, test in enumerate(['500', '250']):
    files = list(path.glob(f'{test}_*.h5'))
    sizes = np.zeros(len(files))

    for i in range(0, len(sizes)):
        sizes[i] = os.stat(files[i]).st_size

    ax.plot(sizes, label=f'{test}')

ax.legend()
plt.show()