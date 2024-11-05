from flask import Blueprint
from flask import request
from flask import jsonify, make_response
from sqlalchemy import delete

import base64
import numpy as np
from PIL import Image
from io import BytesIO

from pathlib import Path

from .core.database import db
from .core.dbmodels import (
    Responses,
    TextResponse,
    MCResponse,
    ImageResponse,
    User,
)
from .core.cookies import jwt_required, cconsent_required

from ..core.utils import hprint


response_bp = Blueprint("response", __name__, template_folder="templates")


def process_open_response(
    response: str,
    current_user: User,
    view_id: str,
    task_id: str,
    item_id: str,
):
    response = response.strip()
    response_is_empty = response == ""

    unique_id = f"u{current_user.public_id}_tst{current_user.active_edit_no}_i{item_id}"
    old_response: TextResponse = TextResponse.query.filter_by(id=unique_id).first()

    if old_response and (response_is_empty or request.method == "DELETE"):
        try:
            db.session.delete(old_response)
            db.session.commit()
            return make_response(
                jsonify({'message': f"Response {unique_id} deleted"}),
                200,
            )
        except Exception as e:
            return make_response(
                jsonify( {'message': f"There was an error deleting response {unique_id}: {e}"} ),
                500,
            )

    if old_response:
        hprint(f"/response: ID already exists, updating entry {unique_id}.")
        db.session.delete(old_response)
        db.session.commit()

    if not response_is_empty:
        new_response = TextResponse(
            id=unique_id,
            item_id=item_id,
            task_id=task_id,
            view_id=view_id,
            user_id=current_user.public_id,
            edit_no=current_user.active_edit_no,
            response=response,
        )
        try:
            db.session.add(new_response)
            db.session.flush()
            db.session.commit()
            print("success")
            return make_response(
                jsonify({'message': f"Response {unique_id} added"}),
                200,
            )
        except Exception as e:
            return make_response(
                jsonify( { 'message': f"There was an error adding response {unique_id}: {e}"} ),
                500,
            )

    if response_is_empty:
        return make_response(
            jsonify( {'message': f"No response to be added as {unique_id}"} ),
            200,
        )


def process_mc_response(
    response: bool,
    current_user: User,
    view_id: str,
    task_id: str,
    item_id: str,
):

    unique_id = f"u{current_user.public_id}_tst{current_user.active_edit_no}_i{item_id}"
    old_response: MCResponse = MCResponse.query.filter_by(id=unique_id).first()

    if old_response:
        db.session.delete(old_response)

        if old_response.response == response:
            try:
                db.session.commit()
                return make_response(
                    jsonify( {'message': f"Deleted response {unique_id}"} ),
                    200,
                )
            except Exception as e:
                return make_response(
                    jsonify( {'message': f"There was an error deleting response {unique_id}: {e}"} ),
                    500,
                )

    new_response = MCResponse(
        id=unique_id,
        item_id=item_id,
        task_id=task_id,
        view_id=view_id,
        user_id=current_user.public_id,
        edit_no=current_user.active_edit_no,
        response=response,
    )
    try:
        db.session.add(new_response)
        db.session.commit()
    except Exception as e:
        return make_response(
            jsonify( {'message': f"There was an error updating response {unique_id}: {e}"} ),
            500,
        )

    return make_response(
        jsonify({'message': f"Updated response {unique_id}"}),
        200,
    )


