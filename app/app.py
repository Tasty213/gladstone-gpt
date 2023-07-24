from flask import Flask, render_template, request, jsonify

from query.vortex_query import VortexQuery

app = Flask(__name__)
query = VortexQuery()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    request_data = request.get_json()
    question = request_data.get("question")
    answer, sources = query.ask_question(question)
    return jsonify(
        {"answer": answer, "sources": [source.metadata for source in sources]}
    )
