from pathlib import Path
from datetime import datetime
import tempfile
from typer.testing import CliRunner
from lxml import etree as et

from teiphy.main import app
from teiphy.collation import ParsingException, WitnessDateException, IntrinsicRelationsException
from teiphy.common import tei_ns, xml_ns

runner = CliRunner()

test_dir = Path(__file__).parent
root_dir = test_dir.parent

input_example = root_dir / "example/ubs_ephesians.xml"
non_xml_example = root_dir / "pyproject.toml"
malformed_example = test_dir / "malformed_example.xml"
no_listwit_example = test_dir / "no_listwit_example.xml"
extra_sigla_example = test_dir / "extra_sigla_example.xml"
no_dates_example = test_dir / "no_dates_example.xml"
no_origin_example = test_dir / "no_origin_example.xml"
no_origin_some_dates_example = test_dir / "no_origin_some_dates_example.xml"
some_origin_some_dates_example = test_dir / "some_origin_some_dates_example.xml"
some_dates_example = test_dir / "some_dates_example.xml"
fixed_rates_example = test_dir / "fixed_rates_example.xml"
bad_date_witness_example = test_dir / "bad_date_witness_example.xml"
intrinsic_odds_excess_indegree_example = test_dir / "intrinsic_odds_excess_indegree_example.xml"
intrinsic_odds_cycle_example = test_dir / "intrinsic_odds_cycle_example.xml"
intrinsic_odds_no_relations_example = test_dir / "intrinsic_odds_no_relations_example.xml"
some_dates_csv_file = test_dir / "some_dates.csv"
bad_dates_csv_file = test_dir / "bad_dates.csv"
non_csv_dates_file = test_dir / "non_csv_dates.txt"


def test_version():
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(app, ["--verbose", "--version"])
        assert result.stdout != ""


def test_non_xml_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(non_xml_example), str(output)])
        assert result.stdout.startswith(
            "Error opening input file: The input file is not an XML file. Make sure the input file type is .xml."
        )


def test_malformed_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(malformed_example), str(output)])
        assert result.stdout.startswith("Error opening input file:")


def test_no_listwit_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(no_listwit_example), str(output)])
        assert isinstance(result.exception, ParsingException)
        assert "An explicit listWit element must be included in the TEI XML collation." in str(result.exception)


def test_extra_sigla_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(extra_sigla_example), str(output)])
        assert "WARNING" in result.stdout
        assert "TheodoreOfMopsuestia" in result.stdout


def test_bad_date_witness_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(bad_date_witness_example), str(output)])
        assert isinstance(result.exception, WitnessDateException)
        assert "The following witnesses have their latest possible dates before the earliest date of origin" in str(
            result.exception
        )


def test_dates_file_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "--calibrate-dates",
                "--dates-file",
                str(some_dates_csv_file),
                str(input_example),
                str(output),
            ],
        )
        text = output.read_text(encoding="utf-8")
        assert "Begin ASSUMPTIONS;" in text
        assert (
            "CALIBRATE UBS = fixed(%d)" % (datetime.now().year - 80) in text
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the origin
        assert (
            "CALIBRATE P46 = uniform(%d,%d)" % (0, datetime.now().year - 80) in text
        )  # neither bound specified, but both inferred
        assert (
            "CALIBRATE 01 = uniform(%d,%d)" % (0, datetime.now().year - 300) in text
        )  # lower bound specified, upper bound inferred
        assert (
            "CALIBRATE 02 = uniform(%d,%d)" % (datetime.now().year - 500, datetime.now().year - 80) in text
        )  # upper bound specified, lower bound inferred
        assert (
            "CALIBRATE 06 = uniform(%d,%d)" % (datetime.now().year - 600, datetime.now().year - 500) in text
        )  # both bounds specified and distinct


def test_bad_dates_file_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "--calibrate-dates",
                "--dates-file",
                str(bad_dates_csv_file),
                str(input_example),
                str(output),
            ],
        )
        assert isinstance(result.exception, ParsingException)
        assert "In dates file" in str(result.exception)


