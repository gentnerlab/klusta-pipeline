
# Merge stimuli information from spike2 mat file into Kwik file

import h5py as h5
import tables
import os
import numpy as np
import argparse
import glob

try: import simplejson as json
except ImportError: import json

from klusta_pipeline.dataio import load_recordings, save_info, load_digmark, load_stim_info
from klusta_pipeline.utils import get_import_list, validate_merge, realign

def get_args():

    parser = argparse.ArgumentParser(description='Compile Spike2 epoch .mat files into KlustaKwik KWD file.')
    parser.add_argument('path', default = './', nargs='?',
                       help='directory containing all of the mat files to compile')
    parser.add_argument('dest', default = './', nargs='?',
                       help='destination directory for kwd and other files')
    return parser.parse_args()

def get_rec_samples(kwd_file,index):
    with h5.File(kwd_file, 'r') as kwd:
        return kwd['/recordings/{}/data'.format(index)].shape[0]

def merge_recording_info(klu_path,mat_path):
    batch = klu_path.split('__')[-1]
    with open(os.path.join(klu_path,batch+'_info.json')) as f:
        info = json.load(f)

    assert 'recordings' not in info

    import_list = get_import_list(mat_path,info['exports'])
    for item in import_list:
        assert os.path.exists(item), item

    mat_data = validate_merge(import_list,info['omit'])
    fs = info['params']['fs']

    chans = set(mat_data[0]['chans'])
    for d2 in mat_data[1:]:
        chans = chans.intersection(d2['chans'])
    chans = list(chans)

    for i,m in zip(info['exports'],mat_data):
        i['chans'] = chans

    rec_list = []
    for import_file in import_list:
        recordings = load_recordings(import_file,chans)
        for r in recordings:
            rec = realign(r,chans,fs,'spline')
            del rec['data']
            rec_list.append(rec)

    info['recordings'] = [{k:v for k,v in rec.items() if k is not 'data'} for rec in rec_list]
    save_info(klu_path,info)
    return info


def merge(spike2mat_folder, kwik_folder):

    info_json = glob.glob(os.path.join(kwik_folder,'*_info.json'))[0]
    with open(info_json, 'r') as f:
        info = json.load(f)

    kwik_data_file = os.path.join(kwik_folder,info['name']+'.kwik')
    kwd_raw_file = os.path.join(kwik_folder,info['name']+'.raw.kwd')\

    with tables.open_file(kwik_data_file, 'r+') as kkfile:

        digmark_timesamples = []
        digmark_recording = []
        digmark_codes = []
        stimulus_timesamples = []
        stimulus_recording = []
        stimulus_codes = []
        stimulus_names = []

        spike_recording_obj = kkfile.get_node('/channel_groups/0/spikes','recording')
        spike_time_samples_obj = kkfile.get_node('/channel_groups/0/spikes','time_samples')

        spike_recording = spike_recording_obj.read()
        spike_time_samples = spike_time_samples_obj.read()

        try:
            assert 'recordings' in info
        except AssertionError:
            info = merge_recording_info(kwik_folder,spike2mat_folder)


        order = np.sort([str(ii) for ii in range(len(info['recordings']))])
        print order

        done = []
        for rr,rid_str in enumerate(order):
            # rr: index of for-loop
            # rid: recording id
            # rid_str: string form of recording id
            rid = int(rid_str)
            rec = info['recordings'][rid_str]

            n_samps = get_rec_samples(kwd_raw_file,rid)

            is_done = np.vectorize(lambda x: x not in done)

            rec_mask = is_done(spike_recording) * (spike_time_samples >= n_samps)
            print rec_mask.sum()
            spike_recording[rec_mask] = order[rr+1]
            spike_time_samples[rec_mask] -= n_samps

            t0 = rec['start_time']
            fs = rec['fs']
            dur = float(n_samps) / fs

            s2mat = os.path.split(rec['file_origin'])[-1]
            s2mat = os.path.join(spike2mat_folder, s2mat)

            codes, times = load_digmark(s2mat)
            rec_mask = (times >= t0) * (times < (t0+dur))

            codes = codes[rec_mask]
            times = times[rec_mask] - t0
            time_samples = (times * fs).round().astype(np.uint64)
            recording = rr * np.ones(codes.shape,np.uint16)

            digmark_timesamples.append(time_samples)
            digmark_recording.append(recording)
            digmark_codes.append(codes)

            codes, times, names = load_stim_info(s2mat)
            rec_mask = (times >= t0) * (times < (t0+dur))

            codes = codes[rec_mask]
            names = names[rec_mask]
            times = times[rec_mask] - t0
            time_samples = (times * fs).round().astype(np.uint64)
            recording = rr * np.ones(codes.shape,np.uint16)

            stimulus_timesamples.append(time_samples)
            stimulus_recording.append(recording)
            stimulus_codes.append(codes)
            stimulus_names.append(names)

            done.append(rid)

        digmark_timesamples = np.concatenate(digmark_timesamples)
        digmark_recording = np.concatenate(digmark_recording)
        digmark_codes = np.concatenate(digmark_codes)
        stimulus_timesamples = np.concatenate(stimulus_timesamples)
        stimulus_recording = np.concatenate(stimulus_recording)
        stimulus_codes = np.concatenate(stimulus_codes)
        stimulus_names = np.concatenate(stimulus_names)

        print digmark_timesamples.dtype
        print digmark_recording.dtype
        print digmark_codes.dtype
        print stimulus_timesamples.dtype
        print stimulus_recording.dtype
        print stimulus_codes.dtype
        print stimulus_names.dtype

        kkfile.create_group("/", "event_types", "event_types")

        kkfile.create_group("/event_types", "DigMark")
        kkfile.create_earray("/event_types/DigMark", 'time_samples', obj=digmark_timesamples)
        kkfile.create_earray("/event_types/DigMark", 'recording', obj=digmark_recording)
        kkfile.create_earray("/event_types/DigMark", 'codes', obj=digmark_codes)


        kkfile.create_group("/event_types", "Stimulus")
        kkfile.create_earray("/event_types/Stimulus", 'time_samples', obj=stimulus_timesamples)
        kkfile.create_earray("/event_types/Stimulus", 'recording', obj=stimulus_recording)
        kkfile.create_earray("/event_types/Stimulus", 'codes', obj=stimulus_codes)
        kkfile.create_earray("/event_types/Stimulus", 'text', obj=stimulus_names)

        spike_recording_obj[:] = spike_recording
        spike_time_samples_obj[:] = spike_time_samples


def main():
    args = get_args()
    spike2mat_folder = os.path.abspath(args.path)
    kwik_folder = os.path.abspath(args.dest)
    merge(spike2mat_folder, kwik_folder)


if __name__ == '__main__':
    main()


