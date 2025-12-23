# -*- coding: utf-8 -*-
"""Tests for utils module."""
import os
import sys
import tempfile
import shutil
import pytest

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from HTSeqCountCluster.utils import csvtolist


@pytest.fixture
def test_dir():
    """Create a temporary directory for testing."""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    shutil.rmtree(test_dir)


def test_csvtolist_returns_sorted_list(test_dir):
    """Test that csvtolist returns a sorted list from CSV file."""
    # Create a temporary CSV file
    csv_content = "sample3\nsample1\nsample2\n"
    csv_file = os.path.join(test_dir, "test.csv")
    
    with open(csv_file, 'w') as f:
        f.write(csv_content)
    
    result = csvtolist(csv_file)
    
    assert result == ['sample1', 'sample2', 'sample3']
    assert isinstance(result, list)


def test_csvtolist_with_specific_column(test_dir):
    """Test that csvtolist can read a specific column."""
    # Create a CSV file with multiple columns
    csv_content = "col1,col2\nsample1,other1\nsample2,other2\n"
    csv_file = os.path.join(test_dir, "test.csv")
    
    with open(csv_file, 'w') as f:
        f.write(csv_content)
    
    result = csvtolist(csv_file, column=0)
    
    assert 'sample1' in result
    assert 'sample2' in result
