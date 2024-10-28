from antlr4.tree.Tree import TerminalNodeImpl
from loguru import logger


class Transition:
    def __call__(self, node, variables):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class ClassTransition(Transition):
    def __init__(self, clazz):
        self.clazz = clazz

    def __call__(self, node, _):
        return isinstance(node, self.clazz)

    def __str__(self):
        return self.clazz.__name__

    def __repr__(self):
        return self.clazz.__name__

    def __eq__(self, other):
        if not isinstance(other, ClassTransition):
            return False
        return self.clazz == other.clazz

    def __hash__(self):
        return hash(self.clazz)


class ObjectTransition(ClassTransition):  # pylint: disable=too-few-public-methods
    def __init__(self):
        super().__init__(object)


class StringTransition(Transition):
    def __init__(self, string):
        self.string = string

    def __call__(self, node, _):
        if hasattr(node, "getText"):
            return node.getText().strip() == self.string
        return False

    def __str__(self):
        return self.string

    def __repr__(self):
        return self.string

    def __eq__(self, other):
        if not isinstance(other, StringTransition):
            return False
        return self.string == other.string

    def __hash__(self):
        return hash(self.string)


class ExceptTransition(Transition):
    def __init__(self, node):
        self.node = node

    def __call__(self, node, variables):
        name = self.node.var if hasattr(self.node, "var") else self.node
        variable = variables.get(name, None)
        if variable is None:
            return False

        return variable != node

    def __str__(self):
        return f"All except {self.node}"

    def __repr__(self):
        return f"All except {self.node}"

    def __eq__(self, other):
        if not isinstance(other, ExceptTransition):
            return False
        return self.node == other.node

    def __hash__(self):
        return hash(self.node)


class VarTransition(Transition):
    def __init__(self, node):
        self.node = node
        self.name = node.var if hasattr(node, "var") else node

    def __call__(self, node, variables):
        name = self.node.var if hasattr(self.node, "var") else self.node
        variable = variables.get(name, None)
        if variable is None:
            variables[name] = node
            return True

        logger.debug(f"Comparing {variable} and {node}")
        res = self.__compare_asts(variable, node)
        logger.debug(f"Result: {res}")
        return res

    @staticmethod
    def __compare_asts(ast1, ast2):
        if ast1 == ast2:
            return True
        if ast1 is None or ast2 is None or not isinstance(ast1, ast2.__class__):
            return False
        if isinstance(ast1, TerminalNodeImpl):
            return ast1.getText() == ast2.getText()
        if isinstance(ast1, str):
            return ast1 == ast2
        if ast1.getChildCount() != ast2.getChildCount():
            return False
        for i in range(ast1.getChildCount()):
            if not VarTransition.__compare_asts(ast1.getChild(i), ast2.getChild(i)):
                return False
        return True

    def __str__(self):
        return f"Saving/Looking {self.name}"

    def __repr__(self):
        return f"Get {self.node}"

    def __eq__(self, other):
        if not isinstance(other, VarTransition):
            return False
        return self.node == other.node

    def __hash__(self):
        return hash(self.node)


class OrTransition(Transition):
    def __init__(self, transitions=None):
        if transitions is None:
            transitions = []
        self.transitions = transitions

    def add_transition(self, transition):
        self.transitions.append(transition)

    def __call__(self, node, variables):
        for transition in self.transitions:
            if not transition(node, variables):
                return False
        return True

    def __str__(self):
        return " or ".join([str(transition) for transition in self.transitions])

    def __repr__(self):
        return " or ".join([str(transition) for transition in self.transitions])

    def __eq__(self, other):
        if not isinstance(other, OrTransition):
            return False
        return self.transitions == other.transitions

    def __hash__(self):
        return hash(tuple(self.transitions))
