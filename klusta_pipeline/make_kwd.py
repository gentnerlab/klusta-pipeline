#!/usr/bin/env python
import os
import argparse
import glob
from klusta_pipeline.maps import port_site
from klusta_pipeline.dataio import load_recordings, load_catlog
from klusta_pipeline.dataio import save_info, save_recording, save_chanlist, save_probe, save_parameters
from klusta_pipeline.utils import get_import_list, validate_merge, transform_recording
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
    parser.add_argument('-s','--sampling_rate',dest='fs',type=float, default=20000.0,
                       help='target sampling rate for waveform alignment')
    parser.add_argument('-c','--common_average_ref',dest='car',type=str, default='',
                       help='turns on common average referencing')
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
        assert os.path.exists(item)

    omit = args.omit.split(',')
    mat_data = validate_merge(import_list,omit)
    chans = mat_data[0]['chans']

    for i,m in zip(info['exports'],mat_data):
        i['chans'] = m['chans']

    port_map = port_site[args.rig]
    save_chanlist(dest,chans,port_map)
    save_probe(args.probe,chans,port_map,dest)

    info['params'] = {
        'exp': info['name'],
        'fs': args.fs,
        'nchan': len(chans),
        'probe': args.probe,
    }
    save_parameters(info['params'],dest)
    save_info(dest,info)

    rec_indx = 0
    # print import_list
    for import_file in import_list:
        recordings = load_recordings(import_file,chans)
        for r in recordings:
            rec = transform_recording(r,chans,args.fs,args.car)
            save_recording(kwd,rec,rec_indx)
            rec_indx += 1

if __name__ == '__main__':
    main()
