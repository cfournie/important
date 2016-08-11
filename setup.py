#!/usr/bin/env python
from distutils.core import setup

with open('README.rst') as fh:
    long_description = fh.read()

setup(
    name='important',
    version='0.0.0.dev1',
    description='Import and requirements checking utilities',
    long_description=long_description,
    url='https://github.com/cfournie/important',
    author='Chris Fournier',
    author_email='chris.m.fournier@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
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
    ],
    keywords=['import', 'requirement', 'unused'],
    packages=['important'],
    entry_points={
        'console_scripts': [
            'important = important.__main__:check',
        ],
    },
    install_requires=['pip', 'click', 'packaging'],
    extras_require={
        'test': ['pytest', 'pytest-cov', 'flake8'],
    },
)
