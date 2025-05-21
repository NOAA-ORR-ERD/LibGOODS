"""
tests of the metadata classes - these test construction but nothing else at present
"""

from libgoods.models import metadata, YAML_DIR

model = 'NGOFS2'
yaml_file = YAML_DIR / 'ngofs2.yaml'


def test_init_from_yaml():
    meta = metadata.Metadata()
    meta = meta.init_from_yaml(yaml_file)
    assert meta.identifer == 'NGOFS2'
    assert False
