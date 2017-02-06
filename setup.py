#!/usr/bin/env python
# Copyright (c) 2016-2017 Chris Fournier. All rights reserved.
# Use of this source code is governed by a MIT-style license that can be found
# in the LICENSE file.
import re

try:
    from setuptools import setup
except:
    from distutils.core import setup

with open('README.rst') as fh:
    long_description = fh.read()

with open('important/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='important',
    version=version,
    description='Utility to find unused packages in requirements \
 and to constrain package usage',
    long_description=long_description,
    url='https://github.com/cfournie/important',
    download_url='https://github.com/cfournie/important/tarball/%s' % version,
    author='Chris Fournier',
    author_email='chris.m.fournier@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=['import', 'requirement', 'unused'],
    packages=['important'],
    entry_points={
        'console_scripts': [
            'important = important.__main__:check',
        ],
    },
    install_requires=[
        'pip>=8',
        'click>=5',
        'setuptools>=0.9',
    ],
)
