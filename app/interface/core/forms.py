from flask import current_app
from flask_wtf import FlaskForm

from functools import wraps


class AJAXForm(FlaskForm):
    action_url: str
    def __init__(self, action_url: str, *args, **kwargs):
        self.action_url = action_url
        super().__init__(*args, **kwargs)


def form_render_kws(
        placeholder: str,
        autocapitalize: str="off",
        autosuggest: str="off",
        autocorrect: str="off",
        autocomplete: str="off",
        spellcheck: str="false",
        **kwargs
    ):
    """Utility function to pass some default arguments to flask-wtf - forms.
    """
    return {
        'placeholder': placeholder,
        'autocapitalize': autocapitalize,
        'autosuggest': autosuggest,
        'autocorrect': autocorrect,
        'autocomplete': autocomplete,
        'spellcheck': spellcheck,
        **kwargs
    }


def auth_form(f):
    """Decprator to pass render-functions of auth-forms (login, signup,
    user-reset) to handle common utilities (ReCAPTCHA and consent)
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        defaults = {
            "consent_missing": False,
            "recaptcha_failed": False,
            "recaptcha_timedout": False,
            "enable_recaptcha": current_app.config.get("ENABLE_RECAPTCHA", False),
            "recaptcha_site_key": current_app.config.get("RECAPTCHA_PUBLIC_KEY", None),
        }
        for key, val in defaults.items():
            kwargs[key] = kwargs.get(key, val)

        return f(*args, **kwargs)

    return decorated
