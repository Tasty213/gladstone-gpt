from urllib import response
from flask import Flask, render_template, request

from .query.vortex_query import VortexQuery

app = Flask(__name__)
query = VortexQuery()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/get_response", methods=["POST"])
def get_response():
    question = request.form.get("user_input")
    return question
