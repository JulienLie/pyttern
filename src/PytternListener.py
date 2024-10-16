class PytternListener():
    def on_match(self, simulator):
        pass

    def step(self, simulator, fsm, ast, variables, matches):
        pass

    def on_transition(self, simulator, current_fsm, current_ast, next_node, next_ast, classes, movements, matches):
        pass

    def on_end(self, simulator, fsm, node):
        pass

    def on_start(self, simulator, fsm, node):
        pass

    def on_new_variable(self, simulator, fsm, node, var):
        pass


class ConsolePytternListener(PytternListener):
    def on_transition(self, simulator, current_fsm, current_ast, next_node, next_ast, classes, movements, _):
        current_ast_str = f"{current_ast.__class__.__name__[:-7]}({current_ast.getText()})".replace("\n", "\\n")
        next_ast_str = f"{next_ast.__class__.__name__[:-7]}({next_ast.getText()})".replace("\n", "\\n")
        print(
            f"Step {simulator.n_step}: Transition from node {current_fsm} to {next_node}, matching {current_ast_str} "
            f"with {classes.__name__.replace('Context', '')}"
            f"and {movements} to {next_ast_str}")

    def on_start(self, simulator, fsm, node):
        print(f"Start matching {fsm} with {node}")

    def on_match(self, simulator):
        print(f"Match found at step {simulator.n_step}!")
