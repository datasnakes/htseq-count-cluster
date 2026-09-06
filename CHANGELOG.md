# Changelog

This file records user-facing changes to HTSeqCountCluster.

## 2.0.0

### Added

- Add throttled Slurm array submission with `sbatch --parsable`.
- Add scheduler-neutral job and resource models shared by the Slurm and
  PBS/Torque backends.
- Add retained submission manifests, scripts, and logs for tracing cluster
  jobs.
- Add one-shot scheduler status checks through the unified command-line
  interface.
- Add strict count-table validation before merging results.
- Add Python 3.14 support and test Python 3.10 through 3.14 in continuous
  integration.
- Add a Great Docs user guide and GitHub Pages deployment workflow.

### Changed

- Require an explicit `sample_id,bam_path` CSV manifest instead of discovering
  TopHat `accepted_hits.bam` files from a one-column sample list.
- Require the `run` subcommand and expose submission, status checks, and merging
  through `htseq-count-cluster`.
- Write count tables as `<sample_id>.counts.tsv` and publish them atomically
  after `htseq-count` succeeds.
- Require Python 3.10 or newer and HTSeq 2.1 or newer.
- Submit PBS/Torque jobs directly instead of constructing shell command
  strings.

### Fixed

- Prevent failed `htseq-count` processes from leaving partial count tables.
- Reject duplicate or misordered gene identifiers during count-table merging.
- Report missing PBS history as `Unknown` instead of assuming success.

### Removed

- Remove the legacy no-subcommand interface and standalone `merge-counts`
  executable.
- Remove implicit TopHat path discovery, the embedded PBS template, polling
  helpers, and the custom logging utility.
- Remove the Sphinx and Read the Docs configuration replaced by Great Docs.

Contributed by [Shaurita Hutchins](https://github.com/sdhutchins).
