#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='HRSDB',
    version='0.2',
    author='Matt Parker',
    author_email='m.parker-12@student.lboro.ac.uk',
    description='Health Record System Database',
    license = "MIT",

    classifiers = [
        "Development Status :: 3 - Alpha"
        "Environment :: Web Environment",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],

    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,

    install_requires=[
        'Flask',
        'Flask-RESTful',
        'SQLALchemy'
    ],

    entry_points={
        'console_scripts': [
            'hrsdb = hrsdb.__main__:main'
        ]
    }
)
