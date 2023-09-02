import argparse
from pathlib import Path

from lxml import etree
import pytest

import extract


def test_all_spec(export_items, run, tmp_path):
    """Test copying all items using '*'"""
    
    output = run(['*'], tmp_path)
    assert output.exists(), f"Expected {output} to exist"
    
    outroot = etree.parse(output).getroot()
    dst = [ extract.determine_item_name(item) for item in outroot ]
    
    assert dst == export_items, "Expected all source items in output file"


def test_all_excluded(run, tmp_path):
    """Test excluding all items using '-*'"""
    output = run(['*', '-*'], tmp_path)
    assert output.exists(), f"Expected {output} to exist"
    
    outroot = etree.parse(output).getroot()
    dst = [ extract.determine_item_name(item) for item in outroot ]
    
    assert dst == [], "Expected all source items to be skipped"


def test_all_from_file(export_items, run, tmp_path):
    """Test loading star spec from file"""
    
    specfile = str(Path(__file__).parent / 'spec_all.txt')
    output = run([f"@{specfile}"], tmp_path)
    assert output.exists(), f"Expected {output} to exist"
    
    outroot = etree.parse(output).getroot()
    dst = [ extract.determine_item_name(item) for item in outroot ]
    
    assert dst == export_items, "Expected all source items in output file"


def test_assure_positive_spec(run, tmp_path):
    """Tests error when no positive specs are present"""
    
    with pytest.raises(SystemExit) as e:
        output = run(['-*'], tmp_path)
    code = e.value.code
    assert code is not None, "Expected an exit code, not None"
    assert int(code) > 0, "Expected a non-zero exit code"
    
