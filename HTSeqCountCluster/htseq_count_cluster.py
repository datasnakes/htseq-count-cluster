"""Command-line interface for submitting and merging HTSeq count jobs."""

from __future__ import annotations

import argparse
import csv
import logging
import shlex
from pathlib import Path

from HTSeqCountCluster.mergecounts import merge_counts_tables
from HTSeqCountCluster.schedulers import JobResources, SampleJob, get_scheduler

LOGGER = logging.getLogger(__name__)


def _validate_sample_id(sample_id: str) -> str:
    """Reject identifiers that could escape the requested output directory."""
    normalized_id = sample_id.strip()
    if not normalized_id:
        raise ValueError("Sample IDs cannot be empty.")
    if Path(normalized_id).name != normalized_id or normalized_id in {".", ".."}:
        raise ValueError(f"Invalid sample ID: {sample_id!r}")
    return normalized_id


def load_sample_jobs(manifest_path: Path, output_path: Path) -> list[SampleJob]:
    """Load explicit ``sample_id,bam_path`` rows from a CSV manifest."""
    jobs = []
    sample_ids = set()
    with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
        rows = csv.DictReader(manifest_file)
        if rows.fieldnames != ["sample_id", "bam_path"]:
            raise ValueError(
                "Sample manifest header must be exactly: sample_id,bam_path"
            )

        for row_number, row in enumerate(rows, start=2):
            sample_id = _validate_sample_id(row["sample_id"])
            if sample_id in sample_ids:
                raise ValueError(
                    f"Duplicate sample ID on row {row_number}: {sample_id}"
                )
            sample_ids.add(sample_id)

            bam_value = row["bam_path"].strip()
            if not bam_value:
                raise ValueError(f"BAM path cannot be empty on row {row_number}.")
            alignment_path = Path(bam_value).expanduser()
            if not alignment_path.is_absolute():
                alignment_path = manifest_path.parent / alignment_path

            jobs.append(
                SampleJob(
                    sample_id=sample_id,
                    alignment_path=alignment_path.resolve(),
                    counts_path=(output_path / f"{sample_id}.counts.tsv").resolve(),
                )
            )

    if not jobs:
        raise ValueError("The sample manifest does not contain any samples.")
    return jobs


def _validate_inputs(jobs: list[SampleJob], gtf_path: Path) -> None:
    """Fail before submission when required scientific inputs are missing."""
    if not gtf_path.is_file():
        raise FileNotFoundError(f"GTF file not found: {gtf_path}")
    missing_alignments = [
        str(job.alignment_path) for job in jobs if not job.alignment_path.is_file()
    ]
    if missing_alignments:
        preview = ", ".join(missing_alignments[:3])
        suffix = " ..." if len(missing_alignments) > 3 else ""
        raise FileNotFoundError(f"BAM file(s) not found: {preview}{suffix}")


def _add_run_arguments(parser: argparse.ArgumentParser) -> None:
    """Define arguments for scheduler submissions."""
    parser.add_argument(
        "-f",
        "--infile",
        required=True,
        help="CSV manifest with sample_id,bam_path columns.",
    )
    parser.add_argument("-g", "--gtf", required=True, help="GTF/GFF annotation file.")
    parser.add_argument(
        "-o", "--outpath", required=True, help="Directory for count tables."
    )
    parser.add_argument(
        "--scheduler",
        choices=("pbs", "slurm"),
        default="pbs",
        help="Batch scheduler (default: pbs).",
    )
    parser.add_argument("-e", "--email", help="Scheduler notification address.")
    parser.add_argument("--cpus-per-task", type=int, default=1)
    parser.add_argument("--memory", default="2G")
    parser.add_argument("--time", dest="walltime", default="12:00:00")
    parser.add_argument(
        "--partition", help="Slurm partition or PBS queue, when required."
    )
    parser.add_argument("--account", help="Scheduler account or allocation.")
    parser.add_argument(
        "--max-concurrent",
        type=int,
        help="Maximum simultaneously running Slurm array tasks.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write submission files and print commands without submitting.",
    )


def _run(arguments: argparse.Namespace) -> None:
    """Validate inputs and dispatch a run request to one scheduler backend."""
    manifest_path = Path(arguments.infile).expanduser().resolve()
    output_path = Path(arguments.outpath).expanduser().resolve()
    gtf_path = Path(arguments.gtf).expanduser().resolve()
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Sample manifest not found: {manifest_path}")
    output_path.mkdir(parents=True, exist_ok=True)

    jobs = load_sample_jobs(manifest_path, output_path)
    _validate_inputs(jobs, gtf_path)
    resources = JobResources(
        cpus_per_task=arguments.cpus_per_task,
        memory=arguments.memory,
        walltime=arguments.walltime,
        partition=arguments.partition,
        account=arguments.account,
    )
    result = get_scheduler(arguments.scheduler).submit(
        jobs,
        gtf_path,
        output_path,
        resources,
        email=arguments.email,
        max_concurrent=arguments.max_concurrent,
        dry_run=arguments.dry_run,
    )
    if result.job_ids:
        LOGGER.info("Submitted job ID(s): %s", ", ".join(result.job_ids))
        return

    LOGGER.info("Dry run created %d script(s).", len(result.script_paths))
    for command in result.submission_commands:
        LOGGER.info("Submission command: %s", shlex.join(command))


def _build_parser() -> argparse.ArgumentParser:
    """Build the public 2.0 command-line interface."""
    parser = argparse.ArgumentParser(
        description="Submit and combine HTSeq count jobs.",
        epilog="Ensure that htseq-count is available in the batch environment.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND", required=True)

    run_parser = subparsers.add_parser(
        "run", help="Submit HTSeq count jobs to PBS/Torque or Slurm."
    )
    _add_run_arguments(run_parser)

    merge_parser = subparsers.add_parser(
        "merge", help="Merge sample count tables into one CSV file."
    )
    merge_parser.add_argument(
        "-d", "--directory", required=True, type=Path, help="Count-table directory."
    )

    status_parser = subparsers.add_parser("status", help="Query a scheduler job once.")
    status_parser.add_argument("job_id")
    status_parser.add_argument("--scheduler", choices=("pbs", "slurm"), default="pbs")
    return parser


def main() -> None:
    """Run the HTSeqCountCluster CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    arguments = _build_parser().parse_args()
    if arguments.command == "run":
        _run(arguments)
    elif arguments.command == "merge":
        merge_counts_tables(arguments.directory)
    elif arguments.command == "status":
        print(get_scheduler(arguments.scheduler).status(arguments.job_id))


if __name__ == "__main__":
    main()
