from .base_models import BaseModel

url_base = 'http://hfrnet-tds.ucsd.edu/thredds/dodsC/HFR/'

regions = {'AKNS':'Alaska_-_North_Slope',
           'GAK':'US_Gulf_of_Alaska',
           'USWC':'US_West_Coast',
           'USEGC':'US_East_and_Gulf_Coast',
           'USHI':'US_Hawaii',
           'PRVI':'Puerto_Rico_and_the_US_Virgin_Islands',
           'GLNA':'Great_Lakes_of_North_America'
          }

class HFRadar(BaseModel):
    chunks = None
    drop_variables = None
    standard_names = {
    'eastward_sea_water_velocity': 'u',
    'northward_sea_water_velocity': 'v',
    }
    tvar = 'time'
    access = 'opendap'
    

    def __init__(self, region, res='6km'):    
        '''
        Regions - must be key from dict above
        Resolution - 500m, 1km, 2km, 6km
        This only handles hourly - can add averages in future
        but URLs are inconsistent for 25h, monthly, annual 
        maybe port code from GOODS which builds urls from server
        '''
        if region in regions:
            fname = 'HFRADAR_' + regions[region] + '_' + res + '_Resolution_Hourly_RTV_best.ncd'
            self.location = url_base + region + '/' + res + '/hourly/RTV/' + fname
        else: 
            raise KeyError('Region must be in ', list(regions.keys()))
    
    
    def filter_variables(self,variable_list=None,is3d=False):
        #variable list default is based on surface u/v variable names
        if variable_list is None:
            variable_list = ['eastward_sea_water_velocity','northward_sea_water_velocity']
     
        vars2include = [self.standard_names[v] for v in variable_list]

        self.ds = self.ds.xsg.subset_vars(vars2include)

        
