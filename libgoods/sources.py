
import model_catalogs as mc
from .model import Model, Metadata
import dataclasses


# HAVE TO MAKE SURE THIS IS "COMPLETE" version
sources_init = mc.setup_source_catalog()


@dataclasses.dataclass
class Catalog(Model):
    identifier: str = ""
    product_type: str = "forecast"  # (forecast or hindcast)

    def __post_init__(self):
        cat = sources_init[self.identifier]
        # # only use these two timings, if they are both in the model catalog
        # timings = set(cat).intersection({'forecast', 'hindcast'})

        bbox = cat.metadata['bounding_box']
        # select out intake catalog for this model (contains all timings like
        # forecast, etc)
        params = set(cat[self.product_type].metadata['standard_names'].keys())
        # don't include coordinate names
        # import pdb; pdb.set_trace()
        params -= {'time', 'longitude', 'latitude'}

        self.metadata = Metadata(
                    identifier=self.identifier,
                    name=cat[self.product_type].description,
                    bounding_box=(tuple(bbox[:2]), tuple(bbox[2:])),
                    bounding_poly=cat.metadata['geospatial_bounds'],  # WKT form
                    info_text="",
                    product_type=self.product_type,
                    start=cat[self.product_type].metadata['overall_start_datetime'],
                    end=cat[self.product_type].metadata['overall_end_datetime'],
                    environmental_parameters=params,
                )

    def get_available_times(self):
        cat = mc.find_availability(model=self.identifier)
        avail = {"forecast": [cat["forecast"].metadata['start_datetime'],
                              cat["forecast"].metadata['end_datetime']],
                 "hindcast": [cat["hindcast"].metadata['start_datetime'],
                              cat["hindcast"].metadata['end_datetime']]}
        return avail


all_sources = {source: Catalog(source) for source in sources_init if 'REGULARGRID' not in source}


# class Catalog(Model):
#     def __init__(self, identifier, product_type="forecast"):
#         self.identifier = identifier
#         self.product_type = product_type
#
#         cat = sources_init[identifier]
#         # # only use these two timings, if they are both in the model catalog
#         # timings = set(cat).intersection({'forecast', 'hindcast'})
#
#         bbox = cat.metadata['bounding_box']
#         # select out intake catalog for this model (contains all timings like
#         # forecast, etc)
#         params = set(cat[product_type].metadata['standard_names'].keys())
#         # don't include coordinate names
#         # import pdb; pdb.set_trace()
#         params -= {'time', 'longitude', 'latitude'}
#
#         metadata = Metadata(
#                     identifier=identifier,
#                     name=cat[product_type].description,
#                     bounding_box=(tuple(bbox[:2]), tuple(bbox[2:])),
#                     bounding_poly=cat.metadata['geospatial_bounds'],  # WKT form
#                     info_text="",
#                     product_type=product_type,
#                     start=cat[product_type].metadata['overall_start_datetime'],
#                     end=cat[product_type].metadata['overall_end_datetime'],
#                     environmental_parameters=params,
#                 )
#         self.metadata = metadata

# # HAVE TO MAKE SURE THIS IS "COMPLETE" version
# sources_init = mc.setup_source_catalog()
#
# all_sources = {}
# for source in sources_init:
#     # Don't want to keep "regulargrid" sources
#     if 'REGULARGRID' in source:
#         continue
#     # print(source)
#     cat = sources_init[source]
#     # import pdb; pdb.set_trace()
#     bbox = cat.metadata['bounding_box']
#     # only use these two timings, if they are both in the model catalog
#     timings = set(cat).intersection({'forecast', 'hindcast'})
#     for timing in timings:
#         # select out intake catalog for this model (contains all timings like
#         # forecast, etc)
#         params = set(cat[timing].metadata['standard_names'].keys())
#         # don't include coordinate names
#         # import pdb; pdb.set_trace()
#         params -= {'time', 'longitude', 'latitude'}
#         model = Model()
#         model.metadata = Metadata(
#             identifier=source,
#             name=cat[timing].description,
#             bounding_box=(tuple(bbox[:2]), tuple(bbox[2:])),
#             bounding_poly=cat.metadata['geospatial_bounds'],  # WKT form
#             info_text="",
#             product_type=timing,
#             start=cat[timing].metadata['overall_start_datetime'],
#             end=cat[timing].metadata['overall_end_datetime'],
#             environmental_parameters=params,
#         )
#         all_sources[source] = model
#
# # all_sources = {source.metadata.identifier: source() for source in {HYCOM, TBOFS}}
