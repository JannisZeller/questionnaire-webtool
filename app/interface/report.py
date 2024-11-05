from flask import Blueprint
from flask import render_template, make_response, jsonify
from flask import request

from io import StringIO

import pandas as pd

import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import use as mpl_use
from matplotlib.figure import Figure
from matplotlib.axes import Axes

import re

from .core import API, call_api, interface_loggedin, get_user_info

from ..core.utils import hprint


report_bp = Blueprint("report_interface", __name__, template_folder="templates")
mpl_use('agg')

def get_iamge_data(fig: Figure) -> str:
    buffer = StringIO()
    fig.savefig(buffer, format="svg", bbox_inches="tight")
    img_data = buffer.getvalue()
    del buffer
    img_data = re.sub(r"(<svg [^>]*)(width=\"\d+\.?\d+(?:pt|%)\")([^>]*>)", r'\1width="100%"\3', img_data)
    img_data = re.sub(r"(<svg [^>]*)(height=\"\d+\.?\d+(?:pt|%)\")([^>]*>)", r"\1\3", img_data)
    return img_data


@report_bp.route("/generate_report", methods=["POST"])
@interface_loggedin()
def generate_report(cookies):
    res, data = call_api(API.generate_report_data, "POST")
    return make_response(
        jsonify({"message": "scoring successful"}),
        200,
    )


@report_bp.route("/get_report_data", methods=["POST"])
@interface_loggedin()
def get_report_data(cookies):
    return make_response(
        jsonify({"data": "1"}),
        200,
    )


@report_bp.route("/report", methods=["GET"])
@interface_loggedin()
def report(cookies):
    # Active test info
    user_info = get_user_info()
    active_edit_no = int(user_info["active_edit_no"])
    active_test_name = user_info["active_test_name"]

    # Get scores
    res, data = call_api(API.report, "GET")
    last_report = data["last_report"] if data["last_report"] else "Keine"
    last_response = data["last_response"] if data["last_response"] else "Keine"
    df_scores_html = None
    df_dimscores_html = None
    img_dimscores = None
    cluster = None

    if res.status_code == 200:
        df_scores = pd.read_json(StringIO(data["df_scores"]))
        df_dimscores = pd.read_json(StringIO(data["df_dimscores"]))
        cluster = data["cluster"]

        def generate_lineplot():
            df_plot = df_dimscores.loc["normed",:].reset_index()
            df_plot.columns = ["Dimension", "Score"]

            df_plot_sd = df_dimscores.loc["uncertainty_normed", :].reset_index()
            df_plot_sd.columns = ["Dimension", "Score"]
            x_sd = df_plot_sd["Dimension"].values
            y_sd_up = df_plot["Score"].values + df_plot_sd["Score"].values
            y_sd_low = df_plot["Score"].values - df_plot_sd["Score"].values

            fig: Figure
            ax: Axes
            fig, ax = plt.subplots(figsize=(8, 5))
            sns.lineplot(df_plot, x="Dimension", y="Score", ax=ax)
            ax.fill_between(x_sd, y_sd_low, y_sd_up, alpha=0.3)
            ax.set_ylim(0, 1.1)
            ax.set_ylabel("Score relativ zum Maximum")
            fig.autofmt_xdate(rotation=20)
            # plt.xticks(rotation=45)
            return fig
        img_dimscores = get_iamge_data(generate_lineplot())

        df_dimscores.index = ["Maximalscore", "Unsicherheit (SD)", "Unsicherheit relativ", "Erreichter Score", "Erreichter Score relativ"]

        df_scores_html = df_scores.to_html(col_space="4em", index=False, justify="center", float_format=lambda s: f"{s:.2f}")
        df_dimscores_html = df_dimscores.to_html(col_space="10em", index=True, justify="center", float_format=lambda s: f"{s:.2f}")


    return render_template(
        "pages/loggedin/report.html",
        active_edit_no=active_edit_no,
        active_test_name=active_test_name,
        img_dimscores=img_dimscores,
        df_dimscores=df_dimscores_html,
        df_scores=df_scores_html,
        cluster=cluster,
        last_report=last_report,
        last_response=last_response,
    )
