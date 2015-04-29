#!/usr/bin/env python

from distutils.core import setup

setup(
    name='klusta-pipeline',
    version='0.0.1',
    description='data pipeline for analyzing spike2 collected data in klustakwik ',
    author='Justin Kiggins',
    author_email='justin.kiggins@gmail.com',
    packages=['klusta_pipeline',
              ],
    entry_points={
        'console_scripts': [
            's2mat_to_kwd = klusta_pipeline.s2mat_to_kwd:main',
            'make_s2mat_list = klusta_pipeline.make_s2mat_list:main'
        ],
    },
)
