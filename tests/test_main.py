from pathlib import Path
import tempfile
from typer.testing import CliRunner
from lxml import etree as et

from teiphy.main import app
from teiphy.collation import ParsingException
from teiphy.common import tei_ns

runner = CliRunner()

test_dir = Path(__file__).parent
root_dir = test_dir.parent

input_example = root_dir / "example/ubs_ephesians.xml"
non_xml_example = root_dir / "pyproject.toml"
malformed_example = test_dir / "malformed_example.xml"
no_listwit_example = test_dir / "no_listwit_example.xml"
extra_sigla_example = test_dir / "extra_sigla_example.xml"
no_dates_example = test_dir / "no_dates_example.xml"
some_dates_example = test_dir / "some_dates_example.xml"


def test_version():
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(app, ["--version"])
        assert result.stdout != ""


def test_non_xml_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(non_xml_example), str(output)])
        assert result.stdout.startswith(
            "Error opening input file: The input file is not an XML file. Make sure the input file type is .xml."
        )


def test_malformed_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(malformed_example), str(output)])
        assert result.stdout.startswith("Error opening input file:")


def test_no_listwit_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(no_listwit_example), str(output)])
        assert isinstance(result.exception, ParsingException)
        assert "An explicit listWit element must be included in the TEI XML collation." in str(result.exception)


def test_extra_sigla_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(extra_sigla_example), str(output)])
        assert "WARNING" in result.stdout
        assert "TheodoreOfMopsuestia" in result.stdout


def test_to_nexus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "22 B10K4V28U24_26" in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_drop_constant():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--drop-constant", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "22 B10K4V28U24_26" not in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_no_labels():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--no-labels", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" not in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_frequency():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--frequency", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "22 B10K4V28U24_26" in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_drop_constant_frequency():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--drop-constant", "--frequency", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "22 B10K4V28U24_26" not in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_ambiguous_as_missing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--ambiguous-as-missing", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "StatesFormat=Frequency" not in text
        assert "{" not in text


def test_to_nexus_calibrate_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--calibrate-dates", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert "CALIBRATE UBS = fixed(50)" in text
        assert "CALIBRATE P46 = uniform(175,225)" in text


def test_to_nexus_calibrate_dates_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--calibrate-dates", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" not in text


def test_to_nexus_calibrate_dates_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--calibrate-dates", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert "CALIBRATE UBS = fixed(50)" in text  # both ends of date range specified and identical
        assert "CALIBRATE P46 = uniform(50,600)" in text  # neither end of date range specified
        assert "CALIBRATE 01 = uniform(300,600)" in text  # lower bound but no upper bound
        assert "CALIBRATE 02 = uniform(50,500)" in text  # upper bound but no lower bound
        assert "CALIBRATE 06 = uniform(500,600)" in text  # both ends of date range specified and distinct


def test_to_nexus_mrbayes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--mrbayes", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "calibrate UBS = fixed(1450);" in text
        assert "calibrate P46 = uniform(1275,1325);" in text


def test_to_nexus_mrbayes_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--mrbayes", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text  # the MRBAYES block is still included, but no calibrations are
        assert "calibrate" not in text


def test_to_nexus_mrbayes_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--mrbayes", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "calibrate UBS = fixed(550)" in text  # both ends of date range specified and identical
        assert "calibrate P46 = uniform(0,550)" in text  # neither end of date range specified
        assert "calibrate 01 = uniform(0,300)" in text  # lower bound but no upper bound
        assert "calibrate 02 = uniform(100,550)" in text  # upper bound but no lower bound
        assert "calibrate 06 = uniform(0,100)" in text  # both ends of date range specified and distinct


def test_to_hennig86():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("nstates")
        assert "xread" in text
        assert "%d %d" % (len(xml_variation_units), len(xml_witnesses)) in text


def test_to_hennig86_drop_constant():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                "--drop-constant",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("nstates")
        assert "xread" in text
        assert "%d %d" % (len(xml_variation_units) - 2, len(xml_witnesses)) in text


def test_to_phylip():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="ascii")
        assert text.startswith("%d %d" % (len(xml_witnesses), len(xml_variation_units)))


def test_to_phylip_drop_constant():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                "--drop-constant",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="ascii")
        assert text.startswith("%d %d" % (len(xml_witnesses), len(xml_variation_units) - 2))


def test_to_fasta():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.fa"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="ascii")
        assert text.startswith(">UBS")
        assert "0" * len(xml_variation_units) in text


def test_to_fasta_drop_constant():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.fa"
        result = runner.invoke(
            app,
            [
                "-t reconstructed",
                "-t defective",
                "-t orthographic",
                "-m lac",
                "-m overlap",
                "-s *",
                "-s T",
                "--fill-correctors",
                "--drop-constant",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="ascii")
        assert text.startswith(">UBS")
        assert "0" * (len(xml_variation_units) - 2) in text


def test_to_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith(",UBS,P46,01,02,03,04,06")
        assert "B10K4V28U24-26," in text


def test_to_csv_drop_constant():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--drop-constant", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith(",UBS,P46,01,02,03,04,06")
        assert "B10K4V28U24-26," not in text


def test_to_csv_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--long-table", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("taxon,character,state,value")
        assert "B10K4V28U24-26," in text


def test_to_csv_drop_constant_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--drop-constant", "--long-table", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("taxon,character,state,value")
        assert "B10K4V28U24-26," not in text


def test_to_tsv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("\tUBS\tP46\t01\t02\t03\t04\t06")


def test_to_tsv_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, ["--long-table", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("taxon\tcharacter\tstate\tvalue")


def test_to_excel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()


def test_to_excel_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, ["--long-table", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()


def test_to_stemma():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--format", "stemma", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert chron_output.exists()
        chron_text = chron_output.read_text(encoding="utf-8")
        assert chron_text.startswith("UBS")
        assert "50    50    50" in chron_text


def test_to_stemma_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--format", "stemma", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert not chron_output.exists()


def test_to_stemma_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--format", "stemma", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert chron_output.exists()
        chron_text = chron_output.read_text(encoding="utf-8")
        assert chron_text.startswith("UBS")
        assert (
            chron_text.count("50   50   50") == 1
        )  # space between columns should be reduced because all dates are now at most 3 digits long
        assert chron_text.count("300  450  600") == 1  # for the one witness with a lower bound and no upper bound
        assert chron_text.count("50  275  500") == 1  # for the one witness with an upper bound and no lower bound
        assert (
            chron_text.count("50  325  600") > 1
        )  # for the remaining witnesses whose bounds are set to the minimum and maximum


def test_to_file_bad_format():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.unk"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert isinstance(result.exception, Exception)
