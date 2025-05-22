

from pathlib import Path

from .coops_fvcom import NGOFS2
# from .coops_fvcom import NGOFS2, LMHOFS, LEOFS, LOOFS, LSOFS, SSCOFS
# from .coops_roms import DBOFS, WCOFS, CBOFS, TBOFS, CIOFS, GOMOFS
# from .doppio import DOPPIO
# from .pacific_islands import HIIG, HIOG, HIOMSG, HIOMSAG, HIOEKG, MARI, MARIG, SAMOA
# from .tamu import TAMU
# from .twdb import SabineLake, GalvestonBay, MatagordaBay, CorpusChristiBay, SanAntonioBay
# from .ncom_regional import AmSeas, Alaska, USEast
# from .wfs import WFCOM, TBCOM
# from .necofs import NECOFS, MassCoastal, BostonHarbor, Hampton, Scituate
# from .hf_radar import HFRadar

YAML_DIR = Path(__file__).parent / 'metadata'

# ALL_MODELS = {"NGOFS2": NGOFS2,
#               "LMHOFS": LMHOFS,
#               "LEOFS": LEOFS,
#               "LOOFS": LOOFS,
#               "LSOFS": LSOFS,
#               "SSCOFS": SSCOFS,
#               "DBOFS": DBOFS,
#               "WCOFS": WCOFS,
#               "CBOFS": CBOFS,
#               "TBOFS": TBOFS,
#               "CIOFS": CIOFS,
#               "GOMOFS": GOMOFS,
#               "DOPPIO": DOPPIO,
#               "HIIG": HIIG,
#               "HIOG": HIOG,
#               "HIOMSG": HIOMSG,
#               "HIOMSAG": HIOMSAG,
#               "HIOEKG": HIOEKG,
#               "MARI": MARI,
#               "MARIG": MARIG,
#               "SAMOA": SAMOA,
#               "TAMU": TAMU,
#               "SabineLake": SabineLake,
#               "MatagordaBay": MatagordaBay,
#               "SanAntonioBay": SanAntonioBay,
#               "CorpusChristiBay": CorpusChristiBay,
#               "GalvestonBay": GalvestonBay,
#               'NCOM US East Coast': USEast,
#               'NCOM Alaska': Alaska,
#               'NCOM American Seas': AmSeas,
#               'WFCOM': WFCOM,
#               'TBCOM': TBCOM,
#               'NECOFS': NECOFS,
#               'MassCoastal': MassCoastal,
#               'BostonHarbor': BostonHarbor,
#               'Hampton': Hampton,
#               'Scituate': Scituate,
#               'HFRadar': HFRadar
#               }


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
            cat.append([m.name,'GOOD'])
        except Exception as e:
            cat.append([m.name,e])

    return cat
