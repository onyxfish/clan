#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
    'google-api-python-client==1.3.1',
    'httplib2==0.9',
    'pyyaml==3.11',
    'Jinja2==2.7.3',
    'requests==2.5.0'
]

if sys.version_info < (2, 7):
    install_requires.append('argparse>=1.2.1')

setup(
    name='clan',
    version='0.2.4',
    description='A command line utility for working with Google Analytics.',
    long_description=open('README').read(),
    author='Christopher Groskopf',
    author_email='staringmonkey@gmail.com',
    url='https://github.com/onyxfish/clan',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    packages=[
        'clan'
    ],
    package_data={
        'clan': ['templates/*']
    },
    entry_points={
        'console_scripts': [
            'clan = clan:_main'
        ]
    },
    include_package_data=True,
    install_requires=install_requires
)
