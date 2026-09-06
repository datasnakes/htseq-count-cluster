"""Tests for direct PBS/Torque submission and status mapping."""

from unittest.mock import MagicMock, patch

from HTSeqCountCluster.schedulers.base import JobResources, SampleJob
from HTSeqCountCluster.schedulers.pbs import PBSScheduler


def _jobs(tmp_path):
    return [
        SampleJob("sample-a", tmp_path / "a.bam", tmp_path / "sample-a.counts.tsv"),
        SampleJob("sample-b", tmp_path / "b.bam", tmp_path / "sample-b.counts.tsv"),
    ]


@patch("HTSeqCountCluster.schedulers.pbs.subprocess.run")
def test_submit_uses_one_qsub_command_per_sample(mock_run, tmp_path):
    mock_run.side_effect = [
        MagicMock(stdout="12345.server\n"),
        MagicMock(stdout="12346.server\n"),
    ]

    result = PBSScheduler().submit(
        _jobs(tmp_path),
        tmp_path / "genes.gtf",
        tmp_path,
        JobResources(memory="8gb", partition="batch"),
    )

    assert result.job_ids == ("12345.server", "12346.server")
    assert mock_run.call_count == 2
    first_command = mock_run.call_args_list[0].args[0]
    assert first_command[0] == "qsub"
    assert "select=1:ncpus=1:mem=8gb" in first_command
    assert "batch" in first_command
    assert all(script.is_file() for script in result.script_paths)


@patch("HTSeqCountCluster.schedulers.pbs.subprocess.run")
def test_dry_run_writes_files_without_calling_qsub(mock_run, tmp_path):
    result = PBSScheduler().submit(
        _jobs(tmp_path),
        tmp_path / "genes.gtf",
        tmp_path,
        JobResources(),
        dry_run=True,
    )

    mock_run.assert_not_called()
    assert result.job_ids == ()
    assert len(result.submission_commands) == 2
    assert result.manifest_path.is_file()


@patch("HTSeqCountCluster.schedulers.pbs.subprocess.run")
def test_status_maps_qstat_running_state(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0, stdout="Job Id: 12345.server\n    job_state = R\n"
    )

    assert PBSScheduler().status("12345.server") == "Running"


@patch("HTSeqCountCluster.schedulers.pbs.subprocess.run")
def test_status_does_not_assume_missing_job_succeeded(mock_run):
    mock_run.return_value = MagicMock(returncode=153, stdout="")

    assert PBSScheduler().status("12345.server") == "Unknown"
