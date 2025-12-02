from . import YAML_DIR
from .metadata import Metadata
from libgoods import standard_names

class BaseModel:
    """
    Base class for all models
    """
    metadata = Metadata.from_yaml(YAML_DIR / 'example_metadata.yaml')
    metadata.identifier = "BASE_MODEL"

    # this should get overwritten by all subclasses
    access = None

    standard_names = {}

    def __init__(self):
        # add the environmental_params to metadata
        self.metadata.env_params = self.env_params

    @property
    def identifier(self):
        return self.metadata.identifier

    @property
    def env_params(self):
        return standard_names.get_env_params(self.standard_names.keys())

