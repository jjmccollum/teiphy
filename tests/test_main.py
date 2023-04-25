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
some_dates_example = test_dir / "some_dates_example.xml"
fixed_rates_example = test_dir / "fixed_rates_example.xml"
bad_date_witness_example = test_dir / "bad_date_witness_example.xml"
intrinsic_odds_excess_indegree_example = test_dir / "intrinsic_odds_excess_indegree_example.xml"
intrinsic_odds_cycle_example = test_dir / "intrinsic_odds_cycle_example.xml"
intrinsic_odds_no_relations_example = test_dir / "intrinsic_odds_no_relations_example.xml"


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


def test_bad_date_witness_input():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(bad_date_witness_example), str(output)])
        assert isinstance(result.exception, WitnessDateException)
        assert "The following witnesses have their latest possible dates before the earliest date of origin" in str(
            result.exception
        )


def test_to_nexus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "\t22 B10K4V28U24_26" in text
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
        assert "\t22 B10K4V28U24_26" not in text
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
        assert "\t22 B10K4V28U24_26" in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_drop_constant_frequency():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--drop-constant", "--frequency", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "\t22 B10K4V28U24_26" not in text
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
        assert "CALIBRATE 18 = fixed(%d)" % (datetime.now().year - 1364) in text
        assert "CALIBRATE P46 = uniform(%d,%d)" % (datetime.now().year - 225, datetime.now().year - 175) in text


def test_to_nexus_calibrate_dates_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--calibrate-dates", str(no_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert "CALIBRATE UBS = offsetlognormal(0,0.0,1.0)" in text


def test_to_nexus_calibrate_dates_some_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--calibrate-dates", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin ASSUMPTIONS;" in text
        assert (
            "CALIBRATE UBS = fixed(%d)" % (datetime.now().year - 50) in text
        )  # both ends of date range specified and identical
        assert "CALIBRATE P46 = offsetlognormal(0,0.0,1.0)" in text  # neither end of date range specified
        assert (
            "CALIBRATE 01 = uniform(%d,%d)" % (0, datetime.now().year - 300) in text
        )  # lower bound but no upper bound
        assert (
            "CALIBRATE 02 = offsetlognormal(%d,0.0,1.0)" % (datetime.now().year - 500) in text
        )  # upper bound but no lower bound
        assert (
            "CALIBRATE 06 = uniform(%d,%d)" % (datetime.now().year - 600, datetime.now().year - 500) in text
        )  # both ends of date range specified and distinct


def test_to_nexus_mrbayes():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--mrbayes", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset treeagepr = uniform(%d,%d)" % (datetime.now().year - 80, datetime.now().year - 50) in text
        assert "calibrate 18 = fixed(%d);" % (datetime.now().year - 1364) in text
        assert "calibrate P46 = uniform(%d,%d);" % (datetime.now().year - 225, datetime.now().year - 175) in text


