import json
from functools import wraps

from antlr4 import ParseTreeVisitor
from cachelib import FileSystemCache
from flask import Flask, render_template, request, redirect, session, flash, get_flashed_messages
from flask_session import Session
from loguru import logger

from PytternListener import PytternListener
from main import generate_tree_from_code
from pytternfsm.python_visitor import Python_Visitor
from simulator.simulator import Simulator

app = Flask(__name__)
app.secret_key = b'a78b11744f599a29207910d3b55eded2dd22cbf9c1dc6c007586b68ff649ac6f'

SESSION_TYPE = 'cachelib'
SESSION_SERIALIZATION_FORMAT = 'json'
SESSION_CACHELIB = FileSystemCache(threshold=500, cache_dir="./sessions")
app.config.from_object(__name__)
Session(app)

""" Helper classes and methods """


class PT_to_JSON(ParseTreeVisitor):
    def visitChildren(self, node):
        elem = {"name": node.__class__.__name__, "children": [], "id": hash(node)}
        if node.start is not None:
            elem["start"] = (node.start.line, node.start.column)
        if node.stop is not None:
            elem["end"] = (node.stop.line, node.stop.column)
        result = self.defaultResult()
        n = node.getChildCount()
        for i in range(n):
            if not self.shouldVisitNextChild(node, result):
                return result

            c = node.getChild(i)
            childResult = c.accept(self)
            result = self.aggregateResult(result, childResult)
        elem["children"] = result
        return elem

    def visitTerminal(self, node):
        return {"name": node.__class__.__name__, "symbol": node.symbol.text, "children": [], 'id': hash(node)}

    def visitErrorNode(self, node):
        return {"name": node.__class__.__name__, "children": [], id: hash(node)}

    def defaultResult(self):
        return []

    def aggregateResult(self, aggregate, nextResult):
        return aggregate + [nextResult]


def file_check():
    def _file_check(f):
        @wraps(f)
        def __file_check(*args, **kwargs):
            if "pyttern_code" in session and "python_code" in session and session["pyttern_code"] is not None and \
                    session["python_code"] is not None:
                return f(*args, **kwargs)
            else:
                return json.dumps({"status": "error", "message": "Missing pyttern or python code"})

        return __file_check

    return _file_check


def get_simulator(pyttern_code, python_code):
    pyttern_tree = generate_tree_from_code(pyttern_code)
    strict = session.get('strict', False)
    pyttern_fsm = Python_Visitor(strict=strict).visit(pyttern_tree)

    python_tree = generate_tree_from_code(python_code)

    return Simulator(pyttern_fsm, python_tree)


def fsm_to_json(fsm):
    nodes = []
    to_check = [fsm]
    visited = set()
    while len(to_check) > 0:
        node = to_check.pop()
        if node in visited:
            continue
        visited.add(node)
        transitions = []
        for next_node, func, mov in node.get_transitions():
            name = str(func)
            transitions.append({"next": str(next_node), "func": name, "mov": str(mov)})
            to_check.append(next_node)
        infos = node.__dict__.copy()
        infos['transitions'] = transitions
        infos['id'] = str(node)
        logger.debug(infos)
        json_obj = json.dumps(infos)
        nodes.append(json_obj)
    return nodes


class JSON_Listener(PytternListener):
    def __init__(self):
        self.data = []

    def step(self, simulator, fsm, ast, variables, matches):
        state_info = (str(fsm), hash(ast))
        current_matchings = [(str(fsm), hash(ast)) for fsm, ast in matches]
        logger.debug(variables)
        var_strs = [f"{var}: {PT_to_JSON().visit(variables[var])}" for var in variables]
        logger.debug(var_strs)
        self.data.append({"state": state_info, "matches": current_matchings, "match": False, "variables": var_strs})

    def on_match(self, simulator):
        self.data[-1]["match"] = True


""" Web endpoints """


@app.route("/")
def index():
    session["n_match"] = 0

    pyttern_code = None
    python_code = None
    pyttern_fsm_graph = "null"
    pyttern_tree_graph = "null"
    python_graph = "null"
    if "pyttern_code" in session and session["pyttern_code"] is not None:
        try:
            pyttern_code = session["pyttern_code"]
            pyttern_tree = generate_tree_from_code(pyttern_code)
            pyttern_tree_graph = PT_to_JSON().visit(pyttern_tree)
            strict = session.get('strict', False)
            pyttern_fsm = Python_Visitor(strict=strict).visit(pyttern_tree)
            pyttern_fsm_graph = fsm_to_json(pyttern_fsm)
        except IOError as e:
            pyttern_code = None
            session.pop('pyttern_code', None)
            print(e)
    if "python_code" in session and session["python_code"] is not None:
        python_code = session["python_code"]
        python_tree = generate_tree_from_code(python_code)
        python_graph = PT_to_JSON().visit(python_tree)

    return render_template(
        'index.html', pyttern_code=pyttern_code, python_code=python_code, python_graph=python_graph,
        pyttern_graph=pyttern_fsm_graph, pyttern_tree=pyttern_tree_graph)


@app.route("/submit-pyttern", methods=['POST'])
def submit_pyttern():
    code = request.files['pyttern-file']
    pyttern_code = code.stream.read()
    session['pyttern_code'] = pyttern_code.decode()

    strict = request.form.get('strict', 'off') == 'on'
    session['strict'] = strict
    return redirect("/")


@app.route("/remove-pyttern", methods=['POST'])
def remove_pyttern():
    session.pop('pyttern_code', None)
    return redirect("/")


@app.route("/submit-code", methods=['POST'])
def submit_code():
    code = request.files['python-file']
    pyttern_code = code.stream.read()
    session['python_code'] = pyttern_code.decode()
    return redirect("/")


@app.route("/remove-python", methods=['POST'])
def remove_python():
    session.pop('python_code', None)
    return redirect("/")


"""API endpoints"""


@app.route("/api/start", methods=['POST'])
@file_check()
def start():
    session["n_match"] = 0

    pyttern_code = session["pyttern_code"]
    python_code = session["python_code"]
    simulator = get_simulator(pyttern_code, python_code)
    json_listener = JSON_Listener()
    simulator.add_listener(json_listener)
    simulator.start()
    first_state = simulator.states[-1]
    fsm, ast, _, _ = first_state
    first_state_info = (str(fsm), hash(ast))
    while len(simulator.states) > 0:
        simulator.step()
    logger.debug(f"Number of steps: {simulator.n_step}")
    session["data"] = json_listener.data
    match_states = [i for i, data in enumerate(json_listener.data) if data["match"]]
    logger.debug(f"Matching states: {match_states}")
    return json.dumps(
        {"status": "ok", "n_steps": simulator.n_step - 1, "state": first_state_info, "match_states": match_states})


@app.route("/api/step", methods=['POST'])
def step():
    current_step = int(request.json["step"])
    logger.info(f"Getting step {current_step}")
    current_data = session["data"][current_step]
    last_data = session["data"][current_step - 1] if current_step > 0 else None
    logger.debug(f"Current step: {current_data}")
    logger.debug(f"Last step: {last_data}")

    state_info = current_data["state"]

    current_matchings = current_data["matches"]
    previous_matchings = last_data["matches"] if last_data is not None else []

    if current_data["match"]:
        flash("New match found", "message")

    return json.dumps(
        {"status": "ok", "state": state_info, "current_matchings": current_matchings,
         "previous_matchings": previous_matchings, "messages": get_flashed_messages(), "match": current_data["match"],
         "variables": current_data["variables"]})
