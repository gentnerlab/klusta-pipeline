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

    return parser.parse_args()

def main():
    args = get_args()

    dest = os.path.abspath(args.dest)

    output_args = vars(args)
    del output_args['dest']

    with open(os.path.join(dest, 'params.json'), 'w') as output:

        json.dump(output_args, output)

        print 'configurations set'

if __name__ == '__main__':
    main()
