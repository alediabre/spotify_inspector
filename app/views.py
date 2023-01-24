from app import app
from app import r
from app import q
from app.scrapy import scrape
from app.graphs import get_graph
from app.get_cookies import captura_cookies

from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from flask import render_template, request, jsonify, make_response


@app.route("/")
def index():
    args = None
    if request.args:
        args = request.args

    return render_template("public/index.html", args=args)


@app.route("/view-following", methods=["GET","POST"])
def view_following():

    LOGGED = True
    if LOGGED == False:
        captura_cookies()

    usuarios = scrape("coder.python21")
    #usuarios = ["theeasyreps", "max_true"]

    with ThreadPoolExecutor(max_workers=cpu_count()) as pool:
        listas = pool.map(scrape,usuarios)

    #listas = []
    grafo = get_graph(usuarios)

    if request.args:
        listas = []
        usuario = request.args.get("usuario")

        lista = scrape(usuario)
        listas.append(lista)
    
    return render_template("public/view_following.html", listas=listas, grafo=grafo)



@app.route("/add-task", methods=["GET","POST"])
def add_task():

    jobs = q.jobs
    message = None

    if request.args:
        usuario = request.args.get("usuario")

        task = q.enqueue(scrape, usuario)

        jobs = q.jobs

        q_len = len(q)

        message = f"Task queued at {task.enqueued_at.strftime('%a %d %b %Y %H:%M:%S')}. {q_len} jobs queued"
    
    return render_template("public/add_task.html", message=message, jobs=jobs)



@app.route("/guestbook")
def guestbook():
    return render_template("public/guestbook.html")


@app.route("/guestbook/create-entry", methods=["POST"])
def create_entry():

    req = request.get_json()

    res = make_response(jsonify(req), 200)

    return res



@app.route("/json", methods=["POST"])
def json():

    if request.is_json:

        req = request.get_json()
        response = {
            "message": "JSON received",
            "name": req.get("name")
        }

        res = make_response(jsonify(response), 200)

        return res
    
    else:

        return "no json", 400
