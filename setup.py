#!/usr/bin/python3
# -*- coding: utf-8 -*-
from os import path

from setuptools import find_packages, setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='opaf',
    version='0.1.0',
    author='Scott Ware',
    url='https://github.com/open-pattern-format/opaf',
    description='An XML based knitting pattern format specification and tooling.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    keywords=['opaf', 'knit'],
    include_package_data=True,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'opaf = opaf.opaf:main',
        ]
    }
)
