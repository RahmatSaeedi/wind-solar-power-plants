"""plantp — the teaching package that accompanies the book.

Every worked example in the book that involves a calculation is produced or
checked by this package and its tests. It is EDUCATIONAL software: it is not
certified design software and must never be connected to a real plant.
"""

__version__ = "0.2.0"

#: Release of the Plant P Reference Data Pack that new examples use (chapter 5 on).
#: Chapters 1-4 and 6 pin release "1.0.0" explicitly; its time series are identical.
DATA_RELEASE = "1.1.0"
RELEASES = ("1.0.0", "1.1.0")
