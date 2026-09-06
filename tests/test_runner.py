"""Tests for execution of one manifest task."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from HTSeqCountCluster.runner import load_manifest_row, run_manifest_task


def test_load_manifest_row_selects_array_index(tmp_path):
    manifest_path = tmp_path / "samples.tsv"
    manifest_path.write_text(
        "sample_id\talignment_path\tcounts_path\n"
        "sample1\t/a.bam\t/a.tsv\n"
        "sample2\t/b.bam\t/b.tsv\n",
        encoding="utf-8",
    )

    assert load_manifest_row(manifest_path, 1)["sample_id"] == "sample2"


@patch("HTSeqCountCluster.runner.subprocess.run")
def test_run_manifest_task_uses_argument_list_and_stdout(mock_run, tmp_path):
    counts_path = tmp_path / "nested" / "sample.counts.tsv"
    manifest_path = tmp_path / "samples.tsv"
    manifest_path.write_text(
        "sample_id\talignment_path\tcounts_path\n"
        f"sample1\t{tmp_path / 'sample input.bam'}\t{counts_path}\n",
        encoding="utf-8",
    )

    run_manifest_task(manifest_path, 0, Path("genes.gtf"))

    assert mock_run.call_args.args[0] == [
        "htseq-count",
        "--format=bam",
        "--stranded=no",
        str(tmp_path / "sample input.bam"),
        "genes.gtf",
    ]
    assert mock_run.call_args.kwargs["check"] is True
    assert counts_path.exists()


@patch("HTSeqCountCluster.runner.subprocess.run")
def test_run_manifest_task_removes_partial_output_after_failure(mock_run, tmp_path):
    mock_run.side_effect = subprocess.CalledProcessError(1, ["htseq-count"])
    counts_path = tmp_path / "sample.counts.tsv"
    manifest_path = tmp_path / "samples.tsv"
    manifest_path.write_text(
        "sample_id\talignment_path\tcounts_path\n"
        f"sample1\t{tmp_path / 'sample.bam'}\t{counts_path}\n",
        encoding="utf-8",
    )

    with pytest.raises(subprocess.CalledProcessError):
        run_manifest_task(manifest_path, 0, Path("genes.gtf"))

    assert not counts_path.exists()
    assert not list(tmp_path.glob("*.tmp"))
