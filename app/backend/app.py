import os
import boto3
from flask import Flask, request, jsonify
from backend.messageData import MessageData
from backend.canvassData import CanvassData
from backend.query.vortex_query import VortexQuery

build_dir = os.getenv("BUILD_DIR", "dist")
app = Flask(__name__, static_folder=f"../{build_dir}", static_url_path="/")
query = VortexQuery()

canvassDataTable = CanvassData(
    boto3.resource("dynamodb", region_name="eu-north-1").Table("canvassData")
)
messageDataTable = MessageData(
    boto3.resource("dynamodb", region_name="eu-north-1").Table("messages")
)


@app.route("/", methods=["GET"])
def index():
    return app.send_static_file("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    try:
        return jsonify(query.ask_question(request.get_json(), messageDataTable))
    except Exception as e:
        if app.debug:
            raise e
        return jsonify({"status": "ERROR", "reason": str(e)})


@app.route("/submit_canvass", methods=["POST"])
def submit_canvass():
    try:
        data = request.get_json()
        canvassDataTable.add_canvass(
            data.get("userId"),
            data.get("firstName"),
            data.get("lastName"),
            data.get("postcode"),
            data.get("email"),
        )
        return jsonify({"status": "SUCCESS"})

    except Exception as e:
        if app.debug:
            raise e
        return jsonify({"status": "ERROR", "reason": str(e)})
