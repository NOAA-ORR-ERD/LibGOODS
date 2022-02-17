"""
A set of dummy models that can be used for testing, exploring the API, etc

"""

from ..data_model import DataSource, Metadata


class DummyCurrents(DataSource):

    metadata = Metadata(
        identifier="dummy_cur",
        name="Example currents for testing",
        bounding_box=((39.01, -128.029), (50.072, -121.958)),
        bounding_poly=(
            (45.638, -121.961),
            (45.585, -122.161),
            (45.578, -122.373),
            (45.606, -122.58),
            (45.678, -122.766),
            (45.826, -122.747),
            (45.966, -122.814),
            (46.106, -122.891),
            (46.183, -123.073),
            (46.151, -123.283),
            (46.265, -123.418),
            (46.265, -123.632),
            (46.261, -123.847),
            (46.28, -124.059),
            (46.43, -124.065),
            (46.582, -124.065),
            (46.429, -124.02),
            (46.558, -123.915),
            (46.702, -123.866),
        ),
        info_text="Dummy model just for testing, etc.",
        forecast_available=True,
        hindcast_available=False,
        environmental_parameters=[
            "surface currents" "sea surface temperature" "ice data"
        ],
    )

    def get_available_times(self, cast_type):
        """
        returns the available times for this model as of right now

        :param cast_type: 'forecast' or 'hindcast'

        Hardcoded result
        """
        if cast_type == "forecast":
            return ("2022-02-15T12:00", "2022-02-20T12:00")
        if cast_type == "hindcast":
            return ("2021-10-01T12:00", "2022-02-15T12:00")


all_dummy_sources = {source.metadata.identifier: source() for source in {DummyCurrents}}
