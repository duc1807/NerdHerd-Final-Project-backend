from flask import Flask, jsonify, request, Response
from logzero import logger
from pymongo import MongoClient
from flask_jwt_extended import JWTManager

from src import supplement_routes

def create_app():
    """ FLASK APP FACTORY """
    app = Flask(__name__)

    """ intialise configurations """
    app.config.from_object("config.Config")

    """ intialise plugins """
    # flask_jwt_extended need config variable `JWT_SECRET_KEY`
    jwt = JWTManager(app)
    # using MongoDB as centralised storage to persist revoked tokens
    db_client = MongoClient(app.config["DATABASE_URI"])
    db = db_client[app.config["DATABASE_NAME"]]
    blacklist_col = db["token_blacklist"]

    @jwt.token_in_blacklist_loader
    def is_token_in_blacklist(decrypted_token: dict) -> bool:
        """
        This decorator sets the callback function that will be called when
        a protected endpoint is accessed and will check if the JWT has been
        been revoked. By default, this callback is not used.

        See also: `handle_login` from module `auth_routes`

        Reference: https://flask-jwt-extended.readthedocs.io/en/stable/blacklist_and_token_revoking/
        """
        logger.info("Checking if user's token is in the blacklist")
        # get JWT ID from the `dict` argument
        jti = decrypted_token["jti"]
        # retrieve list of blacklisted tokens from database
        blacklist_doc = blacklist_col.find_one()
        blacklist = [str(v) for v in blacklist_doc["List"]]
        return jti in blacklist

    """ Definition of the basic routes. """

    # supplement route definitions to this Flask `app`
    # <!-- not the most professional way to do it but at least I get the job done (；一_一) -->
    for supplement_route in supplement_routes:
        supplement_route(app)

    @app.route("/debug/route_list")
    def debug_route_list():
        result = {"url_list": [str(url) for url in app.url_map.iter_rules()]}
        headers = request.headers
        return jsonify({"routes": result, "type_info": {"app": str(type(app))}})

    @app.route("/debug/config")
    def debug_app_config():
        config = app.config
        return jsonify(str(config))

    return app


if __name__ == "__main__":
    app = create_app()
    if app.config["ENV"] == "development": 
        port = app.config["PORT"]
        app.run(host="127.0.0.1", port=port, debug=app.config["DEBUG"])
    else:
        app.run()

""" Side notes:
    - In local environment, to import a global config variable (defined in ./venv/bin/activate),
      use `os.environ.get(key={key}, default={default})`
    - Route format `api/username/<userId>`
    - To retrieve a parameter in URI, use `request.args.get("param_key", "default_value")`
"""