def process_image_response(
        response: str,
        current_user: User,
        view_id: str,
        task_id: str,
        item_id: str,
    ):

    unique_id = f"u{current_user.public_id}_tst{current_user.active_edit_no}_i{item_id}"
    old_response: ImageResponse = ImageResponse.query.filter_by(id=unique_id).first()

    response = response.removeprefix("data:image/png;base64,")
    response = base64.decodebytes(str.encode(response))

    image_array = np.array(Image.open(BytesIO(response)))
    response_is_empty = np.mean(image_array) == 0

    # TODO: Dev purposes
    img_path = Path(f"./dev/image_{current_user.username}_{item_id}.png")
    if not response_is_empty:
        with open(img_path, "wb") as fh:
            hprint(f"Saving image {img_path}")
            fh.write(response)
    else:
        hprint(f"Deleting {img_path} if it exists")
        try:
            img_path.unlink()
        except FileNotFoundError:
            pass


    if old_response and (response_is_empty or request.method == "DELETE"):
        try:
            db.session.delete(old_response)
            db.session.commit()
            return make_response(
                jsonify({'message': f"Response {unique_id} deleted"}),
                200,
            )
        except Exception as e:
            return make_response(
                jsonify( {'message': f"There was an error deleting response {unique_id}: {e}"} ),
                500,
            )

    if old_response:
        hprint(f"/response: ID already exists, updating entry {unique_id}.")
        db.session.delete(old_response)

    if not response_is_empty:
        new_response = ImageResponse(
            id=unique_id,
            item_id=item_id,
            task_id=task_id,
            view_id=view_id,
            user_id=current_user.public_id,
            edit_no=current_user.active_edit_no,
            response=response,
        )
        try:
            db.session.add(new_response)
            db.session.commit()
            return make_response(
                jsonify({'message': f"Response {unique_id} added"}),
                200,
            )
        except Exception as e:
            return make_response(
                jsonify( {'message': f"There was an error adding response {unique_id}: {e}"} ),
                500,
            )

    if response_is_empty:
        return make_response(
            jsonify( {'message': f"No response to be added as {unique_id}"} ),
            200,
        )



@response_bp.route("/response/<view_id>/<task_id>/<item_id>", methods=["POST", "DELETE"])
@jwt_required
@cconsent_required
def response_(current_user: User, view_id: str, task_id: str, item_id: str):
    data = request.get_json()
    item_type = data["item_type"]
    response = data["response"]

    if item_type == "text":
        return process_open_response(response, current_user, view_id, task_id, item_id)

    elif item_type == "mc":
        return process_mc_response(response, current_user, view_id, task_id, item_id)

    elif item_type == "image":
        return process_image_response(response, current_user, view_id, task_id, item_id)

    else:
        return make_response(
            jsonify( {'message': "The item type passed is undefined; it must be `text` or `mc`."} ),
            422,
        )


@response_bp.route("/response_json", methods=["POST", "DELETE"])
@jwt_required
@cconsent_required
def response_json(current_user: User):
    data = request.get_json()
    item_id  = data["item_id"]
    task_id  = data["task_id"]
    view_id  = data["view_id"]
    response_(current_user, view_id, task_id, item_id)


@response_bp.route("/user_responses", methods=["GET"])
@jwt_required
def user_responses(current_user: User):
    responses_dict = Responses.user_dicts(current_user.public_id, current_user.active_edit_no)
    return make_response(
        jsonify(responses_dict),
        200,
    )






#TODO: Dev route
@response_bp.route("/responses", methods=["GET"])
def responses():
    responses_dict = Responses.all_dicts()
    return make_response(
        jsonify(responses_dict),
        200,
    )

#TODO: Dev route
@response_bp.route("/all_user_responses", methods=["GET"])
@jwt_required
def all_user_responses(current_user: User):
    responses_dict = Responses.user_dicts(current_user.public_id)
    return make_response(
        jsonify(responses_dict),
        200,
    )

#TODO: Dev route
@response_bp.route("/user_res_pandas", methods=["GET", "POST"])
@jwt_required
def user_res_pandas(current_user: User):
    """Prompts the generation of the report data for the current_user, i.e.,
    kicks of the scoring
    - HTTP - Status-Codes: 401, 403, 410, 200
    """
    user_id = current_user.public_id
    active_edit_no = current_user.active_edit_no

    dfs_res = Responses.user_pandas(user_id, edit_no=active_edit_no)

    print(dfs_res["text_responses"])


    return make_response(
        jsonify( {"message": "user pandas printed"} ),
        201,
    )


# TODO:
# @response_bp.route("/response/delete", methods=["POST"])
# def delete_person():
#     try:
#         user_id = request.form["user_id"]
#         delete_op = delete(Response).where(Response.user_id==user_id)
#         db.session.execute(delete_op)
#         db.session.commit()
#         return redirect("/")
#     except Exception as e:
#         return (
#             "There was an issue deleting the records for the person " +
#             f"id {user_id}: {e}"
#         )
