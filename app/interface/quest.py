import pandas as pd

from flask import Blueprint
from flask import render_template, url_for
from flask import request

from wtforms.fields import TextAreaField, BooleanField, FileField

from .core import API, AJAXForm
from .core import call_api, interface_loggedin, get_user_info

from ..core.data import View
from ..core.data import questionnaire


quest_bp = Blueprint("quest_interface", __name__, template_folder="templates")



class openForm(AJAXForm):
    response_text = TextAreaField(name="response")

class MCForm(AJAXForm):
    yesbox = BooleanField(name="1")
    nobox = BooleanField(name="0")

class ImageForm(AJAXForm):
    image_data: bytes = None
    image = FileField(name="image")



def build_forms(view: View) -> dict[str, openForm|MCForm]:
    """Builds a suitable list of forms to pass to the respective template for
    each questionnaire view.
    """
    forms = {}
    for task in view.tasks:
        for item in task.items:
            # No "_external=True". Otherwise the AJAX requests will be cross-
            #   origin and lead to CORS-issues. When properly separating front-
            #   and backend, use a reverse proxy.
            action_url = (
                url_for(
                    API.response.url_for, # _external=True,
                    view_id=view.id, task_id=task.id, item_id=item.id
                )
            )
            kwargs = {'action_url': action_url, 'prefix': item.id}
            if task.task_type == "text":
                form = openForm(**kwargs)
            if task.task_type == "mc":
                form = MCForm(**kwargs)
            if task.task_type == "image":
                form = ImageForm(**kwargs)
            forms[item.id] = form
    return forms


def users_current_responses(cookies: dict) -> pd.DataFrame:
    """Retrieves the current user's (via cookies) current responses to the
    questionnaire.
    """
    res, data = call_api(API.user_responses, "GET")

    user_responses = [
        response
        for response_lists in data.values()
        for response in response_lists
    ]

    df_ur = pd.DataFrame(user_responses)
    return df_ur


def prepopulate_forms(
        view: View,
        df_ur: pd.DataFrame,
        forms: dict[str, openForm|MCForm],
    ):
    """Populates forms with the users current responses
    """
    view_id = view.id
    if df_ur.size <= 0:
        return forms

    df_ur_cview = df_ur[df_ur['view_id'] == view_id][['item_id', 'response']]
    if df_ur_cview.size <= 0:
        return forms

    worked_items = df_ur_cview['item_id'].to_list()
    for key, form in forms.items():
        if key in worked_items:
            msk = df_ur_cview['item_id'] == key
            response = df_ur_cview['response'][msk].to_list()[0]
            if isinstance(form, openForm):
                form.response_text.data = response
            if isinstance(form, MCForm):
                form.yesbox.data = response
                form.nobox.data  = response is False
            if isinstance(form, ImageForm):
                form.image_data = response
    return forms


def surrounding_views(view_id: str) -> tuple[str, str]:
    """Gets the names / ids of the previous and next views.
    """
    previous_view_idx = int(view_id.removeprefix("A")) - 1
    next_view_idx = int(view_id.removeprefix("A")) + 1
    previous_view = f"A{previous_view_idx}" if previous_view_idx > 0 else None
    next_view = f"A{next_view_idx}" if next_view_idx < 25 else None
    return previous_view, next_view


def views_progress(views: dict, df_ur: pd.DataFrame) -> dict:
    """Alters the "progress"-status of the `views`-dict based on the users
    current responses `df_ur` (passed as a `pd.DataFrame`).
    """
    if df_ur.size <= 0:
        return views
    for view_id, specs in views.items():
        df_ur_cview: pd.DataFrame = df_ur[df_ur['view_id'] == view_id]
        if df_ur_cview.size > 0:
            cview = questionnaire[view_id]
            if cview.n_items() == df_ur_cview.shape[0]:
                specs['progress'] = "finished"
            else:
                specs['progress'] = "some"
    return views


@quest_bp.route("/quest/", methods=["GET", "POST"])
@quest_bp.route("/quest/<view_id>", methods=["GET", "POST"])
@interface_loggedin()
def quest(cookies, view_id: str=None):
    # Active test info
    user_info = get_user_info()
    active_edit_no = int(user_info["active_edit_no"])
    active_test_name = user_info["active_test_name"]

    # Initializting the views-dict
    views = questionnaire.asdict()

    # Getting current responses
    df_ur = users_current_responses(cookies)

    # Views progress
    views_progress(views, df_ur)

    # Render wrapper
    def render(**kwargs):
        return render_template(
            "pages/loggedin/quest.html",
            active_edit_no=active_edit_no,
            active_test_name=active_test_name,
            views=views,
            **kwargs,
        )

    if view_id is None:
        return render(next_view="A1")

    if view_id not in questionnaire:
        return render(task_missing=True)

    # Opening necessairy forms
    view: View = questionnaire[view_id]
    forms = build_forms(view)

    # Pre-Populating forms
    if request.method == "GET":
        forms = prepopulate_forms(view, df_ur, forms)

    # Current, next, & previous views
    views[view_id]['is_active'] = True
    previous_view, next_view = surrounding_views(view_id)

    return render(
        current_view=view_id,
        previous_view=previous_view,
        next_view=next_view,
        forms=forms,
    )
