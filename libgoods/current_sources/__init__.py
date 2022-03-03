"""
Currents package

classes for all the sources of currents
"""

from .hycom import HYCOM
from .tbofs import TBOFS

all_currents = {source.metadata.identifier: source() for source in {HYCOM, TBOFS}}
