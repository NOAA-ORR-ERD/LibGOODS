from libgoods import api
import datetime
import os

model_id = 'NYOFS'
env_params = "surface currents"
#env_params = ["surface currents"]
axiom = False

EXAMPLE_BBOXES = {
    "CBOFS": (-76.5, 36.75, -75.25, 37.75),
    "CIOFS": (-154.5, 58.0, -151.0, 60.0),
    "CREOFS": (-123.9, 46.1, -123.6, 46.3),
    "CREOFS_RGRID": (-123.9, 46.1, -123.6, 46.3),
    "DBOFS": (-75.5, 38.5, -74.5, 39.25),
    "GFS-1-2DEG": (-85.0, 25.0, -60.0, 48.0),
    "GFS_1_4DEG": (-85.0, 25.0, -60.0, 48.0),
    "GFS-1DEG": (-85.0, 25.0, -60.0, 48.0),
    "GOMOFS": (-70, 41, -66, 44),
    "GOFS": (-79.10, 31.84, -68.159, 42.29),
    "LEOFS": (-83.6, 41.5, -82.6, 42.1),
    "LMHOFS": (-88, 41.57, -86, 44),
    "LOOFS": (-78.6, 43.4, -77.1, 43.7),
    "LSOFS": (-89.4, 47.0, -86.4, 47.75),
    "NGOFS2": (-91.5, 29.25, -91, 29.75),
    "NYOFS": (-74.1, 40.49, -73.95, 40.61),
    "SFBOFS": (-122.55, 37.75, -122.4, 37.9),
    "TBOFS": (-82.9, 27.3, -82.6, 27.7),
    "WCOFS": (-122.0, 25.0, -115.0, 35.0),
}

supported_models = {    
                    'GOFS':['hycom-forecast-agg',],
                    'WCOFS':['coops-forecast-noagg',],
                    'NGOFS2':['coops-forecast-noagg',],
                    'CREOFS':['coops-forecast-noagg',],
                    'LMHOFS':['coops-forecast-noagg',],
                    'CIOFS':['coops-forecast-agg',],
                    'LSOFS-FVCOM':['coops-forecast-noagg',],
                    'CBOFS':['coops-forecast-agg',],
                    'LEOFS':['coops-forecast-noagg',],
                    'DBOFS':['coops-forecast-agg',],
                    'LOOFS-FVCOM':['coops-forecast-noagg',],
                    'SFBOFS':['coops-forecast-noagg',],
                    'TBOFS':['coops-forecast-agg',],
                    'NYOFS':['coops-forecast-agg',],
                    'GOMOFS':['coops-forecast-agg',],
                    'GFS_1_4DEG':['ucar-forecast-agg',],
                    'GFS-1-2DEG':['ucar-forecast-agg',],
                    'GFS-1DEG':['ucar-forecast-agg',],
                    'WCOFS':['ioos-forecast-agg',],
                    'CREOFS_RGRID':['ioos-forecast-agg',],
                    }
                        

model_source = supported_models[model_id][0]

start = datetime.datetime.today()
end = start + datetime.timedelta(days=2)

bounds = EXAMPLE_BBOXES[model_id]

    

print('subsetting')
ds = api.get_model_subset(model_id,model_source,start,end,bounds,surface_only=True,environmental_parameters=env_params,axiom=axiom)

print('downloading output')
ofn = os.path.join('output',model_id + '.nc')
ofn = api.get_model_output(ds,ofn,axiom=axiom)

