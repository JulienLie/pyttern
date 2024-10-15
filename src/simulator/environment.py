from dataclasses import dataclass

from antlr4 import ParserRuleContext

from simulator.pyttern_fsm import FSM


@dataclass
class Environment:
    pattern_fsm: FSM
    code_ast: ParserRuleContext
    variables: dict
    match_set: list

    def __iter__(self):
        return iter((self.pattern_fsm, self.code_ast, self.variables, self.match_set))
