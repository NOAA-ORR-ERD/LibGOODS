"""
tests of the data models base class
"""

import pytest
pytest.skip("Skipping -- obsolete", allow_module_level=True)

import copy

from libgoods.model import Model, Metadata, CastMetadata

sample_NYOFS_forecast_metadata = {'axis': {'T': 'time', 'X': 'nx', 'Y': 'ny'},
 'catalog_dir': 'c:/users/jay.hennen/documents/code/libgoods/model_catalogs/model_catalogs/catalogs/complete/',
 'output_period_(hr)': 1,
 'overall_end_datetime': '48 hours after present time',
 'overall_start_datetime': '7 days before present time',
 'standard_names': {'eastward_sea_water_velocity': 'u',
  'eastward_wind': 'air_u',
  'northward_sea_water_velocity': 'v',
  'northward_wind': 'air_v',
  'ocean_sigma_coordinate': 'sigma',
  'sea_floor_depth': 'depth',
  'sea_surface_height_above_mean_sea_level': 'zeta',
  'time': 'time',
  'upward_sea_water_velocity': 'w'}
  }

class TestCastMetadata:
    def test_construction(self):
        cm = CastMetadata()
        assert isinstance(cm.env_params, set)
        assert len(cm.env_params) == 0
        cm.init_from_model_cast_metadata(sample_NYOFS_forecast_metadata)
        assert 'eastward_wind' in cm.standard_names
        assert 'surface winds' in cm.env_params or 'winds' in cm.env_params

class TestMetadata:
    def test_construction(self):
        md = Metadata()
        assert len(md.env_params) == 0
        assert isinstance(md.forecast_metadata, CastMetadata)

    def test_env_params(self):
        md = Metadata()
        edited_sample_data = copy.deepcopy(sample_NYOFS_forecast_metadata)
        del edited_sample_data['standard_names']['eastward_wind']
        md.forecast_metadata.init_from_model_cast_metadata(edited_sample_data)
        md.nowcast_metadata.init_from_model_cast_metadata(sample_NYOFS_forecast_metadata)
        md.hindcast_metadata.init_from_model_cast_metadata(sample_NYOFS_forecast_metadata)
        md.compute_env_params()
        #winds aren't in forecast, so they won't appear in the overall metadata either.
        assert 'surface winds' not in md.env_params
        assert 'surface winds' in md.nowcast_metadata.env_params
        assert 'surface winds' in md.hindcast_metadata.env_params
        assert 'surface winds' not in md.forecast_metadata.env_params
