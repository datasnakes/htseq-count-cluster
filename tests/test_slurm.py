"""Tests for Slurm array submission and status parsing."""

from unittest.mock import MagicMock, patch

from HTSeqCountCluster.schedulers.base import JobResources, SampleJob
from HTSeqCountCluster.schedulers.slurm import SlurmScheduler


def _jobs(tmp_path):
    return [
        SampleJob("sample-a", tmp_path / "a.bam", tmp_path / "sample-a.counts.tsv"),
        SampleJob("sample-b", tmp_path / "b.bam", tmp_path / "sample-b.counts.tsv"),
    ]


@patch("HTSeqCountCluster.schedulers.slurm.subprocess.run")
def test_submit_uses_parsable_throttled_array(mock_run, tmp_path):
    mock_run.return_value = MagicMock(stdout="12345;cluster\n")

    result = SlurmScheduler().submit(
        _jobs(tmp_path),
        tmp_path / "genes.gtf",
        tmp_path,
        JobResources(
            cpus_per_task=2,
            memory="8G",
            walltime="02:00:00",
            partition="express",
            account="lab_account",
        ),
        email="researcher@example.com",
        max_concurrent=1,
    )

    command = mock_run.call_args.args[0]
    assert result.job_ids == ("12345",)
    assert "--parsable" in command
    assert "--array=0-1%1" in command
    assert "--cpus-per-task=2" in command
    assert "--partition=express" in command
    assert "--account=lab_account" in command
    assert "--mail-type=END,FAIL" in command
    assert result.manifest_path.read_text(encoding="utf-8").count("\n") == 3
    assert "SLURM_ARRAY_TASK_ID" in result.script_paths[0].read_text(encoding="utf-8")


@patch("HTSeqCountCluster.schedulers.slurm.subprocess.run")
def test_dry_run_writes_files_without_calling_sbatch(mock_run, tmp_path):
    result = SlurmScheduler().submit(
        _jobs(tmp_path),
        tmp_path / "genes.gtf",
        tmp_path,
        JobResources(),
        dry_run=True,
    )

    mock_run.assert_not_called()
    assert result.job_ids == ()
    assert result.script_paths[0].is_file()
    assert result.manifest_path.is_file()


@patch("HTSeqCountCluster.schedulers.slurm.subprocess.run")
def test_status_reads_running_job_from_squeue(mock_run):
    mock_run.return_value = MagicMock(stdout="12345_0|RUNNING\n")

    assert SlurmScheduler().status("12345") == "Running"
    assert mock_run.call_count == 1


@patch("HTSeqCountCluster.schedulers.slurm.subprocess.run")
def test_status_falls_back_to_sacct(mock_run):
    mock_run.side_effect = [
        MagicMock(stdout=""),
        MagicMock(stdout="12345_0|COMPLETED|\n12345_1|COMPLETED|\n"),
    ]

    assert SlurmScheduler().status("12345") == "Finished"
    assert mock_run.call_args.args[0][0] == "sacct"
