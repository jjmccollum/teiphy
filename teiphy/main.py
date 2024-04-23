from typing import List  # for list-like inputs
from importlib.metadata import version  # for checking package version
from pathlib import Path  # for validating file address inputs
from lxml import etree as et  # for parsing XML input
import typer

from .format import Format
from .collation import Collation, ClockModel, AncestralLogger, TableType


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
    proportion: bool = typer.Option(
        False,
        help="If set, populate the output distance matrix's cells with proportions of disagreements over variation units where both witnesses are extant; this option is only used if --table distance is specified.",
    ),
    calibrate_dates: bool = typer.Option(
        False,
        help="Add an Assumptions block containing age distributions for witnesses to NEXUS output; this option is intended for NEXUS inputs to BEAST 2.",
    ),
    mrbayes: bool = typer.Option(
        False,
        help="Add a MrBayes block containing model settings and age calibrations for witnesses to NEXUS output; this option is intended for inputs to MrBayes.",
    ),
    clock: ClockModel = typer.Option(
        ClockModel.strict,
        help="The clock model to use; this option is intended for inputs to MrBayes and BEAST 2. MrBayes does not presently support a local clock model, so it will default to a strict clock model if a local clock model is specified.",
    ),
    ancestral_logger: AncestralLogger = typer.Option(
        AncestralLogger.state,
        help="The type of logger to use for ancestral state reconstruction data; this option is intended for inputs to BEAST 2. If \"state\", then only the reconstructed states at the root of each sampled tree will be logged. If \"sequence\", then each sampled tree's reconstructed states for all ancestors will be logged (WARNING: this will be memory-intensive!). If \"none\", then no ancestral states will be logged.",
    ),
    table: TableType = typer.Option(
        TableType.matrix,
        help="The type of table to use for CSV/Excel output. If \"matrix\", then the table will have rows for witnesses and columns for all variant readings, with frequency values in cells (the --split-missing flag can be used with this option). If \"distance\", then the table will have rows and columns for witnesses, with the number or proportion of disagreements between each pair in the corresponding cell (the --proportion flag can be used with this option). If \"nexus\", then the table will have rows for witnesses and columns for variation units with reading IDs in cells (the --ambiguous-as-missing flag can be used with this option). If \"long\", then the table will consist of repeated rows with column entries for taxa, characters, reading indices, and reading texts.",
    ),
    split_missing: bool = typer.Option(
        False,
        help="Treat missing characters/variation units as having a contribution of 1 split over all states/readings; if False, then missing data is ignored (i.e., all states are 0). Not applicable for non-tabular formats.",
    ),
    seed: int = typer.Option(
        None,
        help="Seed for random number generation (used for setting default initial values of transcriptional rate parameters for BEAST 2 XML output); if not specified, then the default seeding of the numpy.random.default_rng class will be used.",
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
        proportion=proportion,
        calibrate_dates=calibrate_dates,
        mrbayes=mrbayes,
        clock_model=clock,
        ancestral_logger=ancestral_logger,
        table_type=table,
        split_missing=split_missing,
        seed=seed,
    )
