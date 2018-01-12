# Functions to do stuff with h5 files
from __future__ import division
import numpy as np
import logging
import h5py
import json
from mdaio import readmda


def h5_wrap(h5_function):
    """
    Decorator to open h5 files if the path was provided to a function.
    :param h5_function: a function that receives an h5file as first argument
    :return: decorated function that takes open('r' mode) or path as first argument
    """

    def file_checker(h5_file, *args, **kwargs):
        if type(h5_file) is not h5py._hl.files.File:
            h5_file = h5py.File(h5_file, 'r')
        logging.debug('H5 file: {}'.format(h5_file))
        return_value = h5_function(h5_file, *args, **kwargs)
        return return_value

    return file_checker


# gets the sampling frequency of a recording
def get_record_sampling_frequency(h5, recording=0):
    path = 'recordings/{0:d}'.format(recording)
    return h5[path].attrs.get('sample_rate')


def get_dset_group_attr(data_set, attr_name):
    return data_set.parent.attrs[attr_name]


def get_rec_list(k_file):
    """
    :param k_file:
    :return: list of recordings in an h5file (kwik/kwd) as a sorted numpy array
    """
    return np.sort(map(int, k_file['/recordings'].keys()))


def get_data_set(kwd_file, rec):
    """
    :param kwd_file:
    :param rec: number of rec
    :return: h5 dataset object with
    """
    logging.debug('Getting dataset from rec {}'.format(rec))
    return kwd_file['/recordings/{}/data'.format(int(rec))]


# Table functions
def load_table_slice(table, row_list=None, col_list=None):
    """
    Loads a slice of a h5 dataset.
    It can load sparse columns and rows. To do this, it first grabs the smallest chunks that contains them.
    :param table: dataset of an h5 file.
    :param row_list: list of rows to get (int list)
    :param col_list: list of cols to get (int list)
    :return: np.array of size row_list, col_list with the concatenated rows, cols.
    """
    table_cols = table.shape[1]
    table_rows = table.shape[0]
    d_type = table.dtype

    col_list = np.arange(table_cols) if col_list is None else np.array(col_list)
    row_list = np.arange(table_rows) if row_list is None else np.array(row_list)

    raw_table_slice = np.empty([np.ptp(row_list) + 1, np.ptp(col_list) + 1], dtype=np.dtype(d_type))
    table.read_direct(raw_table_slice,
                      np.s_[np.min(row_list): np.max(row_list) + 1, np.min(col_list): np.max(col_list) + 1])
    # return raw_table_slice
    return raw_table_slice[row_list - np.min(row_list), :][:, col_list - np.min(col_list)]


# passing stuff to binary
def dset_to_binary_file(data_set, out_file, chan_list=None, chunk_size=8000000):
    """
    :param data_set: a table from an h5 file to write to a binary. has to be daughter of a rec
    :param out_file: binary file - has to be open in 'w' mode.
    :param chan_list: list of channels (must be list or tuple). Default (None) will do the whole table
    :param chunk_size: size in samples of the chunk
    :return:
    """
    samples_data = data_set.shape[0]
    channels_data = data_set.shape[1]
    data_type = data_set.dtype
    logging.info('Ripping dataset from {}'.format(data_set.parent.name))
    if chan_list is None:
        logging.debug('Counting channels')
        chan_list = range(channels_data)
    logging.info('Channel list: {}'.format(chan_list))

    samples_chunk = min(chunk_size, samples_data)
    channels_chunk = len(chan_list)

    chunk_buffer = np.empty((samples_chunk, channels_chunk), dtype=np.dtype(data_type))
    chunk_starts = np.arange(0, samples_data, samples_chunk)
    n_chunks = chunk_starts.size

    logging.info('About to store {} entire chunks'.format(n_chunks - 1))
    for start in chunk_starts:
        logging.info('Chunk start: {0}'.format(start))
        end = min(start + samples_chunk, samples_data)
        chunk_buffer[0: end - start, :] = load_table_slice(data_set,
                                                           np.arange(start, end),
                                                           chan_list)
        out_file.write(chunk_buffer[0: end - start].astype(np.dtype(data_type)).tostring())

    stored = n_chunks * chunk_buffer.size + chunk_buffer[0: end - start, :].size
    logging.info('{} elements written'.format(stored))
    return stored


