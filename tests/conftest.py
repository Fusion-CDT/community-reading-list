import sys
from pathlib import Path

# The scripts aren't a package, so make them importable by name
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
