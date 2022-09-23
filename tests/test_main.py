from pathlib import Path
import tempfile
from typer.testing import CliRunner

from teiphy.main import app

runner = CliRunner()

test_dir = Path(__file__).parent
root_dir = test_dir.parent

input_example = root_dir / "example/ubs_ephesians.xml"
non_xml_example = root_dir / "pyproject.toml"
malformed_example = test_dir / "malformed_example.xml"
no_dates_example = test_dir / "no_dates_example.xml"
some_dates_example = test_dir / "some_dates_example.xml"


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


def test_to_nexus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_no_labels():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--no-labels", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "CharStateLabels" not in text
        assert "StatesFormat=Frequency" in text


def test_to_nexus_states_present():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--states-present", str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("#NEXUS")
        assert "StatesFormat=Frequency" not in text


def test_to_nexus_states_present_ambiguous_as_missing():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.nexus"
        result = runner.invoke(app, ["--states-present", "--ambiguous-as-missing", str(input_example), str(output)])
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


def test_to_hennig86():
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


def test_to_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.csv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith(",UBS,P46,01,02,03,04,06")


def test_to_tsv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.tsv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text(encoding="utf-8")
        assert text.startswith("\tUBS\tP46\t01\t02\t03\t04\t06")


def test_to_excel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir) / "test.xlsx"
        result = runner.invoke(app, [str(input_example), str(output)])
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
