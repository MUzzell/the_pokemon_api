# -*- coding: utf-8 -*-

# pip3 install -e docker/build.init/python3-distribution/root/distribution
from setuptools import setup

setup(
    name='pokemon-api-backend',
    version='0.0.1',
    entry_points={'console_scripts': [
        'service = backend.app:main',
    ]},
    extras_require={
        'test': [
            'pytest==3.3.2',
            'pytest-mock==1.6.3'
        ]
    }
)
