#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError as e:
    from distutils.core import setup

long_description = '''
Aerolito is an AIML alternative based on YAML. Aerolito provides features 
for natural language processing simulation. Example of usage::

    from aerolito import Kernel
    kernel = Kernel('config.yml')

    print kernel.respond(u'Hello')
'''

setup(
    name='Aerolito',
    version='0.1',
    url='https://renatopp.com/aerolito',
    download_url='https://github.com/renatopp/aerolito/',
    license='MIT License',
    author='Renato de Pontes Pereira',
    author_email='renato.ppontes@gmail.com',
    description='Python library for natural language processing simulation',
    long_description=long_description,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup'
    ],
    keywords='artificial intelligence natural language processing simulation yaml aiml markup aerolito',
    packages=[
        'aerolito',
    ],
    install_requires=[
        'pyyaml',
    ],
)

