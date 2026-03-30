from pathlib import Path

YAML_DIR = Path(__file__).parent / "metadata"

# do we need them in the whole namespace?

from .base import BaseModel
from .coops_fvcom import LEOFS, LMHOFS, LOOFS, LSOFS, NGOFS2, SSCOFS, SFBOFS
from .coops_roms import CBOFS, CIOFS, DBOFS, GOMOFS, TBOFS, WCOFS
from .doppio import DOPPIO
from .espc import ESPC
from .gfs import GFS
from .hf_radar import HFRadar
from .ncom_regional import Alaska, AmSeas, USEast
from .necofs import NECOFS, BostonHarbor, Hampton, MassCoastal, Scituate
from .pacific_islands import HIIG, HIOEKG, HIOG, HIOMSAG, HIOMSG, MARIG, SAMOA, WPAC
from .tamu import TAMU
#from .twdb import CorpusChristiBay, GalvestonBay, MatagordaBay, SabineLake, SanAntonioBay
from .wfs import TBCOM, WFCOM

# fixme: should this be an instance or the model class??
#        it's currently the class, and get_models instantiates them,
#        but I think maybe it should be the instance already ??

# getting clever to build the list of all models
# it's imported, it should be auto-added.
ALL_MODELS = {mod.metadata.identifier: mod
              for mod in vars().values()
              if type(mod) is type
                  and issubclass(mod, BaseModel)
              }

del ALL_MODELS[BaseModel.metadata.identifier]

def get_models():
    """
    Get the model objects for all the models

    :returns: a list of (model name, model_id) pairs


    """
    catalog = []

    for key in ALL_MODELS:
        m = ALL_MODELS[key]()
        catalog.append([m.metadata.name, key])

    return catalog


def get_model_metadata(model_ids=None,):
    """
    Returns the metadata for all the models available

    :param model_ids=None: Sequence of ids of the models you want.
                           If None -- all available with be returned

    :returns: list of Metadata objects
    """


    metas = [mod().metadata for mod in ALL_MODELS.values()]
    if model_ids is not None:
        metas = [mod for mod in metas if mod.identifier in model_ids]
    return (metas)


def open_all():
    """
    Check all model datasets to see if models.open_ds() returns an error.
    Return errors
    """
    cat = []

    for key in ALL_MODELS:
        m = ALL_MODELS[key]()
        print(m.metadata.name)
        try:
            m.open_ds()
            cat.append([m.metadata.name, "GOOD"])
        except Exception as e:
            cat.append([m.metadata.name, e])

    return cat