@h5_wrap
def kwd_to_binary(kwd_file, out_file_path, chan_list=None, chunk_size=8000000):
    """
    :param kwd_file: kwd file or kwd file
    :param out_file_path: path to the bin file that will be created
    :param chan_list: list of channels (must be list or tuple). Default (None) will do the whole table
    :param chunk_size: size in samples of the chunk
    :return:
    """
    # get the dataset of each recording and concatenateit to the out_file_path
    logging.info('Writing kwd_file {} to binary'.format(kwd_file.filename))
    logging.info('Channels to extract: {}'.format(chan_list))
    logging.info('Creating binary file {}'.format(out_file_path))
    if chan_list is not None:
        if (type(chan_list) is not list) and (type(chan_list) is not tuple):
            assert (type(chan_list) is int)
            chan_list = [chan_list]
        chan_list = list(chan_list)
    rec_list = get_rec_list(kwd_file)
    logging.info('Will go through recs {}'.format(rec_list))
    out_file = open(out_file_path, 'wt')
    stored_elements = map(lambda rec_name: dset_to_binary_file(get_data_set(kwd_file, rec_name),
                                                               out_file,
                                                               chan_list=chan_list,
                                                               chunk_size=chunk_size
                                                               ),
                          rec_list)
    out_file.close()
    elements_in = np.array(stored_elements).sum()
    logging.info('{} elements written'.format(elements_in))


@h5_wrap
def get_data_size(kwd_file, rec):
    return get_data_set(kwd_file, rec).shape[0]

@h5_wrap
def get_rec_sizes(kwd_file):
    rec_list = get_rec_list(kwd_file)
    rec_sizes = {i: get_data_size(kwd_file, rec_list[i])
                 for i in range(0, rec_list.size)}
    return rec_sizes

@h5_wrap
def get_rec_starts(kwd_file):
    rec_sizes= get_rec_sizes(kwd_file)
    starts_vec = np.array(rec_sizes.values()).cumsum()
    starts_vec = np.hstack([0, starts_vec[:-1]])
    rec_starts = {rec: r_start for r_start, rec in zip(starts_vec, rec_sizes.iterkeys())}
    return rec_starts

def load_grp_file(grp_file_path):
    return np.loadtxt(grp_file_path, dtype={'names': ('cluster_id', 'group'), 
                                       'formats': ('i2', 'S8')}, 
                      skiprows=1)

# offset the recs
def ref_to_rec_starts(rec_sizes, spk_array):
    start = 0
    spk_rec = np.empty_like(spk_array)
    rec_array = np.empty_like(spk_array)
    
    for rec, size in rec_sizes.iteritems():
        end = start + size
        this_rec_spk = (spk_array>start) & (spk_array<end)
        spk_rec[this_rec_spk] = spk_array[this_rec_spk] - start
        rec_array[this_rec_spk] = rec
        start = end
    
    return rec_array, spk_rec

def insert_table(group, table, name, attr_dict=None):
    return group.create_dataset(name, data=table)

def insert_group(parent_group, name, attr_dict_list=None):
    new_group = parent_group.create_group(name)
    if attr_dict_list is not None:
        append_atrributes(new_group, attr_dict_list)
    return new_group

def append_atrributes(h5obj, attr_dict_list):
    for attr_dict in attr_dict_list:
        #print attr_dict['name'] + ' {0} - {1}'.format(attr_dict['data'], attr_dict['dtype'])
        h5obj.attrs.create(attr_dict['name'], attr_dict['data'], dtype=attr_dict['dtype'])
        #h5obj.attrs.create(attr['name'], attr['data'], dtype=attr['dtype'])