def test_to_nexus_mrbayes_no_dates():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--mrbayes", str(no_dates_example), str(output)])
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
        result = runner.invoke(app, ["--mrbayes", str(some_dates_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "Begin MRBAYES;" in text
        assert "prset treeagepr = offsetgamma(%d,1.0,1.0);" % (datetime.now().year - 50) in text
        assert (
            "calibrate UBS = fixed(%d);" % (datetime.now().year - 50) in text
        )  # both ends of date range specified and identical
        assert "calibrate P46 = offsetgamma(0,1.0,1.0);" in text  # neither end of date range specified
        assert (
            "calibrate 01 = uniform(%d,%d);" % (0, datetime.now().year - 300) in text
        )  # lower bound but no upper bound
        assert (
            "calibrate 02 = offsetgamma(%d,1.0,1.0);" % (datetime.now().year - 500) in text
        )  # upper bound but no lower bound
        assert (
            "calibrate 06 = uniform(%d,%d);" % (datetime.now().year - 600, datetime.now().year - 500) in text
        )  # both ends of date range specified and distinct


def test_to_nexus_mrbayes_strict_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(
            app,
            [
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
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
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
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tnt"
        result = runner.invoke(
            app,
            [
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
    xml_witnesses = xml.xpath("//tei:listWit/tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.phy"
        result = runner.invoke(
            app,
            [
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
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.fa"
        result = runner.invoke(
            app,
            [
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
    xml_witnesses = xml.xpath("//tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        beast_xml_sequences = beast_xml.xpath("//sequence")
        beast_xml_charstatelabels = beast_xml.xpath("//charstatelabels")
        beast_xml_site_distributions = beast_xml.xpath("//distribution[@spec=\"TreeLikelihood\"]")
        assert len(beast_xml_sequences) == len(xml_witnesses)
        assert len(beast_xml_charstatelabels) == len(xml_variation_units)
        assert len(beast_xml_site_distributions) == len(xml_variation_units)
        beast_xml_singleton_sequences = beast_xml.xpath("//charstatelabels[@characterName=\"B10K4V28U24-26\"]")
        assert len(beast_xml_singleton_sequences) == 1
        assert beast_xml_singleton_sequences[0].get("value") is not None
        assert "DUMMY" in beast_xml_singleton_sequences[0].get("value")


def test_to_beast_drop_constant():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_witnesses = xml.xpath("//tei:witness", namespaces={"tei": tei_ns})
    xml_variation_units = xml.xpath("//tei:app", namespaces={"tei": tei_ns})

    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        beast_xml_sequences = beast_xml.xpath("//sequence")
        beast_xml_charstatelabels = beast_xml.xpath("//charstatelabels")
        beast_xml_site_distributions = beast_xml.xpath("//distribution[@spec=\"TreeLikelihood\"]")
        assert len(beast_xml_sequences) == len(xml_witnesses)
        assert len(beast_xml_charstatelabels) == len(xml_variation_units) - 2
        assert len(beast_xml_site_distributions) == len(xml_variation_units) - 2
        beast_xml_singleton_sequences = beast_xml.xpath("//charstatelabels[@characterName=\"B10K4V28U24-26\"]")
        assert len(beast_xml_singleton_sequences) == 0


def test_to_beast_no_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        beast_xml_traits = beast_xml.xpath("//trait[@traitname=\"date\"]")
        assert len(beast_xml_traits) == 1
        assert beast_xml_traits[0].get("value") is not None
        assert beast_xml_traits[0].get("value") == ""
        beast_xml_origin_parameters = beast_xml.xpath("//origin")
        assert len(beast_xml_origin_parameters) == 1
        assert float(beast_xml_origin_parameters[0].get("value")) == 1.0
        assert float(beast_xml_origin_parameters[0].get("lower")) == 0.0
        assert beast_xml_origin_parameters[0].get("upper") == "Infinity"


def test_to_beast_some_dates():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        beast_xml_traits = beast_xml.xpath("//trait[@traitname=\"date\"]")
        assert len(beast_xml_traits) == 1
        assert beast_xml_traits[0].get("value") is not None
        assert beast_xml_traits[0].get("value") == "UBS=%d,01=%d,06=%d" % (
            50,
            int((datetime.now().year + 300) / 2),
            550,
        )
        beast_xml_origin_parameters = beast_xml.xpath("//origin")
        assert len(beast_xml_origin_parameters) == 1
        assert float(beast_xml_origin_parameters[0].get("value")) == 1.0
        assert float(beast_xml_origin_parameters[0].get("lower")) == datetime.now().year - 50
        assert beast_xml_origin_parameters[0].get("upper") == "Infinity"


def test_to_beast_variable_rates():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(input_example, parser=parser)
    xml_transcriptional_categories = xml.xpath(
        "//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        for xml_transcriptional_category in xml_transcriptional_categories:
            transcriptional_category = xml_transcriptional_category.get("{%s}id" % xml_ns)
            beast_xml_transcriptional_rate_categories = beast_xml.xpath(
                "//stateNode[@id=\"%s_rate\"]" % transcriptional_category
            )
            assert len(beast_xml_transcriptional_rate_categories) == 1
            assert float(beast_xml_transcriptional_rate_categories[0].get("value")) == 2.0
            assert beast_xml_transcriptional_rate_categories[0].get("estimate") == "true"


def test_to_beast_fixed_rates():
    parser = et.XMLParser(remove_comments=True)
    xml = et.parse(fixed_rates_example, parser=parser)
    xml_transcriptional_categories = xml.xpath(
        "//tei:interpGrp[@type=\"transcriptional\"]/tei:interp", namespaces={"tei": tei_ns}
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
                "//stateNode[@id=\"%s_rate\"]" % transcriptional_category
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
        root_frequencies_xml = beast_xml.find("//rootFrequencies/frequencies")
        assert root_frequencies_xml.get("value") is not None
        assert root_frequencies_xml.get("value") == "0.25 0.25 0.25 0.25"


def test_to_beast_strict_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        assert beast_xml.find("//branchRateModel") is not None
        branch_rate_model = beast_xml.find("//branchRateModel")
        assert branch_rate_model.get("spec") == "StrictClockModel"


def test_to_beast_uncorrelated_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        assert beast_xml.find("//branchRateModel") is not None
        branch_rate_model = beast_xml.find("//branchRateModel")
        assert branch_rate_model.get("spec") == "UCRelaxedClockModel"


def test_to_beast_local_clock():
    parser = et.XMLParser(remove_comments=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xml"
        result = runner.invoke(
            app,
            [
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
        assert beast_xml.find("//branchRateModel") is not None
        branch_rate_model = beast_xml.find("//branchRateModel")
        assert branch_rate_model.get("spec") == "RandomLocalClockModel"


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
        assert "50    65    80" in chron_text


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
        assert chron_text.count("50    50    50") == 1
        assert (
            chron_text.count("300  %d  %d" % (int((datetime.now().year + 300) / 2), datetime.now().year)) == 1
        )  # for the one witness with a lower bound and no upper bound
        assert chron_text.count("50   275   500") == 1  # for the one witness with an upper bound and no lower bound
        assert (
            chron_text.count("50  %d  %d" % (int((datetime.now().year + 50) / 2), datetime.now().year)) > 1
        )  # for the remaining witnesses whose bounds are set to the minimum and maximum


def test_to_file_bad_format():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.unk"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert isinstance(result.exception, Exception)
