
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
}
port_site['ibon32'] = port_site['paukstis32']
port_site['bodegh16'] = {'Port_%d' % (i+1) : i+1 for i in range(16) }
port_site['burung16'] = port_site['bodegh16']