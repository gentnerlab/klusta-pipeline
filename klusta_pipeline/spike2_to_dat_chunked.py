import h5py as h5
import numpy as np


s2mat = '/mnt/cube/btheilma/matfiles/B1083/Pen03_Lft_AP0_ML1000__Site01_Z2100__B1083_cat_P03_S01_1/SubB1083Pen03Site01Epc01File01_03-29-16+18-58-16_B1083_block.mat'

datfile = '/mnt/cube/btheilma/matfiles/B1083/Pen03_Lft_AP0_ML1000__Site01_Z2100__B1083_cat_P03_S01_1/SubB1083Pen03Site01Epc01File01_03-29-16+18-58-16_B1083_block_chunked.dat'

chunksize = 250000

with h5.File(s2mat, 'r') as f:

	chans = [s for s in f.keys() if 'Port' in s]
	nchans = len(chans)
	nsamps = int(f[chans[0]]['length'][0][0])

	with open(datfile, 'wb') as outfile:
		chunk = 0
		while (chunk)*chunksize < nsamps:
			print('Sample {} of {}'.format(chunk*chunksize, nsamps))
			t_data = np.zeros((chunksize, len(chans)))
			for chnum, chan in enumerate(chans):
				if (chunk+1)*chunksize < nsamps:
					t_data[:, chnum] = f[chan]['values'][0, chunk*chunksize:(chunk+1)*chunksize]
				else:
					t_data = np.zeros((nsamps - chunk*chunksize, nchans))
					t_data = f[chan]['values'][0, chunk*chunksize:]
				t_data_bin = t_data.astype(np.int16).tobytes()
				outfile.write(t_data_bin)
			chunk = chunk+1
