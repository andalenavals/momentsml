"""
Subpackage for genrating plots

The modules in this subpackage typically define functions that plot something on matplotlib axes passed as first argument, based on the content of some astropy tables.
"""
__all__ = []

from . import utils
from . import scatter
from . import hist
from . import hexbin
from . import contour
from . import bin
from . import mcbin
from . import figures
from . import exp


