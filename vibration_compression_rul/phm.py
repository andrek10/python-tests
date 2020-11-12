from pathlib import Path
import ak4_1_1 as ak
import h5py
import numpy as np

compopt = 4
path = Path(f'C:\\Users\\andre\\Desktop\\PHMCompressed')

for test in ['1_1', '1_2', '1_3', '1_4', '1_5', '1_6', '1_7', '2_1', '2_2', '2_3', '2_4', '2_5', '2_6', '2_7', '3_1', '3_2', '3_3']:
    phm = ak.load.PHM('E:', test, ['vibv'])
    for i in range(0, len(phm)):
        vib = phm[i]
        h5 = h5py.File(path.joinpath(f'{test}_{str(i).zfill(10)}_{compopt}.h5'), 'w')
        h5.create_dataset('vib', data=vib, compression='gzip', compression_opts=compopt, shuffle=True)
        # h5.create_dataset('vib', data=vib, compression='lzf')
        h5.close()
        if i % 10 == 0:
            print(f'Finished {i} in {test}')