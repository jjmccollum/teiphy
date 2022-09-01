from typing import List # for list-like inputs
from pathlib import Path # for validating file address inputs
from lxml import etree as et # for parsing XML input
import typer

from teiphy import Collation

app = typer.Typer()

@app.command()
def to_nexus(
    trivial_reading_types: List[str] = typer.Option(
        [], 
        "-t",
        help="Reading types to treat as trivial and collapse with the previous substantive reading (e.g., reconstructed, defective, orthographic, subreading). If more than one type is applicable, this argument can be specified multiple times."
    ),
    missing_reading_types: List[str] = typer.Option(
        [],
        "-m",
        help="Reading types to treat as missing data (e.g., lac, overlap). If more than one type is applicable, this argument can be specified multiple times."
    ),
    suffixes: List[str] = typer.Option(
        [],
        "-s",
        help="Suffixes to ignore for manuscript witness sigla. Typically, these will be things like the sigla for first hands (*) and main texts (T), although you may also wish to use it to combine multiple attestations (often signified by /1, /2 in lectionaries) in the same witness. If more than one suffix is used, this argument can be specified multiple times."
    ),
    fill_correctors: bool = typer.Option(
        False, 
        help="Fill in missing readings in witnesses with type \"corrector\" using the witnesses they follow in the TEI XML witness list."
    ),
    verbose: bool = typer.Option(
        False, 
        help="Enable verbose logging (mostly for debugging purposes)."
    ),
    input_addr: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ), output_addr: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
    )):
    # Make sure the input is an XML file:
    if input_addr.suffix != ".xml":
        print("Error opening input file: The input file is not an XML file. Make sure the input file type is .xml.")
    # If it is, then try to parse it:
    xml = None
    try:
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_addr, parser=parser)
    except Exception as e:
        print("Error opening input file: %s" % e)
    # Make sure the output is a valid file type:
    if output_addr.suffix != ".nex" and output_addr.suffix != ".nxs":
        print("Error opening output file: The output file is not a NEXUS file. Make sure the output file type is .nex or .nxs.")
    # Initialize the internal representation of the collation:
    coll = Collation(xml, suffixes, trivial_reading_types, missing_reading_types, fill_correctors, verbose)
    coll.to_nexus(output_addr)

@app.command()
def to_csv(
    trivial_reading_types: List[str] = typer.Option(
        [], 
        "-t",
        help="Reading types to treat as trivial and collapse with the previous substantive reading (e.g., reconstructed, defective, orthographic, subreading). If more than one type is applicable, this argument can be specified multiple times."
    ),
    missing_reading_types: List[str] = typer.Option(
        [],
        "-m",
        help="Reading types to treat as missing data (e.g., lac, overlap). If more than one type is applicable, this argument can be specified multiple times."
    ),
    suffixes: List[str] = typer.Option(
        [],
        "-s",
        help="Suffixes to ignore for manuscript witness sigla. Typically, these will be things like the sigla for first hands (*) and main texts (T), although you may also wish to use it to combine multiple attestations (often signified by /1, /2 in lectionaries) in the same witness. If more than one suffix is used, this argument can be specified multiple times."
    ),
    fill_correctors: bool = typer.Option(
        False, 
        help="Fill in missing readings in witnesses with type \"corrector\" using the witnesses they follow in the TEI XML witness list."
    ),
    split_missing: bool = typer.Option(
        False,
        help="Treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0)."
    ),
    verbose: bool = typer.Option(
        False, 
        help="Enable verbose logging (mostly for debugging purposes)."
    ),
    input_addr: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ), output_addr: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
    )):
    # Make sure the input is an XML file:
    if input_addr.suffix != ".xml":
        print("Error opening input file: The input file is not an XML file. Make sure the input file type is .xml.")
    # If it is, then try to parse it:
    xml = None
    try:
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_addr, parser=parser)
    except Exception as e:
        print("Error opening input file: %s" % e)
    # Make sure the output is a valid file type:
    if output_addr.suffix != ".csv":
        print("Error opening output file: The output file is not a CSV file. Make sure the output file type is .csv.")
    # Initialize the internal representation of the collation:
    coll = Collation(xml, suffixes, trivial_reading_types, missing_reading_types, fill_correctors, verbose)
    coll.to_csv(output_addr, split_missing)

@app.command()
def to_excel(
    trivial_reading_types: List[str] = typer.Option(
        [], 
        "-t",
        help="Reading types to treat as trivial and collapse with the previous substantive reading (e.g., reconstructed, defective, orthographic, subreading). If more than one type is applicable, this argument can be specified multiple times."
    ),
    missing_reading_types: List[str] = typer.Option(
        [],
        "-m",
        help="Reading types to treat as missing data (e.g., lac, overlap). If more than one type is applicable, this argument can be specified multiple times."
    ),
    suffixes: List[str] = typer.Option(
        [],
        "-s",
        help="Suffixes to ignore for manuscript witness sigla. Typically, these will be things like the sigla for first hands (*) and main texts (T), although you may also wish to use it to combine multiple attestations (often signified by /1, /2 in lectionaries) in the same witness. If more than one suffix is used, this argument can be specified multiple times."
    ),
    fill_correctors: bool = typer.Option(
        False, 
        help="Fill in missing readings in witnesses with type \"corrector\" using the witnesses they follow in the TEI XML witness list."
    ),
    split_missing: bool = typer.Option(
        False,
        help="Treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0)."
    ),
    verbose: bool = typer.Option(
        False, 
        help="Enable verbose logging (mostly for debugging purposes)."
    ),
    input_addr: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
    ), output_addr: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
    )):
    # Make sure the input is an XML file:
    if input_addr.suffix != ".xml":
        print("Error opening input file: The input file is not an XML file. Make sure the input file type is .xml.")
    # If it is, then try to parse it:
    xml = None
    try:
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input_addr, parser=parser)
    except Exception as e:
        print("Error opening input file: %s" % e)
    # Make sure the output is a valid file type:
    if output_addr.suffix != ".xlsx":
        print("Error opening output file: The output file is not an Excel file, or it is an Excel file whose file type (.xls) is no longer supported. Make sure the output file type is .xlsx.")
    # Initialize the internal representation of the collation:
    coll = Collation(xml, suffixes, trivial_reading_types, missing_reading_types, fill_correctors, verbose)
    coll.to_excel(output_addr, split_missing)

if __name__ == "__main__":
    app()