def test_non_csv_dates_file_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "--calibrate-dates",
                "--dates-file",
                str(non_csv_dates_file),
                str(input_example),
                str(output),
            ],
        )
        assert result.stdout.startswith(
            "Error opening dates file: The dates file is not a CSV file. Make sure the dates file type is .csv."
        )


def test_to_nexus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "\t35 B10K6V20U12" in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_drop_constant():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--drop-constant", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "\t35 B10K6V20U12" not in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_no_labels():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--no-labels", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" not in text
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_frequency():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--frequency", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "\t35 B10K6V20U12" in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_drop_constant_frequency():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--drop-constant", "--frequency", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "\t35 B10K6V20U12" not in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_ambiguous_as_missing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--ambiguous-as-missing", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "StatesFormat=Frequency" not in text
        assert "{" not in text


def test_to_nexus_fragmentary_threshold():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fragmentary-threshold",
                0.5,
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "04                   " not in text
        assert "06C2                 " not in text


def test_to_nexus_fragmentary_threshold_fill_correctors():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--fragmentary-threshold",
                0.5,
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "04                   " not in text
        assert "06C2                 " in text


def test_to_nexus_fragmentary_threshold_bad_threshold():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fragmentary-threshold",
                1.1,
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 1
        assert result.stdout.startswith("Error: the fragmentary variation unit proportion threshold is")


def test_to_nexus_calibrate_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--calibrate-dates", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert "CALIBRATE 81 = fixed(%d)" % (datetime.now().year - 1044) in text
        assert "CALIBRATE P46 = uniform(%d,%d)" % (datetime.now().year - 399, datetime.now().year - 200) in text


def test_to_nexus_calibrate_dates_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--calibrate-dates", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert "CALIBRATE UBS = offsetlognormal(0,0.0,1.0)" in text


def test_to_nexus_calibrate_dates_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--calibrate-dates", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert (
            "CALIBRATE UBS = fixed(%d)" % (datetime.now().year - 80) in text
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the origin
        assert (
            "CALIBRATE P46 = uniform(%d,%d)" % (0, datetime.now().year - 80) in text
        )  # neither bound specified, but both inferred
        assert (
            "CALIBRATE 01 = uniform(%d,%d)" % (0, datetime.now().year - 300) in text
        )  # lower bound specified, upper bound inferred
        assert (
            "CALIBRATE 02 = uniform(%d,%d)" % (datetime.now().year - 500, datetime.now().year - 80) in text
        )  # upper bound specified, lower bound inferred
        assert (
            "CALIBRATE 06 = uniform(%d,%d)" % (datetime.now().year - 600, datetime.now().year - 500) in text
        )  # both bounds specified and distinct


def test_to_nexus_mrbayes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--mrbayes", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset treeagepr = uniform(%d,%d)" % (datetime.now().year - 80, datetime.now().year - 50) in text
        assert "calibrate 81 = fixed(%d);" % (datetime.now().year - 1044) in text
        assert "calibrate P46 = uniform(%d,%d);" % (datetime.now().year - 399, datetime.now().year - 200) in text


def test_to_nexus_mrbayes_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--mrbayes", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset treeagepr = offsetgamma(0,1.0,1.0)" in text
        assert "calibrate 18 = offsetgamma(0,1.0,1.0);" in text


