import gnome.scripting as gs

files = files = ['nos.lsofs.fields.f002.20231003.t06z.nc',
                 'nos.lsofs.fields.f002.20231003.t12z.nc',
                 'nos.lsofs.fields.f002.20231003.t18z.nc',
                 ]

curr = gs.GridCurrent.from_netCDF(files)



