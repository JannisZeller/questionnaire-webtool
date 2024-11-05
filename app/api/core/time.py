import datetime as dt


def utc_now() -> dt.datetime:
    """Helper function for retrieving the current (UTC-) time.
    """
    t = dt.datetime.now(dt.UTC)
    return t


def get_reset_code_exp_time() -> str:
    """Wrapper function to get the expiration time of a reset code.

    Returns
    -------
    exp_time : str
        Expiration time as an iso-string.
    """
    td = dt.timedelta(minutes=10)
    exp_time = utc_now() + td
    return exp_time.isoformat()
