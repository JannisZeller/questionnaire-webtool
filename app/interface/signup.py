import requests
from requests.auth import HTTPBasicAuth

from flask import Blueprint
from flask import render_template, redirect, url_for
from flask import current_app, request

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError, Email


from ..api import API

from .core import (
    interface,
    validate_consent,
    form_render_kws,
    validate_recaptcha,
    auth_form,
)


signup_bp = Blueprint("signup_interface", __name__, template_folder="templates")


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(message="Der Benutzername ist ein Pflichtfeld."),
            Length(min=2, max=30, message="Benutzername zu kurz (<2) oder zu lang (>30)."),
        ],
        render_kw=form_render_kws("Benutzername")
    )
    email = EmailField(
        validators=[
            InputRequired(message="Die E-Mail Adresse ist ein Pflichtfeld."),
            Email(message="Keine gültige E-Mail Adresse"),
            Length(max=50, message="E-Mail Adresse zu lang (>50)."),
        ],
        render_kw=form_render_kws("E-Mail")
    )
    password = PasswordField(
        validators=[
            InputRequired(message="Das Passwort ist ein Pflichtfeld."),
            Length(max=50, message="Passwort zu lang (>50).")
        ],
        render_kw=form_render_kws("Passwort")
    )

    def validate_username(self, username: StringField):
        res = requests.get(
            url_for(API.check_username.url_for, _external=True),
            json={'username': username.data.strip()},
        )
        username_exists = res.json()['username_exists']
        if username_exists:
            raise ValidationError("Dieser Benutzername existiert bereits.")

    def validate_email(self, email: EmailField):
        res = requests.get(
            url_for(API.check_email.url_for, _external=True),
            json={'email': email.data.strip()},
        )
        email_exists = res.json()['email_exists']
        if email_exists:
            raise ValidationError("Es gibt schon einen Account mit dieser E-Mail Adresse.")


@signup_bp.route("/signup", methods=["GET", "POST"])
@interface
def signup(cookies):
    """Interface-Route for signing up.
    """
    form = RegisterForm()

    @auth_form
    def render(**kwargs):
        return render_template(
            "pages/loggedout/signup.html",
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
            url_for(API.signup.url_for, _external=True),
            auth=auth,
            json={'email': form.email.data.strip()},
            cookies=cookies,
        )

        if res.status_code == 200:
            return redirect(url_for("auth_interface.login"))

        if res.status_code == 412:
            return render(consent_missing=True)

    return render()
