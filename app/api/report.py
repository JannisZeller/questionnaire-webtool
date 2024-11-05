from flask import Blueprint
from flask import jsonify, make_response

import pandas as pd

import app.api.core.qutools as qutools

from .core.cookies import jwt_required
from .core.database import db
from .core.dbmodels import Responses, User, Score
from .core.models import Scorer, Regressor, Clusterer
from .core.models import get_model_instances

from ..config import load_env_json

from ..core.utils import hprint


report_bp = Blueprint("report", __name__, template_folder="templates")

scorer, regressor, clusterer = get_model_instances()

# A1a.: Der Lehrer wechselt zu schnell von der einfachen Gleichgewichtssituation zu einer dynamischen Bewegungssituation. Dieser Wechsel würde eine strukturiertere Betrachtung der Kräfte erfordern.
# A1b.1: Es wirkt immer eine Kraft in Bewegunsrichtung
# A1b.2: Verwechslung von Kräftegleichgewicht und drittem newtonschen Axiom


# TODO: dev route
@report_bp.route("/user_scores", methods=["GET", "POST"])
@jwt_required
def user_scores(current_user: User):
    # df = Score.user_pandas(current_user.public_id, current_user.active_edit_no)
    # if df.shape[0] > 0:
    #     ret = df.to_html()
    #     return make_response(ret)
    scores = Score.user_scorelist(current_user.public_id, current_user.active_edit_no)
    if len(scores) > 0:
        return make_response(jsonify(scores))
    return make_response(jsonify({'message': "No scores available."}))



def store_scores(df: pd.DataFrame, user_id: int, edit_no: int) -> None:
    """Stores the scores, passed as a pd.DataFrame in the database.
    Automatically overwrites existing scores.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing an ID-column and a column for each questionnaire
        task.
    user_id : int
        The user-id (User.public_id) of the user, the scores belong to.
    """

    for task in df.drop(columns="ID").columns:
        id = f"u{user_id}_tst{edit_no}_tsk{task}"

        old_score: Score = Score.query.filter_by(id=id).first()
        if old_score:
            db.session.delete(old_score)
            db.session.commit()

        score_ = df[task].values[0]
        score = Score(
            id=id,
            task_id=task,
            user_id=user_id,
            edit_no=edit_no,
            score=int(score_),
        )
        db.session.add(score)

    db.session.commit()


def compute_scores(user_id: int, edit_no: int) -> None:
    """Computes the scores for the user belonging to the passed id. Empty
    responses are scored as 0-points. Uses the pck-tooling functionality that
    is part of the api.core modules.

    Parameters
    ----------
    user_id : int
        The user-id (User.public_id) of the user, to be scored.
    """
    # Retrieve Responses
    dfs_res = Responses.user_pandas(user_id, edit_no=edit_no)

    # Multiple Choice Items
    df_mc = dfs_res["mc_responses"]
    if df_mc.size > 0:
        # retrieving
        df_mc = df_mc.rename(columns={"item_id": "item"})
        df_mc = df_mc[["item", "response"]]
        df_mc = qutools.item_dots(df_mc, "item")
        df_mc = qutools.pivot_mc_item_df(df_mc)

        # scoring
        df_mc = qutools.score_mc_items(df_mc)
        df_mc = qutools.score_mc_tasks(df_mc)
        df_mc["ID"] = "id"
    else:
        df_mc = qutools.df_mc_zero()

    # Text Items
    df_text = dfs_res["text_responses"]
    if df_text.size > 0:
        # retrieving
        df_text = df_text.rename(columns={"item_id": "item", "response": "text"})
        df_text = df_text[["item", "text"]]
        df_text = qutools.item_dots(df_text, "item")

        # cleaning
        df_text["text"] = df_text["text"].map(qutools.whitespace_remover)
        df_text["text"] = df_text["text"].map(qutools.abbreviations_replacer)
        df_text["text"] = df_text["text"].map(qutools.empty_aliases_remover)

        # preprocessing
        df_text = qutools.pivot_text_item_df(df_text)
        df_text = qutools.concat_taskwise(df_text)
        df_text = qutools.melt_tasks(df_text)
        df_text = qutools.drop_empty(df_text)
        df_text = qutools.add_item_names(df_text)

        # scoring
        if scorer is None:
            adhoc_scorer = Scorer()
            pred_scores = adhoc_scorer.predict(df_text["text"].to_list())
        else:
            pred_scores = scorer.predict(df_text["text"].to_list())
        df_text["predicted_scores"] = pred_scores
        df_text["ID"] = "id"

        # reshaping
        df_tscores = qutools.pivot_to_wide(df_text)
    else:
        df_tscores = qutools.df_text_zero()

    # Combine MC and Text Scores
    df = qutools.combinde_text_mc_cols(df_tscores, df_mc, merge_on="ID")

    return df




@report_bp.route("/generate_report_data", methods=["GET", "POST"])
@jwt_required
def generate_report_data(current_user: User):
    """Prompts the generation of the report data for the current_user, i.e.,
    kicks of the scoring
    - HTTP - Status-Codes: 401, 403, 410, 200
    """
    user_id = current_user.public_id
    edit_no = current_user.active_edit_no

    # Check last response time
    last_response_time = Responses.get_last_response_time(user_id, edit_no)

    # Check last report time
    last_report_time = Score.get_last_report_time(user_id, edit_no)

    no_report = last_report_time is None
    responses_avalable = last_response_time is not None
    if not no_report and responses_avalable:
        report_outdated = last_response_time > last_report_time

    if responses_avalable and (no_report or report_outdated):
        df = compute_scores(user_id, edit_no=edit_no)
        store_scores(df, user_id, edit_no)

        return make_response(
            jsonify( {'message': "Scoring finished."} ),
            201,
        )

    else:
        return make_response(
            jsonify( {'message': "No responses / Old report is still up to date."} ),
            201,
        )


@report_bp.route("/report", methods=["GET"])
@jwt_required
def report_(current_user: User):
    """Collects the previously generated report data for the current_user.
    - HTTP - Status-Codes: 401, 403, 410, 200, 204
    """
    user_id = current_user.public_id
    edit_no = current_user.active_edit_no

    scores: list[Score] = Score.query.filter_by(user_id=user_id, edit_no=edit_no).all()

    # Check last response time
    last_response_time = Responses.get_last_response_time(user_id, edit_no)

    # Check last report time
    last_report_time = Score.get_last_report_time(user_id, edit_no)

    # Return incomplete if not all scores for the user/edit_no are present
    if len(scores) < 27:
        return make_response(
            jsonify({
                'message': "Not all scores available.",
                'last_report': last_report_time,
                'last_response': last_response_time,
            }),
            204,
        )

    df = Score.user_pandas(user_id, edit_no)
    X = df.values

    if regressor is None:
        cnfg = load_env_json("./env/config.jsonc")
        regressor_mode = cnfg.get("DIMSCORES_MODE", "regression")
        adhoc_regressor = Regressor(regressor_mode)
        df_dimscores = adhoc_regressor.dimscores(X)
    else:
        df_dimscores = regressor.dimscores(X)
    df_dimscores = qutools.append_dimscore_infos(df_dimscores)

    if clusterer is None:
        adhoc_clusterer = Clusterer()
        clst = adhoc_clusterer.predict(X)
    else:
        clst = clusterer.predict(X)

    data = {
        "df_scores": df.to_json(),
        "df_dimscores": df_dimscores.to_json(),
        "cluster": clst,
        'last_report': last_report_time,
        'last_response': last_response_time,
    }

    return make_response(
        jsonify(data),
        200,
    )
