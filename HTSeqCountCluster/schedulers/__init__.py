"""Scheduler selection for HTSeqCountCluster."""

from HTSeqCountCluster.schedulers.base import JobResources, SampleJob, SubmissionResult
from HTSeqCountCluster.schedulers.pbs import PBSScheduler
from HTSeqCountCluster.schedulers.slurm import SlurmScheduler


def get_scheduler(name: str):
    """Construct the requested scheduler backend."""
    if name == "pbs":
        return PBSScheduler()
    if name == "slurm":
        return SlurmScheduler()
    raise ValueError(f"Unsupported scheduler: {name}")


__all__ = [
    "JobResources",
    "SampleJob",
    "SubmissionResult",
    "get_scheduler",
]
