'''
test functions in remote_data module
'''

from pathlib import Path
from urllib.error import HTTPError, URLError

from libgoods.utilities.remote_data import get_datafile

TEMP_DIR = Path(__file__).parents[1] / "temp_test_files"

def test_exception():
    """
    bogus file to raise an exception - do this if we have an internet
    connection before testing it
    """

    bogus = TEMP_DIR / 'bogus.txt'

    # just making sure that the test is a valid test!
    bogus.unlink(missing_ok=True)

    try:
        try:
            get_datafile(bogus)
        except HTTPError:
            assert not bogus.exists()  # if we got the error, we don't want the file created
            pass
        # with pytest.raises(HTTPError):
        #     get_datafile(bogus)
    except URLError:
        'no internet connection'
        return


def test_get_datafile():
    """
    downloads CLISShio.txt to make sure get_datafile works as expected
    Uses testdata['CatsMover']['tide'] as test file. If it exists, it moves
    it '*.renamed'. It then trys to download file and if it fails for any
    reason (most likely internet connection is missing), then copy the
    file back from '*.renamed' to testdata['CatsMover']['tide']
    At the end also, move the renamed file back
    """

    data_file = TEMP_DIR / "CLISShio.txt"
    # file_ = testdata['CatsMover']['tide']
    # delete it if it's there already
    data_file.unlink(missing_ok=True)

    for attempt in (1, 2):
        # do this twice to make sure it still works as expected after file has
        # been downloaded in 1st call
        # try:
        r_file = get_datafile(data_file)  # noqa: F841
        assert data_file.is_file()
        # except:
        #     if renamed is not None:
        #         shutil.move(renamed, file_)
        #     reason = ("Most likely urllib2.HTTPError exception in "
        #               "get_datafile(). Check internet connectivity.")
        #     pytest.xfail(reason=reason)
        #     return

