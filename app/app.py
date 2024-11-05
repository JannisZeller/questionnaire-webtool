from flask import Flask
from flask import url_for  # noqa: F401


from .config import ConsentCookieSession
from .config import set_config_from_json, register_blueprint_list, print_status

from .api.core.database import db
from .api import blueprints as backend_blueprints

from .interface import blueprints as frontend_blueprints

from .test import create_admin, create_testuser, test_responses


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="./interface/templates",
        static_folder="./interface/static",
    )

    app.session_interface = ConsentCookieSession()

    set_config_from_json(app, "./env/config.jsonc")
    set_config_from_json(app, "./env/secret_config.jsonc")

    register_blueprint_list(app, backend_blueprints, "/api")
    register_blueprint_list(app, frontend_blueprints)
    print_status(app)

    db.init_app(app)

    with app.app_context():
        db.drop_all()
        db.create_all()
        create_admin(db)
        create_testuser(db)
        create_testuser(db, "testmail", app.config["TEST_RECIEVER_ADDRESS"])
        test_responses(db)

    return app


def run_app():
    app = create_app()
    app.run(ssl_context="adhoc", debug=True, threaded=True) # host='0.0.0.0', port=5001,

# run with "flask run --host=0.0.0.0 --port=5001 --debug" for external visibility
