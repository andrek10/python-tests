from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np

test = 2
compopt = 10
path = Path(f'C:\\Users\\andre\\Desktop\\IMSCompressed\\{test}')

if test == 1:
    vibrationString = 'vib6'
elif test == 2:
    vibrationString = 'vib1'
elif test == 3:
    vibrationString = 'vib3'

ims = ak.load.IMS('E:', test, [vibrationString])

for i in range(0, len(ims)):
    vib = ims[i]
    h5 = h5py.File(path.joinpath(f'{str(i).zfill(10)}_{compopt}.h5'), 'w')
    # h5.create_dataset('vib', data=vib, compression='gzip', compression_opts=compopt, shuffle=True)
    h5.create_dataset('vib', data=vib, compression='lzf')
    h5.close()
    if i % 10 == 0:
        print(f'Finished {i}')