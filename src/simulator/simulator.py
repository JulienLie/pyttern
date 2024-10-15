import json

from antlr4 import TerminalNode
from loguru import logger

from pytternfsm.match_set import MatchSet
from simulator.pyttern_fsm import Movement
from .environment import Environment


class Simulator:
    def __init__(self, pattern_fsm, code_ast, count=True):
        self.pattern_fsm = pattern_fsm
        self.code_ast = code_ast
        self.count = count
        self.match_set = MatchSet()
        self.states = []
        self.accepted_states = []
        self.visited_states = []
        self.n_step = 0
        self._listeners = []

    def add_listener(self, listener):
        self._listeners.append(listener)

    def remove_listener(self, listener):
        self._listeners.remove(listener)

    def remove_all_listeners(self):
        self._listeners = []

    def start(self):
        logger.info("Starting simulation")
        state = Environment(self.pattern_fsm, self.code_ast, {}, [])
        self.states.append(state)
        for listener in self._listeners:
            listener.on_start(self, self.pattern_fsm, self.code_ast)
        return self

    def step(self):
        logger.debug(f"Step {self.n_step}")
        self.n_step += 1
        if len(self.states) == 0:
            raise Exception("No more states to process")
        current_state = self.states.pop()
        current_fsm, current_ast, variables, matches = current_state
        for listener in self._listeners:
            listener.step(self, current_fsm, current_ast, variables, matches)

        if self.is_matching(current_state):
            self.accepted_states += self.visited_states
            self.visited_states = []
            return

        match, new_variables = Simulator.check_var(current_ast, current_fsm.var, variables)
        if new_variables is not variables:
            for listener in self._listeners:
                listener.on_new_variable(self, current_fsm.var, new_variables[current_fsm.var])
        if not match:
            return

        for next_node, func, movements in current_fsm.get_transitions():
            if not func(current_ast, new_variables):
                continue
            next_ast = self.move_ast(current_ast, movements)
            if next_ast is None:
                continue
            new_state = (next_node, next_ast, new_variables.copy(), matches + [(current_fsm, current_ast)])
            if new_state in self.visited_states:
                continue
            if new_state in self.accepted_states:
                logger.info(f"Match found")
                self.match_set.record((self.n_step, match))
                for listener in self._listeners:
                    listener.on_match(self)
                continue
            self.visited_states.append(new_state)
            self.states.append(new_state)
            for listener in self._listeners:
                listener.on_transition(self, current_fsm, current_ast, next_node, next_ast, func, movements, new_state[3])

    def move_ast(self, ast, movements):
        current_ast = ast
        for movement in movements:
            match movement:
                case Movement.MRS:
                    try:
                        parent = current_ast.parentCtx
                        siblings = list(parent.getChildren())
                        index = siblings.index(current_ast)
                        current_ast = siblings[index+1]
                    except IndexError:
                        return None
                case Movement.MLC:
                    try:
                        children = list(current_ast.getChildren())
                        current_ast = children[0]
                    except AttributeError:
                        return None
                    except IndexError:
                        return None
                case Movement.MP:
                    current_ast = current_ast.parentCtx
        return current_ast

    def is_matching(self, state):
        fsm, ast, _, match = state
        if isinstance(ast, TerminalNode) and str(ast) == "<EOF>" and len(list(fsm.get_out_transitions())) == 0:
            logger.info(f"Match found")
            self.match_set.record(match)
            for listener in self._listeners:
                listener.on_match(self)
            return True
        return False

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def check_var(current_ast, var, variables):
        if var is None:
            return True, variables

        if var in variables:
            if Simulator.match(current_ast, variables[var]):
                return True, variables
            return False, variables
        new_variables = variables.copy()
        new_variables[var] = current_ast
        return True, new_variables

    @staticmethod
    def match(ast, value):
        if isinstance(ast, TerminalNode):
            return str(ast) == value
        return False


