# htseq-count-cluster
A cli wrapper for running htseq's `htseq-count` on a cluster.

## Install

`pip install git+https://github.com/datasnakes/htseq-analysis-scripts.git`

or

`pip install --user git+https://github.com/datasnakes/htseq-analysis-scripts.git`

## Features
- For use with large datasets (ours used 120 different human samples)
- For use with SGE/SGI cluster systems
- Submits multiple jobs
- Merges counts files into one counts table/csv file


## ToDo
[ ] - Monitor Jobs
[ ] - Enhance wrapper input for other use cases.


## Maintainers
Shaurita Hutchins | [@sdhutchins](https://github.com/sdhutchins) | [✉](mailto:sdhutchins@outlook.com)
Rob Gilmore | [@grabear]: https://github.com/grabear | [✉](mailto:robgilmore127@gmail.com)


Please feel free to [open an issue](https://github.com/datasnakes/htseq-count-cluster/issues/new) if you have a question/feedback/problem
or [submit a pull request](https://github.com/datasnakes/htseq-count-cluster/compare) to add a feature/refactor/etc. to this project.
