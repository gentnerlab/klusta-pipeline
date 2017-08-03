#!/usr/bin/env python
import argparse, os, glob
import datetime, resource
from string import Template
from klusta_pipeline import TEMPLATE_DIR

def get_args():
    parser = argparse.ArgumentParser(description='Compile KWD file into flat binary .dat file for kilosort.')
    parser.add_argument('path', default='./', nargs='?',
                        help='kwd directory containing the *.prb file to extract')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination directory for chanMap.mat file')
    parser.add_argument('local_sort_dir', default='./', nargs='?',
                        help='local data directory on sorting computer')
    parser.add_argument('--kilodir', default='/home/mthielk/github/KiloSort', 
                                dest='kilodir', type=str, 
                                help='path to kilosort folder')
    parser.add_argument('--npy_matdir', default='/home/mthielk/github/npy-matlab',
                                dest='npy_matdir', type=str,
                                help='path to npy-matlab scripts')
    parser.add_argument('-s', '--sampling_rate', dest='fs', type=float, default=None,
                                help='target sampling rate for waveform alignment. If omitted, uses recording sampling rate')
    parser.add_argument('--Nchan', dest='Nchan', type=float, default=None,
                                help='Target number of channels. If omitted, uses recording value')
    parser.add_argument('--Nfilt', dest='Nfilt', type=float, default=96,
                                help='Target number of filters for kilosort to use. 2-4 times more than Nchan, should be a multiple of 32. Defaults to 96')
    return parser.parse_args()

def main():
    args = get_args()
    tstart = datetime.datetime.now()

    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    assert len(glob.glob(os.path.join(path,'*.raw.kwd')))==1, "Error finding .raw.kwd file"
    catlog = glob.glob(os.path.join(path,'*.raw.kwd'))[0]
    blockname = os.path.split(catlog)[-1].split('.')[0]

    if args.fs is None or args.Nchan is None:
        params_file = os.path.join(path, 'params.prm')
        with open(params_file, 'r') as f:
            contents = f.read()
        metadata = {}
        exec(contents, {}, metadata)

    if args.fs is None:
        fs = metadata['traces']['sample_rate']
    else:
        fs = args.fs

    if args.Nchan is None:
        Nchan = metadata['traces']['nchannels']
    else:
        Nchan = args.Nchan

    params = {
        'kilodir': args.kilodir,
        'npy_matdir': args.npy_matdir,
        'datadir': args.local_sort_dir,
        'blockname': blockname,
        'fs': fs,
        'Nchan': Nchan,
        'Nfilt': args.Nfilt
    }

    with open(os.path.join(TEMPLATE_DIR, 'master.template'), 'r') as src:
        master_template = Template(src.read())
    with open(os.path.join(TEMPLATE_DIR, 'config.template'), 'r') as src:
        config_template = Template(src.read())

    with open(os.path.join(dest, 'master.m'), 'w') as f:
        f.write(master_template.substitute(params))
    with open(os.path.join(dest, 'config.m'), 'w') as f:
        f.write(config_template.substitute(params))

    print 'peak memory usage: %f GB' % (resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024. / 1024.)
    print 'time elapsed: %s' % (datetime.datetime.now() - tstart)