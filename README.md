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

## ToDo
- Monitor Jobs
- Enhance wrapper input for other use cases.
- Add pandas script for merging counts files.

