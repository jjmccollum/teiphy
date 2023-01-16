from typing import List  # for list-like inputs
from importlib.metadata import version  # for checking package version
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
    frequency: bool = typer.Option(
        False,
        help="Use the StatesFormat=Frequency setting instead of the StatesFormat=StatesPresent setting (and thus represent all states with frequency vectors rather than symbols) in NEXUS output.",
    ),
    drop_constant: bool = typer.Option(
        False,
        help="If set, do not write constant sites (i.e., variation units with one substantive reading) to output.",
    ),
    ambiguous_as_missing: bool = typer.Option(
        False,
        help="Use the missing symbol instead of multistate symbols (and thus treat all ambiguities as missing data) in NEXUS output; this option is only applied if the --frequency option is not set.",
    ),
    calibrate_dates: bool = typer.Option(
        False,
        help="Add an Assumptions block containing date distributions for witnesses to NEXUS output; this option is intended for inputs to BEAST2.",
    ),
    mrbayes: bool = typer.Option(
        False,
        help="Add a MrBayes block containing model settings and age calibrations for witnesses to NEXUS output; this option is intended for inputs to MrBayes.",
    ),
    long_table: bool = typer.Option(
        False,
        help="Generate a long table with columns for taxa, characters, reading indices, and reading values instead of a matrix. Not applicable for non-tabular formats. Note that if this option is set, ambiguous readings will be treated as missing data, and the --split-missing option will be ignored.",
    ),
    split_missing: bool = typer.Option(
        False,
        help="Treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Not applicable for non-tabular formats.",
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
        drop_constant=drop_constant,
        char_state_labels=labels,
        frequency=frequency,
        ambiguous_as_missing=ambiguous_as_missing,
        calibrate_dates=calibrate_dates,
        mrbayes=mrbayes,
        long_table=long_table,
        split_missing=split_missing,
    )
