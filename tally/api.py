from flask import Flask
from flask import request

app = Flask(__name__)


@app.route("/tally", methods=["GET", "POST"])
def tally():
    if request.method == "POST":
        return request.form["label"]
    else:
        return "Getting"
