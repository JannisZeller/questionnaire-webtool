from .api import API, call_api

def get_user_info(key: str=None):
    res, data = call_api(API.user_info, "GET")
    if key is None:
        return data
    else:
        return data[key]
