from flask import Blueprint, Response
from flask import jsonify, make_response
from flask import request

from werkzeug.security import generate_password_hash

from .core.database import db
from .core.dbmodels import User, TestEdit

from .core.cookies import cconsent_required, hash_string


signup_bp = Blueprint("signup", __name__, template_folder="templates")


@signup_bp.route("/check_username", methods=["GET"])
def check_username() -> Response:
    """Checks wether username (already) exists.
    Used in username validation for signup.
    - HTTP - Status-Codes: 200, 409
    """
    # username = request.args.get('username')
    username = request.get_json()['username']
    username_exists = User.query.filter_by(username=username).first() is not None
    res = jsonify({'username_exists': username_exists})

    if not username_exists:
        res.status_code = 200
        return res

    res.status_code = 409
    return res


@signup_bp.route("/check_email", methods=["GET"])
def check_email() -> Response:
    """Checks wether E-Mail address (already) exists.
    Used in username validation for signup.
    - HTTP - Status-Codes: 200, 409
    """
    # email = request.args.get('email')
    email = request.get_json()['email']
    hashed_email = hash_string(email)
    email_exists = User.query.filter_by(email=hashed_email).first() is not None
    res = jsonify({'email_exists': email_exists})

    if not email_exists:
        res.status_code = 200
        return res

    res.status_code = 409
    return res


@signup_bp.route("/signup", methods=["POST"])
@cconsent_required
def signup_() -> Response:
    """Route for signup.
    Username and password are accepted as a HTTPBasicAuth-Header.
    - Consent cookie required to allow ReCaptcha
    - HTTP - Status-Codes: 200, 412
    """
    auth = request.authorization # TODO: Keep auth header or use arguments / data?
    data = request.get_json()

    hashed_email = hash_string(data['email'])
    hashed_password = generate_password_hash(auth.password, method="scrypt")

    new_user: User = User(
        username=auth.username,
        email=hashed_email,
        password=hashed_password,
        is_admin=False,
    )

    db.session.add(new_user)
    db.session.flush()

    new_edit = TestEdit(
        id=f"u{new_user.public_id}_t{0}",
        user_id=new_user.public_id,
        edit_no=0,
        edit_name="Standard"
    )
    db.session.add(new_edit)

    db.session.commit()

    return make_response(
        jsonify({'message': "User created."}),
        200,
    )
