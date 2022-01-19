"""
currents package

classes for all the sources of currents
"""

from .hycom import HYCOM

all_currents = {'hycom': HYCOM(),
                }
