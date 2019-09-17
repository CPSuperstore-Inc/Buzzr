from flask import Flask, render_template, redirect, request, flash, session
from time import time
import operator

from Buzzr.api import app as api
from Buzzr.filters import app as filters
from Buzzr.security import SECRET_KEY

names = {}
start = None

app = Flask(__name__)

app.config['SECRET_KEY'] = SECRET_KEY

app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(filters)

class Null:
    def __init__(self):
        self.value = 10000

    def __float__(self):
        return self.value

    def __str__(self):
        return "No Response..."

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other


@app.context_processor
def inject_dict_for_all_templates():
    return {
        "development": False
    }


@app.route("/")
def index():
    return render_template("index.twig")


@app.route("/buzzer", methods=["GET", "POST"])
def cont():
    if request.method == "GET":
        return render_template("buzzer.twig")
    else:
        name = request.form["name"]
        if name in names:
            flash("The name you have requested is in use. Please select another name and try again.")
        else:
            session["name"] = name
            names[name] = Null()
        return redirect("/buzzer")


@app.route("/buzzer/buzz")
def buzz():
    if start is None:
        flash("You Buzzed Too Early!")
    else:
        delta = time() - start
        names[session["name"]] = delta
        flash("Clicked! Response Time: {}s".format(round(delta, 2)))
    return redirect("/buzzer?ps=true")


@app.route("/logout")
def logout():
    del session["name"]
    return redirect("/")


@app.route("/cont")
def control():
    n = sorted(names.items(), key=operator.itemgetter(1))
    return render_template("control.twig", names=n, running=start is not None)


@app.route("/cont/start")
def control_start():
    global start
    start = time()
    for n in names:
        names[n] = Null()
    return redirect("/cont")

@app.route("/cont/stop")
def control_stop():
    global start
    start = None
    return redirect("/cont")
