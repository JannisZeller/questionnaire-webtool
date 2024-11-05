from flask import Blueprint, Response
from flask import jsonify, make_response
from flask import current_app, request

from sqlalchemy.exc import IntegrityError

from smtplib import SMTP
from email.message import EmailMessage

from werkzeug.security import generate_password_hash, check_password_hash
import string
import secrets

from .core.database import db

from .core.dbmodels import User, Reset
from .core.cookies import (
    construct_user_jwt,
    add_jwt_cookie,
    jwt_required,
    cconsent_required,
    hash_string,
)

from ..core.utils import hprint


auth_bp = Blueprint("auth", __name__, template_folder="templates")




@auth_bp.route("/cuser", methods=["GET"])
@jwt_required
def cuser(current_user: User) -> Response:
    """Returns the currently logged in username and public_id.
    - JWT required from current login
    - HTTP - Status-Codes: 200, 401, 403, 410
    """
    res = jsonify({
        'public_id': current_user.public_id,
        'username': current_user.username,
        'active_edit_no': current_user.active_edit_no,
    })
    res.status_code = 200
    return res


@auth_bp.route("/renew_token", methods=["GET"])
@cconsent_required
@jwt_required
def renew_token(current_user) -> Response:
    """"Renews the login JWT and sends a corresponting response setting the
    cookie.
    - Consent cookie required to store the new JWT cookie
    - JWT required from current login
    - HTTP - Status-Codes: 200, 401, 403, 410, 412
    """
    token = construct_user_jwt(current_user)
    res = jsonify({'token_generated': True})
    res = add_jwt_cookie(res, token)
    res.status_code = 200
    return res


@auth_bp.route("/login", methods=["POST"])
@cconsent_required
def login() -> Response:
    """"User login via request.authorization.
    - Consent cookie required to store the JWT cookie
    - HTTP - Status-Codes: 200, 401, 412
    """

    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response(
            "Could not verify",
            401,
            {'WWW-Authenticate': 'Basic realm="Login required"'},
        )

    user: User = User.query.filter_by(username=auth.username).first()

    if not user:
        return make_response(
            "Could not verify",
            401,
            {'WWW-Authenticate': 'Basic realm="No such user"'},
        )

    if check_password_hash(user.password, auth.password):
        token = construct_user_jwt(user)
        res = jsonify({'token_generated': True})
        res = add_jwt_cookie(res, token)
        res.status_code = 200
        return res

    return make_response(
        "Could not verify",
        401,
        {'WWW-Authenticate': 'Basic realm="Wrong password"'},
    )


@auth_bp.route("/logout", methods=["GET"])
@cconsent_required
@jwt_required
def logout(current_user: User) -> Response:
    """"User logout.
    - JWT required from current login
    - HTTP - Status-Codes: 200, 401, 403, 410, 412
    """
    key = current_app.config['JWT_COOKIE_KEY']

    res = jsonify({'message': "Logging out"})
    res.delete_cookie(key)
    res.status_code = 200
    return res


