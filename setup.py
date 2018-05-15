#!/usr/bin/env python3

""" This is the setup.py script for setting up the package and fulfilling any
necessary requirements.
"""

from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path

# Set the home path of the setup script/package
home = path.abspath(path.dirname(__file__))
name = 'HTSeqCountCluster'


def readme():
    """Get the long description from the README file."""
    with open(path.join(home, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name=name,
    author='Shaurita Hutchins & Robert Gilmore',
    author_email='datasnakes@gmail.com',
    description="A cli for running multiple pbs/qsub jobs with HTSeq's htseq-count script on a cluster.",
    version='0.1',
    long_description=readme(),
    url='https://github.com/datasnakes/htseq-count-cluster',
    license='MIT',
    keywords='science lab pyschiatry rnaseq htseq',
    platform='Linux',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
        ],
    # Packages will be automatically found if not in this list.
    packages=find_packages(),
    include_package_data=True,
    package_data={
            'HTSeqCountCluster': ['pbsjob/*.pbs'],
            },
    entry_points={
        'console_scripts': [
                'htseq-count-cluster=HTSeqCountCluster.htseq_count_cluster:main',
                'merge-counts=HTSeqCountCluster.mergecounts:main'
                ]
    },
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose']
)
