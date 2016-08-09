#!/usr/bin/env python
import argparse, os, glob
import datetime, resource
import h5py as h5
import numpy as np
from h5_util import kwd_to_binary


def get_args():
    parser = argparse.ArgumentParser(description='Compile KWD file into flat binary .dat file for kilosort.')
    parser.add_argument('path', default='./', nargs='?',
                        help='directory containing the *.raw.kwd file to extract')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination directory for .dat file')
    parser.add_argument('-c', '--chunking', dest='chunk', action='store_true',
                        help='turns on chunking to minimize memory usage and selection of channels to export '
                             '(at cost of speed)')
    parser.add_argument('--chunk-size', dest='chunk_size', type=int, default=8000000,
                        help='number of samples per chunk, default is 8000000')
    parser.add_argument('--channels', dest='chans', type=str, default='',
                        help='comma-separate list of channels to include in export, default is all of them '
                             '(only in -c mode)')
    return parser.parse_args()


def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    assert len(glob.glob(os.path.join(path, '*.raw.kwd'))) == 1, "Error finding .raw.kwd file in {}".format(path)
    kwd = glob.glob(os.path.join(path, '*.raw.kwd'))[0]
    name = os.path.split(kwd)[-1].split('.')[0]
    out_dat = os.path.join(dest, name + '.dat')
    if args.chunk:
        print "Exporting to binary using chunked version"
        print "Output file: {}".format(out_dat)
        if args.chans == '':
            print "Channels: all channels"
            chan_list = None
        else:
            chan_list = [int(i) for i in args.chans.split(',')]
            print "Channels: {}".format(chan_list)
        print "Chunk size: {} samples".format(args.chunk_size)

        kwd_to_binary(kwd, out_dat, chan_list=chan_list, chunk_size=args.chunk_size)
    else:
        if args.chans is not '':
            raise NotImplementedError
        n_chans = -1
        n_samples = 0
        with h5.File(kwd, 'r') as kwd_f:
            recordings = np.sort(np.array(kwd_f['recordings'].keys(), dtype=int)).astype('unicode')
            for recording in recordings:
                assert n_chans == -1 or n_chans == kwd_f['recordings'][recording]['data'].shape[1]
                n_chans = kwd_f['recordings'][recording]['data'].shape[1]
                n_samples += kwd_f['recordings'][recording]['data'].shape[0]
            print "total number of samples %d" % (n_samples)
            data = np.empty((n_samples, n_chans), dtype='int16')
            idx = 0
            for recording in recordings:
                rec_len = kwd_f['recordings'][recording]['data'].shape[0]
                print "loading recording %s with length of %d" % (recording, rec_len)
                data[idx:idx + rec_len, :] = kwd_f['recordings'][recording]['data']
                idx += rec_len
        print "writing data"
        with open(out_dat, 'wb') as outfile:
            outfile.write(data.tobytes())

    print 'peak memory usage: %f GB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024. / 1024.)
    print 'time elapsed: %s' % (datetime.datetime.now() - tstart)


if __name__ == '__main__':
    main()
