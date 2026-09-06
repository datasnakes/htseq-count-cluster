"""PBS/Torque submission and one-shot job-status support."""

from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex

from HTSeqCountCluster.runner import write_manifest, write_task_script
from HTSeqCountCluster.schedulers.base import (
    JobResources,
    SampleJob,
    Scheduler,
    SubmissionResult,
    validate_submission,
)

_SAFE_JOB_NAME = re.compile(r"[^A-Za-z0-9_-]+")


def _normalize_job_name(name: str) -> str:
    """Return a conservative name accepted by common PBS installations."""
    normalized = _SAFE_JOB_NAME.sub("_", name).strip("_-")
    return (normalized or "htseq-count")[:64]


class PBSScheduler(Scheduler):
    """Submit one independently traceable PBS/Torque job per sample."""

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
        validate_submission(jobs, resources, max_concurrent)
        if max_concurrent is not None:
            raise ValueError("--max-concurrent is supported only for Slurm arrays.")

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        submission_name = _normalize_job_name(f"htseq-count-{timestamp}-{token_hex(2)}")
        submission_directory = (
            output_directory.resolve() / ".htseq-count-cluster" / submission_name
        )
        scripts_directory = submission_directory / "scripts"
        logs_directory = submission_directory / "logs"
        scripts_directory.mkdir(parents=True, exist_ok=False)
        logs_directory.mkdir(parents=True, exist_ok=False)

        manifest_path = submission_directory / "samples.tsv"
        write_manifest(manifest_path, jobs)

        commands: list[tuple[str, ...]] = []
        script_paths: list[Path] = []
        for task_index, job in enumerate(jobs):
            job_name = _normalize_job_name(f"htseq-{job.sample_id}")
            script_path = scripts_directory / f"{task_index:04d}-{job_name}.sh"
            write_task_script(
                script_path,
                manifest_path,
                str(task_index),
                gtf_path.resolve(),
            )
            script_paths.append(script_path)

            command = [
                "qsub",
                "-N",
                job_name,
                "-l",
                f"select=1:ncpus={resources.cpus_per_task}:mem={resources.memory}",
                "-l",
                f"walltime={resources.walltime}",
                "-o",
                str(logs_directory / f"{job_name}.out"),
                "-e",
                str(logs_directory / f"{job_name}.err"),
            ]
            if resources.partition:
                command.extend(("-q", resources.partition))
            if resources.account:
                command.extend(("-A", resources.account))
            if email:
                command.extend(("-M", email, "-m", "ae"))
            command.append(str(script_path))
            commands.append(tuple(command))

        if dry_run:
            return SubmissionResult(
                job_ids=(),
                script_paths=tuple(script_paths),
                manifest_path=manifest_path,
                submission_commands=tuple(commands),
            )

        job_ids = []
        for command in commands:
            completed_process = subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            job_id = completed_process.stdout.strip().split(maxsplit=1)[0]
            if not job_id:
                raise RuntimeError("qsub succeeded without returning a job ID.")
            job_ids.append(job_id)

        return SubmissionResult(
            job_ids=tuple(job_ids),
            script_paths=tuple(script_paths),
            manifest_path=manifest_path,
            submission_commands=tuple(commands),
        )

    def status(self, job_id: str) -> str:
        """Map the state from ``qstat -f`` to the public status vocabulary."""
        completed_process = subprocess.run(
            ["qstat", "-f", job_id],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed_process.returncode != 0:
            return "Unknown"

        state_match = re.search(
            r"^\s*job_state\s*=\s*(\S+)",
            completed_process.stdout,
            flags=re.MULTILINE,
        )
        if not state_match:
            return "Unknown"
        return _normalize_state(state_match.group(1))


def _normalize_state(state: str) -> str:
    """Normalize standard PBS single-letter job states."""
    normalized = state.upper()
    if normalized in {"Q", "H", "W", "T"}:
        return "Queued"
    if normalized in {"R", "E", "B"}:
        return "Running"
    if normalized in {"C", "F"}:
        return "Finished"
    return "Unknown"
