import sys
import argparse
import re
from pathlib import Path

from lxml import etree


def main(args:argparse.Namespace):
    """Creates a an export with selected items from the input."""
    
    # Get list of things to include and possibly exclude
    take, skip = parse_specs(args)
    
    if not take:
        error(1, "No items to include specified.")
        
    
    # Open the input file, and get it's root element:
    parser = etree.XMLParser(strip_cdata=False)
    intree = etree.parse(args.infile, parser=parser)
    inroot = intree.getroot()
    
    # Create a root element for the output file
    outroot = etree.Element(inroot.tag)
    outroot.attrib.update(inroot.attrib)
    outroot.text = '\n\n'
    outroot.tail = '\n'
    
    # Loop through items in input file, add to output if needed
    for item in inroot:
        if not include(item, take, skip):
            continue
        outroot.append(item)
        item.tail = '\n\n'
    
    # Create an ElementTree for the output, and use it to write the file
    outtree = etree.ElementTree(outroot)
    outtree.write(args.outfile, with_tail=True, xml_declaration=True, encoding='UTF-8')


def include(item, take, skip) -> bool:
    """Determine whether to include this item"""
    
    # Get the name as used in the take/skip specs
    itemname = determine_item_name(item)
    
    # Process skip list first, then take
    for lst, rv in (skip, False), (take, True):
        for spec in lst:
            if isinstance(spec, str):
                if spec != itemname:
                    continue
                return rv
            else:
                if not spec.match(itemname):
                    continue
                return rv
    
    return False


def determine_item_name(item) -> str:
    """Determine the name as used in the item specs"""
    
    tag = item.tag
    name = str(item.attrib['name'])
    if tag == 'Class':
        itemtype = 'cls'
    elif tag == 'Routine':
        itemtype = str(item.attrib['type']).lower()
    else:
        print(f"Warning: skipping element {tag}, don't know how to handle it")
        return ''
    
    return f"{name}.{itemtype}"


def parse_specs(args:argparse.Namespace):
    """Splits take and skip specs, handles regexes"""
    
    # Setup lists for results
    take:list[str|re.Pattern] = []
    skip:list[str|re.Pattern] = []
    
    for spec in args.items:
        if spec[0] == '@':
            # File containing the specs
            read_spec_file(Path(spec[1:]), take, skip)
        else:
            check_single_spec(spec, take, skip)
    
    return take, skip


def read_spec_file(specfile:Path, take, skip):
    if not specfile.exists():
        return error(2, f"Spec file '{specfile}' does not exist")
    
    with specfile.open(encoding='UTF-8') as f:
        for line in f:
            line = line.strip()
            check_single_spec(line, take, skip)


def check_single_spec(spec, take, skip):
    """Checks a single spec (take/skip, normal/regex)"""
    
    # Determine if this is a take or skip spec
    if spec[0] == '-':
        addto = skip
        spec = spec[1:]
    else:
        addto = take
    
    # Determine whether we need a regex
    if not '*' in spec:
        addto.append(spec)
        return
    
    # Create regular expression
    spec = spec.replace('\\', '\\\\')
    spec = spec.replace('.', r'\.')
    spec = spec.replace('*', '.*')
    rx = re.compile(spec, re.I)
    
    addto.append(rx)
    

def error(exitcode:int, msg:str):
    print(msg, file=sys.stderr)
    sys.exit(exitcode)


def setup_argparse():
    """Set up the argparse argument parser"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", type=argparse.FileType('rb'),
       help="The name of the input file, containing the export"
            " to extract from")
    parser.add_argument("outfile",
       help="The name of the output file to create")
    parser.add_argument("items", nargs='+', metavar='item',
       help="The names of one or more items to extract;"
            " prefix with @ to read from a file")
    return parser


if __name__ == '__main__':
    parser = setup_argparse()
    args = parser.parse_args()
    main(args)
