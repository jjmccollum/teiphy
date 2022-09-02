from pathlib import Path
import tempfile
from typer.testing import CliRunner

from teiphy.main import app

runner = CliRunner()

root_dir = Path("__file__").parent.parent
input_example = root_dir/"example/ubs_ephesians.xml"

def test_to_nexus():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir)/"test.nexus"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text()
        assert text.startswith("#NEXUS")


def test_to_csv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir)/"test.csv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text()
        assert text.startswith(",P46,P49,P92,P132,01,01C1")


def test_to_tsv():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir)/"test.tsv"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()
        text = output.read_text()
        assert text.startswith("\tP46\tP49\tP92\tP132\t01\t01C1")


def test_to_excel():
    with tempfile.TemporaryDirectory() as tmp_dir:
        output = Path(tmp_dir)/"test.xlsx"
        result = runner.invoke(app, [str(input_example), str(output)])
        assert result.exit_code == 0
        assert output.exists()

