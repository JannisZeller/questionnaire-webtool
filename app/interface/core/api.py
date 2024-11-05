import requests
from requests import Response as reqResponse

from flask import Response
from flask import url_for
from flask import request, current_app

from typing import Literal

from ...api import APIMethod, API  # noqa: F401


def call_api(
        api_method: APIMethod,
        method: str=Literal["GET", "POST", "PUT", "DELETE"],
        fun_kwargs: dict={},
    ) -> tuple[reqResponse|Response, dict]:

    if current_app.config["API_INTERFACE_COMMUNICATION"] == "functional":
        # hprint(f"Functional API-call ({api_method.url_for})")
        res = api_method(**fun_kwargs)
        data = res.get_json()

    if current_app.config["API_INTERFACE_COMMUNICATION"] == "request":
        # hprint(f"Request API-call url_for({api_method.url_for})")
        res = requests.request(
            method=method,
            url=url_for(api_method.url_for, _external=True),
            cookies=request.cookies.to_dict(),
        )
        data = res.json()

    # hprint(f"  Response: {res}")
    # hprint(f"  Data: {data}")

    return res, data
