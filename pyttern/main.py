import argparse
import io
from functools import cache

from antlr4 import FileStream, CommonTokenStream, InputStream
from loguru import logger

from .PytternListener import ConsolePytternListener
from .antlr import Python3Parser
from .antlr.Python3Lexer import Python3Lexer
from .pyttern_error_listener import Python3ErrorListener
from .pytternfsm.python_visitor import Python_Visitor
from .pytternfsm.tree_pruner import TreePruner
from .simulator.simulator import Simulator


@cache
def generate_tree_from_code(code):
    code = code.strip()
    stream = InputStream(code)
    return generate_tree_from_stream(stream)


@cache
def generate_tree_from_stream(stream):
    logger.info("Generating tree")
    lexer = Python3Lexer(stream)
    stream = CommonTokenStream(lexer)
    py_parser = Python3Parser(stream)

    error = io.StringIO()

    py_parser.removeErrorListeners()
    error_listener = Python3ErrorListener(error)
    py_parser.addErrorListener(error_listener)

    tree = py_parser.file_input()
    if len(error_listener.symbol) > 0:
        raise IOError(
            f"Syntax error in {stream} at line {error_listener.line} "
            f"({repr(error_listener.symbol)}) : {error.getvalue()}")

    pruned_tree = TreePruner().visit(tree)

    return pruned_tree


@cache
def generate_tree_from_file(file):
    file_input = FileStream(file, encoding="utf-8")
    return generate_tree_from_stream(file_input)


def run_application():
    from visualizer.web import application
    application.app.run(debug=True)


def main(pattern, code, args=None):
    if args and args.web:
        run_application()
        return

    try:
        pattern_tree = generate_tree_from_file(pattern)
        code_tree = generate_tree_from_file(code)
    except Exception as e:
        print(e)
        return

    fsm = Python_Visitor().visit(pattern_tree)

    simu = Simulator(fsm, code_tree)

    listener = ConsolePytternListener()
    simu.add_listener(listener)
    simu.start()

    while len(simu.states) > 0:
        simu.step()
    print(simu.match_set.matches)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--web", action="store_true")

    parser.add_argument("pattern")
    parser.add_argument("code")

    args = parser.parse_args()
    main(args.pattern, args.code, args)