def test_to_nexus_mrbayes_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--verbose", "--mrbayes", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset treeagepr = offsetgamma(%d,1.0,1.0);" % (datetime.now().year - 80) in text
        assert (
            "calibrate UBS = fixed(%d);" % (datetime.now().year - 80) in text
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the origin
        assert (
            "calibrate P46 = uniform(%d,%d)" % (0, datetime.now().year - 80) in text
        )  # neither bound specified, but both inferred
        assert (
            "calibrate 01 = uniform(%d,%d);" % (0, datetime.now().year - 300) in text
        )  # lower bound specified, upper bound inferred
        assert (
            "calibrate 02 = uniform(%d,%d);" % (datetime.now().year - 500, datetime.now().year - 80) in text
        )  # upper bound specified, lower bound inferred
        assert (
            "calibrate 06 = uniform(%d,%d);" % (datetime.now().year - 600, datetime.now().year - 500) in text
        )  # both bounds specified and distinct


def test_to_nexus_mrbayes_strict_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--mrbayes",
                "--clock",
                "strict",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset clockvarpr=strict;" in text


def test_to_nexus_mrbayes_uncorrelated_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--mrbayes",
                "--clock",
                "uncorrelated",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset clockvarpr=igr;" in text


def test_to_nexus_mrbayes_local_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--mrbayes",
                "--clock",
                "local",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert (
            "prset clockvarpr=strict;" in text
        )  # MrBayes does not presently support local clock models, so we default to strict models


def test_to_hennig86():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
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
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
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
        assert "%d %d" % (len(xml_variation_units) - 1, len(xml_witnesses)) in text


def test_to_phylip():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
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
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--drop-constant",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="ascii")
        assert text.startswith("%d %d" % (len(xml_witnesses), len(xml_variation_units) - 1))


def test_to_fasta():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.fa"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
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
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.fa"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
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


def test_to_beast():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        beast_xml_sequences = beast_xml.xpath(".//sequence")
        beast_xml_charstatelabels = beast_xml.xpath(".//charstatelabels")
        beast_xml_site_distributions = beast_xml.xpath(".//distribution[@spec=\"TreeLikelihood\"]")
        assert len(beast_xml_sequences) == len(xml_witnesses)
        assert len(beast_xml_charstatelabels) == len(xml_variation_units)
        assert len(beast_xml_site_distributions) == len(xml_variation_units)
        beast_xml_singleton_sequences = beast_xml.xpath(".//charstatelabels[@characterName=\"B10K6V20U12\"]")
        assert len(beast_xml_singleton_sequences) == 1
        assert beast_xml_singleton_sequences[0].get("value") is not None
        assert "DUMMY" in beast_xml_singleton_sequences[0].get("value")
        assert "WARNING: the latest witness" in result.stdout


def test_to_beast_drop_constant():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath(".//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--drop-constant",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        beast_xml_sequences = beast_xml.xpath(".//sequence")
        beast_xml_charstatelabels = beast_xml.xpath(".//charstatelabels")
        beast_xml_site_distributions = beast_xml.xpath(".//distribution[@spec=\"TreeLikelihood\"]")
        assert len(beast_xml_sequences) == len(xml_witnesses)
        assert len(beast_xml_charstatelabels) == len(xml_variation_units) - 2
        assert len(beast_xml_site_distributions) == len(xml_variation_units) - 2
        beast_xml_singleton_sequences = beast_xml.xpath(".//charstatelabels[@characterName=\"B10K6V20U12\"]")
        assert len(beast_xml_singleton_sequences) == 0


def test_to_beast_no_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(no_dates_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        beast_xml_traits = beast_xml.xpath(".//trait[@traitname=\"date\"]")
        assert len(beast_xml_traits) == 1
        assert beast_xml_traits[0].get("value") is not None
        assert beast_xml_traits[0].get("value") == ""
        assert len(beast_xml.xpath(".//origin")) == 1
        beast_xml_origin = beast_xml.find(".//origin")
        assert float(beast_xml_origin.get("value")) == 0.0  # the minimum height of the tree
        assert float(beast_xml_origin.get("lower")) == 0.0  # the minimum height of the tree
        assert beast_xml_origin.get("upper") == "Infinity"


def test_to_beast_some_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(some_dates_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        beast_xml_traits = beast_xml.xpath(".//trait[@traitname=\"date\"]")
        assert len(beast_xml_traits) == 1
        assert beast_xml_traits[0].get("value") is not None
        assert "UBS=80" in beast_xml_traits[0].get(
            "value"
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the origin
        assert "01=%d" % int((datetime.now().year + 300) / 2) in beast_xml_traits[0].get(
            "value"
        )  # 01 does not have an explicit upper bound on its date, so its upper bound should be fixed to
        assert "02=290" in beast_xml_traits[0].get(
            "value"
        )  # 02 has an explicit upper bound of 500, and its lower bound should be set to 80 based on the origin date
        assert "06=550"  # 06 has the lower and upper bounds on its date explicitly specified
        assert len(beast_xml.xpath(".//origin")) == 1
        beast_xml_origin = beast_xml.find(".//origin")
        assert float(beast_xml_origin.get("value")) == datetime.now().year - 80  # minimum height of the tree
        assert float(beast_xml_origin.get("lower")) == datetime.now().year - 80  # minimum height of the tree
        assert beast_xml_origin.get("upper") == "Infinity"


def test_to_beast_no_origin():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(no_origin_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert len(beast_xml.xpath(".//origin")) == 1
        beast_xml_origin = beast_xml.find(".//origin")
        assert (
            float(beast_xml_origin.get("value")) == 1450.0
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert (
            float(beast_xml_origin.get("lower")) == 1450.0
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert beast_xml_origin.get("upper") == "Infinity"


def test_to_beast_no_origin_some_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(no_origin_some_dates_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert len(beast_xml.xpath(".//origin")) == 1
        beast_xml_origin = beast_xml.find(".//origin")
        assert (
            float(beast_xml_origin.get("value")) == datetime.now().year - 50
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert (
            float(beast_xml_origin.get("lower")) == datetime.now().year - 50
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert beast_xml_origin.get("upper") == "Infinity"


def test_to_beast_some_origin_some_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(some_origin_some_dates_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert len(beast_xml.xpath(".//origin")) == 1
        beast_xml_origin = beast_xml.find(".//origin")
        assert (
            float(beast_xml_origin.get("value")) == 1420.0
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert (
            float(beast_xml_origin.get("lower")) == 1420.0
        )  # this should equal the difference between the earliest possible tip date and the latest possible tip date
        assert (
            float(beast_xml_origin.get("upper")) == 1450.0
        )  # this should equal the difference between the earliest possible origin date and the latest possible tip date


def test_to_beast_variable_rates():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_transcriptional_categories = xml.xpath(
        ".//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--seed",
                "1337",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        expected_rates = [
            9.499649179019467,
            8.750762619939191,
            25.00430409157674,
            19.873724085272503,
            9.988999535304949,
            21.828078913817116,
        ]  # Gamma(5,2)-distributed numbers generated with seed 1337
        for i, xml_transcriptional_category in enumerate(xml_transcriptional_categories):
            transcriptional_category = xml_transcriptional_category.get("{%s}id" % xml_ns)
            beast_xml_transcriptional_rate_categories = beast_xml.xpath(
                ".//stateNode[@id=\"%s_rate\"]" % transcriptional_category
            )
            assert len(beast_xml_transcriptional_rate_categories) == 1
            assert float(beast_xml_transcriptional_rate_categories[0].get("value")) == expected_rates[i]
            assert beast_xml_transcriptional_rate_categories[0].get("estimate") == "true"


def test_to_beast_fixed_rates():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(fixed_rates_example, parser=parser)
    xml_transcriptional_categories = xml.xpath(
        ".//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(fixed_rates_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        for xml_transcriptional_category in xml_transcriptional_categories:
            transcriptional_category = xml_transcriptional_category.get("{%s}id" % xml_ns)
            transcriptional_rate = float(
                xml_transcriptional_category.xpath("./tei:certainty", namespaces={"tei": tei_ns})[0].get("degree")
            )
            beast_xml_transcriptional_rate_categories = beast_xml.xpath(
                ".//stateNode[@id=\"%s_rate\"]" % transcriptional_category
            )
            assert len(beast_xml_transcriptional_rate_categories) == 1
            assert float(beast_xml_transcriptional_rate_categories[0].get("value")) == transcriptional_rate
            assert beast_xml_transcriptional_rate_categories[0].get("estimate") == "false"


def test_to_beast_intrinsic_odds_excess_indegree():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(intrinsic_odds_excess_indegree_example, parser=parser)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(intrinsic_odds_excess_indegree_example),
                str(output),
            ],
        )
        assert isinstance(result.exception, IntrinsicRelationsException)
        assert "the following readings have more than one intrinsic relation pointing to them" in str(result.exception)


def test_to_beast_intrinsic_odds_cycle():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(intrinsic_odds_cycle_example, parser=parser)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(intrinsic_odds_cycle_example),
                str(output),
            ],
        )
        assert isinstance(result.exception, IntrinsicRelationsException)
        assert "the intrinsic relations contain a cycle" in str(result.exception)


def test_to_beast_intrinsic_odds_no_relations():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                str(intrinsic_odds_no_relations_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        root_frequencies_xml = beast_xml.find(".//rootFrequencies/frequencies")
        assert root_frequencies_xml.get("value") is not None
        assert root_frequencies_xml.get("value") == "0.25 0.25 0.25 0.25"


def test_to_beast_strict_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--clock",
                "strict",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//branchRateModel") is not None
        branch_rate_model = beast_xml.find(".//branchRateModel")
        assert branch_rate_model.get("spec") == "StrictClockModel"


def test_to_beast_uncorrelated_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--clock",
                "uncorrelated",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//branchRateModel") is not None
        branch_rate_model = beast_xml.find(".//branchRateModel")
        assert branch_rate_model.get("spec") == "UCRelaxedClockModel"


def test_to_beast_local_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--clock",
                "local",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//branchRateModel") is not None
        branch_rate_model = beast_xml.find(".//branchRateModel")
        assert branch_rate_model.get("spec") == "RandomLocalClockModel"


def test_to_beast_state_ancestral_logger():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--ancestral-logger",
                "state",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//logger[@id=\"ancestralStateLogger\"]") is not None
        ancestral_log = beast_xml.find(".//logger[@id=\"ancestralStateLogger\"]/log")
        assert ancestral_log.get("spec") == "beastlabs.evolution.likelihood.AncestralStateLogger"


def test_to_beast_sequence_ancestral_logger():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--ancestral-logger",
                "sequence",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//logger[@id=\"ancestralSequenceLogger\"]") is not None
        ancestral_log = beast_xml.find(".//logger[@id=\"ancestralSequenceLogger\"]/log")
        assert ancestral_log.get("spec") == "beastclassic.evolution.likelihood.AncestralSequenceLogger"


def test_to_beast_sequence_no_logger():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "-treconstructed",
                "-tdefective",
                "-torthographic",
                "-tsubreading",
                "-mlac",
                "-moverlap",
                "-s*",
                "-sT",
                "--fill-correctors",
                "--ancestral-logger",
                "none",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        beast_xml = et.parse(output, parser=parser)
        assert beast_xml.find(".//logger[@id=\"ancestralStateLogger\"]") is None
        assert beast_xml.find(".//logger[@id=\"ancestralSequenceLogger\"]") is None


def test_to_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "B10K6V20U12," in text


def test_to_csv_drop_constant():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--drop-constant", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "B10K6V20U12," not in text


def test_to_csv_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "long", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("taxon,character,state,value")
        assert "B10K6V20U12," in text


def test_to_csv_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "nexus", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",B10K1V1U24-26,B10K1V6U20-24,B10K1V14U2,B10K1V15U26-40")
        assert "B10K6V20U12," in text
        assert "{1 2}" in text


def test_to_csv_ambiguous_as_missing_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--ambiguous-as-missing", "--table", "nexus", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",B10K1V1U24-26,B10K1V6U20-24,B10K1V14U2,B10K1V15U26-40")
        assert "B10K6V20U12," in text
        assert "{1 2}" not in text


def test_to_csv_distance_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "distance", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert ",13," in text


def test_to_csv_proportion_distance_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--table", "distance", "--proportion", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert ",0.5," in text


def test_to_csv_show_ext_distance_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "distance", "--show-ext", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        print(text)
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert (
            ",17/38," in text
        )  # note that type "lac" readings are not treated as missing with the above inputs, so the only variation not counted for the second part is the one where P46 is ambiguous


def test_to_csv_proportion_show_ext_distance_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--table", "distance", "--proportion", "--show-ext", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert (
            ",0.4473684210526316/38," in text
        )  # note that type "lac" readings are not treated as missing with the above inputs, so the only variation not counted for the second part is the one where P46 is ambiguous


def test_to_csv_similarity_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "similarity", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert ",22," in text


def test_to_csv_proportion_similarity_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--table", "similarity", "--proportion", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert ",0.5789473684210527," in text


def test_to_csv_show_ext_similarity_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--table", "similarity", "--show-ext", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        print(text)
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert (
            "22/38" in text
        )  # note that type "lac" readings are not treated as missing with the above inputs, so the only variation not counted for the second part is the one where P46 is ambiguous


def test_to_csv_proportion_show_ext_similarity_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--table", "similarity", "--proportion", "--show-ext", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert (
            "0.5789473684210527/38" in text
        )  # note that type "lac" readings are not treated as missing with the above inputs, so the only variation not counted for the second part is the one where P46 is ambiguous


def test_to_csv_idf_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, ["--verbose", "--table", "idf", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",UBS,Byz,Lect,P46,P49,01")
        assert "\nUBS," in text
        assert "9.90215396342428" in text


def test_to_csv_drop_constant_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--drop-constant", "--table", "long", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("taxon,character,state,value")
        assert "B10K6V20U12," not in text


def test_to_csv_drop_constant_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app, ["--verbose", "--drop-constant", "--table", "nexus", str(input_example), str(output)]
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",B10K1V1U24-26,B10K1V6U20-24,B10K1V14U2,B10K1V15U26-40")
        assert "B10K6V20U12," not in text
        assert "{1 2}" in text


def test_to_csv_drop_constant_ambiguous_as_missing_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(
            app,
            [
                "--verbose",
                "--drop-constant",
                "--ambiguous-as-missing",
                "--table",
                "nexus",
                str(input_example),
                str(output),
            ],
        )
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith(",B10K1V1U24-26,B10K1V6U20-24,B10K1V14U2,B10K1V15U26-40")
        assert "B10K6V20U12," not in text
        assert "{1 2}" not in text


def test_to_tsv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, ["--verbose", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("\tUBS\tByz\tLect\tP46\tP49\t01")


def test_to_tsv_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, ["--verbose", "--table", "long", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("taxon\tcharacter\tstate\tvalue")


def test_to_tsv_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, ["--verbose", "--table", "nexus", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("\tB10K1V1U24-26\tB10K1V6U20-24\tB10K1V14U2\tB10K1V15U26-40")
        assert "B10K6V20U12" in text
        assert "{1 2}" in text


def test_to_tsv_distance_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, ["--verbose", "--table", "distance", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("\tUBS\tByz\tLect\tP46\tP49\t01")
        assert "\nUBS\t" in text
        assert "\t13\t" in text


def test_to_excel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, ["--verbose", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()


def test_to_excel_long_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, ["--verbose", "--table", "long", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()


def test_to_excel_nexus_table():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, ["--verbose", "--table", "nexus", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()


def test_to_phylip_distance_matrix():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(app, ["--verbose", "--table", "distance", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("%d" % (len(xml_witnesses)))
        assert (
            "UBS 0 11" in text
        )  # note that type "lac" readings are not treated as missing with the above inputs, so the only variation not counted as a disagreement is the one where Byz is ambiguous


def test_to_phylip_similarity_matrix():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath(".//tei:listWit/tei:witness", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(app, ["--verbose", "--table", "similarity", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8-sig")
        assert text.startswith("%d" % (len(xml_witnesses)))
        assert "UBS 38 26" in text  # UBS agrees with itself 38 times and agrees with Byz 26 times


def test_to_stemma():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--verbose", "--format", "stemma", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS Byz Lect P46 P49 01")
        assert (
            "παρρησιασωμαι |*1 παρρησιασομαι" in text
        )  # variation units with no ana attribute should default to weights of 1
        assert (
            "ο |*5 ος" in text
        )  # variation units with one attribute should have the weight associated with that category
        assert (
            "τοις.ιδιοις.ανδρασιν |*6 υποτασσεσθε.τοις.ιδιοις.ανδρασιν τοις.ιδιοις.ανδρασιν.υποτασσεσθωσαν υποτασεσθωσαν.τοις.ιδιοις.ανδρασιν τοις.ιδιοις.ανδρασιν.υποτασσεσθε"
            in text
        )  # variation units with multiple ana attributes should have weights equal to the average weights of their categories
        chron_output = Path(str(output) + "_chron")
        assert chron_output.exists()
        chron_text = chron_output.read_text(encoding="utf-8")
        assert chron_text.startswith("UBS")
        assert (
            "80    80    80" in chron_text
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the latest possible date of the origin


def test_to_stemma_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--verbose", "--format", "stemma", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert not chron_output.exists()


def test_to_stemma_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--verbose", "--format", "stemma", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert chron_output.exists()
        chron_text = chron_output.read_text(encoding="utf-8")
        assert chron_text.startswith("UBS")
        assert (
            chron_text.count("80    80    80") == 1
        )  # the UBS witness, whose lower and upper bounds equal 50, will have its lower and upper bounds updated to 80 to ensure that it is not earlier than the origin
        assert (
            chron_text.count("300  %d  %d" % (int((datetime.now().year + 300) / 2), datetime.now().year)) == 1
        )  # for 01, which has a lower bound and no upper bound
        assert chron_text.count("80   290   500") == 1  # for 02, which has an upper bound and no lower bound
        assert (
            chron_text.count("80  %d  %d" % (int((datetime.now().year + 80) / 2), datetime.now().year)) > 1
        )  # for the remaining witnesses whose bounds are set to the minimum and maximum


def test_to_stemma_no_origin_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test"
        result = runner.invoke(app, ["--verbose", "--format", "stemma", str(no_origin_some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("* UBS P46 01 02 03 04 06")
        chron_output = Path(str(output) + "_chron")
        assert chron_output.exists()  # a chron file should be written, since all witnesses have bounds on their dates
        chron_text = chron_output.read_text(encoding="utf-8")
        assert chron_text.startswith("UBS")
        assert (
            chron_text.count("50    50    50") == 1
        )  # the UBS witness has explicitly specified lower and upper bounds of 50
        assert (
            chron_text.count("300  %d  %d" % (int((datetime.now().year + 300) / 2), datetime.now().year)) == 1
        )  # for 01, whose lower bound is explicit and whose upper bound is inferred
        assert (
            chron_text.count("50   275   500") == 1
        )  # for 02, which upper bound is explicit and whose lower bound is inferred
        assert (
            chron_text.count("50  %d  %d" % (int((datetime.now().year + 50) / 2), datetime.now().year)) > 1
        )  # for the remaining witnesses whose bounds are set to the minimum (UBS lower bound) and maximum (current year)


def test_to_file_bad_format():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.unk"
        result = runner.invoke(app, ["--verbose", str(input_example), str(output)])
        assert isinstance(result.exception, Exception)
