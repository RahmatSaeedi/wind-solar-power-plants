"""Chapter 5 companion programs.

Importing this package puts companion/ on sys.path, so that "import plantp"
works when a program is started with "python -m companion.ch05.<name>" from
the project root. An installed package (pip install -e .) would not need it.
"""
import sys
from pathlib import Path

_COMPANION = str(Path(__file__).resolve().parents[1])
if _COMPANION not in sys.path:
    sys.path.insert(0, _COMPANION)
