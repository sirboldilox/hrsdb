#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='HRSDB',
    version='0.1',
    description='Health Record System Database',
    author='Matt Parker',
    author_email='m.parker-12@student.lboro.ac.uk',

    packages=find_packages(),
    scripts=[
        'scripts/hrsdb_init',
        'scripts/hrsdb_add_patient',
    ],
    entry_points={
        'console_scripts': [
            'hrsdb_http = hrsdb.__main__:main'
        ]
    }
)
