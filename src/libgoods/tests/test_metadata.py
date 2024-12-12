"""
tests of the metadata classes - these test construction but nothing else at present
"""

from libgoods import metadata

model = 'CBOFS'
source = 'coops-forecast-agg'
yaml_dir = metadata.yaml_file_directory

yaml_file = yaml_dir / 'cbofs.yaml'


class TestMetadata:

    def test_init_from_yaml(self):
        meta = metadata.Metadata()
        meta = meta.init_from_yaml(yaml_file)
        assert "surface currents" in meta.env_params
