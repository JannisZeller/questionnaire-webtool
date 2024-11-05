from requests import Response as reqResponse

from flask import Response
from flask import redirect, render_template, make_response
from flask import request, current_app

from functools import wraps
from typing import Callable

from .api import call_api, API


def propagate_cookies(res_from: reqResponse|Response, res_to: Response):
    """Utility function to pass cookies from an (api-) requests.Response to a
    (interface-) flask.Response.
    """
    if isinstance(res_from, reqResponse):
        cookies: dict = res_from.cookies.get_dict()
        for key, val in cookies.items():
            res_to.set_cookie(key, val, samesite="lax")

    if isinstance(res_from, Response):
        for key, val in res_from.headers:
            if key == "Set-Cookie":
                res_to.headers.add(key, val)

    return res_to


def validate_consent(cookies: dict, render: Callable[[], Response]):
    """Utility function for consent-validation in terms of a consent cookie
    with the 'CONSENT_COOKIE_KEY'-key.

    - Handles the consent_cookie validation and renders the corresponding
    template.
    - The `render`-Callable needs to accept the following bollean
    keyword-agruments: `[consent_missing]`
    - If the validation succeeds simply `1` is returned.
    """
    key = current_app.config['CONSENT_COOKIE_KEY']
    consent_cookie = cookies.get(key)
    if not consent_cookie or consent_cookie != "1":
        return render(consent_missing=True)
    return 1


def interface(f):
    """Wrapper function to pass on cookies as a dict.

    Basically every interface / "frontend" route is either @interface - or
    @interface_loggedin - wrapped.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        cookies: dict = request.cookies.to_dict()
        res = f(cookies, *args, **kwargs)
        return res
    return decorated


def interface_loggedin(redirect_: bool=True, propagate_cookies_: bool=True):
    """Wrapper function to pass on cookies as a dict. This version is used, if
    there is the page is only for logged-in users. It handles the cases of
    non-existance, non-validity, and expiration of a login-JWT. In such cases
    it redirects to / renders the corresponding views.

    Basically every interface / "frontend" route is either @interface- or
    @interface_loggedin-wrapped.

    - If `redirect_==True` it redirects to the base path if no user is logged in.
    - If `propagate_cookies_==True` cookies from the api-response
    (requests.Response) are passed on to the interface response.
    """
    def fl_wrapper(f: Callable):
        @wraps(f)
        def decorated(*args, **kwargs):
            req_cookies=request.cookies.to_dict()
            api_res, _ = call_api(API.cuser, method="GET")

            if api_res.status_code==401 or api_res.status_code==403:
                if redirect_:
                    return redirect("/")
                else:
                    return render_template("pages/loggedout/index.html")

            if api_res.status_code==410:
                res = make_response(render_template(
                    "pages/loggedout/tokenexpired.html"
                ))

                key = current_app.config['JWT_COOKIE_KEY']
                res.delete_cookie(key)
                return res

            if not propagate_cookies_:
                return f(req_cookies, *args, **kwargs)

            res = f(req_cookies, *args, **kwargs)

            try:
                res, status_code = res
            except (ValueError, TypeError):
                res, status_code = res, None

            res = make_response(res)

            res = propagate_cookies(api_res, res)

            if status_code:
                return res, status_code
            else:
                return res

        return decorated
    return fl_wrapper
