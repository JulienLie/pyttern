from antlr4 import TerminalNode
from loguru import logger

from ..antlr import Python3ParserVisitor, Python3Parser
from ..pytternfsm import python_type_transition as ptt
from ..pytternfsm.python_type_transition import get_specific_child
from ..simulator.pyttern_fsm import FSM, Movement
from ..simulator.transitions import ClassTransition, StringTransition, ObjectTransition, ExceptTransition, \
    VarTransition, OrTransition


def is_specific_statement(ctx, clazz):
    if not isinstance(ctx, Python3Parser.StmtContext):
        return False
    return ptt.get_specific_child(ctx, clazz) is not None


class Python_Visitor(Python3ParserVisitor):
    def __init__(self, strict=False):
        super().__init__()
        self.strict = strict
        self.depth = 0
        self.current_fsm_node = None
        self.up_to = []

    def text_node(self, text):
        next_node = FSM()
        transition = self.get_up_transition(
            next_node, StringTransition(
                text))
        self.current_fsm_node.add_transition(*transition)

        self.current_fsm_node = next_node
        return next_node

    def get_up_transition(self, next_node, pred=None):
        if pred is None:
            pred = ObjectTransition()

        up_to = self.up_to.pop() if len(self.up_to) > 0 else None
        if up_to is not None:
            node, depth = up_to
            null_node = FSM()
            null_transition = (null_node, pred, [])
            self.current_fsm_node.add_transition(*null_transition)
            self.current_fsm_node = null_node

            self_transition = (null_node, ExceptTransition(node), [Movement.MP])
            self.current_fsm_node.add_transition(*self_transition)

            up_node = FSM()
            transition = (next_node, VarTransition(node), [Movement.MP] * depth + [Movement.MRS])

            self.depth = 0
            return transition

        transition = (next_node, pred, [Movement.MP] * self.depth + [Movement.MRS])
        self.depth = 0
        return transition

    def visit(self, tree):
        FSM.default_name = 1
        self.depth = 0
        start_node = FSM("START")
        self.current_fsm_node = start_node
        super().visit(tree)

        return start_node

    def visitChildren(self, node, clazz=None):
        children = list(node.getChildren())
        if len(children) == 0:
            logger.debug(f"Handling {node.__class__.__name__} as Terminal")
            return self.text_node(node.getText())

        if clazz is None:
            clazz = node.__class__

        start = None
        end = None
        if node.start is not None and node.stop is not None:
            start = (node.start.line - 1, node.start.column)
            end = (node.stop.line - 1, node.stop.column)
        next_node = FSM(start=start, end=end)
        transition = (next_node, ClassTransition(clazz), [Movement.MLC])
        self.current_fsm_node.add_transition(*transition)

        self.current_fsm_node = next_node

        old_depth = self.depth
        self.depth = 0
        up_to = self.up_to
        self.up_to = []

        while len(children) > 1 and is_specific_statement(children[-1], Python3Parser.Double_wildcardContext):
            children.pop()
            logger.debug("Remove double wildcard")

        for i in range(len(children)):
            if i == len(children) - 1:
                self.depth = old_depth + 1
                self.up_to = up_to + self.up_to
            c = children[i]
            c.accept(self)

        return next_node

    def visitTerminal(self, node):
        if str(node) == "<EOF>":
            return

        node_text = str(node).strip()

        return self.text_node(node_text)

    @staticmethod
    def get_type_transition(ctx, default=None):
        ttype = ctx.getChild(0, Python3Parser.Wildcard_typeContext)
        if ttype is None:
            return default
        clazz = []
        for child in ttype.getChildren(lambda x: isinstance(x, Python3Parser.NameContext)):
            clazz.append(f"{child.getText()}Transition")
        logger.debug(f"Wildcard types: {clazz}")
        transition = OrTransition()
        for c in clazz:
            tran = getattr(ptt, c)
            transition.add_transition(tran())
        return transition

    def visitSimple_wildcard(self, ctx: Python3Parser.Simple_wildcardContext):
        pred = ObjectTransition()
        pred = self.get_type_transition(ctx, pred)

        numbers = ctx.getChild(0, Python3Parser.Wildcard_numberContext)
        if numbers is not None:
            low = int(numbers.NUMBER(0).getText())
            for i in range(1, low):
                sibling = FSM()
                transition = (sibling, pred, [Movement.MRS])
                self.current_fsm_node.add_transition(*transition)
                self.current_fsm_node = sibling

        next_node = FSM()
        transition = self.get_up_transition(next_node, pred)
        self.current_fsm_node.add_transition(*transition)

        if numbers is not None:
            low = int(numbers.NUMBER(0).getText())
            high = int(numbers.NUMBER(1).getText()) if numbers.NUMBER(1) is not None else low
            for i in range(low, high):
                old_transi = self.current_fsm_node.transitions[::]
                sibling = FSM()
                right_transition = (sibling, pred, [Movement.MRS])
                for transi in old_transi:
                    if transi[0] == self.current_fsm_node:
                        transi = (sibling, transi[1], transi[2])
                    sibling.add_transition(*transi)
                self.current_fsm_node.add_transition(*right_transition)
                self.current_fsm_node = sibling

        self.current_fsm_node = next_node

        return next_node

    def visitDouble_wildcard(self, ctx: Python3Parser.Double_wildcardContext):
        stmt_parent = ctx.parentCtx
        block_parent = stmt_parent.parentCtx
        while not isinstance(stmt_parent, Python3Parser.StmtContext):
            stmt_parent = stmt_parent.parentCtx
            block_parent = stmt_parent.parentCtx

        if block_parent.children[-1] != stmt_parent:
            if self.strict:
                pred = self.get_type_transition(ctx, ObjectTransition())
                self_transition = (self.current_fsm_node, pred, [Movement.MRS])
                self.current_fsm_node.add_transition(*self_transition)
            return self.current_fsm_node

        ttype = ctx.getChild(0, Python3Parser.Wildcard_typeContext)
        if ttype is not None:
            logger.warning("Wildcard type in double wildcard is not yet supported")
            pass

        up_node = FSM()
        up_transition = self.get_up_transition(up_node)
        self.current_fsm_node.add_transition(*up_transition)
        self.current_fsm_node = up_node
        return up_node

    def visitStmt_wildcard(self, ctx: Python3Parser.Stmt_wildcardContext):
        return ctx.getChild(0).accept(self)

    def visitExpr_wildcard(self, ctx: Python3Parser.Expr_wildcardContext):
        return ctx.getChild(0).accept(self)

    def visitStmt(self, ctx: Python3Parser.StmtContext):
        child = ctx.getChild(0)
        if isinstance(child, Python3Parser.Stmt_wildcardContext):
            return child.accept(self)

        if not self.strict:
            self_transition = (self.current_fsm_node, ObjectTransition(), [Movement.MRS])
            self.current_fsm_node.add_transition(*self_transition)

        if is_specific_statement(ctx, Python3Parser.Compound_wildcardContext):
            save_node = FSM()
            save_transition = (save_node, VarTransition(ctx), [])
            self.current_fsm_node.add_transition(*save_transition)
            self.current_fsm_node = save_node
            self.up_to.append((ctx, self.depth))

            res = self.visitChildren(ctx)

            next_stmts = FSM.get_next_nodes(res, ClassTransition(Python3Parser.StmtContext))
            next_stmt = next(next_stmts, None)
            if next_stmt is not None:
                skip_transition = (next_stmt, ObjectTransition(), [])
                res.add_transition(*skip_transition)
            return res

        strict_node = get_specific_child(ctx, Python3Parser.Strict_modeContext)
        if strict_node is not None:
            res = strict_node.accept(self)
            return res

        return self.visitChildren(ctx)

    def visitVar_wildcard(self, ctx: Python3Parser.Var_wildcardContext):
        var_name = ctx.name().getText()
        next_node = FSM()
        transition = self.get_up_transition(next_node, VarTransition(var_name))
        self.current_fsm_node.add_transition(*transition)
        self.current_fsm_node = next_node
        return next_node

    def visitSimple_compound_wildcard(self, ctx: Python3Parser.Simple_compound_wildcardContext):
        next_node = FSM()
        pred = self.get_type_transition(ctx, ObjectTransition())

        numbers = ctx.getChild(0, Python3Parser.Wildcard_numberContext)
        if numbers is not None:
            low = int(numbers.NUMBER(0).getText())
            for i in range(1, low):
                # Go through all children until finding a body
                child_node = FSM()
                transition = (child_node, pred, [Movement.MLC])
                self.current_fsm_node.add_transition(*transition)
                self.depth += 1
                self_transition = (child_node, ObjectTransition(), [Movement.MRS])
                child_node.add_transition(*self_transition)
                self.current_fsm_node = child_node

                down_node = FSM()
                down_transition = (down_node, ClassTransition(Python3Parser.BlockContext), 3 * [Movement.MLC])
                self.depth += 3
                self.current_fsm_node.add_transition(*down_transition)

                self.current_fsm_node = down_node

        transition = (next_node, pred, [Movement.MLC])
        self.current_fsm_node.add_transition(*transition)
        self_transition = (next_node, ObjectTransition(), [Movement.MRS])
        next_node.add_transition(*self_transition)
        #self.depth += 1
        self.current_fsm_node = next_node

        node = ctx.getChild(0, Python3Parser.BlockContext).accept(self)

        if numbers is not None:
            high = int(numbers.NUMBER(1).getText()) if numbers.NUMBER(1) is not None else low
            for i in range(low, high):
                child_node = FSM()
                transition = (child_node, ClassTransition(Python3Parser.BlockContext), 4 * [Movement.MLC])
                next_node.add_transition(*transition)

                self_transition = (child_node, ObjectTransition(), [Movement.MRS])
                child_node.add_transition(*self_transition)

                down_transition = (node, ClassTransition(Python3Parser.BlockContext), [Movement.MLC])
                self.depth += 3
                child_node.add_transition(*down_transition)
                next_node = child_node

        return next_node

    def visitMultiple_compound_wildcard(self, ctx: Python3Parser.Multiple_compound_wildcardContext):
        next_node = FSM()
        transition = (next_node, ObjectTransition(), [Movement.MLC])
        self.current_fsm_node.add_transition(*transition)

        self_transition = (next_node, ObjectTransition(), [Movement.MRS])
        next_node.add_transition(*self_transition)

        back_transition = (self.current_fsm_node, ObjectTransition(), [])
        next_node.add_transition(*back_transition)

        self.current_fsm_node = next_node

        ctx.getChild(0, Python3Parser.BlockContext).accept(self)

        return next_node

    def visitCompound_wildcard(self, ctx: Python3Parser.Compound_wildcardContext):
        return ctx.getChild(0).accept(self)

    def visitList_wildcard(self, ctx: Python3Parser.List_wildcardContext):
        next_node = FSM()
        transition = self.get_up_transition(
            next_node)
        self.current_fsm_node.add_transition(*transition)
        self_transition = (next_node, ObjectTransition(), [Movement.MRS])
        next_node.add_transition(*self_transition)
        self.current_fsm_node = next_node

        return next_node

    def visitAtom_wildcard(self, ctx: Python3Parser.Atom_wildcardContext):
        return ctx.getChild(0).accept(self)

    def visitStrict_mode(self, ctx: Python3Parser.Strict_modeContext):
        children = list(ctx.getChildren(lambda x: not isinstance(x, TerminalNode)))
        pre = self.strict
        self.strict = True
        for child in children:
            logger.debug(child)
            res = child.accept(self)
            logger.debug(res)
        self.strict = pre
        return self.current_fsm_node

    def visitContains_wildcard(self, ctx: Python3Parser.Contains_wildcardContext):
        logger.warning("Not yet implemented")
        return self.visitChildren(ctx)
