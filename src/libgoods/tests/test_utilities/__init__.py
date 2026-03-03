import pandas as pd


# utility for the tests:
def utc_now(freq="min"):
    """
    get now rounded to a given unit:

    freq='h' # hour
    freq='min' # minute
    freq='s'  seconds

    or any other freq pandas accepts
    """
    now = pd.Timestamp.now("UTC").replace(tzinfo=None)
    #    now = pd.to_datetime(datetime.datetime.utcnow())
    now = now.round(freq=freq)
    return now

