from flask import Blueprint
from flask import render_template


htmx_bp = Blueprint("htmx_interface", __name__, template_folder="templates")


@htmx_bp.route("/htmx")
def main():
    """Interface-Route directing to the htmx view for experiments.
    """
    return render_template("/htmx.html")
