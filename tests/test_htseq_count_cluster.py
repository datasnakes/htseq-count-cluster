"""Tests for the public command-line interface."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from HTSeqCountCluster.htseq_count_cluster import load_sample_jobs, main


def test_load_sample_jobs_resolves_relative_bam_paths(tmp_path):
    bam_path = tmp_path / "alignments" / "sample one.bam"
    bam_path.parent.mkdir()
    bam_path.touch()
    manifest_path = tmp_path / "samples.csv"
    manifest_path.write_text(
        "sample_id,bam_path\nsample-1,alignments/sample one.bam\n",
        encoding="utf-8",
    )

    jobs = load_sample_jobs(manifest_path, tmp_path / "counts")

    assert jobs[0].sample_id == "sample-1"
    assert jobs[0].alignment_path == bam_path
    assert jobs[0].counts_path == tmp_path / "counts" / "sample-1.counts.tsv"


def test_load_sample_jobs_requires_explicit_header(tmp_path):
    manifest_path = tmp_path / "samples.csv"
    manifest_path.write_text("sample1,/data/sample1.bam\n", encoding="utf-8")

    with pytest.raises(ValueError, match="header must be exactly"):
        load_sample_jobs(manifest_path, tmp_path / "counts")


def test_load_sample_jobs_rejects_duplicate_ids(tmp_path):
    manifest_path = tmp_path / "samples.csv"
    manifest_path.write_text(
        "sample_id,bam_path\nsample1,a.bam\nsample1,b.bam\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Duplicate sample ID"):
        load_sample_jobs(manifest_path, tmp_path / "counts")


@patch("HTSeqCountCluster.htseq_count_cluster._run")
@patch(
    "sys.argv",
    [
        "htseq-count-cluster",
        "run",
        "-f",
        "samples.csv",
        "-g",
        "genes.gtf",
        "-o",
        "counts",
    ],
)
def test_main_run_defaults_to_pbs(mock_run):
    main()

    assert mock_run.call_args.args[0].scheduler == "pbs"


@patch("HTSeqCountCluster.htseq_count_cluster.merge_counts_tables")
@patch("sys.argv", ["htseq-count-cluster", "merge", "-d", "counts"])
def test_main_merge_subcommand(mock_merge):
    main()

    mock_merge.assert_called_once_with(Path("counts"))


@patch("HTSeqCountCluster.htseq_count_cluster.get_scheduler")
@patch(
    "sys.argv",
    ["htseq-count-cluster", "status", "--scheduler", "pbs", "12345.server"],
)
def test_main_status_subcommand(mock_get_scheduler, capsys):
    scheduler = MagicMock()
    scheduler.status.return_value = "Running"
    mock_get_scheduler.return_value = scheduler

    main()

    assert capsys.readouterr().out == "Running\n"
    scheduler.status.assert_called_once_with("12345.server")
