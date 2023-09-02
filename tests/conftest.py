import argparse
from pathlib import Path

from lxml import etree
import pytest

import extract


@pytest.fixture
def run():
    def run(specs:list[str], tmp_path) -> Path:
        here = Path(__file__).parent
        
        input = str(here / 'export.xml')
        output = tmp_path / 'out.xml'
        
        ns = argparse.Namespace()
        ns.infile = input
        ns.outfile = str(output)
        ns.items = specs
        
        extract.main(ns)
        
        return output
        
    return run


@pytest.fixture(scope='session')
def export_items() -> list[str]:
    here = Path(__file__).parent
    input = str(here / 'export.xml')
    intree = etree.parse(input)
    name = extract.determine_item_name
    return [ name(item) for item in intree.getroot() ]

