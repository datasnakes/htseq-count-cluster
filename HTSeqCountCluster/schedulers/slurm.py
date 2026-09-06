"""Slurm array submission and one-shot job-status support."""

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
    """Return a short Slurm-safe name while retaining recognizable sample text."""
    normalized = _SAFE_JOB_NAME.sub("_", name).strip("_-")
    return (normalized or "htseq-count")[:96]


class SlurmScheduler(Scheduler):
    """Submit all samples as one throttled Slurm array."""

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
        output_directory = output_directory.resolve()
        gtf_path = gtf_path.resolve()

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        job_name = _normalize_job_name(f"htseq-count-{timestamp}-{token_hex(2)}")
        submission_directory = output_directory / ".htseq-count-cluster" / job_name
        logs_directory = submission_directory / "logs"
        logs_directory.mkdir(parents=True, exist_ok=False)

        manifest_path = submission_directory / "samples.tsv"
        script_path = submission_directory / "run-array.sh"
        write_manifest(manifest_path, jobs)
        write_task_script(
            script_path, manifest_path, '"${SLURM_ARRAY_TASK_ID}"', gtf_path
        )

        array_specification = f"0-{len(jobs) - 1}"
        if max_concurrent is not None:
            array_specification += f"%{max_concurrent}"

        command = [
            "sbatch",
            "--parsable",
            f"--job-name={job_name}",
            "--nodes=1",
            "--ntasks=1",
            f"--cpus-per-task={resources.cpus_per_task}",
            f"--mem={resources.memory}",
            f"--time={resources.walltime}",
            f"--array={array_specification}",
            f"--output={logs_directory}/%x_%A_%a.out",
            f"--error={logs_directory}/%x_%A_%a.err",
        ]
        if resources.partition:
            command.append(f"--partition={resources.partition}")
        if resources.account:
            command.append(f"--account={resources.account}")
        if email:
            command.extend((f"--mail-user={email}", "--mail-type=END,FAIL"))
        command.append(str(script_path))

        if dry_run:
            return SubmissionResult(
                job_ids=(),
                script_paths=(script_path,),
                manifest_path=manifest_path,
                submission_commands=(tuple(command),),
            )

        completed_process = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        # --parsable may return "job_id;cluster_name" on federated clusters.
        job_id = completed_process.stdout.strip().split(";", maxsplit=1)[0]
        if not job_id:
            raise RuntimeError("sbatch succeeded without returning a job ID.")

        return SubmissionResult(
            job_ids=(job_id,),
            script_paths=(script_path,),
            manifest_path=manifest_path,
            submission_commands=(tuple(command),),
        )

    def status(self, job_id: str) -> str:
        """Query current jobs first, then accounting for completed jobs."""
        queue_result = subprocess.run(
            ["squeue", "--noheader", "--jobs", job_id, "--format=%i|%T"],
            check=True,
            capture_output=True,
            text=True,
        )
        queue_states = _parse_states(queue_result.stdout, job_id)
        if queue_states:
            return _normalize_states(queue_states)

        accounting_result = subprocess.run(
            [
                "sacct",
                "--allocations",
                "--noheader",
                "--parsable2",
                "--jobs",
                job_id,
                "--format=JobIDRaw,State",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        accounting_states = _parse_states(accounting_result.stdout, job_id)
        return _normalize_states(accounting_states) if accounting_states else "Unknown"


def _parse_states(output: str, job_id: str) -> list[str]:
    """Extract states for a job allocation and any of its array tasks."""
    states = []
    for line in output.splitlines():
        fields = line.strip().split("|", maxsplit=2)
        if len(fields) < 2:
            continue
        reported_id, state = fields[:2]
        if reported_id == job_id or reported_id.startswith(f"{job_id}_"):
            states.append(state.split()[0].rstrip("+"))
    return states


def _normalize_states(states: list[str]) -> str:
    """Summarize Slurm states using the package's stable status vocabulary."""
    state_set = {state.upper() for state in states}
    if state_set & {"RUNNING", "COMPLETING"}:
        return "Running"
    if state_set & {"PENDING", "CONFIGURING", "REQUEUED", "RESIZING"}:
        return "Queued"
    if state_set and state_set <= {"COMPLETED"}:
        return "Finished"
    if state_set & {
        "BOOT_FAIL",
        "CANCELLED",
        "DEADLINE",
        "FAILED",
        "NODE_FAIL",
        "OUT_OF_MEMORY",
        "PREEMPTED",
        "TIMEOUT",
    }:
        return "Failed"
    return "Unknown"
