#!/usr/bin/env python
import argparse, os, glob
import datetime, resource
from string import Template
from klusta_pipeline import TEMPLATE_DIR
from h5_util import KwikFile

def get_args():
    parser = argparse.ArgumentParser(description='Compile KWD file into flat binary .dat file for kilosort.')
    parser.add_argument('path', default='./', nargs='?',
                        help='kilo directory containing the npy file to convert')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination kwd directory for kwik file')
    return parser.parse_args()

def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    file_names = {'clu': 'spike_clusters.npy',
             'spk': 'spike_times.npy',
              'grp': 'cluster_groups.csv',
              'par': 'params.py',
              'temp': 'spike_templates.npy',
             }

    for file_type in file_names:
        if len(glob.glob(os.path.join(path, file_names[file_type]))) == 1:
            file_names[file_type] = glob.glob(os.path.join(path, file_names[file_type]))[0]
        else:
            file_names[file_type] = False

    assert len(glob.glob(os.path.join(dest, '*.raw.kwd'))) == 1, "Error finding .raw.kwd file in {}".format(dest)
    file_names['kwd'] = glob.glob(os.path.join(dest, '*.raw.kwd'))[0]
    name = os.path.split(file_names['kwd'])[-1].split('.')[0]
    file_names['kwk'] = os.path.join(dest, name + '.kwik')

    k = KwikFile(file_names)
    k.make_spk_tables()
    k.make_rec_groups()
    k.make_clu_groups()

    print 'peak memory usage: %f GB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024. / 1024.)
    print 'time elapsed: %s' % (datetime.datetime.now() - tstart)