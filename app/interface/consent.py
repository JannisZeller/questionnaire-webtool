from flask import Blueprint
from flask import redirect, make_response
from flask import request

from ..api import API

from .core import call_api, propagate_cookies, interface


consent_bp = Blueprint("consent_interface", __name__, template_folder="templates")

@consent_bp.route("/consent")
@interface
def consent(cookies):
    """Interface-Route to consent to the terms of use and retrieve the consent
    cookie.
    A interface-route is used to use a redirect-response without breaking the
    "only json"-pattern of the "API".
    """
    res, _ = call_api(API.consent, "GET")

    if res.status_code == 200:
        browser_res = make_response(redirect(request.referrer))
        browser_res = propagate_cookies(res, browser_res)
        return browser_res

    return redirect(request.referrer)
