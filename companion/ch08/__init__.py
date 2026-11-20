"""Chapter 8 companion scripts (generators and electrical machines)."""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_COMPANION = os.path.dirname(_HERE)
if _COMPANION not in sys.path:
    sys.path.insert(0, _COMPANION)
