#!/usr/bin/env python

from distutils.core import setup

setup(
    name='klusta-pipeline',
    version='0.0.2',
    description='data pipeline for analyzing spike2 collected data in klustakwik ',
    author='Justin Kiggins',
    author_email='justin.kiggins@gmail.com',
    packages=['klusta_pipeline',
              ],
    entry_points={
        'console_scripts': [
            'make_kwd = klusta_pipeline.make_kwd:main',
            'merge_stim_kwik = klusta_pipeline.merge_stim_kwik:main',
            'display_probe = klusta_pipeline.probe:_display',
            'kwd2dat = klusta_pipeline.kwd2dat:main',
            'make_mat_chanMap = klusta_pipeline.make_mat_chanMap:main',
            'make_kilo_scripts = klusta_pipeline.make_kilo_scripts:main'
        ],
    },
)
