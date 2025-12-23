# -*- coding: utf-8 -*-
"""Tests for htseq_count_cluster module."""
import os
import sys
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from HTSeqCountCluster.htseq_count_cluster import (
    call_htseq,
    htseq_jobber,
    check_job_status,
    main
)


def test_call_htseq_returns_correct_command():
    """Test that call_htseq returns the expected command string."""
    infile = "sample.bam"
    gtf = "genes.gtf"
    outfile = "output"
    
    result = call_htseq(infile, gtf, outfile)
    
    expected = "htseq-count -f bam -s no {} {} -o {}_htseq.out".format(
        infile, gtf, outfile
    )
    assert result == expected
    assert "htseq-count" in result
    assert "-f bam" in result
    assert "-s no" in result
    assert infile in result
    assert gtf in result


@patch('HTSeqCountCluster.htseq_count_cluster.PBSJob')
@patch('HTSeqCountCluster.htseq_count_cluster.os.path.join')
def test_htseq_jobber_creates_jobs(mock_join, mock_pbs_job):
    """Test that htseq_jobber creates PBS jobs for each sample."""
    mock_join.side_effect = lambda *args: "/".join(args)
    mock_job = MagicMock()
    mock_job.submit_cmd.return_value = "12345"
    mock_pbs_job.return_value = mock_job
    
    input_path = "/path/to/input"
    inputlist = ["sample1", "sample2"]
    gtf = "genes.gtf"
    outpath = "/path/to/output"
    email = "test@example.com"
    
    jobids = htseq_jobber(input_path, inputlist, gtf, outpath, email)
    
    assert len(jobids) == 2
    assert mock_pbs_job.call_count == 2
    assert mock_job.submit_cmd.call_count == 2


@patch('HTSeqCountCluster.htseq_count_cluster.Qstat')
def test_check_job_status_finished(mock_qstat_class):
    """Test check_job_status returns 'Finished' when job not found."""
    mock_qstat = MagicMock()
    mock_qstat.watch.return_value = "Job id not found."
    mock_qstat_class.return_value = mock_qstat
    
    result = check_job_status("12345")
    assert result == "Finished"


@patch('HTSeqCountCluster.htseq_count_cluster.Qstat')
def test_check_job_status_queued(mock_qstat_class):
    """Test check_job_status returns 'Queued' when job is waiting."""
    mock_qstat = MagicMock()
    mock_qstat.watch.return_value = "Waiting for 12345 to start running."
    mock_qstat_class.return_value = mock_qstat
    
    result = check_job_status("12345")
    assert result == "Queued"


@patch('HTSeqCountCluster.htseq_count_cluster.Qstat')
def test_check_job_status_running(mock_qstat_class):
    """Test check_job_status returns 'Running' when job is running."""
    mock_qstat = MagicMock()
    mock_qstat.watch.return_value = "Waiting for 12345 to finish running."
    mock_qstat_class.return_value = mock_qstat
    
    result = check_job_status("12345")
    assert result == "Running"


@patch('HTSeqCountCluster.htseq_count_cluster.htseq_jobber')
@patch('HTSeqCountCluster.htseq_count_cluster.csvtolist')
@patch('sys.argv', ['htseq-count-cluster', 'run', '-p', '/path', '-f', 'samples.csv', 
                    '-g', 'genes.gtf', '-o', '/output'])
def test_main_run_subcommand(mock_csvtolist, mock_htseq_jobber):
    """Test main function with 'run' subcommand."""
    mock_csvtolist.return_value = ['sample1', 'sample2']
    
    main()
    
    mock_csvtolist.assert_called_once_with('samples.csv')
    mock_htseq_jobber.assert_called_once()


@patch('HTSeqCountCluster.htseq_count_cluster.merge_counts_tables')
@patch('sys.argv', ['htseq-count-cluster', 'merge', '-d', '/path/to/counts'])
def test_main_merge_subcommand(mock_merge):
    """Test main function with 'merge' subcommand."""
    main()
    
    mock_merge.assert_called_once_with(files_dir='/path/to/counts')


@patch('HTSeqCountCluster.htseq_count_cluster.htseq_jobber')
@patch('HTSeqCountCluster.htseq_count_cluster.csvtolist')
@patch('sys.argv', ['htseq-count-cluster', '-p', '/path', '-f', 'samples.csv',
                    '-g', 'genes.gtf', '-o', '/output'])
def test_main_legacy_mode(mock_csvtolist, mock_htseq_jobber):
    """Test main function with legacy mode (no subcommand)."""
    mock_csvtolist.return_value = ['sample1', 'sample2']
    
    main()
    
    mock_csvtolist.assert_called_once_with('samples.csv')
    mock_htseq_jobber.assert_called_once()