@auth_bp.route("/request_account_reset", methods=["POST"])
@cconsent_required
def request_account_reset() -> Response:
    """"Account-reset request: Sends an E-Mail with a reset link if E-Mail
    address passed is in database.
    - Consent cookie required to allow sending an E-Mail to the adress passed.
    - HTTP - Status-Codes: 200, 404, 412
    """

    data = request.get_json()
    reciever_addr = data['email']

    # Checking email adress
    hashed_email = hash_string(reciever_addr)
    user: User = User.query.filter_by(email=hashed_email).first()
    if not user:
        return make_response(
            jsonify({'message': "No account with this E-Mail"}),
            404,
        )

    # Constructing reset code and token
    def add_reset_code() -> str:
        reset_code = ''.join(secrets.choice(
            string.ascii_uppercase + string.digits
        ) for _ in range(10))
        hashed_reset_code = hash_string(reset_code)

        existing_reset: Reset = Reset.query.filter_by(user_id=user.public_id).first()
        if existing_reset:
            print("Removing duplicated user-resets.")
            db.session.delete(existing_reset)
            db.session.commit()

        reset: Reset = Reset(
            user_id=user.public_id,
            hashed_reset_code=hashed_reset_code,
        )

        db.session.add(reset)
        db.session.commit()
        return reset_code

    try:
        reset_code = add_reset_code()
    except IntegrityError:
        reset_code = add_reset_code()
        print("Reset code already active, generating new one.")

    # Sending mail
    sender_addr = "no-reply@fdw-assessment.edu"

    msg = EmailMessage()
    msg['Subject'] = "FDW-Assessment Account Zurücksetzen"
    msg['From'] = f"FDW-Assessment <{sender_addr}>"
    msg['To'] = reciever_addr
    msg.set_content(
        "Bitte nutzen Sie den Code am Ende dieser E-Mail um Ihren Account " +
        "zurückzusetzen. Der Code ist 10 Minuten gültig.\n\n" +
        # "Der Link zum zurücksetzen von Accounts lautet:" +
        # f" https://{current_app.config['DEV_DOMAIN']}/user_reset.\n\n" + # TODO: Correct link
        f"Reset-Code:  {reset_code}"
    )

    with SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(
            current_app.config["GMAIL_ADDRESS"],
            current_app.config["GMAIL_PW"],
        )
        # smtp.sendmail(sender_addr, reciever_addr, msg.encode("utf-8"))
        smtp.send_message(msg)
        hprint("/api/auth: Reset Mail sent.")

    return make_response(
        jsonify({'message': "E-Mail sent."}),
        200,
    )


@auth_bp.route("/account_reset", methods=["PUT"])
@cconsent_required
def account_reset() -> Response:
    """"Account-reset: Takes the request containing new username and/or
    password as a HTTP-basic auth header and the reset-code as data. If the
    reset code is
    - Consent cookie required to allow sending an E-Mail to the adress passed.
    - HTTP - Status-Codes: 200, 401, 409, 410, 412
    """

    # Validate reset_code
    data = request.get_json()
    reset_code = data['reset_code']
    hashed_reset_code = hash_string(reset_code)

    reset: Reset = Reset.query.filter_by(hashed_reset_code=hashed_reset_code).first()
    if reset is None:
        return make_response(
            jsonify({'message': "Reset token invalid"}),
            401,
        )
    if reset.is_expired():
        return make_response(
            jsonify({'message': "Reset token expired"}),
            410,
        )

    # Retrieving resetting user
    user_id = reset.user_id
    resetting_user: User = User.query.filter_by(public_id=user_id).first()

    # Getting new password and username
    auth = request.authorization
    username = auth.username.strip()

    # Updating user
    if username != "":
        # Validate new username
        user_with_name: User = User.query.filter_by(username=username).first()
        if user_with_name is not None and resetting_user != user_with_name:
            return make_response(
                jsonify({'username_exists': True}),
                409,
            )
        resetting_user.username = username
    if auth.password != "":
        resetting_user.password = generate_password_hash(
            auth.password,
            method="scrypt",
        )
    db.session.commit()

    # Dropping reset code
    db.session.delete(reset)
    db.session.commit()

    return make_response(
        jsonify({'message': "User information updated."}),
        200,
    )


@auth_bp.route("/resets", methods=["GET"])
def get_all_resets() -> Response:
    """ADMIN-ROUTE: Viewing all active reset-codes.
    - HTTP - Status-Codes: 200
    """

    # TODO: Only for admins
    # if not current_user.is_admin:
    #     return jsonify({"message": "Only for admins."})

    resets: list[Reset] = Reset.query.all()
    output = [reset.as_dict() for reset in resets]

    for reset in resets:
        print(reset.is_expired())
    return make_response(
        jsonify({"resets": output}),
        200,
    )
