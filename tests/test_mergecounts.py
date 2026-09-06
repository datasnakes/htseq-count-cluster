"""Tests for strict merging of HTSeq count tables."""

import csv

import pytest

from HTSeqCountCluster.mergecounts import merge_counts_tables


def test_merge_counts_tables_writes_sorted_sample_columns(tmp_path):
    (tmp_path / "sample-b.counts.tsv").write_text(
        "gene1\t4\ngene2\t5\n", encoding="utf-8"
    )
    (tmp_path / "sample-a.counts.tsv").write_text(
        "gene1\t1\ngene2\t2\n", encoding="utf-8"
    )

    merged_path = merge_counts_tables(tmp_path)

    with merged_path.open(encoding="utf-8", newline="") as merged_file:
        rows = list(csv.reader(merged_file))
    assert rows == [
        ["Genes", "sample-a", "sample-b"],
        ["gene1", "1", "4"],
        ["gene2", "2", "5"],
    ]


def test_merge_counts_tables_rejects_mismatched_gene_order(tmp_path):
    (tmp_path / "sample-a.counts.tsv").write_text(
        "gene1\t1\ngene2\t2\n", encoding="utf-8"
    )
    (tmp_path / "sample-b.counts.tsv").write_text(
        "gene2\t4\ngene1\t5\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Gene IDs or row order"):
        merge_counts_tables(tmp_path)


def test_merge_counts_tables_rejects_duplicate_gene_ids(tmp_path):
    (tmp_path / "sample.counts.tsv").write_text(
        "gene1\t1\ngene1\t2\n", encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Duplicate gene ID"):
        merge_counts_tables(tmp_path)


def test_merge_counts_tables_rejects_empty_directory(tmp_path):
    with pytest.raises(ValueError, match=r"No \*\.counts\.tsv files"):
        merge_counts_tables(tmp_path)
