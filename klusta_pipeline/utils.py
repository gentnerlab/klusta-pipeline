import os
import glob
import itertools
import numpy as np
import h5py as h5
from scipy import interpolate
from random import sample
from klusta_pipeline import MAX_CHANS
import datetime as dt
from sklearn.linear_model import LinearRegression

def validate_merge(import_list,omit):
    mat_data = []
    chans = ['Port_%i'%(p+1) for p in range(MAX_CHANS)]
    chans = [ch for ch in chans if ch not in omit]
    for s2mat in import_list:
        mat_chans=[]
        with h5.File(s2mat, 'r') as f:
            for ch in chans:
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
            # check if all files have same sampling rate
            #assert ref[ch]['interval']==chk[ch]['interval']

    return mat_data


def get_pen(penstr):
    '''extracts penetration data from the penetration folder'''
    pen = penstr.split('_')
    d = dict(
        index = int(pen[0][3:]),
        hemisphere = {'Rgt':'right','Lft':'left'}[pen[1]],
        anterior = int(pen[2][2:]),
        lateral = int(pen[3][2:]),
        )
    return d

def get_site(sitestr):
    '''extracts site data from the site folder'''
    site = sitestr.split('_')
    d = dict(
        index = int(site[0][4:]),
        depth = int(site[1][1:]),
    )
    return d

def get_epoch(epcstr):
    '''extracts epoch data from the epoch folder'''
    epc = epcstr.split('_')
    d = dict(
        index = int(epc[0][3:]),
        datetime = dt.datetime.strptime(epc[1],'%Y-%m-%d+%H-%M-%S').ctime(),
        prot = '_'.join(epc[2:]),
    )
    return d

def get_file_info(filename):
    ''' extracts experimental metadata from a filename '''
    d = dict(filename=filename)
    if filename.startswith('AutoSv'):
        d.update(
            datetime = dt.datetime.strptime(filename[7:22],'%m%d%y_%H-%M-%S').ctime()
        )
    elif filename.startswith('Sub'):
        print filename
        datestr = filename.split('_')[1]
        d.update(
            datetime = dt.datetime.strptime(datestr,'%m-%d-%y+%H-%M-%S').ctime(),
        )
    else:
        pass 
    
    return d
        
def get_info(smrx):
    ''' takes the full path to an smrx file and returns experimental metadata'''
    path = smrx.split('\\')
    subj, _,pen, site, epc, filename = path[-6:]
    d = dict(
        subject = subj,
        pen = get_pen(pen),
        site = get_site(site),
        epoch = get_epoch(epc),
        file = get_file_info(filename),
    )
    return d
    
def get_import_list(export,info):
    import_list = []
    for item in info:
        import_list.append(
            os.path.join(
                export,
                item['file']['filename'].split('.')[0]+'.mat',
            )
        )
    return import_list


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

def do_car(data):
    '''common average reference. 
    for each channel, subtract off the mean of the other channels
    '''
    car_data = np.empty(data.shape,data.dtype)
    for ch,waveform in enumerate(data.T):
        common_av = np.vstack((data.T[:ch,:],data.T[ch+1:,:])).mean(axis=0)
        car_data[:,ch] = waveform-common_av
    return car_data

def realign(r,chans,fs):

    start = np.amax([r[lbl]['times'][0] for lbl in chans])
    stop = np.amin([r[lbl]['times'][-1] for lbl in chans])
    t_new = np.arange(start,stop,1.0/fs)

    shape = len(t_new), len(chans) 

    rec = {
        'data': np.empty(shape,np.int16),
        'name': '',
        'description': '',
        'file_origin': r['file_origin'],
        'start_time': start,
        'fs': fs,
    }

    for ch,lbl in enumerate(chans):
        spline = interpolate.InterpolatedUnivariateSpline(r[lbl]['times'], r[lbl]['values'])
        rec['data'][:,ch] = spline(t_new)

    return rec

def subsample_data(data,npts=1000000,axis=0):
    pts = data.shape[0]
    indx = sample(range(pts), npts) if pts > npts else range(pts)
    return data[indx,:]

def calc_weights(rec_list):
    linreg = LinearRegression()
    data = np.vstack(tuple(r['data'] for r in rec_list))
    coeffs = []
    
    data = subsample_data(data)

    for ch,waveform in enumerate(data.T):
        X = np.vstack((data.T[:ch,:],data.T[ch+1:,:]))
        linreg.fit(X.T,waveform)
        coeffs.append(linreg.coef_)
    return coeffs

def do_war(data,weights):
    '''common average reference. 
    for each channel, subtract off the weighted average of the other channels
    '''
    car_data = np.empty(data.shape,data.dtype)
    for ch,(waveform,w) in enumerate(zip(data.T,weights)):
        X = np.vstack((data.T[:ch,:],data.T[ch+1:,:]))
        car_data[:,ch] = waveform - X.T.dot(w)
    return car_data
