#!/usr/bin/env python
"""Extract spiketimes from mountainsort MDA to kwik file
"""
import argparse
import os
import glob
import datetime
import resource
from .mdaio import readmda
from .h5_util import KwikFile


def get_args():
    parser = argparse.ArgumentParser(
        description='Extract spiketimes from mountainsort MDA to kwik file')
    parser.add_argument(
        'path',
        default='./',
        nargs='?',
        help='mountainsort folder containing mda file to convert')
    parser.add_argument('dest', default='./', nargs='?',
                        help='desination kwd directory for kwik file')
    parser.add_argument(
        '--mda-filename',
        dest='mda_filename',
        type=str,
        default='firings.mda')
    return parser.parse_args()


def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    file_names = {'mda': args.mda_filename,
                  'param': 'params.json'}

    for file_type in file_names:
        if len(glob.glob(os.path.join(path, file_names[file_type]))) == 1:
            file_names[file_type] = glob.glob(
                os.path.join(path, file_names[file_type]))[0]
        else:
            file_names[file_type] = False
            print('%s file type not found' % (file_type))

    assert len(glob.glob(os.path.join(dest, '*.raw.kwd'))
               ) == 1, "Error finding .raw.kwd file in {}".format(dest)
    file_names['kwd'] = glob.glob(os.path.join(dest, '*.raw.kwd'))[0]
    name = os.path.split(file_names['kwd'])[-1].split('.')[0]
    file_names['kwk'] = os.path.join(dest, name + '.kwik')

    k = KwikFile(file_names)
    k.make_spk_tables(realign_to_recordings=False)
    k.make_rec_groups()
    k.make_clu_groups()

    print(
        'peak memory usage: %f GB' %
        (resource.getrusage(
            resource.RUSAGE_SELF).ru_maxrss /
            1024. /
            1024.))
    print('time elapsed: %s' % (datetime.datetime.now() - tstart))
