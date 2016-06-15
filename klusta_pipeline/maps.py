import numpy as np

#applies the transformation of sites to headstage introduced by an adapter
def apply_adapter(a_port_site, adapter):
    '''
    a_port_site: a dictionary with port: site (mapping channels in a headstage to ports in a recording system)
    adapter: n_site x 2 numpy array
            col 0: site in headstage end
            col 1: site in porbe end
    retunrs: new dictionary with port: mapped_site, where mapped_site is the probe site that connects to that channel instead of site
    '''
    new_port_site = {port : adapter[adapter[:, 1] == site][0, 0] for port, site in a_port_site.iteritems()}
    return new_port_site

# n_site x 2 numpy array
# col 0: site in headstage end
# col 1: site in porbe end
site_headstage = {
    'A32-HST32V': np.transpose(np.array([[11, 9, 7, 5, 3, 2, 6, 8, 10, 12,
                      1, 4, 13, 14, 15, 16, 
                      26, 24, 20, 19, 18, 17, 
                      32, 30, 31, 28, 29, 27, 25, 22, 23, 21], 
                     [1, 2, 3, 4, 6, 8, 10, 12, 14, 16, 
                      5, 7, 9, 11, 13, 15,
                      21, 23, 25, 27, 29, 31,
                      17, 18, 19, 20, 22, 24, 26, 28, 30, 32]], dtype=np.int)
    )}

# dictionary yields port:site
port_site = {
    'paukstis32': {
        'Port_1': 15,
        'Port_2': 6,
        'Port_3': 5,
        'Port_4': 4,
        'Port_5': 16,
        'Port_6': 3,
        'Port_7': 2,
        'Port_8': 1,
        'Port_9': 32,
        'Port_10': 31,
        'Port_11': 30,
        'Port_12': 17,
        'Port_13': 29,
        'Port_14': 28,
        'Port_15': 27,
        'Port_16': 18,
        'Port_17': 13,
        'Port_18': 12,
        'Port_19': 11,
        'Port_20': 10,
        'Port_21': 14,
        'Port_22': 9,
        'Port_23': 8,
        'Port_24': 7,
        'Port_25': 26,
        'Port_26': 25,
        'Port_27': 24,
        'Port_28': 19,
        'Port_29': 23,
        'Port_30': 22,
        'Port_31': 21,
        'Port_32': 20,
    },
    'paukstis16-ec': {
        'Port_1': 14,
        'Port_2': 15,
        'Port_3': 9,
        'Port_4': 16,
        'Port_5': 1,
        'Port_6': 8,
        'Port_7': 2,
        'Port_8': 3,
        'Port_9': 12,
        'Port_10': 11,
        'Port_11': 10,
        'Port_12': 13,
        'Port_13': 4,
        'Port_14': 7,
        'Port_15': 6,
        'Port_16': 5,
    },
}
port_site['ibon32'] = port_site['paukstis32']
port_site['bodegh16'] = {'Port_%d' % (i+1) : i+1 for i in range(16) }
port_site['burung16'] = port_site['bodegh16']

# Burung system with 32 channels trhough amps 2, 3, with no adapter
port_site['burung32'] = {'Port_%d' % (i+1+16) : i+1 for i in range(32)} 

# Buring system with the A32 adapter for neuronexus probes
port_site['burung32-A32-HST32V'] = apply_adapter(port_site['burung32'], site_headstage['A32-HST32V'])