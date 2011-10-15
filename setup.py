#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Renato de Pontes Pereira'
__author_email__ = 'renato.ppontes@gmail.com'
__version__ = '0.1'
__date__ = '2011 10 15'

try:
    import setuptools
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()

from setuptools import setup, find_packages

long_description = '''
Aerolito is an AIML alternative based on YAML. Aerolito provides features 
for natural language processing simulation. Example of usage::

    from aerolito import Kernel
    kernel = Kernel('config.yml')

    print kernel.respond(u'Hello')
'''

setup(
    name='aerolito',
    version = __version__,
    author = __author__,
    author_email=__author_email__,
    license='MIT License',
    url='http://renatopp.com/aerolito',
    download_url='https://github.com/renatopp/aerolito/',
    description='Python library for natural language processing simulation',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
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
    packages=['aerolito'],
    install_requires=['pyyaml'],
)

