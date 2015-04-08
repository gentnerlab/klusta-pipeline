#!/usr/bin/env python
import glob

def main():
    mat_files = glob.glob('Epc*_N?_*/*.mat')
    if len(mat_files) < 1:
        print 'No files to compile'
        return
    with open('files_to_compile.txt','w') as f:
        for mat in mat_files:
            print mat
            f.write(mat+'\n')

if __name__ == '__main__':
    main()