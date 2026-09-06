"""Shared data structures and interfaces for cluster schedulers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SampleJob:
    """Describe one HTSeq count operation without scheduler-specific details."""

    sample_id: str
    alignment_path: Path
    counts_path: Path


@dataclass(frozen=True)
class JobResources:
    """Resources requested for each scheduler task."""

    cpus_per_task: int = 1
    memory: str = "2G"
    walltime: str = "12:00:00"
    partition: str | None = None
    account: str | None = None


@dataclass(frozen=True)
class SubmissionResult:
    """Record scheduler identifiers and files created during submission."""

    job_ids: tuple[str, ...]
    script_paths: tuple[Path, ...] = ()
    manifest_path: Path | None = None
    submission_commands: tuple[tuple[str, ...], ...] = ()


class Scheduler(ABC):
    """Interface implemented by supported batch schedulers."""

    @abstractmethod
    def submit(
        self,
        jobs: list[SampleJob],
        gtf_path: Path,
        output_directory: Path,
        resources: JobResources,
        *,
        email: str | None = None,
        max_concurrent: int | None = None,
        dry_run: bool = False,
    ) -> SubmissionResult:
        """Submit sample jobs and return scheduler metadata."""

    @abstractmethod
    def status(self, job_id: str) -> str:
        """Return a normalized, one-shot status for a scheduler job."""


def validate_submission(
    jobs: list[SampleJob],
    resources: JobResources,
    max_concurrent: int | None,
) -> None:
    """Validate scheduler-neutral submission constraints before writing files."""
    if not jobs:
        raise ValueError("At least one sample is required for submission.")
    if resources.cpus_per_task < 1:
        raise ValueError("cpus_per_task must be at least 1.")
    if max_concurrent is not None and max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1.")
