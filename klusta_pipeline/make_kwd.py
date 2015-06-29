#!/usr/bin/env python
import os
import argparse
import itertools
import glob
import h5py as h5
import numpy as np
from scipy import interpolate

# assume spike2 export to mat with the following parameters:
# - channel names are "Port_N" where N is the 1-indexed 1401 Port number

MAX_CHAN = 48

def get_args():

    parser = argparse.ArgumentParser(description='Compile Spike2 epoch .mat files into KlustaKwik KWD file.')
    parser.add_argument('export', default = './', nargs='?',
                       help='directory containing all of the mat files to compile')
    parser.add_argument('-s','--sampling_rate',dest='fs',type=float, default=20000.0,
                       help='target sampling rate for waveform alignment')
    parser.add_argument('-c','--common_average_ref',dest='car',action='store_true', default=False,
                       help='turns on common average referencing')

    return parser.parse_args()

def validate_merge(export):
    mat_data = []
    for s2mat in glob.glob(export + '\\*.mat'):
        mat_chans=[]
        with h5.File(s2mat, 'r') as f:
            for ch in ['Port_%i'%(p+1) for p in range(MAX_CHAN)]:
                try:
                    chan_data = f[ch]
                    mat_chans.append(ch)
                except KeyError:
                    continue
        mat_data.append(
            {
                'chans': mat_chans,
                'name': s2mat,
            }
        )
    assert len(mat_data)>0, 'No mat files found'
    ref = mat_data[0]
    for chk in mat_data[1:]:
        # check if all files have same number of chans
        assert len(ref['chans'])==len(chk['chans'])
        # check if all files have same chans
        for ch in ref['chans']:
            assert ch in chk['chans']

    return ref['chans']

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)

def chunkit(t,v):
    dt = np.diff(t)
    interval = min(dt)
    breaks = np.nonzero(dt>1.5*interval)[0]
    if len(breaks)>0:
        yield t[0:breaks[0]],v[0:breaks[0]]
        for start,stop in pairwise(breaks):
            yield t[start+1:stop],v[start+1:stop]
        yield t[breaks[-1]+1:],v[breaks[-1]+1:]
    else:
        yield t,v
        

def load_recordings(export,chans):
    recordings = []
    for s2mat in glob.glob(export + '\\*.mat'):
        print 'Loading %s' % s2mat
        s2mat_recordings = []
        with h5.File(s2mat, 'r') as f:
            for ch in chans:
                chan_data = f[ch]
                times = chan_data['times'][0]
                values = chan_data['values'][0]
                for ii, (t,v) in enumerate(chunkit(times,values)):
                    d = {ch: {'times':t,'values':v}}
                    try:
                        s2mat_recordings[ii].update(d)
                    except IndexError:
                        print ' rec %i (%0.2f seconds long)' % (ii,t[-1]-t[0])
                        s2mat_recordings.append(d)
                print '  %s' % ch
            recordings += s2mat_recordings
    return recordings

def get_kwd(export):
    # catLog = glob.glob(export+'\\*.catLog')[0]
    exp = export.split('\\')[-1]
    return os.path.join(export, exp + '.raw.kwd')

def do_car(data):
    '''for each channel, subtract off the mean of the other channels'''
    car_data = np.empty(data.shape,data.dtype)
    for ch,waveform in enumerate(data.T):
        common_av = np.vstack((data.T[:ch,:],data.T[ch+1:,:])).mean(axis=0)
        car_data[:,ch] = waveform-common_av
    return car_data

def transform(r,chans,fs):

    start = np.amax([d['times'][0] for d in r.values()])
    stop = np.amin([d['times'][-1] for d in r.values()])
    t_new = np.arange(start,stop,1.0/fs)

    shape = len(t_new), len(chans) 
    data = np.empty(shape,np.int16)

    for ch,lbl in enumerate(chans):
        spline = interpolate.InterpolatedUnivariateSpline(r[lbl]['times'], r[lbl]['values'])
        data[:,ch] = spline(t_new)

    return data

def transform_recordings(recordings,chans,fs,car):
    dataset = []
    while len(recordings)>0:
        r = recordings.pop(0)
        data = transform(r,chans,fs)
        if car==True:
            data = do_car(data)
        dataset.append(data)

    return dataset

def save_dataset(kwd,dataset):
    print 'saving %i recordings to raw.kwd...' % len(dataset)
    with h5.File(kwd, 'w') as kwd_f:
        for rec, data in enumerate(dataset):
            print ' saving...'
            kwd_f.create_dataset('recordings/%i/data' % rec, data=data)
            print ' saved!'
            
def save_chanlist(kwd_dir,chans):
    chanfile = os.path.join(kwd_dir,'kwd_chans.txt')
    with open(chanfile,'w') as f:
        for ch in chans:
            f.write('%s\n'%ch)
    print 'chans saved to %s' % chanfile
    

def main():
    args = get_args()
    export = os.path.abspath(args.export)
    kwd = get_kwd(export)

    if not os.path.exists(kwd):
        chans = validate_merge(export)
        recordings = load_recordings(export,chans)
        dataset = transform_recordings(recordings,chans,args.fs,args.car)
        save_dataset(kwd,dataset)
        save_chanlist(export,chans)
    else: 
        raise IOError('%s already exists, please delete or rename and run again' % kwd)

    # # copy over the spike template
    # try:
    #     copyfile(os.path.join(KK_PIPELINE_DIR, params['probe'] + ".prb"), os.path.join(os.getcwd(), params['probe'] + ".prb"))
    # except IOError:
    #     print "Could not copy probe file %s to current directory. You'll have to do this manually." % os.path.join(KK_PIPELINE_DIR,params['probe'] + ".prb")

    # # read the parameters template
    # params_template_in = os.path.join(KK_PIPELINE_DIR,'params.template')
    # with open(params_template_in,'r') as src:
    #     params_template = Template(src.read())

    # # write the parameters
    # with open('params.prm', 'w') as pf:
    #     pf.write(params_template.substitute(params))

if __name__ == '__main__':
    main()
