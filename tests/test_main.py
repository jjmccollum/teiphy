from pathlib import Path
import tempfile
from typer.testing import CliRunner

from teiphy.main import app

runner = CliRunner()

root_dir = Path("__file__").parent.parent
input_example = root_dir/"example/ubs_ephesians.xml"

def test_to_nexus():
    with tempfile.NamedTemporaryFile() as output:
        result = runner.invoke(app, ["to-nexus", str(input_example), output.name])
        assert result.exit_code == 0
        assert Path(output.name).exists()
        text = Path(output.name).read_text()
        assert text.startswith("#NEXUS")


