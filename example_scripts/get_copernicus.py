import datetime
import copernicusmarine

#ME amacfadyen wIkyonos1

start_time = datetime.datetime.now()

lon_min = 33.22
lon_max = 51.44
lat_min = 8.72
lat_max = 22.63

current_posix = copernicusmarine.subset(
  dataset_id=" cmems_mod_med_phy-cur_anfc_4.2km-2D_PT1H-m",
  variables=["uo","vo"],
  minimum_longitude=-180,
  maximum_longitude=179.91668701171875,
  minimum_latitude=-80,
  maximum_latitude=90,
  start_datetime="2024-02-24T12:00:00",
  end_datetime="2024-02-24T12:00:00",
  minimum_depth=0.49402499198913574,
  maximum_depth=0.49402499198913574,
)
#datasetID = 'cmems_mod_glo_phy-cur_anfc_0.083deg_PT6H-i'
# datasetID = 'cmems_mod_glo_phy_anfc_merged-uv_PT1H-i '
# current_posix = copernicusmarine.subset(
  # dataset_id=datasetID,
  # variables=["utotal", "vtotal"],
  # minimum_longitude=lon_min,
  # maximum_longitude=lon_max,
  # minimum_latitude=lat_min,
  # maximum_latitude=lat_max,
  # start_datetime=(
      # start_time - datetime.timedelta(hours=12)
  # ).strftime("%Y-%m-%dT%H:%M:%S"), # 12 hr buffer ensures coverage
  # # removing end_datetime gets as much output as available? not sure....
  # #end_datetime=end_time.strftime("%Y-%m-%dT%H:%M:%S"),
  # minimum_depth=0.49402499198913574,
  # maximum_depth=0.49402499198913574,
# )
current_file = current_posix.name
