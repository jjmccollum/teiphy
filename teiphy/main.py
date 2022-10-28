from typing import List  # for list-like inputs
from importlib.metadata import version # for checking package version
from pathlib import Path  # for validating file address inputs
from lxml import etree as et  # for parsing XML input
import typer

from .format import Format
from .collation import Collation


app = typer.Typer(rich_markup_mode="rich")

def version_callback(value: bool):
    if value:
        teiphy_version = version("teiphy")
        typer.echo(teiphy_version)
        raise typer.Exit()

@app.command()
def to_file(
    trivial_reading_types: List[str] = typer.Option(
        [],
        "-t",
        help="Reading types to treat as trivial and collapse with the previous substantive reading (e.g., reconstructed, defective, orthographic, subreading). If more than one type is applicable, this argument can be specified multiple times.",
    ),
    missing_reading_types: List[str] = typer.Option(
        [],
        "-m",
        help="Reading types to treat as missing data (e.g., lac, overlap). If more than one type is applicable, this argument can be specified multiple times.",
    ),
    suffixes: List[str] = typer.Option(
        [],
        "-s",
        help="Suffixes to ignore for manuscript witness sigla. Typically, these will be things like the sigla for first hands (*) and main texts (T), although you may also wish to use it to combine multiple attestations (often signified by /1, /2 in lectionaries) in the same witness. If more than one suffix is used, this argument can be specified multiple times.",
    ),
    fill_correctors: bool = typer.Option(
        False,
        help="Fill in missing readings in witnesses with type \"corrector\" using the witnesses they follow in the TEI XML witness list.",
    ),
    labels: bool = typer.Option(
        True,
        help="Print the CharStateLabels block (containing variation unit labels and reading texts converted to ASCII) in NEXUS output.",
    ),
    states_present: bool = typer.Option(
        False,
        help="Use the StatesFormat=StatesPresent setting instead of the StatesFormat=Frequency setting (and thus represent all states with single symbols rather than frequency vectors) in NEXUS output.",
    ),
    ambiguous_as_missing: bool = typer.Option(
        False,
        help="Use the missing symbol instead of Equate symbols (and thus treat all ambiguities as missing data) in NEXUS output; this option is only applied if the --states-present option is also set.",
    ),
    verbose: bool = typer.Option(False, help="Enable verbose logging (mostly for debugging purposes)."),
    version: bool = typer.Option(
        False,
        callback=version_callback,
        is_eager=True,
        help="Print the current version.",
    ),
    format: Format = typer.Option(None, case_sensitive=False, help="The output format."),
    input: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        writable=False,
        readable=True,
        resolve_path=True,
        help="Input TEI XML collation file to convert.",
    ),
    output: Path = typer.Argument(
        ...,
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        readable=False,
        resolve_path=True,
        help="Output for converted collation. If --format is not specified, then the format will be derived from the extension of this file.",
    ),
):
    # Make sure the input is an XML file:
    if input.suffix.lower() != ".xml":
        print("Error opening input file: The input file is not an XML file. Make sure the input file type is .xml.")
    # If it is, then try to parse it:
    xml = None
    try:
        parser = et.XMLParser(remove_comments=True)
        xml = et.parse(input, parser=parser)
    except Exception as err:
        print(f"Error opening input file: {err}")

    coll = Collation(xml, suffixes, trivial_reading_types, missing_reading_types, fill_correctors, verbose)
    coll.to_file(
        output,
        format=format,
        char_state_labels=labels,
        states_present=states_present,
        ambiguous_as_missing=ambiguous_as_missing,
    )
