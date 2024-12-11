import netCDF4 as nc4

import datetime

def round_dt_to_seconds(dt):
    dt += datetime.timedelta(seconds=0.5)
    return dt.replace(microsecond=0)

def round_dt_to_minutes(dt):
    dt += datetime.timedelta(seconds=30)
    return dt.replace(microsecond=0).replace(second=0)


# def roundSeconds(dateTimeObject):
#     newDateTime = dateTimeObject + datetime.timedelta(seconds=.5)
#     return newDateTime.replace(microsecond=0)



# file = "LakeErie-FVCOM-3D-WithIce.nc"

file = 'nos.lsofs.fields.f002.20231003.t18z.nc'

files = ['nos.lsofs.fields.f002.20231003.t06z.nc',
         'nos.lsofs.fields.f002.20231003.t12z.nc',
         'nos.lsofs.fields.f002.20231003.t18z.nc',
         ]

with nc4.MFDataset(files, 'r') as fidr:
#with nc4.Dataset(file, 'r') as fidr:
    print('\nInteger Time ("Itime", "Itime2" variables)\n----------------------')
    Itime = fidr.variables['Itime'][:]
    Itime_units = fidr.variables['Itime'].units

    Itime2 = fidr.variables['Itime2'][:]
    Itime2_units = fidr.variables['Itime2'].units

    day_part = nc4.num2date(Itime, units=Itime_units)
    time_part = [datetime.timedelta(milliseconds=int(ms)) for ms in Itime2]
    int_time = day_part + time_part

    print(f'Itime = {Itime} ({Itime_units})')
    print(f'Itime2 = {Itime2} ({Itime2_units})')
    print(int_time)

    print('\n\nFloat Time ("time" variable)\n----------------------')
    time = fidr.variables['time'][:]
    time_units = fidr.variables['time'].units
    float_time = nc4.num2date(time, units=time_units)
    float_time2 = [round_dt_to_minutes(dt) for dt in float_time]
    print(f'time = {time} ({time_units})')
    print(float_time2)

    print('\n\nString Time ("Times" variable)\n----------------------')
    Times = fidr.variables['Times'][:]
    string_time = [b''.join(T).decode('ascii') for T in Times]
    print(f'Times = {string_time}')

for st, ft, ft2, it in zip(string_time, float_time, float_time2, int_time):
    print(st, ft, ft2, it)


