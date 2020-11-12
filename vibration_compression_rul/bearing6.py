from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np

compopt = 4
path = Path(f'C:\\Users\\andre\\Desktop\\bearing6Compressed')

for test in ['500', '250']:
    b6 = ak.load.Bearing6('E:', 10, test, ['vib'])
    for i in range(0, len(b6)):
    # for i in range(0, 1):
        vib, = b6[i]
        h5 = h5py.File(path.joinpath(f'{test}_{str(i).zfill(10)}_{compopt}.h5'), 'w')
        h5.create_dataset('vib', data=vib[:61440], compression='gzip', compression_opts=compopt, shuffle=True)
        # h5.create_dataset('vib', data=vib, compression='lzf')
        h5.close()
        if i % 10 == 0:
            print(f'Finished {i} of {len(b6)} in {test}')