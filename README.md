[![Build Status](https://github.com/datasnakes/htseq-count-cluster/actions/workflows/package-build.yml/badge.svg?branch=main)](https://github.com/datasnakes/htseq-count-cluster/actions/workflows/package-build.yml)
[![Documentation](https://img.shields.io/website?url=https%3A%2F%2Fdatasnakes.github.io%2Fhtseq-count-cluster%2F&label=docs)](https://datasnakes.github.io/htseq-count-cluster/)
[![PyPI version](https://img.shields.io/pypi/v/HTSeqCountCluster.svg)](https://pypi.org/project/HTSeqCountCluster/)
[![Python versions](https://img.shields.io/pypi/pyversions/HTSeqCountCluster.svg)](https://pypi.org/project/HTSeqCountCluster/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18028846.svg)](https://doi.org/10.5281/zenodo.18028846)
[![License](https://img.shields.io/github/license/datasnakes/htseq-count-cluster.svg)](https://github.com/datasnakes/htseq-count-cluster/blob/main/LICENSE)

# HTSeqCountCluster

HTSeqCountCluster submits [`htseq-count`](https://htseq.readthedocs.io/) jobs
through PBS/Torque or a throttled Slurm array. It validates BAM paths, retains
scheduler scripts and manifests, and merges count tables only when their gene
identifiers and row order match.

The [documentation](https://datasnakes.github.io/htseq-count-cluster/), built
with [Great Docs](https://posit-dev.github.io/great-docs/), covers scheduler
behavior and 2.0 migration. The [changelog](CHANGELOG.md) summarizes each
release.

## Background

This project grew from an [issue I opened on the HTSeq
repository](https://github.com/simon-anders/htseq/issues/43) about using multiple
cores to process many BAM files. That discussion inspired this approach: run one
`htseq-count` job per sample in parallel, then merge the count tables.

## Install

HTSeqCountCluster 2.0 requires Python 3.10 or newer and HTSeq 2.1 or newer.

```bash
python -m pip install HTSeqCountCluster
```

## Prepare inputs

Create a two-column CSV manifest. Relative BAM paths resolve from the manifest
directory.

```csv
sample_id,bam_path
control-1,/data/aligned/control-1.bam
treated-1,aligned/treated-1.bam
```

The batch environment must provide `htseq-count` and HTSeqCountCluster;
environment-module configuration remains site-specific.

## Submit a Slurm array

```bash
htseq-count-cluster run \
  --scheduler slurm \
  --infile samples.csv \
  --gtf genes.gtf \
  --outpath counts \
  --partition short \
  --memory 4G \
  --time 02:00:00 \
  --max-concurrent 8
```

## Submit PBS/Torque jobs

```bash
htseq-count-cluster run \
  --scheduler pbs \
  --infile samples.csv \
  --gtf genes.gtf \
  --outpath counts \
  --partition batch \
  --memory 4gb \
  --time 02:00:00
```

Use `--dry-run` to validate inputs and print the `sbatch` or `qsub` command
without submitting. Submission files are retained for inspection.

## Check status

Status checks do not poll:

```bash
htseq-count-cluster status --scheduler slurm 12345678
htseq-count-cluster status --scheduler pbs 12345.server
```

## Merge count tables

```bash
htseq-count-cluster merge --directory counts
```

This writes `counts/merged_counts_table.csv` and rejects duplicate gene
identifiers or inconsistent gene order.

## Build the documentation

[Great Docs](https://posit-dev.github.io/great-docs/) requires Python 3.11 or
newer and [Quarto](https://quarto.org/docs/get-started/).

```bash
python -m pip install -e ".[docs]"
great-docs build --no-refresh
```

The generated site is written to `great-docs/_site/`; `great-docs/` is
ephemeral and ignored.

## Maintainers

Shaurita Hutchins ([@sdhutchins](https://github.com/sdhutchins)) and Robert
Gilmore ([@grabear](https://github.com/grabear)).

## Citations

Cite HTSeqCountCluster and HTSeq when using this package.

### HTSeqCountCluster

Hutchins, S. D. (2025). *HTSeqCountCluster* [Computer software]. Zenodo.
[https://doi.org/10.5281/zenodo.18028846](https://doi.org/10.5281/zenodo.18028846)


### HTSeq

Anders, S., Pyl, P. T., & Huber, W. (2015). HTSeq—a Python framework to work
with high-throughput sequencing data. *Bioinformatics, 31*(2), 166–169.
[https://doi.org/10.1093/bioinformatics/btu638](https://doi.org/10.1093/bioinformatics/btu638)
