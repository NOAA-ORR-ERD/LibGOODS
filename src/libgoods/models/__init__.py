from pathlib import Path

YAML_DIR = Path(__file__).parent / "metadata"

# do we need them in the whole namespace?

from .base_models import BaseModel

from .coops_fvcom import NGOFS2, LMHOFS, LEOFS, LOOFS, LSOFS, SSCOFS
from .coops_roms import DBOFS, WCOFS, CBOFS, TBOFS, CIOFS, GOMOFS
# from .doppio import DOPPIO
# from .pacific_islands import HIIG, HIOG, HIOMSG, HIOMSAG, HIOEKG, MARI, MARIG, SAMOA
# from .tamu import TAMU
# from .twdb import SabineLake, GalvestonBay, MatagordaBay, CorpusChristiBay, SanAntonioBay
# from .ncom_regional import AmSeas, Alaska, USEast
# from .wfs import WFCOM, TBCOM
# from .necofs import NECOFS, MassCoastal, BostonHarbor, Hampton, Scituate
# from .hf_radar import HFRadar

# fixme: should this be an instance or teh model class??
#        it's currently the class, and get_models instantiates them,
#        but I think maybe it should be the instance already ??

# getting clever to build the list of all models
# it's imported, it should be auto-added.
ALL_MODELS = {mod().identifier: mod
              for mod in vars().values()
              if type(mod) is type
                  and issubclass(mod, BaseModel)
                  and (mod is not BaseModel)
              }


def get_models(which='all'):
    """
    Get the model objects for all the models

    :param which: Which set of models do you want.
                  Currently the only option is 'all'
                  but in the future -- who knows?

                  default: 'all'

    :returns: a list of (model name, model_id) pairs

    fixme: why??
    """
    catalog = []

    for key in ALL_MODELS:
        m = ALL_MODELS[key]()
        catalog.append([m.metadata.name, key])

    return catalog


def open_all():
    """
    Check all model datasets to see if models.open_ds() returns an error.
    Return errors
    """
    cat = []

    for key in ALL_MODELS:
        m = ALL_MODELS[key]()
        print(m.name)
        try:
            m.open_ds()
            cat.append([m.name, "GOOD"])
        except Exception as e:
            cat.append([m.name, e])

    return cat
