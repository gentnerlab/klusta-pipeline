#!/usr/bin/env python
"""generates MDA file for mountainsort
"""
import argparse
import os
import glob
import h5py as h5
import numpy as np
import datetime
import resource
from .mdaio import writemda16i


def get_args():
    parser = argparse.ArgumentParser(
        description='Compile KWD file into MDA file for mountainsort.')
    parser.add_argument(
        'path',
        default='./',
        nargs='?',
        help='directory containing the *.raw.kwd file to extract')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination directory for raw.mda file')
    return parser.parse_args()


def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    assert len(glob.glob(os.path.join(path, '*.raw.kwd'))
               ) == 1, "Error finding .raw.kwd file in {}".format(path)
    kwd = glob.glob(os.path.join(path, '*.raw.kwd'))[0]
    out_mda = os.path.join(dest, 'raw.mda')

    n_chans = -1
    n_samples = 0
    with h5.File(kwd, 'r') as kwd_f:
        recordings = np.sort(
            np.array(
                list(
                    kwd_f['recordings'].keys()),
                dtype=int)).astype('unicode')
        for recording in recordings:
            assert n_chans == - \
                1 or n_chans == kwd_f['recordings'][recording]['data'].shape[1]
            n_chans = kwd_f['recordings'][recording]['data'].shape[1]
            n_samples += kwd_f['recordings'][recording]['data'].shape[0]
        print("total number of samples %d" % (n_samples))
        data = np.empty((n_samples, n_chans), dtype='int16')
        idx = 0
        for recording in recordings:
            rec_len = kwd_f['recordings'][recording]['data'].shape[0]
            print(
                "loading recording %s with length of %d" %
                (recording, rec_len))
            data[idx:idx + rec_len, :] = kwd_f['recordings'][recording]['data']
            idx += rec_len

    print("writing data")
    writemda16i(data.T, out_mda)

    print(
        'peak memory usage: %f GB' %
        (resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss /
            1024. /
            1024.))
    print('time elapsed: %s' % (datetime.datetime.now() - tstart))


if __name__ == '__main__':
    main()
