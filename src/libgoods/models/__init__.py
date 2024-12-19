
from .coops_fvcom import NGOFS2, LMHOFS, LEOFS, LOOFS, LSOFS, SSCOFS
from .coops_roms import DBOFS, WCOFS, CBOFS, TBOFS, CIOFS, GOMOFS
from .doppio import DOPPIO
from .pacific_islands import HIIG, HIOG, HIOMSG, HIOMSAG, HIOEKG, MARI, MARIG, SAMOA
from .tamu import TAMU
from .twdb import SabineLake, GalvestonBay, MatagordaBay, CorpusChristiBay, SanAntonioBay 

ALL_MODELS = {"NGOFS2": NGOFS2,
              "LMHOFS": LMHOFS,
              "LEOFS": LEOFS,
              "LOOFS": LOOFS,
              "LSOFS": LSOFS,
              "SSCOFS": SSCOFS,
              "DBOFS": DBOFS,
              "WCOFS": WCOFS,
              "CBOFS": CBOFS,
              "TBOFS": TBOFS,
              "CIOFS": CIOFS,
              "GOMOFS": GOMOFS,
              "DOPPIO": DOPPIO,
              "HIIG": HIIG,
              "HIOG": HIOG,
              "HIOMSG": HIOMSG,
              "HIOMSAG": HIOMSAG,
              "HIOEKG": HIOEKG,
              "MARI": MARI,
              "MARIG": MARIG,
              "SAMOA": SAMOA,
              "TAMU": TAMU
              }


def get_models():
    """
    To Do: add filtering, selection, etc?

    get the model objects for all models
    """
    catalog = []
    
    for key in ALL_MODELS:
        m = ALL_MODELS[key]()
        catalog.append([m.name,key])
        
    return catalog


