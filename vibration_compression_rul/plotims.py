import os
import matplotlib.pyplot as plt
from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np
plt.close("all")

test = 2
fig, ax = plt.subplots()
for compopt in [10]:
    path = Path(f'C:\\Users\\andre\\Desktop\\IMSCompressed\\{test}').absolute()

    files = list(path.glob(f'*_{compopt}.h5'))

    sizes = np.zeros(len(files))

    for i in range(0, len(sizes)):
        sizes[i] = os.stat(files[i]).st_size

    ax.plot(sizes, label=f'{compopt}')

ax.legend()
plt.show()