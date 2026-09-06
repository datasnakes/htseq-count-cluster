"""Run one HTSeq task from a scheduler-neutral sample manifest."""

from __future__ import annotations

import argparse
import csv
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from HTSeqCountCluster.schedulers.base import SampleJob


def htseq_arguments(alignment_path: Path, gtf_path: Path) -> list[str]:
    """Build the stable HTSeq arguments shared by PBS and Slurm."""
    return [
        "htseq-count",
        "--format=bam",
        "--stranded=no",
        str(alignment_path),
        str(gtf_path),
    ]


def write_manifest(path: Path, jobs: list[SampleJob]) -> None:
    """Persist scheduler-neutral task inputs for a submitted job group."""
    with path.open("w", encoding="utf-8", newline="") as manifest_file:
        writer = csv.writer(manifest_file, delimiter="\t", lineterminator="\n")
        writer.writerow(("sample_id", "alignment_path", "counts_path"))
        for job in jobs:
            writer.writerow(
                (job.sample_id, str(job.alignment_path), str(job.counts_path))
            )


def write_task_script(
    path: Path,
    manifest_path: Path,
    task_index: str,
    gtf_path: Path,
) -> None:
    """Write a safely quoted shell wrapper for one manifest task index."""
    index_placeholder = "__HTSEQ_COUNT_CLUSTER_TASK_INDEX__"
    command = shlex.join(
        [
            sys.executable,
            "-m",
            "HTSeqCountCluster.runner",
            "--manifest",
            str(manifest_path),
            "--index",
            index_placeholder,
            "--gtf",
            str(gtf_path),
        ]
    ).replace(index_placeholder, task_index)
    path.write_text(
        f"#!/usr/bin/env bash\nset -euo pipefail\n\n{command}\n", encoding="utf-8"
    )
    path.chmod(0o750)


def load_manifest_row(manifest_path: Path, index: int) -> dict[str, str]:
    """Load exactly one array task without relying on shell text parsing."""
    with manifest_path.open(encoding="utf-8", newline="") as manifest_file:
        rows = csv.DictReader(manifest_file, delimiter="\t")
        for row_index, row in enumerate(rows):
            if row_index == index:
                required_fields = {"sample_id", "alignment_path", "counts_path"}
                if not required_fields <= row.keys():
                    raise ValueError("Task manifest is missing required columns.")
                return row
    raise IndexError(f"Manifest has no sample at array index {index}.")


def run_manifest_task(manifest_path: Path, index: int, gtf_path: Path) -> None:
    """Execute HTSeq and write its count table to the declared sample output."""
    task = load_manifest_row(manifest_path, index)
    counts_path = Path(task["counts_path"])
    counts_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_counts_path = counts_path.with_name(
        f".{counts_path.name}.{os.getpid()}.tmp"
    )
    try:
        with temporary_counts_path.open("w", encoding="utf-8") as counts_file:
            subprocess.run(
                htseq_arguments(Path(task["alignment_path"]), gtf_path),
                check=True,
                stdout=counts_file,
            )
        # Publish the table atomically so a failed HTSeq process never leaves a
        # partial file that a downstream merge could mistake for valid output.
        temporary_counts_path.replace(counts_path)
    except BaseException:
        temporary_counts_path.unlink(missing_ok=True)
        raise


def main() -> None:
    """Run the manifest row selected by a Slurm array index."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--index", required=True, type=int)
    parser.add_argument("--gtf", required=True, type=Path)
    arguments = parser.parse_args()
    run_manifest_task(arguments.manifest, arguments.index, arguments.gtf)


if __name__ == "__main__":
    main()
