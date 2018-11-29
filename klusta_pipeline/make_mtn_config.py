#!/usr/bin/env python
'''
Generate a JSON file containing configuration parameters for MountainSort
'''

import json
import argparse, os

def get_args():
    parser = argparse.ArgumentParser(description='Generate params.json for mountainsort configuration')
    parser.add_argument('dest', default='./', nargs='?',
                        help='destination directory (default: ./)')
    parser.add_argument('--sign', dest='detect_sign', type=int, default=-1,
                        help='Detect sign (default: -1)')
    parser.add_argument('--rate',dest='samplerate',  type=int, default=20000,
                        help='Sample rate (default: 20000)')
    parser.add_argument('--radius', dest='adjacency_radius', type=int, default=-1,
                        help='Adjacency radius (default: -1)')
    parser.add_argument('--klusta', dest='klusta_dir', type=str, default='',
                        help='klusta directory to load sample rate from. Overrides --rate option')
    return parser.parse_args()

def main():
    args = get_args()

    dest = os.path.abspath(args.dest)

    output_args = vars(args)
    output_args = {key:output_args[key] for key in ('detect_sign', 'samplerate', 'adjacency_radius')}

    if args.klusta_dir:
        klusta_dir = os.path.abspath(args.klusta_dir)
        params_file = os.path.join(klusta_dir, 'params.prm')
        with open(params_file, 'r') as f:
            contents = f.read()
        metadata = {}
        exec(contents, {}, metadata)
        output_args['samplerate'] = metadata['traces']['sample_rate']

    with open(os.path.join(dest, 'params.json'), 'w') as output:

        json.dump(output_args, output)

        print('configurations set')

if __name__ == '__main__':
    main()
