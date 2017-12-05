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


### Command-line options
```bash
usage: htseq_count_cluster.py [-h] [-p INPATH] [-f INFILE] [-g GTF]
                              [-o OUTPATH] [-e EMAIL]

This is a command line wrapper around htseq-count.

optional arguments:
  -h, --help            show this help message and exit
  -p INPATH, --inpath INPATH
                        Path of your samples/sample folders.
  -f INFILE, --infile INFILE
                        Name and path of your input csv file.
  -g GTF, --gtf GTF     Name and path of your input csv file.
  -o OUTPATH, --outpath OUTPATH
                        Directory of your output counts file. The counts file
                        will be named.
  -e EMAIL, --email EMAIL
                        Directory of your output counts file. The counts file
                        will be named.

Ensure that htseq-count is in your path.
```


## ToDo
- [ ] Monitor Jobs
- [ ] Enhance wrapper input for other use cases.


## Maintainers
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)

Rob Gilmore | [@grabear](https://github.com/grabear) | [✉](mailto:robgilmore127@gmail.com)


Please feel free to [open an issue](https://github.com/datasnakes/htseq-count-cluster/issues/new) if you have a question/feedback/problem
or [submit a pull request](https://github.com/datasnakes/htseq-count-cluster/compare) to add a feature/refactor/etc. to this project.
