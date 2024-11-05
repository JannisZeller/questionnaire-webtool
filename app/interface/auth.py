import requests
from requests.auth import HTTPBasicAuth

from flask import Blueprint
from flask import render_template, redirect, url_for, make_response
from flask import request, current_app

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


from ..api import API

from .core import (
    call_api,
    propagate_cookies,
    interface,
    interface_loggedin,
    validate_consent,
    form_render_kws,
    validate_recaptcha,
    auth_form,
)


auth_bp = Blueprint("auth_interface", __name__, template_folder="templates")


class LoginForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(message="Der Benutzername ist ein Pflichtfeld."),
            Length(max=30,message="Der Benutzername darf maximal 30 Zeichan lang sein."),
        ],
        render_kw=form_render_kws("Benutzername")
    )
    password = PasswordField(
        validators=[
            InputRequired(message="Das Passwort ist ein Pflichtfeld."),
            Length(max=20, message="Das Passwort darf maximal 20 Zeichan lang sein.")],
        render_kw=form_render_kws("Passwort")
    )


@auth_bp.route("/login", methods=["GET", "POST"])
@interface
def login(cookies):
    """Interface-Route for logging in.
    """
    form = LoginForm()

    @auth_form
    def render(**kwargs):
        kwargs["login_error"] = kwargs.get("login_error", False)
        return render_template(
            "pages/loggedout/login.html",
            form=form,
            **kwargs,
        )

    consent_val = validate_consent(cookies, render)
    if consent_val != 1:
        return consent_val


    if form.validate_on_submit():

        recaptcha_val = validate_recaptcha(request, render)
        if recaptcha_val != 1:
            return recaptcha_val

        auth = HTTPBasicAuth(
            form.username.data.strip().encode("utf-8"),
            form.password.data.encode("utf-8"),
        )

        res = requests.post(
            url_for(API.login.url_for, _external=True),
            auth=auth,
            cookies=cookies,
        )

        if res.status_code == 200:
            browser_res = make_response(redirect("/"))

            key = current_app.config['JWT_COOKIE_KEY']
            browser_res.set_cookie(key, res.cookies[key])
            return browser_res

        if res.status_code == 412:
            return render(consent_missing=True)

        else:
            return render(login_error=True)

    return render()


@auth_bp.route("/logout", methods=["GET", "POST"])
@interface
def logout(cookies):
    """Interface-Route for logging out.
    """
    res, data = call_api(API.logout, "GET")

    if res.status_code == 200:
        browser_res = make_response(redirect("/"))

        key = current_app.config['JWT_COOKIE_KEY']
        browser_res.delete_cookie(key)
        return browser_res


@auth_bp.route("/refresh_session", methods=["GET", "POST"])
@interface_loggedin()
def refresh_session(cookies):
    """Interface-Route to refresh session.
    A interface-route is used to use a redirect-response without breaking the
    "only json"-pattern of the "API".
    """
    res, data = call_api(API.renew_token, "GET")

    if res.status_code == 200:
        browser_res = make_response(redirect(request.referrer))
        browser_res = propagate_cookies(res, browser_res)
        return browser_res
