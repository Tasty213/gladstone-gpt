import os
from flask import Flask, request, jsonify
from backend.query.vortex_query import VortexQuery

build_dir = os.getenv("BUILD_DIR", "dist")
app = Flask(__name__, static_folder=f"../{build_dir}", static_url_path="/")
query = VortexQuery()


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        return jsonify(query.ask_question(request.get_json()))
    except Exception as e:
        if app.debug:
            raise e
        return jsonify({"status": "ERROR", "reason": str(e)})
