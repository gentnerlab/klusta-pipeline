#!/usr/bin/env python
import argparse, os
import h5py as h5
import numpy as np
from string import Template
from shutil import copyfile

# assume spike2 export to mat with the following parameters:
# - aligned starts
# - all chans same length
# - channel names are "Port_N" where N is the 1-indexed 1401 Port number (and, hopefully, electrode site)

KK_PIPELINE_DIR = os.path.dirname(os.path.realpath(__file__))

# for each electrode, we need a list of channel names.
# list indices correspond to indices in the KWD array
CHANMAP = { 
    'A1x16-5mm50': [
        'Port_6',
        'Port_11',
        'Port_3',
        'Port_14',
        'Port_1',
        'Port_16',
        'Port_2',
        'Port_15',
        'Port_5',
        'Port_12',
        'Port_4',
        'Port_13',
        'Port_7',
        'Port_10',
        'Port_8',
        'Port_9',
        ],
    'N-Form': ['Port_%i'%(ch+1) for ch in range(32)],
    }

def read_s2mat(mat,site_map):
    with h5.File(mat, 'r') as f_in:
        n_samp = int(np.amin([f_in[site]['length'][0,0] for ch, site in enumerate(site_map)]))
        shape = (n_samp,len(site_map)) # samples,channels
        data = np.empty(shape,np.int16)

        for ch, site in enumerate(site_map):
            data[:,ch] = f_in[site]['values'][0,:n_samp]
        
    return data


def get_args():

    parser = argparse.ArgumentParser(description='Compile Spike2 epoch .mat files into KlustaKwik KWD file.')
    parser.add_argument('mat_list', 
                       help='a text file listing all of the mat files to compile')
    parser.add_argument('probe', default='A1x16-5mm50',
                       help='probe (edit this file to fix mappings)')

    return parser.parse_args()

def get_fs_from_mat(mat,site_map):
    with h5.File(mat, 'r') as f:
        for ii, ch in enumerate(site_map):
            if ii == 0:
                fs =  1 / f[ch]['interval'][0][0]
            else: # make sure all channels have the same sampling rate
                assert fs == 1 / f[ch]['interval'][0][0]
            return fs


def main():
    args = get_args()

    # get experiment info from file structure
    subj, _, pen, site = os.getcwd().split('/')[-4:]
    exp = '_'.join((subj,pen,site))
    kwd = exp + '.raw.kwd'

    params = {
        'probe': args.probe,
        'exp': exp,
        }

    if not os.path.exists(kwd):
        # open KWD file (destination HDF5)
        print 'Opening %s' % kwd
        with h5.File(kwd, 'w') as kwd_f, open(args.mat_list,'r') as mlist_f:
            # for each mat file in the list
            for rec, mat in enumerate(mlist_f):
                mat = mat.strip()
                # read in data from MAT and write to KWD
                print 'Copying %s into Recording/%s' % (mat,rec)
                data = read_s2mat(mat,CHANMAP[args.probe])
                kwd_f.create_dataset('recordings/%i/data' % rec, data=data)

                # grab parameters from first MAT file
                if rec == 0:
                    params['fs'] = get_fs_from_mat(mat,CHANMAP[args.probe])
                    params['nchan'] = data.shape[1]
                else: # make sure all recordings have the same sampling rate and num chans
                    assert params['fs'] == get_fs_from_mat(mat,CHANMAP[args.probe])
                    assert params['nchan'] == data.shape[1]
    else: 
        print '%s already exists, please delete and run again' % kwd
        raise IOError('%s already exists, please delete and run again' % kwd)

    # copy over the spike template
    try:
        copyfile(os.path.join(KK_PIPELINE_DIR, params['probe'] + ".prb"), os.path.join(os.getcwd(), params['probe'] + ".prb"))
    except IOError:
        print "Could not copy probe file %s to current directory. You'll have to do this manually." % os.path.join(KK_PIPELINE_DIR,params['probe'] + ".prb")

    # read the parameters template
    params_template_in = os.path.join(KK_PIPELINE_DIR,'params.template')
    with open(params_template_in,'r') as src:
        params_template = Template(src.read())

    # write the parameters
    with open('params.prm', 'w') as pf:
        pf.write(params_template.substitute(params))

if __name__ == '__main__':
    main()
