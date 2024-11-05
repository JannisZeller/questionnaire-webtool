from flask import Flask, Blueprint, Request
from flask.sessions import SecureCookieSessionInterface, SecureCookieSession

import json


# Config as JSONC (with comments) loaders
class JSONCDecoder(json.JSONDecoder):
    def __init__(self, **kw):
        super().__init__(**kw)

    def decode(self, s: str) -> str:
        s = '\n'.join(
            line if not line.lstrip().startswith('//')
            else ''
            for line in s.split('\n')
        )
        return super().decode(s)

def load_env_json(path: str) -> dict:
    with open(path) as f:
        dct = json.load(f, cls=JSONCDecoder)
    return dct

def set_config_from_json(app: Flask, path: str):
    cnfg = load_env_json(path)
    for key, val in cnfg.items():
        app.config[key] = val


# Register multiple blueprints
def register_blueprint_list(app: Flask, bp_list: list[Blueprint], prefix: str=None):
    for bp in bp_list:
        app.register_blueprint(bp, url_prefix=prefix)


# Custom Flask-session to wait for user confirmation before setting
#   session cookie
class ConsentCookieSession(dict, SecureCookieSessionInterface):
    def no_set_cookie(self, *args, **kwargs):
        return False
    def yes_set_cookie(self, *args, **kwargs):
        return True

    def open_session(self, app: Flask, request: Request) -> SecureCookieSession:
        consent_cookie = request.cookies.get(app.config["CONSENT_COOKIE_KEY"])
        consent_given = consent_cookie == "1"

        if consent_given:
            self.should_set_cookie = self.yes_set_cookie
        else:
            self.should_set_cookie = self.no_set_cookie

        return super().open_session(app, request)


def print_status(app: Flask):
    if app.config["ENABLE_RECAPTCHA"]:
        print("(Interface) ReCAPTCHA: Enabled")
    else:
        print("(Interface) ReCAPTCHA: Disabled")
