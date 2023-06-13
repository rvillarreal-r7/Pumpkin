#!/usr/bin/env python3
"""Setup for Pumpkin"""


from setuptools import (
    find_packages,
    setup,
)

from pathlib import Path

def read(rel_path):
    init = Path(__file__).resolve().parent / rel_path
    return init.read_text('utf-8', 'ignore')

def get_version():
    ver_path = 'mobsf/MobSF/init.py'
    for line in read(ver_path).splitlines():
        if line.startswith('VERSION'):
            return line.split('\'')[1]
    raise RuntimeError('Unable to find version string.')