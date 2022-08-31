#!/usr/bin/env python3

import argparse # for parsing command-line arguments
from lxml import etree as et # for reading TEI XML inputs

from tei_collation_converter import Collation

"""
Entry point to the script. Parses command-line arguments and calls the core functions.
"""
def main():
    parser = argparse.ArgumentParser(description="Converts a specified TEI XML collation to a given output format.")
    parser.add_argument("-t", metavar="trivial_reading_types", type=str, action="append", help="Reading types to treat as trivial and collapse with the previous substantive reading (e.g., reconstructed, defective, orthographic, subreading). If more than one type is applicable, this argument can be specified multiple times.")
    parser.add_argument("-m", metavar="missing_reading_types", type=str, action="append", help="Reading types to treat as missing data (e.g., lac, overlap). If more than one type is applicable, this argument can be specified multiple times.")
    parser.add_argument("-s", metavar="suffix", type=str, action="append", help="Suffixes to ignore for manuscript witness sigla. Typically, these will be things like the sigla for first hands (*) and main texts (T), although you may also wish to use it to combine multiple attestations (often signified by /1, /2 in lectionaries) in the same witness. If more than one suffix is used, this argument can be specified multiple times.")
    parser.add_argument("--fill-correctors", action="store_true", help="Fill in missing readings in witnesses with type \"corrector\" using the witnesses they follow in the TEI XML witness list.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging (mostly for debugging purposes).")
    parser.add_argument("input", type=str, help="TEI XML collation file to convert.")
    parser.add_argument("output", metavar="output", type=str, help="Filename for the output (the format will be detected based on the file type).")
    args = parser.parse_args()
    # Parse the optional arguments:
    manuscript_suffixes = [] if args.s is None else args.s
    trivial_reading_types = [] if args.t is None else args.t
    missing_reading_types = [] if args.m is None else args.m
    fill_corrector_lacunae = args.fill_correctors
    verbose = args.verbose
    # Parse the positional arguments:
    input_addr = args.input
    output_addr = args.output
    # Make sure the input is an XML file:
    if not input_addr.endswith(".xml"):
        print("Error opening input file: The input file is not an XML file. Make sure the input file type is of type .xml.")
        exit(1)
    # If it is, then try to parse it:
    xml = None
    try:
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_addr, parser=parser)
    except Exception as e:
        print("Error opening input file: %s" % e)
        exit(1)
    # Make sure the output is a valid file type:
    if not output_addr.endswith(".nex") and not output_addr.endswith(".nxs"):
        print("Error opening output file: Currently, the only supported output format is NEXUS (.nex, .nxs). Make sure the output file is of this type.")
        exit(1)
    # Initialize the internal representation of the collation:
    coll = Collation(xml, manuscript_suffixes, trivial_reading_types, missing_reading_types, fill_corrector_lacunae, verbose)
    if output_addr.endswith(".nex") or output_addr.endswith(".nxs"):
        coll.to_nexus(output_addr)
    exit(0)

if __name__=="__main__":
    main()