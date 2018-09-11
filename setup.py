#!/usr/bin/env python3
""" This is the setup.py script for setting up the package and fulfilling any
necessary requirements.
"""

from setuptools import setup, find_packages
from codecs import open  # To use a consistent encoding
from os import path
from sphinx.setup_command import BuildDoc

cmdclass = {'build_sphinx': BuildDoc}

# Set the home path of the setup script/package
home = path.abspath(path.dirname(__file__))
name = 'HTSeqCountCluster'
version = '1.3'


def readme():
    """Get the long description from the README file."""
    with open(path.join(home, 'README.rst'), encoding='utf-8') as f:
        return f.read()


setup(
    name=name,
    author='Shaurita Hutchins & Robert Gilmore',
    author_email='datasnakes@gmail.com',
    description="A cli for running multiple pbs/qsub jobs with HTSeq's htseq-count script on a cluster.",
    version=version,
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/datasnakes/htseq-count-cluster',
    license='MIT',
    keywords='science lab pyschiatry rnaseq htseq',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
        ],
    project_urls={
            'Documentation': 'https://tinyurl.com/yb7kz7zz',
            },
    # Packages will be automatically found if not in this list.
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
          'HTSeq>=0.9.1',
          'pandas>=0.20.3',
          'logzero>=1.3.1'
      ],
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
    tests_require=['nose'],
    command_options={
    'build_sphinx': {
        'project': ('setup.py', name),
        'version': ('setup.py', version),
        'release': ('setup.py', version),
        'source_dir': ('setup.py', 'docs')}},
)
