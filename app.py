import flask_login
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from logzero import logger
from pymongo import MongoClient

from src.auth import login_manager
from src import list_all_bps


def create_app():
    app = Flask(__name__)

    # intialise configurations
    app.config.from_object("config.Config")
    # intialise plugins
    login_manager.init_app(app)
    # Setup CORS headers
    CORS(app)

    # Definition of the routes. Import all blueprints
    for bp in list_all_bps:
        app.register_blueprint(bp)
    
    # Flask Blueprints: http://flask.pocoo.org/docs/latest/blueprints
    @app.route("/")
    def hello_world():
        logger.info("/")
        return "Hello World"

    @app.route("/open_db")
    def open_db():
        client = MongoClient(app.config["DATABASE_URI"])
        db = client["crescorex"]
        return str(db.list_collection_names())

    @app.route("/meta/<info>")
    def fetch_meta(info):
        logger.info(f"/meta/{info}")

        info_dict = {"url_list": app.url_map}
        headers = request.headers
        return jsonify(
            {
                "info": str(info_dict[info]).split("\n"),
                "header": (headers.get("Connection")),
            }
        )

    return app


if __name__ == "__main__":
    app = create_app()
    port = app.config["PORT"]
    app.run(host="127.0.0.1", port=port, debug=app.config["DEBUG"])

"""
    - In local environment, to import a global config variable (defined in ./venv/bin/activate),
      use `os.environ.get(key={key}, default={default})`
    - Route format `api/username/<userId>`
    - To retrieve a parameter in URI, use `request.args.get("param_key", "default_value")`
"""