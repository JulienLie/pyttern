from loguru import logger

from antlr import Python3Parser
from simulator.transitions import transition


def get_specific_child(ctx, clazz):
    try:
        child = ctx
        logger.debug(f"Check {clazz} statement")
        while not isinstance(child, clazz):
            if child.getChildCount() != 1:
                logger.debug("Too many children")
                return None
            child = child.getChild(0)
        logger.debug("Found specific statement")
        return child
    except AttributeError:
        logger.debug("no children")
        return None


class AssignTransition(transition):
    def __init__(self):
        super().__init__()

    def __call__(self, node, _):
        expr_node = get_specific_child(node, Python3Parser.Expr_stmtContext)
        if expr_node is not None and len(expr_node.ASSIGN()) > 0:
            return True
        return False

    def __str__(self):
        return "Assignment"

    def __repr__(self):
        return "Assignment"

    def __eq__(self, other):
        return isinstance(other, AssignTransition)

    def __hash__(self):
        return super(object).__hash__()


class ForTransition(transition):
    def __init__(self):
        super().__init__()

    def __call__(self, node, _):
        for_node = get_specific_child(node, Python3Parser.For_stmtContext)
        return for_node is not None

    def __str__(self):
        return "For"

    def __repr__(self):
        return "For"

    def __eq__(self, other):
        return isinstance(other, ForTransition)

    def __hash__(self):
        return super(object).__hash__()


class WhileTransition(transition):
    def __init__(self):
        super().__init__()

    def __call__(self, node, _):
        while_node = get_specific_child(node, Python3Parser.While_stmtContext)
        return while_node is not None

    def __str__(self):
        return "While"

    def __repr__(self):
        return "While"

    def __eq__(self, other):
        return isinstance(other, WhileTransition)

    def __hash__(self):
        return super(object).__hash__()
