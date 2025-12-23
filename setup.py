#!/usr/bin/env python3
"""Setup script for HTSeqCountCluster package.

This setup.py is maintained for backward compatibility.
Modern build configuration is in pyproject.toml (PEP 517/518).
"""

from pathlib import Path
from setuptools import setup, find_packages

try:
    from sphinx.setup_command import BuildDoc
    cmdclass = {'build_sphinx': BuildDoc}
except ImportError:
    cmdclass = {}

# Set the home path of the setup script/package
home = Path(__file__).parent.absolute()
name = 'HTSeqCountCluster'
version = '1.4'

def readme():
    """Get the long description from the README file."""
    readme_file = home / 'README.md'
    return readme_file.read_text(encoding='utf-8')


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
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        ],
    project_urls={
            'Website': 'https://tinyurl.com/yb7kz7zz',
            'Documentation': 'http://htseq-count-cluster.rtfd.io/',
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
    extras_require={
        'test': ['pytest>=6.0', 'pytest-cov'],
        'dev': ['pytest>=6.0', 'pytest-cov', 'sphinx'],
    },
    command_options={
    'build_sphinx': {
        'project': ('setup.py', name),
        'version': ('setup.py', version),
        'release': ('setup.py', version),
        'source_dir': ('setup.py', 'docs')}},
)