class KwikFile:
    def __init__(self, file_names, chan_group=0):
        self.file_names = file_names

        if file_names['mda']:
            spikes = readmda(file_names['mda']).astype(int)
            self.spk = spikes[1,:] - 1 # really, 1 indexing?
            self.clu = spikes[2,:]
            with open(file_names['param'], 'r') as f:
                params = json.load(f)
            self.s_f = params['samplerate']

        else: # its a kilosort conversion
            if file_names['clu']:
                self.clu = np.squeeze(np.load(file_names['clu']))
            elif file_names['temp']:
                self.clu = np.squeeze(np.load(file_names['temp']))
            else:
                raise IOError('both spike_clusters.npy and spike_templates.npy weren\'t found')
            self.spk = np.load(file_names['spk'])
            
            with open(file_names['par'], 'r') as f:
                exec(f.read())
                self.s_f = sample_rate
        
        if 'grp' in file_names and file_names['grp']:
            self.grp = load_grp_file(file_names['grp'])
        else:
            self.grp = [(i, 'unsorted') for i in np.unique(self.clu)]

        self.rec_kwik = None
        self.spk_kwik = None
        self.kwf = None
        self.chan_group = chan_group
        self.create_kwf()
        
        
    def create_kwf(self):
        with h5py.File(self.file_names['kwk'], 'w') as kwf:
            kwf.create_group('/channel_groups')
            kwf.create_group('/recordings')
        
    def make_spk_tables(self, realign_to_recordings=True):
        with h5py.File(self.file_names['kwd'], 'r') as kwd:
            rec_sizes = get_rec_sizes(kwd)
            self.rec_kwik, self.spk_kwik = ref_to_rec_starts(rec_sizes, self.spk)
        
        with h5py.File(self.file_names['kwk'], 'r+') as kwf:
            chan_group = kwf['/channel_groups'].require_group('{}'.format(self.chan_group))
            spikes_group = chan_group.require_group('spikes')
            insert_table(spikes_group, self.rec_kwik.flatten(), 'recording')
            if realign_to_recordings:
                insert_table(spikes_group, self.spk_kwik.flatten() , 'time_samples')
                insert_table(spikes_group, self.spk_kwik.flatten() /self.s_f, 'time_fractional')
            else:
                insert_table(spikes_group, self.spk.flatten() , 'time_samples')
    
            clusters_group = spikes_group.require_group('clusters')
            insert_table(clusters_group, self.clu, 'main')
            insert_table(clusters_group, self.clu, 'original')
    
    def make_rec_groups(self):
        rec_list = np.unique(self.rec_kwik)
        rec_start_samples = get_rec_starts(self.file_names['kwd'])
        
        with h5py.File(self.file_names['kwk'], 'r+') as kwf:
            rec_group = kwf.require_group('recordings')
            for rec in rec_list:
                rec_name = 'recording_{}'.format(rec)
                attribs = [{'name': 'name', 'data': rec_name, 'dtype': 'S{}'.format(len(rec_name))}, 
                          {'name': 'sample_rate', 'data': self.s_f, 'dtype': np.dtype(np.float64)},
                          {'name': 'start_sample', 'data': rec_start_samples[rec], 'dtype': np.int64},
                          {'name': 'start_time', 'data': rec_start_samples[rec]/self.s_f, 'dtype': np.float64}]
                insert_group(rec_group, str(rec), attribs)
    
    def make_clu_groups(self, name='main'):
        clu_grp_dict = {'good': 2,
                           'mua': 1,
                           'noise': 0,
                           'unsorted': 3}
            
        with h5py.File(self.file_names['kwk'], 'r+') as kwf:
            chan_group = kwf['/channel_groups'].require_group('{}'.format(self.chan_group))
            clusters_group = chan_group.require_group('clusters')
            desc_group = clusters_group.require_group(name)
            
            for clu in self.grp:
                attribs = [{'name': 'cluster_group', 
                            'data': clu_grp_dict[clu[1]], 
                            'dtype': np.int64}]
                
                insert_group(desc_group, str(clu[0]), attribs)
