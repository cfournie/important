#!/usr/bin/env python

from distutils.core import setup

setup(name='important',
      version='0.0',
      description='Import and requirements checking utilities',
      author='Chris Fournier',
      author_email='chris.m.fournier@gmail.com',
      url='',
      packages=['requirements'],
      install_requires=['pip', 'click'],
)
