#!/usr/bin/env python
import argparse
import os
import glob
import datetime
import resource
import numpy as np
import scipy as sp
import scipy.io as sio


def get_args():
    parser = argparse.ArgumentParser(
        description='Compile KWD file into flat binary .dat file for kilosort.')
    parser.add_argument(
        'path',
        default='./',
        nargs='?',
        help='kwd directory containing the *.prb file to extract')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination directory for chanMap.mat file')
    return parser.parse_args()


def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    assert len(glob.glob(os.path.join(path, '*.prb'))
               ) == 1, "Error finding .prb file in {}".format(path)
    prb_file = glob.glob(os.path.join(path, '*.prb'))[0]

    with open(prb_file, 'r') as f:
        contents = f.read()
    metadata = {}
    exec(contents, {}, metadata)

    Nchannels = 0
    for group in metadata['channel_groups']:
        Nchannels = max(
            Nchannels, np.max(
                metadata['channel_groups'][group]['channels']))
    Nchannels += 1

    connected = np.array([True] * Nchannels).reshape((Nchannels, 1))
    chanMap = np.arange(Nchannels) + 1
    chanMap0ind = np.arange(Nchannels)

    xcoords = np.ones((Nchannels, 1)) * -1
    ycoords = np.ones((Nchannels, 1)) * -1
    kcoords = np.ones((Nchannels, 1)) * -1

    for group in metadata['channel_groups']:
        for channel in metadata['channel_groups'][group]['geometry']:
            xcoords[channel], ycoords[channel] = metadata['channel_groups'][group]['geometry'][channel]
            kcoords[channel] = group + 1

    chan_map = {'Nchannels': Nchannels,
                'connected': connected,
                'chanMap': chanMap,
                'chanMap0ind': chanMap0ind,
                'xcoords': xcoords,
                'ycoords': ycoords,
                'kcoords': kcoords}
    sio.savemat(os.path.join(dest, 'chanMap.mat'), chan_map)

    print(('peak memory usage: %f GB' %
           (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024. / 1024.)))
    print(('time elapsed: %s' % (datetime.datetime.now() - tstart)))
