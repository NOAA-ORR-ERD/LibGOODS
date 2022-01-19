"""
currents package

classes for all the sources of currents
"""

from .hycom import HYCOM
from .tbofs import TBOFS

all_currents = {'hycom': HYCOM(),
                'tbofs': TBOFS(),
                }
