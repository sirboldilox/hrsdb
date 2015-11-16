#!/usr/bin/env python

from distutils.core import setup

setup(
    name='HRSDB',
    version='0.1',
    description='Health Record System Database',
    author='Matt Parker',
    author_email='m.parker-12@student.lboro.ac.uk',
    packages=['sqlalchemy', 'flask'],
    scripts=['scripts/hrsdb']
)
