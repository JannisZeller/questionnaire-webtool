from flask import Blueprint
from flask import redirect, render_template, make_response, url_for, jsonify
from flask import current_app, request

from flask_wtf import FlaskForm
from wtforms.fields import StringField
from wtforms.validators import Length

import requests

from .core import interface, interface_loggedin, call_api, get_user_info
from .core import API

from ..core.utils import hprint


account_bp = Blueprint("account_interface", __name__, template_folder="templates")


class NewTestEditForm(FlaskForm):
    edit_name = StringField(name="edit_name", validators=[Length(max=20)])


def load_existing_edits(active_edit_no: int) -> dict:
    test_edits: list[dict]
    res, test_edits = call_api(API.user_test_edits, "GET")
    for te in test_edits:
        te["edit_no"] = int(te["edit_no"])
        te["is_active"] = False
        if te["edit_no"] == active_edit_no:
            te["is_active"] = True
    test_edits.sort(key=lambda x: x["edit_no"])
    return test_edits


@account_bp.route("/account", methods=["GET", "POST"])
@interface_loggedin()
def account(cookies):
    """Interface-Route for account settings.
    """
    # User info
    userinfo = get_user_info()
    active_edit_no = int(userinfo["active_edit_no"])
    active_test_name = userinfo["active_test_name"]
    username = userinfo['username']

    # Existing edits
    test_edits = load_existing_edits(active_edit_no)

    # Forms and action urls
    new_te_form = NewTestEditForm()

    rename_tes_formdata = {}
    rename_url = API.rename_test_edit.url_for
    rename_url = url_for(rename_url)
    for te in test_edits:
        rename_te_formdata = {}
        rename_te_formdata["rename_url"] = rename_url
        rename_te_formdata["edit_name"] = te["edit_name"]
        rename_tes_formdata[te['edit_no']] = rename_te_formdata
    print(rename_tes_formdata)

    activate_urls = {
        te["edit_no"]: (url_for(
            API.set_active_edit_no.url_for, edit_no=te['edit_no'],
        ))
        for te in test_edits
    }

    delete_urls = {
        te["edit_no"]: (url_for(
            API.delete_test_edit.url_for, edit_no=te['edit_no'],
        ))
        for te in test_edits
    }

    if new_te_form.validate_on_submit():
        _ = requests.request(
            method="POST",
            url=url_for(API.test_edit.url_for, _external=True),
            cookies=request.cookies.to_dict(),
            json={"edit_name": request.form["edit_name"]}
        )
        test_edits = load_existing_edits(active_edit_no)
        return redirect(request.referrer)

    return render_template(
        "pages/loggedin/account.html",
        active_edit_no=active_edit_no,
        active_test_name=active_test_name,
        name=username,
        test_edits=test_edits,
        new_te_form=new_te_form,
        activate_urls=activate_urls,
        delete_urls=delete_urls,
        rename_tes_formdata=rename_tes_formdata,
    )


@account_bp.route("/delete_user", methods=["GET"])
@interface
def delete_user(cookies):
    """Interface-Route for account deletion-request for the interface.
    Passes the deletion-request on to the api. Deletes the JWT-cookie if
    sucessfully deleted the user and redirects to base.
    """
    res, data = call_api(API.delete_current_user, "DELETE")

    if res.status_code == 200:
        browser_res = make_response(redirect("/"))

        key = current_app.config['JWT_COOKIE_KEY']
        browser_res.delete_cookie(key)

        return browser_res
