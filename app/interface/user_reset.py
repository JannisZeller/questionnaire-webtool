import requests
from requests.auth import HTTPBasicAuth

from flask import Blueprint
from flask import render_template, url_for
from flask import request, current_app

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, Email


from ..api import API

from .core import interface, form_render_kws, validate_recaptcha, auth_form


user_reset_bp = Blueprint("user_reset_interface", __name__, template_folder="templates")


class ResetFrom(FlaskForm):
    username = StringField(
        validators=[Length(max=30)],
        render_kw=form_render_kws("Benutzername")
    )
    password = PasswordField(
        validators=[Length(max=20)],
        render_kw=form_render_kws("Passwort")
    )
    reset_code = StringField(
        validators=[InputRequired("Der Reset-Code ist ein Plfichtfeld."), Length(max=20)],
        render_kw=form_render_kws("Reset-Code")
    )


class RequestResetForm(FlaskForm):
    email = EmailField(
        validators=[
            InputRequired(),
            Email(message="E-Mail Adresse ungültig."),
            Length(max=50),
        ],
        render_kw=form_render_kws("E-Mail")
    )


@user_reset_bp.route("/request_reset", methods=["GET", "POST"])
@interface
def request_reset(cookies: dict):
    """Interface-Route for requesting a user-reset code (via E-Mail)
    """
    form = RequestResetForm()

    @auth_form
    def render(**kwargs):
        defaults = {
            "no_user": False,
            "email_sent": False,
        }
        for key, val in defaults.items():
            kwargs[key] = kwargs.get(key, val)
        return render_template(
            "pages/loggedout/request_reset.html",
            form=form,
            **kwargs,
        )


    key = current_app.config['CONSENT_COOKIE_KEY']
    consent_cookie = cookies.get(key)

    if not consent_cookie or consent_cookie != "1":
        return render(consent_missing=True)

    if form.validate_on_submit():
        validate_recaptcha(request, render)

        res = requests.post(
            url_for(API.request_account_reset.url_for, _external=True),
            json={'email': form.email.data},
            cookies=cookies,
        )

        if res.status_code == 404:
            return render(no_user=True)

        return render(email_sent=True)

    return render()




@user_reset_bp.route("/user_reset", methods=["GET", "POST"])
@interface
def user_reset(cookies: dict):
    """Interface-Route for executing a user-reset (given a code that has
    been previously retrieved via the `/request_reset`-route).
    """
    form = ResetFrom()

    @auth_form
    def render(**kwargs):
        defaults = {
            "user_updated": False,
            "token_invalid": False,
            "token_expired": False,
            "user_already_exists": False,
        }
        for key, val in defaults.items():
            kwargs[key] = kwargs.get(key, val)
        return render_template(
            "pages/loggedout/user_reset.html",
            form=form,
            **kwargs,
        )

    key = current_app.config['CONSENT_COOKIE_KEY']
    consent_cookie = cookies.get(key)

    if not consent_cookie or consent_cookie != "1":
        return render(consent_missing=True)


    if form.validate_on_submit():
        validate_recaptcha(request, render)

        auth = HTTPBasicAuth(
            form.username.data.encode("utf-8"),
            form.password.data.encode("utf-8"),
        )

        res = requests.put(
            url_for(API.account_reset.url_for, _external=True),
            auth=auth,
            json={'reset_code': form.reset_code.data},
            cookies=cookies,
        )

        print(res)

        if res.status_code == 401:
            return render(token_invalid=True)

        if res.status_code == 409:
            return render(user_already_exists=True)

        if res.status_code == 410:
            return render(token_expired=True)

        return render(user_updated=True)


    return render()
