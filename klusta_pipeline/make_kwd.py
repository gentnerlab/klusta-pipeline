#!/usr/bin/env python
import os
import argparse
import glob
from klusta_pipeline.maps import port_site
from klusta_pipeline.dataio import load_recordings, load_catlog
from klusta_pipeline.dataio import save_info, save_recording, save_chanlist, save_probe, save_parameters
from klusta_pipeline.utils import get_import_list, validate_merge, realign, calc_weights, do_war, do_car
from klusta_pipeline.probe import get_channel_groups, clean_dead_channels, build_geometries

# assume spike2 export to mat with the following parameters:
# - channel names are "Port_N" where N is the 1-indexed 1401 Port number

def get_args():

    parser = argparse.ArgumentParser(description='Compile Spike2 epoch .mat files into KlustaKwik KWD file.')
    parser.add_argument('rig',type=str, 
                       help='defines the rig that the data was collected on')
    parser.add_argument('probe',type=str, 
                       help='defines the probe that the data was collected on')
    parser.add_argument('path', default = './', nargs='?',
                       help='directory containing all of the mat files to compile')
    parser.add_argument('dest', default = './', nargs='?',
                       help='destination directory for kwd and other files')
    parser.add_argument('-s','--sampling_rate',dest='fs',type=float, default=None,
                       help='target sampling rate for waveform alignment')
    parser.add_argument('-c','--common_average_ref',dest='car',action='store_true',
                       help='turns on common average referencing')
    parser.add_argument('-w','--weighted',dest='weighted',action='store_true',
                       help='weights channels for common average referencing')
    parser.add_argument('-x','--drop',dest='omit',type=str, default='',
                       help='comma-separate list of channel labels to drop if they exist')

    return parser.parse_args()

def main():
    args = get_args()
    path = os.path.abspath(args.path)
    dest = os.path.abspath(args.dest)

    info = dict(args.__dict__)

    catlog = glob.glob(os.path.join(path,'*.catLog'))[0]
    info['name'] = os.path.split(catlog)[-1].split('.')[0]

    kwd = os.path.join(dest, info['name'] + '.raw.kwd')
    if os.path.exists(kwd):
        raise IOError('%s already exists, please delete or rename and run again' % kwd)

    info['exports'] = load_catlog(catlog)
    import_list = get_import_list(path,info['exports'])
    for item in import_list:
        assert os.path.exists(item), item

    omit = args.omit.split(',')
    mat_data = validate_merge(import_list,omit)

    chans = set(mat_data[0]['chans'])
    for d2 in mat_data[1:]:
        chans = chans.intersection(d2['chans'])
    chans = list(chans)

    for i,m in zip(info['exports'],mat_data):
        i['chans'] = chans

    port_map = port_site[args.rig]
    save_chanlist(dest,chans,port_map)
    save_probe(args.probe,chans,port_map,dest)

    fs = 1.0 / mat_data[0][chans[0]]['interval'] if args.fs is None else args.fs

    info['params'] = {
        'exp': info['name'],
        'fs': fs,
        'nchan': len(chans),
        'probe': args.probe,
    }
    save_parameters(info['params'],dest)
    save_info(dest,info)

    rec_list = []
    # print import_list
    for import_file in import_list:
        recordings = load_recordings(import_file,chans)
        for r in recordings:
            rec = realign(r,chans,args.fs)
            rec['data'] -= rec['data'].mean(axis=0)
            rec_list.append(rec)

    weights = calc_weights(rec_list) if args.weighted else None

    for indx, rec in enumerate(rec_list):
        if args.weighted:
            rec['data'] = do_war(rec['data'],weights)
        elif args.car:
            rec['data'] = do_car(rec['data'])

        save_recording(kwd,rec,indx)

if __name__ == '__main__':
    main()
