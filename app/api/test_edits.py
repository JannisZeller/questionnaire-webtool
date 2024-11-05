from flask import Blueprint, Response
from flask import jsonify, make_response
from flask import current_app, request

from sqlalchemy import text

from .core.database import db
from .core.dbmodels import User, TestEdit, Responses, Score
from .core.cookies import jwt_required


test_edits_bp = Blueprint("test_edits", __name__, template_folder="templates")


# TODO: Remove "GET"
@test_edits_bp.route("/test_edit/", methods=["POST"])
@jwt_required
def test_edit(current_user: User):
    public_id = current_user.public_id
    data = request.get_json()
    edit_name = data["edit_name"]

    max_ex_edits = db.session.execute(text(
        f"SELECT MAX(edit_no) FROM test_edit WHERE user_id={public_id}"
    )).all()[0][0]
    print(max_ex_edits)

    edit_no = int(max_ex_edits)+1
    new_te = TestEdit(
        id=f"u{public_id}_t{edit_no}",
        user_id=public_id,
        edit_no=edit_no,
        edit_name=edit_name,
    )
    db.session.add(new_te)
    db.session.commit()

    print(f"Set up test-edit 'u{public_id}_t{edit_no}' ({edit_name})")

    return make_response(jsonify({
        "message": f"Set up test-edit 'u{public_id}_t{edit_no}' ({edit_name})"
    }), 200)


# TODO: Refine
@test_edits_bp.route("/user_test_edits/", methods=["GET"])
@jwt_required
def user_test_edits(current_user: User):
    public_id = current_user.public_id
    test_edits: list[TestEdit] = TestEdit.query.filter_by(user_id=public_id).all()
    return make_response(jsonify([te.as_dict() for te in test_edits]), 200)


# TODO: Refine
@test_edits_bp.route("/delete_test_edit/<edit_no>", methods=["DELETE"])
@jwt_required
def delete_test_edit(current_user: User, edit_no: str):
    public_id = current_user.public_id
    edit_no = int(edit_no)

    if edit_no == 0:
        return make_response(jsonify({
            'message': "The default edit with edit no 0 might not be deleted.",
        }), 403)

    # Delete connected data
    _ = [
        response_class.query.filter_by(user_id=public_id, edit_no=edit_no).delete()
        for response_class in Responses.res_classes
    ]
    _ = Score.query.filter_by(user_id=public_id, edit_no=edit_no).delete()

    # Get edit name
    te: TestEdit = TestEdit.query.filter_by(user_id=public_id, edit_no=edit_no).first()
    edit_name = te.edit_name

    # Delete edit
    db.session.delete(te)

    # Activate default edit if necessary
    if current_user.active_edit_no == edit_no:
        current_user.active_edit_no = 0

    db.session.commit()

    return make_response(jsonify({
        "message": f"Deleted test-edit 'u{public_id}_t{edit_no}' ({edit_name})",
        "deleted_edit_no": edit_no,
    }), 200)


@test_edits_bp.route("/rename_test_edit/", methods=["PUT"])
def rename_test_edit():
    data = request.get_json()
    edit_no = data["edit_no"]
    new_edit_name = data["new_edit_name"]

    test_edit: TestEdit = TestEdit.query.filter_by(edit_no=edit_no).first()
    old_edit_name = test_edit.edit_name
    test_edit.edit_name = new_edit_name
    db.session.commit()

    return make_response(jsonify({
        "message": f"Renamed TE{edit_no} from \"{old_edit_name}\" to \"{new_edit_name}\"",
        "old_edit_name": old_edit_name,
        "new_edit_name": new_edit_name,
    }), 200)


# TODO: dev route
@test_edits_bp.route("/test_edits/", methods=["GET"])
def test_edits():
    test_edits: list[TestEdit] = TestEdit.query.all()
    output = [te.as_dict() for te in test_edits]
    return make_response(jsonify({"test edits": output}), 200)
