from flask import Blueprint, Response
from flask import jsonify, make_response
from flask import current_app

from .core.database import db
from .core.dbmodels import User, TestEdit, Responses, Score, Reset
from .core.cookies import jwt_required

from ..core.utils import hprint


user_bp = Blueprint("user", __name__, template_folder="templates")


@user_bp.route("/user", methods=["GET"])
def get_all_users() -> Response:
    """ADMIN-ROUTE: Display all users
    - HTTP - Status-Codes: 200
    """
    # TODO: Dev route

    # TODO: Only for admins
    # if not current_user.is_admin:
    #     return jsonify({"message": "Only for admins."})
    users: list[User] = User.query.all()
    output = [user.as_dict() for user in users]
    return make_response(jsonify({"users": output}), 200)


# TODO:
# @user_bp.route("/user/<public_id>", methods=["PUT"])
# def promote_user(public_id: str) -> Response:

#     # if not current_user.is_admin:
#     #     return jsonify({"message": "Only for admins."})

#     user: User = User.query.filter_by(public_id=public_id).first()
#     if not user:
#         return jsonify({"message": "No user found."})

#     user.is_admin = True
#     db.session.commit()

#     return jsonify({"message": f"User {user.name} has been promoted to admin."})


@user_bp.route("/user_info", methods=["GET"])
@jwt_required
def user_info(current_user: User):
    user_name = current_user.username
    public_id = current_user.public_id
    active_edit_no = current_user.active_edit_no

    active_test_edit: TestEdit = (TestEdit
        .query
        .filter_by(user_id=public_id, edit_no=active_edit_no)
        .first()
    )
    active_test_name = active_test_edit.edit_name
    return make_response(
        jsonify({
            "username": user_name,
            "public_id": public_id,
            "active_edit_no": active_edit_no,
            "active_test_name": active_test_name,
        }),
        200,
    )



@user_bp.route("/user/<public_id>", methods=["DELETE"])
@jwt_required
def delete(current_user: User, public_id: str):
    """Route for user deletion.
    - JWT required for authentication. Non-admin users can only delete
    themselves.
    - HTTP - Status-Codes: 200, 401, 403, 410
    """
    if not (current_user.is_admin or current_user.public_id==public_id):
        return make_response(
            jsonify({"message": "Only admins can delete accounts, which are not themselves"}),
            401,
        )

    # Getting user
    user: User = User.query.filter_by(public_id=public_id).first()
    if not user:
        return make_response(
            jsonify({"message": "No user found."}),
            404,
        )

    # Delete connected data
    _ = [
        response_class.query.filter_by(user_id=public_id).delete()
        for response_class in Responses.res_classes
    ]
    _ = TestEdit.query.filter_by(user_id=public_id).delete()
    _ = Score.query.filter_by(user_id=public_id).delete()
    _ = Reset.query.filter_by(user_id=public_id).delete()

    db.session.delete(user)
    db.session.commit()

    return make_response(
        jsonify({"message": f"Deleted user {user.username}."}),
        200,
    )


@user_bp.route("/delete_current_user/", methods=["DELETE"])
@jwt_required
def delete_current_user(current_user: User):
    """Route for current user deletion.
    - JWT required for authentication. Non-admin users can only delete
    themselves.
    - HTTP - Status-Codes: 204, 401, 403, 410, 412
    """
    delete(current_user.public_id)

    res = jsonify({'message': "Deleted current user.", 'user_deleted': True})

    key = current_app.config['JWT_COOKIE_KEY']
    res.delete_cookie(key)
    res.status_code = 204

    return res


# TODO: remove "GET"
@user_bp.route("/set_active_edit_no/<edit_no>", methods=["POST"])
@jwt_required
def set_active_edit_no(current_user: User, edit_no: int):
    """Route for switching the active test of a user by its `edit_no`,
    i.e., the test number.
    - JWT required for authentication.
    - HTTP - Status-Codes: 200, 401, 403, 410, 412
    """
    current_user.active_edit_no = edit_no
    db.session.commit()

    data = user_info()
    data = data.get_json()

    return make_response(
        jsonify({
            "message": f"User: {data['public_id']} - active test no: {data['active_edit_no']}.",
            "active_test_name": data["active_test_name"],
            "active_edit_no": data["active_edit_no"],
        }),
        200,
    )
