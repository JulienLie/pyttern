from antlr4 import TerminalNode, Token

from antlr import Python3ParserVisitor, Python3Parser


class TreePruner(Python3ParserVisitor):

    def visitChildren(self, node):
        result = super().visitChildren(node)

        node.children = result
        for child in result:
            if child is not None:
                child.parentCtx = node

        return node

    def prune_single_child(self, node):
        new_child = self.visitChildren(node)
        while len(new_child.children) == 1:
            new_child = new_child.getChild(0)
            if isinstance(new_child, TerminalNode):
                return new_child
            if isinstance(new_child, Python3Parser.NameContext):
                return new_child
            if isinstance(new_child, Python3Parser.Expr_wildcardContext):
                return new_child
        return new_child

    def visitTest(self, ctx: Python3Parser.TestContext):
        return self.prune_single_child(ctx)

    def visitTfpdef(self, ctx:Python3Parser.TfpdefContext):
        return self.prune_single_child(ctx)

    def visitExpr(self, ctx:Python3Parser.ExprContext):
        return self.prune_single_child(ctx)

    def visitTerminal(self, node):
        sym = node.getSymbol()
        if sym.type in [Python3Parser.NEWLINE, Python3Parser.INDENT, Python3Parser.DEDENT]:
            return None
        if sym.type == Token.EOF:
            sym.text = "<EOF>"
            return node
        txt = node.getText().strip()
        if txt in "():,.":
            return None
        return node

    def visitErrorNode(self, node):
        return node

    def defaultResult(self):
        return []

    def aggregateResult(self, aggregate, nextResult):
        if nextResult is None:
            return aggregate
        return aggregate + [nextResult]
