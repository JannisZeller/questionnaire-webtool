from flask import Blueprint
from flask import render_template, make_response
from flask import current_app

from ..api import API

from .core import call_api, interface_loggedin, get_user_info

index_bp = Blueprint("index_interface", __name__, template_folder="templates")


@index_bp.route("/")
@interface_loggedin(redirect_=False)
def home(cookies):
    """Interface-Route home.
    """
    username = get_user_info("username")
    return render_template("pages/loggedin/home.html", name=username)


@index_bp.route("/about")
def about():
    """Interface-Route about (imprint & data privacy statement).
    """
    res, data = call_api(API.cuser, method="GET")

    if res.status_code==401 or res.status_code==403:
        return render_template("pages/loggedout/about.html")

    if res.status_code==410:
        res = make_response(render_template(
            "pages/loggedout/tokenexpired.html"
        ))
        key = current_app.config['JWT_COOKIE_KEY']
        res.delete_cookie(key)
        return res

    return render_template("pages/loggedin/about.html")
