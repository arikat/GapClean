# gapclean/__init__.py

__version__ = "1.0.5"

# Import main API function for easy access
from gapclean.gapclean import clean_alignment

# Import exception classes for error handling
from gapclean.gapclean import (
    GapCleanError,
    InputValidationError,
    AlignmentError
)

# Define what gets imported with "from gapclean import *"
__all__ = [
    'clean_alignment',
    'GapCleanError',
    'InputValidationError',
    'AlignmentError',
    '__version__'
]
