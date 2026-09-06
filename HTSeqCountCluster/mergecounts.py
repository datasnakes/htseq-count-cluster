"""Combine per-sample HTSeq count tables."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _sample_name(counts_path: Path) -> str:
    """Derive the sample identifier from the 2.0 count-table suffix."""
    return counts_path.name.removesuffix(".counts.tsv")


def _read_count_table(counts_path: Path) -> tuple[list[str], list[str]]:
    """Read one two-column HTSeq table and reject ambiguous gene identifiers."""
    gene_ids = []
    counts = []
    seen_gene_ids = set()
    with counts_path.open(encoding="utf-8", newline="") as counts_file:
        rows = csv.reader(counts_file, delimiter="\t")
        for row_number, row in enumerate(rows, start=1):
            if len(row) != 2:
                raise ValueError(
                    f"{counts_path} row {row_number} must contain exactly two columns."
                )
            gene_id, count = row
            if gene_id in seen_gene_ids:
                raise ValueError(f"Duplicate gene ID in {counts_path}: {gene_id}")
            seen_gene_ids.add(gene_id)
            gene_ids.append(gene_id)
            counts.append(count)
    if not gene_ids:
        raise ValueError(f"Count table is empty: {counts_path}")
    return gene_ids, counts


def merge_counts_tables(files_dir: str | Path) -> Path:
    """Merge count tables only when their gene identifiers and order agree."""
    files_directory = Path(files_dir).expanduser().resolve()
    count_files = sorted(files_directory.glob("*.counts.tsv"))
    if not count_files:
        raise ValueError(f"No *.counts.tsv files found in {files_directory}.")

    sample_names = [_sample_name(path) for path in count_files]
    if len(sample_names) != len(set(sample_names)):
        raise ValueError(
            "Sample names derived from count-table filenames must be unique."
        )

    expected_gene_ids: list[str] | None = None
    sample_counts: list[list[str]] = []
    for counts_path in count_files:
        gene_ids, counts = _read_count_table(counts_path)
        if expected_gene_ids is None:
            expected_gene_ids = gene_ids
        elif gene_ids != expected_gene_ids:
            raise ValueError(
                f"Gene IDs or row order in {counts_path} do not match {count_files[0]}."
            )
        sample_counts.append(counts)
        LOGGER.info("Loaded count table for %s.", _sample_name(counts_path))

    merged_path = files_directory / "merged_counts_table.csv"
    with merged_path.open("w", encoding="utf-8", newline="") as merged_file:
        writer = csv.writer(merged_file, lineterminator="\n")
        writer.writerow(["Genes", *sample_names])
        assert expected_gene_ids is not None
        for row_index, gene_id in enumerate(expected_gene_ids):
            writer.writerow([gene_id, *(counts[row_index] for counts in sample_counts)])

    LOGGER.info("Merged counts were saved in %s.", merged_path)
    return merged_path
