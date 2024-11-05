from flask import Response
from flask import jsonify, make_response
from flask import current_app, request

import jwt

import datetime as dt
from functools import wraps
from hashlib import sha256

from typing import Callable

from .dbmodels import User
from .time import utc_now



def construct_user_jwt(user: User) -> str:
    """Function to construct a JWT for user authentication.

    Parameters
    ----------
    user : User
        The user for whom the JWT should be constructed.
    """
    td = dt.timedelta(
        minutes=int(current_app.config['JWT_VALID_MINUTES']),
        seconds=int(current_app.config['JWT_VALID_SECONDS']),
    )
    expiration_ts = utc_now() + td
    token: str = jwt.encode(
        {'public_id': user.public_id, 'exp': expiration_ts},
        current_app.config['SECRET_KEY'],
        algorithm="HS256",
    )
    return token



def add_jwt_cookie(res: Response, token: str) -> Response:
    """"Function appending a JWT-cookie to a flask.Response.
    Potentiall add
    ```python
        res.headers.add("Access-Control-Allow-Origin", "*")
        res.headers.add("Access-Control-Allow-Credentials", True)
    ```
    in the future.

    Parameters
    ----------
    res : Response
        The flask.Response to which the JWT-cookie should be appended.
    token : str
        The JWT-token as a raw string as returned by
        "app.api.core.construct_user_jwt".
    """
    key = current_app.config['JWT_COOKIE_KEY']
    res.set_cookie(key, token, samesite="lax", secure=True)
    return res



def hash_string(s: str) -> str:
    """"Utility function to encode a UTF-8 encoded string, to a UTF-8 encoded
    sha256-hash.

    Parameters
    ----------
    s : str
    """
    return sha256(str.encode(s)).hexdigest()



def cconsent_required(f) -> Callable:
    """"Wrapper for routes requiring a consent for data privacy and alike. The
    consent must be passed as the 'CONSENT_COOKIE_KEY'-cookie.

    #### Possible Status-Codes
    - 412 if the consent cookie is not recieved or is not "1".
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        key = current_app.config['CONSENT_COOKIE_KEY']
        cookie_consent = request.cookies.get(key)

        if not cookie_consent:
            return make_response(
                jsonify({'message': "Consent cookie is not set"}),
                412,
            )

        if cookie_consent != "1":
            return make_response(
                jsonify({'message': "Consent cookie is not 1"}),
                412,
            )

        return f(*args, **kwargs)

    return decorated



def jwt_auth_core(f, *args, **kwargs):
    """The core utility of the @jwt_required and @jwt_required_no_refresh
    decorators. Checks for and validates the JWT-cookie and calls the decorated
    function if the validation is successful. Sends error flask.Responses in
    case of faliure with the following codes:

    #### Possible Status-Codes
    - 401 if the JWT-cookie is missing.
    - 410 if the JWT-cookie has expired.
    - 403 if the JWT-cookie is invalid.
    """
    key = current_app.config['JWT_COOKIE_KEY']
    token = request.cookies.get(key)

    if not token:
        res = make_response(
            jsonify({'message' : 'Token is missing!'}),
            401,
        )
        return res, None

    try:
        token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        res = make_response(
            jsonify({'message': 'Token expired!', 'token_expired': True}),
            410,
        )
        return res, None
    except jwt.InvalidTokenError:
        res = make_response(
            jsonify({'message': 'Token is invalid!'}),
            403,
        )
        return res, None

    current_user = User.query.filter_by(public_id=token['public_id']).first()
    if not current_user:
        res = jsonify({'message': 'User does not exist anymore'})
        res.delete_cookie(current_app.config['JWT_COOKIE_KEY'])
        res.status_code = 403
        return res, None

    res = f(current_user, *args, **kwargs)

    return res, current_user



def jwt_required(f) -> Callable[[], Response]:
    """JWT-validation wrapper that appends a new JWT to the sent response, i. e.
    refreshes the current login-session.

    #### Possible Status-Codes
    - 401 if the JWT-cookie is missing.
    - 410 if the JWT-cookie has expired.
    - 403 if the JWT-cookie is invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        res, current_user = jwt_auth_core(f, *args, **kwargs)
        if current_user is not None:
            new_token = construct_user_jwt(current_user)
            res = add_jwt_cookie(res, new_token)
        return res

    return decorated



def jwt_required_no_refresh(f) -> Callable[[], Response]:
    """JWT-validation wrapper without login-session refresh.

    #### Possible Status-Codes
    - 401 if the JWT-cookie is missing.
    - 410 if the JWT-cookie has expired.
    - 403 if the JWT-cookie is invalid.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        res, _ = jwt_auth_core(f, *args, **kwargs)
        return res

    return decorated
