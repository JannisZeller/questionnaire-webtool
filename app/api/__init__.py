from flask import Response

from typing import Callable

from .auth import auth_bp
from .auth import (
    cuser, login, logout, renew_token, request_account_reset, account_reset
)

from .response import response_bp
from .response import user_responses, response_

from .user import user_bp
from .user import delete_current_user, user_info, set_active_edit_no

from .signup import signup_bp
from .signup import check_username, check_email, signup_

from .consent import consent_bp
from .consent import consent_

from .report import report_bp
from .report import report_, generate_report_data

from .test_edits import test_edits_bp
from .test_edits import user_test_edits, test_edit, delete_test_edit, rename_test_edit

blueprints = [
    auth_bp,
    user_bp,
    response_bp,
    signup_bp,
    consent_bp,
    report_bp,
    test_edits_bp,
]


class APIMethod():
    def __init__(self, fun: Callable[[], Response], url_for: str):
        self.kernel = fun
        self.url_for = url_for

    def __call__(self, *args, **kwargs) -> Response:
        return self.kernel(*args, **kwargs)


class API:
    cuser = APIMethod(cuser, "auth.cuser")

    signup = APIMethod(signup_, "signup.signup_")

    login = APIMethod(login, "auth.login")

    user_info = APIMethod(user_info, "user.user_info")

    delete_current_user = APIMethod(delete_current_user, "user.delete_current_user")

    logout = APIMethod(logout, "auth.logout")

    renew_token = APIMethod(renew_token, "auth.renew_token")

    consent = APIMethod(consent_, "consent.consent_")

    user_test_edits = APIMethod(user_test_edits, "test_edits.user_test_edits")

    set_active_edit_no = APIMethod(set_active_edit_no, "user.set_active_edit_no")

    test_edit = APIMethod(test_edit, "test_edits.test_edit")

    rename_test_edit = APIMethod(rename_test_edit, "test_edits.rename_test_edit")

    delete_test_edit = APIMethod(delete_test_edit, "test_edits.delete_test_edit")

    user_responses = APIMethod(user_responses, "response.user_responses")

    response = APIMethod(response_, "response.response_")

    check_username = APIMethod(check_username, "signup.check_username")

    check_email = APIMethod(check_email, "signup.check_email")

    request_account_reset = APIMethod(request_account_reset, "auth.request_account_reset")

    account_reset = APIMethod(account_reset, "auth.account_reset")

    report = APIMethod(report_, "report.report_")

    generate_report_data = APIMethod(generate_report_data, "report.generate_report_data")
