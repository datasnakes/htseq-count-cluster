[![Build Status](https://travis-ci.org/datasnakes/htseq-count-cluster.svg?branch=master)](https://travis-ci.org/datasnakes/htseq-count-cluster)

# htseq-count-cluster

A cli wrapper for running [htseq](https://github.com/simon-anders/htseq)'s `htseq-count` on a cluster.

## Install

`pip install git+https://github.com/datasnakes/htseq-analysis-scripts.git`

## Features

- For use with large datasets (we've previously used a dataset of 120 different human samples)
- For use with SGE/SGI cluster systems
- Submits multiple jobs
- Command line interface/script
- Merges counts files into one counts table/csv file
- Uses `accepted_hits.bam` file output of `tophat`

### Command-line options

| Argument |                                                                             Description                                                                             | Required |
|:--------:|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:--------:|
|   `-p`   | This is the path of your .bam files.  Presently, this script looks for a folder that is the sample name and searches for an accepted_hits.bam file (tophat output). |    Yes   |
|   `-i`   |                                                     You should have a csv file list of your samples or folder names (no header).                                                    |    Yes   |
|   `-g`   |                                                           This should be the path to your genes.gtf file.                                                           |    Yes   |
|   `-o`   |                                                  This should be an existing directory for your output counts files.                                                 |    Yes   |
|   `-e`   |                                        Email yourself when the script completes.  This can be left empty or not used at all.                                        |    No    |

#### Help message output

```
usage: htseq_count_cluster.py [-h] -p INPATH -f INFILE -g GTF -o OUTPATH
                              [-e EMAIL]

This is a command line wrapper around htseq-count.

optional arguments:
  -h, --help            show this help message and exit
  -p INPATH, --inpath INPATH
                        Path of your samples/sample folders.
  -f INFILE, --infile INFILE
                        Name or path to your input csv file.
  -g GTF, --gtf GTF     Name or path to your gtf/gff file.
  -o OUTPATH, --outpath OUTPATH
                        Directory of your output counts file. The counts file
                        will be named.
  -e EMAIL, --email EMAIL
                        Email address to send script completion to.

*Ensure that htseq-count is in your path.


```

### Examples

#### Run htseq_count_cluster.py

```bash
python htseq_count_cluster.py -p path/to/samples/ -f samples.csv -g genes.gtf -o path/to/cluster-output/
```
This script uses logzero so there will be color coded logging information to your shell.

A common linux practice is to use `screen` to create a new shell and run a program
so that if it does produce output to the stdout/shell, the user can exit that particular
shell without the program ending and utilize another shell.


#### Merge output counts files
In order to prep your data for `DESeq2` or `edgeR`, it's best to have 1 merged
counts file.
```bash
python mergecounts.py -d path/to/cluster-output/
```

##### Help message for mergecounts.py

```
usage: mergecounts.py [-h] -d DIRECTORY

Merge multiple counts tables into 1 counts .csv file.

Your output file will be named:  merged_counts_table.csv

optional arguments:
  -h, --help            show this help message and exit
  -d DIRECTORY, --directory DIRECTORY
                        Path to folder of counts files.
```

## ToDo

- [ ] Monitor jobs.
- [ ] Enhance wrapper input for other use cases.
- [ ] Add example data.


## Maintainers

Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)


## Help

Please feel free to [open an issue](https://github.com/datasnakes/htseq-count-cluster/issues/new) if you have a question/feedback/problem
or [submit a pull request](https://github.com/datasnakes/htseq-count-cluster/compare) to add a feature/refactor/etc. to this project.
