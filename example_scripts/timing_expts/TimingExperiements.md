# Example Results:

## Chris' machine: MacOS, home network: 55Mbps at the moment

The multi-file example is about 70MB, so if I'm doing the math right, my network should b able to dowload it all in about 10 seconds. So that's not the bottleneck.

### TBOFS_netcdf4_example.py: 

Frequent errors, usually Gateway, but there are others. I wrapped the opendap calls in a try: accept so it would retry.

Timing (with no errors): 8.65 minutes
                         7.20 minutes
                         7.36 minutes

Oddly, I've run it a few times with no gateway errors, while the DASK one is getting them pretty frequently ...

### TBOFS_dask_example.py:

Very frequent errors, usually doesn't run, but did once ???

#### Setting to single threaded:

```
import dask
# set to no threading
dask.config.set(scheduler='synchronous')
```

Then it ran:

process took:  12.52 minutes
process took:  9.62 minutes

But with occasional:


"""syntax error, unexpected WORD_WORD, expecting SCAN_ATTR or SCAN_DATASET or SCAN_ERROR
context: <html^><head><title>502 Bad Gateway</title></head><body><center><h1>502 Bad Gateway</h1></center></body></html>
"""

which is the same thing I get from the "raw" netcdf script -- I assume it's a server-side error, but netCDF4 doesn't handle it very well. Not sure what dask is doing -- maybe it's trying again? which would be nice.

### netcdf version 1.6.0:

We know that newer netCDF4 versions are not thread safe

The itermittent errors were with nerCDF4 1.6.2 -- downgrading to  netcdf4-1.6.0 results in it running without faiure (though a bunch of the gateway errors).

With dask.config.set(scheduler='threading':
  process took:  11.86 minutes

With dask.config.set(scheduler='single-threaded'):
  process took:  9.80 minutes

With dask.config.set(scheduler='synchronous'):
  process took:  10.20 minutes

With dask.config.set(scheduler='multiprocessing'):
     dask.config.set(scheduler='processes')
(same?)
Total Fail.

With:
```
from dask.distributed import Client
client = Client()
dask.config.set(scheduler='distributed')
```
Same (similar) fail as with "processes" -- perhaps netcdf4 is not picklable, and thus not usabae in multipel processes?










