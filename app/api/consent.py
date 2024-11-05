from flask import Blueprint, Response
from flask import jsonify
from flask import current_app


consent_bp = Blueprint("consent", __name__, template_folder="templates")


@consent_bp.route("/consent", methods=["GET"])
def consent_() -> Response:
    """Returns a response setting the consent cookie to 1.
    - HTTP - Status-Codes: 200
    """
    key = current_app.config['CONSENT_COOKIE_KEY']

    res = jsonify({'consent_cookie': True})
    res.set_cookie(key, "1", samesite="lax")
    res.status_code = 200
    return res
