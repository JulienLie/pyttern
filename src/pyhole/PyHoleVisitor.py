# Generated from Python3.g4 by ANTLR 4.7.2

import codecs
import re
from ast import *

from .HoleAST import (HoleAST, StrictMode, MultipleCompoundHole,
                      CompoundHole, VarHole, DoubleHole, SimpleHole)
from .antlr.Python3Parser import Python3Parser
from .antlr.Python3ParserVisitor import Python3ParserVisitor

# Bind operator to their classes
operators = {
    'unary': {
        '+': UAdd,
        '-': USub,
        '~': Invert
    },
    'and': And,
    'or': Or,
    '+': Add,
    '-': Sub,
    '*': Mult,
    '@': MatMult,
    '/': Div,
    '%': Mod,
    '**': Pow,
    '<<': LShift,
    '>>': RShift,
    '|': BitOr,
    '^': BitXor,
    '&': BitAnd,
    '//': FloorDiv,
    '~': Invert,
    'not': Not,
    '==': Eq,
    '!=': NotEq,
    '<': Lt,
    '<=': LtE,
    '>': Gt,
    '>=': GtE,
    'is': Is,
    'is not': IsNot,
    'in': In,
    'not in': NotIn,
    '+=': Add,
    '-=': Sub,
    '*=': Mult,
    '@=': MatMult,
    '/=': Div,
    '%=': Mod,
    '&=': BitAnd,
    '|=': BitOr,
    '^=': BitXor,
    '<<=': LShift,
    '>>=': RShift,
    '**=': Pow,
    '//=': FloorDiv
}


def set_lineno(obj, ctx):
    start = ctx.start.line
    end = ctx.stop.line
    if isinstance(obj, (stmt, HoleAST)):
        obj.lineno = start
        obj.lineno_end = end


# This class defines a complete generic visitor for a parse tree produced by Python3Parser.

class PyHoleVisitor(Python3ParserVisitor):

    def visitMatch_stmt(self, ctx: Python3Parser.Match_stmtContext):
        subject = ctx.subject_expr().accept(self)
        body = []
        cases = ctx.case_block()
        for i in range(len(cases)):
            c = cases[i]
            child_result = c.accept(self)
            if child_result is not None:
                if isinstance(child_result, list):
                    body.extend(child_result)
                else:
                    body.append(child_result)
            else:
                print(type(c))

        return Match(subject, body)

    def visitCase_block(self, ctx: Python3Parser.Case_blockContext):
        patterns = ctx.patterns().accept(self)
        guard = ctx.guard().accept(self) if ctx.guard() is not None else None
        body = ctx.block().accept(self)
        return match_case(patterns, guard, body)

    def visitGuard(self, ctx: Python3Parser.GuardContext):
        return ctx.test().accept(self)

    def visitAs_pattern(self, ctx: Python3Parser.As_patternContext):
        or_pattern = ctx.or_pattern().accept(self)
        target = ctx.pattern_capture_target().accept(self)
        return MatchAs(or_pattern, target)

    def visitOr_pattern(self, ctx: Python3Parser.Or_patternContext):
        if len(ctx.closed_pattern()) == 1:
            return ctx.closed_pattern(0).accept(self)

        patterns = list(map(lambda x: x.accept(self), ctx.closed_pattern()))
        return MatchOr(patterns)


    def visitLiteral_pattern(self, ctx: Python3Parser.Literal_patternContext):
        expr = ctx.getChild(0).accept(self)
        return MatchValue(expr)

    def visitCapture_pattern(self, ctx: Python3Parser.Capture_patternContext):
        pattern = ctx.pattern_capture_target().accept(self)
        return MatchAs(name=pattern)

    def visitWildcard_pattern(self, ctx: Python3Parser.Wildcard_patternContext):
        return MatchAs(None)

    def visitSequence_pattern(self, ctx: Python3Parser.Sequence_patternContext):
        from .antlr import Python3Parser
        sequence_patterns = ctx.getChild(0,
                                         (Python3Parser.Maybe_sequence_patternContext,
                                          Python3Parser.Open_sequence_patternContext))
        if sequence_patterns is None:
            return MatchSequence()

        patterns = sequence_patterns.accept(self)
        return MatchSequence(patterns)

    def visitMaybe_sequence_pattern(self, ctx: Python3Parser.Maybe_sequence_patternContext):
        maybe_star_patterns = [maybe_start_pattern.accept(self)
                               for maybe_start_pattern in ctx.maybe_star_pattern()]
        return maybe_star_patterns

    def visitStar_pattern(self, ctx: Python3Parser.Star_patternContext):
        name = ctx.getChild(1).accept(self)
        return MatchStar(name)

    def visitName(self, ctx: Python3Parser.NameContext):
        if ctx.UNDERSCORE() is not None:
            return '_'
        return super().visitName(ctx)

    def visitStrings(self, ctx: Python3Parser.StringsContext):
        strings = [self.cleanup_string(s.accept(self)) for s in ctx.STRING()]
        string = ''.join(strings)
        return Constant(string)

    def __init__(self):
        super().__init__()
        self.context = Load()

    def aggregateResult(self, aggregate, next_result):
        if aggregate is None:
            return next_result

        if isinstance(aggregate, list):
            aggregate.append(next_result)
            return aggregate

        if next_result is None:
            return aggregate

        return [aggregate, next_result]

    def visitChildren(self, ctx):
        children = super().visitChildren(ctx)
        if not isinstance(children, list):
            set_lineno(children, ctx)
        # print(type(ctx).__name__ + " " + str(children))
        return children

    # Visit a parse tree produced by Python3Parser#file_input.
    def visitFile_input(self, ctx: Python3Parser.File_inputContext):
        body = []
        stmts = ctx.stmt()
        n = len(stmts)
        for i in range(n):
            c = stmts[i]
            child_result = c.accept(self)
            body.append(child_result)

        return Module(body, [])

    # Visit a parse tree produced by Python3Parser#decorator.
    def visitDecorator(self, ctx: Python3Parser.DecoratorContext):
        name = ctx.dotted_name().accept(self)
        if '.' in name:
            name = name.split('.')
            attr = name.pop()
            while len(name) > 0:
                attr = Attribute(Name(name.pop(), self.context), attr, self.context)
            name = attr
        if ctx.OPEN_PAREN() is not None:
            args = ctx.arglist().accept(self) if ctx.arglist() is not None else []
            return Call(name, args, [])
        if isinstance(name, Attribute):
            return name
        return Name(name, self.context)

    # Visit a parse tree produced by Python3Parser#decorators.
    def visitDecorators(self, ctx: Python3Parser.DecoratorsContext):
        return list(map(lambda x: x.accept(self), ctx.decorator()))

    # Visit a parse tree produced by Python3Parser#decorated.
    def visitDecorated(self, ctx: Python3Parser.DecoratedContext):
        decorator = ctx.decorators().accept(self)
        decorated = ctx.getChild(1).accept(self)
        decorated.decorator_list = decorator
        return decorated

    # Visit a parse tree produced by Python3Parser#async_funcdef.
    def visitAsync_funcdef(self, ctx: Python3Parser.Async_funcdefContext):
        funcdef = ctx.funcdef()
        name = funcdef.name().accept(self)
        args = funcdef.parameters().accept(self)
        returns = funcdef.test().accept(self) if funcdef.test() is not None else None
        block = funcdef.block().accept(self)

        return AsyncFunctionDef(name, args, block, [], returns=returns)

    # Visit a parse tree produced by Python3Parser#funcdef.
    def visitFuncdef(self, ctx: Python3Parser.FuncdefContext):
        if ctx.name() is not None:
            name = ctx.name().accept(self)
        elif ctx.simple_hole() is not None:
            name = ctx.simple_hole().accept(self)
        else:
            name = ctx.var_hole().accept(self)
        args = ctx.parameters().accept(self)

        returns = ctx.test().accept(self) if ctx.test() is not None else None

        block = ctx.block().accept(self)

        return FunctionDef(name, args, block, [], returns=returns)

    # Visit a parse tree produced by Python3Parser#parameters.
    def visitParameters(self, ctx: Python3Parser.ParametersContext):
        args = ctx.typedargslist()
        return args.accept(self) if args is not None \
            else arguments(posonlyargs=[], args=[], kwonlyargs=[], kw_defaults=[], defaults=[])

    # Visit a parse tree produced by Python3Parser#typedargslist.
    def visitTypedargslist(self, ctx: Python3Parser.TypedargslistContext):
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []
        vararg = None
        kwarg = None
        kw = False

        childs = list(ctx.getChildren())
        while len(childs) > 0:
            c = childs.pop(0)
            if type(c).__name__ == 'TfpdefContext':
                kwonlyargs.append(c.accept(self))
                if kw:
                    kw_defaults.append(None)
            elif type(c).__name__ == 'TestContext':
                if kw:
                    kw_defaults.pop()
                kw_defaults.append(c.accept(self))
            elif c.accept(self) == '*':
                kw = True
                vararg = childs.pop(0).accept(self)
                if vararg == ',':
                    vararg = None
                args = kwonlyargs[::]
                defaults = kw_defaults[::]
                kwonlyargs = []
                kw_defaults = []

            elif c.accept(self) == '**':
                kwarg = childs.pop(0).accept(self)

        if not kw:
            args = kwonlyargs[::]
            defaults = kw_defaults[::]
            kwonlyargs = []
            kw_defaults = []

        return arguments(posonlyargs=[],
                         args=args,
                         vararg=vararg,
                         kwonlyargs=kwonlyargs,
                         kw_defaults=kw_defaults,
                         kwarg=kwarg,
                         defaults=defaults)

    # Visit a parse tree produced by Python3Parser#tfpdef.
    def visitTfpdef(self, ctx: Python3Parser.TfpdefContext):
        if ctx.expr_hole() is not None:
            return ctx.expr_hole().accept(self)
        val = ctx.name().accept(self)
        type_val = ctx.test().accept(self) if ctx.test() is not None else None
        return arg(val, annotation=type_val)

    # Visit a parse tree produced by Python3Parser#varargslist.
    def visitVarargslist(self, ctx: Python3Parser.VarargslistContext):
        args = []
        defaults = []
        kwonlyargs = []
        kw_defaults = []
        vararg = None
        kwarg = None
        kw = False

        childs = list(ctx.getChildren())
        while len(childs) > 0:
            c = childs.pop(0)
            if type(c).__name__ == 'VfpdefContext':
                kwonlyargs.append(c.accept(self))
                if kw:
                    kw_defaults.append(None)
            elif type(c).__name__ == 'TestContext':
                if kw:
                    kw_defaults.pop()
                kw_defaults.append(c.accept(self))
            elif c.accept(self) == '*':
                kw = True
                vararg = childs.pop(0).accept(self)
                if vararg == ',':
                    vararg = None
                args = kwonlyargs[::]
                defaults = kw_defaults[::]
                kwonlyargs = []
                kw_defaults = []

            elif c.accept(self) == '**':
                kwarg = childs.pop(0).accept(self)

        if not kw:
            args = kwonlyargs[::]
            defaults = kw_defaults[::]
            kwonlyargs = []
            kw_defaults = []

        return arguments(
            posonlyargs=[],
            args=args,
            vararg=vararg,
            kwonlyargs=kwonlyargs,
            kw_defaults=kw_defaults,
            kwarg=kwarg,
            defaults=defaults)

    # Visit a parse tree produced by Python3Parser#vfpdef.
    def visitVfpdef(self, ctx: Python3Parser.VfpdefContext):
        return arg(ctx.name().accept(self))

    # Visit a parse tree produced by Python3Parser#simple_stmt.
    def visitSimple_stmts(self, ctx: Python3Parser.Simple_stmtsContext):
        vals = list(map(lambda x: x.accept(self), ctx.simple_stmt()))
        return vals if len(vals) > 1 else vals[0]

    # Visit a parse tree produced by Python3Parser#expr_stmt.
    def visitExpr_stmt(self, ctx: Python3Parser.Expr_stmtContext):

        if ctx.ASSIGN(0) is not None:
            targets = self.visitChildren(ctx)
            value = targets.pop()
            targets = list(filter(lambda x: x != '=', targets))
            return Assign(targets, value)

        target = ctx.testlist_star_expr(0).accept(self)

        if ctx.annassign() is not None:
            values = ctx.annassign().accept(self)
            if len(values) == 1:
                return AnnAssign(target, values[0])

            return AnnAssign(target, values[0], values[1])

        if ctx.augassign() is not None:
            op = ctx.augassign().accept(self)
            val = ctx.getChild(2).accept(self)
            return AugAssign(target, op, val)

        return Expr(target)

    # Visit a parse tree produced by Python3Parser#annassign.
    def visitAnnassign(self, ctx: Python3Parser.AnnassignContext):
        values = []
        tests = ctx.test()

        for i in range(len(tests)):
            c = tests[i]
            child_result = c.accept(self)
            values.append(child_result)

        return values

    # Visit a parse tree produced by Python3Parser#testlist_star_expr.
    def visitTestlist_star_expr(self, ctx: Python3Parser.Testlist_star_exprContext):
        values = self.visitChildren(ctx)
        if not isinstance(values, list):
            return values
        values = list(filter(lambda x: x != ',', values))
        return Tuple(values, self.context)

    # Visit a parse tree produced by Python3Parser#augassign.
    def visitAugassign(self, ctx: Python3Parser.AugassignContext):
        op = ctx.getChild(0).accept(self)
        clazz = operators[op]

        return clazz()

    # Visit a parse tree produced by Python3Parser#del_stmt.
    def visitDel_stmt(self, ctx: Python3Parser.Del_stmtContext):
        prev_ctx = self.context
        self.context = Del()
        exprs = ctx.exprlist().accept(self)
        if not isinstance(exprs, Tuple):
            exprs = [exprs]
        else:
            exprs = exprs.elts
        self.context = prev_ctx
        return Delete(exprs)

    # Visit a parse tree produced by Python3Parser#pass_stmt.
    def visitPass_stmt(self, ctx: Python3Parser.Pass_stmtContext):
        return Pass()

    # Visit a parse tree produced by Python3Parser#flow_stmt.
    def visitFlow_stmt(self, ctx: Python3Parser.Flow_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#break_stmt.
    def visitBreak_stmt(self, ctx: Python3Parser.Break_stmtContext):
        return Break()

    # Visit a parse tree produced by Python3Parser#continue_stmt.
    def visitContinue_stmt(self, ctx: Python3Parser.Continue_stmtContext):
        return Continue()

    # Visit a parse tree produced by Python3Parser#return_stmt.
    def visitReturn_stmt(self, ctx: Python3Parser.Return_stmtContext):
        if ctx.testlist() is None:
            return Return()
        value = ctx.testlist().accept(self)
        return Return(value)

    # Visit a parse tree produced by Python3Parser#yield_stmt.
    def visitYield_stmt(self, ctx: Python3Parser.Yield_stmtContext):
        value = ctx.yield_expr().accept(self)
        return Expr(value)

    # Visit a parse tree produced by Python3Parser#raise_stmt.
    def visitRaise_stmt(self, ctx: Python3Parser.Raise_stmtContext):
        tests = ctx.test()
        if len(tests) == 0:
            return Raise()
        exc = tests[0].accept(self)
        if len(tests) == 2:
            cause = tests[1].accept(self)
            return Raise(exc, cause)

        return Raise(exc)

    # Visit a parse tree produced by Python3Parser#import_name.
    def visitImport_name(self, ctx: Python3Parser.Import_nameContext):
        names = ctx.dotted_as_names().accept(self)
        return Import(names)

    # Visit a parse tree produced by Python3Parser#import_from.
    def visitImport_from(self, ctx: Python3Parser.Import_fromContext):
        level = len(ctx.DOT()) + 3 * len(ctx.ELLIPSIS())
        module = ctx.dotted_name().accept(self) if ctx.dotted_name() is not None else None
        import_as = ctx.import_as_names()
        names = import_as.accept(self) if import_as is not None else [alias("*")]
        return ImportFrom(module, names, level)

    # Visit a parse tree produced by Python3Parser#import_as_name.
    def visitImport_as_name(self, ctx: Python3Parser.Import_as_nameContext):
        names = ctx.name()
        name = names[0].accept(self)
        if len(names) == 2:
            al = names[1].accept(self)
            return alias(name, al)
        return alias(name)

    # Visit a parse tree produced by Python3Parser#dotted_as_name.
    def visitDotted_as_name(self, ctx: Python3Parser.Dotted_as_nameContext):
        name = ctx.dotted_name().accept(self)
        asname_node = ctx.name()
        if asname_node is not None:
            asname = asname_node.accept(self)
            return alias(name, asname)
        return alias(name)

    # Visit a parse tree produced by Python3Parser#import_as_names.
    def visitImport_as_names(self, ctx: Python3Parser.Import_as_namesContext):
        return list(map(lambda x: x.accept(self), ctx.import_as_name()))

    # Visit a parse tree produced by Python3Parser#dotted_as_names.
    def visitDotted_as_names(self, ctx: Python3Parser.Dotted_as_namesContext):
        return list(map(lambda x: x.accept(self), ctx.dotted_as_name()))

    # Visit a parse tree produced by Python3Parser#dotted_name.
    def visitDotted_name(self, ctx: Python3Parser.Dotted_nameContext):
        names = list(map(lambda x: x.accept(self), ctx.name()))
        return '.'.join(names)

    # Visit a parse tree produced by Python3Parser#global_stmt.
    def visitGlobal_stmt(self, ctx: Python3Parser.Global_stmtContext):
        names = []
        name = ctx.name()
        for i in range(len(name)):
            c = name[i]
            child_result = c.accept(self)
            names.append(child_result)

        return Global(names)

    # Visit a parse tree produced by Python3Parser#nonlocal_stmt.
    def visitNonlocal_stmt(self, ctx: Python3Parser.Nonlocal_stmtContext):
        names = []
        name = ctx.name()
        for i in range(len(name)):
            c = name[i]
            child_result = c.accept(self)
            names.append(child_result)

        return Nonlocal(names)

    # Visit a parse tree produced by Python3Parser#assert_stmt.
    def visitAssert_stmt(self, ctx: Python3Parser.Assert_stmtContext):
        tests = ctx.test()
        test = tests[0].accept(self)
        if len(tests) == 2:
            msg = tests[1].accept(self)
            return Assert(test, msg)
        return Assert(test)

    # Visit a parse tree produced by Python3Parser#if_stmt.
    def visitIf_stmt(self, ctx: Python3Parser.If_stmtContext):
        tests = ctx.test()
        blocks = ctx.block()
        if len(blocks) > len(tests):
            cur_block = blocks.pop().accept(self)
        else:
            cur_block = []
        while len(tests) > 0:
            cur_test = tests.pop().accept(self)
            body = blocks.pop().accept(self)
            ifstmt = If(cur_test, body, cur_block)
            cur_block = [ifstmt]

        return cur_block[0]

    # Visit a parse tree produced by Python3Parser#while_stmt.
    def visitWhile_stmt(self, ctx: Python3Parser.While_stmtContext):
        test = ctx.test().accept(self)
        block = ctx.block(0).accept(self)

        if ctx.ELSE() is None:
            return While(test, block, [])

        else_body = ctx.block(1).accept(self)
        return While(test, block, else_body)

    # Visit a parse tree produced by Python3Parser#for_stmt.
    def visitFor_stmt(self, ctx: Python3Parser.For_stmtContext):
        target = ctx.exprlist().accept(self)
        ite = ctx.testlist().accept(self)
        body = ctx.block(0).accept(self)
        orelse = ctx.block(1).accept(self) if ctx.block(1) is not None else []
        return For(target, ite, body, orelse)

    # Visit a parse tree produced by Python3Parser#try_stmt.
    def visitTry_stmt(self, ctx: Python3Parser.Try_stmtContext):
        """
        Visit a parse tree produced by Python3Parser#try_stmt.

        Extracts the try statement's body and exception handlers from the parse tree
        and creates a Try object with these components.

        Args:
            ctx (Python3Parser.Try_stmtContext): The parse tree context for the try statement.

        Returns:
            Try: A Try object with the try statement's body, exception handlers, else block,
            and finally block.
        """
        # Extract the try statement's body and exception handlers from the parse tree
        blocks = ctx.block()
        blocks.reverse()
        body = blocks.pop().accept(self)

        handlers = []
        clauses = ctx.except_clause()
        # Extract each exception handler and its body
        for i in range(len(clauses)):
            c = clauses[i]
            child_result = c.accept(self)
            handler = child_result
            handler.body = blocks.pop().accept(self)
            handlers.append(handler)

        # Check if there are any exception handlers
        if len(handlers) == 0:
            # If not, check if there is a final block
            final = blocks.pop().accept(self)
            return Try(body, handlers, [], final)

        # If there are exception handlers, check if there is an else block
        if len(blocks) == 0:
            return Try(body, handlers, [], [])

        next_body = blocks.pop().accept(self)
        # If there is an else block, extract it
        if ctx.ELSE() is None:
            return Try(body, handlers, [], next_body)
        # If there is no else block, check if there is a finally block
        elif ctx.FINALLY() is None:
            return Try(body, handlers, next_body, [])
        # If there is both an else and finally block, extract the finally block
        else:
            final_body = blocks.pop().accept(self)
            return Try(body, handlers, next_body, final_body)

    # Visit a parse tree produced by Python3Parser#with_stmt.
    def visitWith_stmt(self, ctx: Python3Parser.With_stmtContext):
        items = list(map(lambda x: x.accept(self), ctx.with_item()))
        body = ctx.block().accept(self)
        return With(items, body)

    # Visit a parse tree produced by Python3Parser#with_item.
    def visitWith_item(self, ctx: Python3Parser.With_itemContext):
        ctx_expr = ctx.test().accept(self)
        if ctx.expr() is None:
            return withitem(ctx_expr)

        opt_vars = ctx.expr().accept(self)
        return withitem(ctx_expr, opt_vars)

    # Visit a parse tree produced by Python3Parser#except_clause.
    def visitExcept_clause(self, ctx: Python3Parser.Except_clauseContext):
        if ctx.test() is None:
            return ExceptHandler()

        test = ctx.test().accept(self)
        if ctx.name() is None:
            return ExceptHandler(test)

        name = ctx.name().accept(self)
        return ExceptHandler(test, name)

    # Visit a parse tree produced by Python3Parser#block.
    def visitBlock(self, ctx: Python3Parser.BlockContext):
        if ctx.simple_stmts() is not None:
            stmts = ctx.simple_stmts().accept(self)
            return stmts if isinstance(stmts, list) else [stmts]

        body = []
        stmts = ctx.stmt()
        for i in range(len(stmts)):
            c = stmts[i]
            child_result = c.accept(self)
            if child_result is not None:
                if isinstance(child_result, list):
                    body.extend(child_result)
                else:
                    body.append(child_result)
            else:
                print(type(c))

        return body

    # Visit a parse tree produced by Python3Parser#tests.
    def visitTest(self, ctx: Python3Parser.TestContext):
        if ctx.IF() is not None:
            body = ctx.or_test(0).accept(self)
            test = ctx.or_test(1).accept(self)
            orelse = ctx.test().accept(self)
            return IfExp(test, body, orelse)

        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#lambdef.
    def visitLambdef(self, ctx: Python3Parser.LambdefContext):
        args = ctx.varargslist()
        args = args.accept(self) if args is not None else arguments([], [], None, [], [], None, [])
        body = ctx.test().accept(self)
        return Lambda(args, body)

    # Visit a parse tree produced by Python3Parser#lambdef_nocond.
    def visitLambdef_nocond(self, ctx: Python3Parser.Lambdef_nocondContext):
        args = ctx.varargslist().accept(self)
        body = ctx.test_nocond().accept(self)
        return Lambda(args, body)

    # Visit a parse tree produced by Python3Parser#or_test.
    def visitOr_test(self, ctx: Python3Parser.Or_testContext):
        ors = ctx.and_test()
        n = len(ors)
        if n == 1:
            return self.visitChildren(ctx)

        vals = list(map(lambda x: x.accept(self), ors))
        return BoolOp(Or(), vals)

    # Visit a parse tree produced by Python3Parser#and_test.
    def visitAnd_test(self, ctx: Python3Parser.And_testContext):
        ands = ctx.not_test()
        n = len(ands)
        if n == 1:
            return self.visitChildren(ctx)

        vals = list(map(lambda x: x.accept(self), ands))
        return BoolOp(And(), vals)

    # Visit a parse tree produced by Python3Parser#not_test.
    def visitNot_test(self, ctx: Python3Parser.Not_testContext):
        test = ctx.not_test()
        if test is None:
            return self.visitChildren(ctx)
        return UnaryOp(Not(), test.accept(self))

    # Visit a parse tree produced by Python3Parser#comparison.
    def visitComparison(self, ctx: Python3Parser.ComparisonContext):
        exprs = ctx.expr()
        if len(exprs) == 1:
            return self.visitChildren(ctx)

        tests = ctx.comp_op()
        test = []
        expr = []
        n = len(tests)
        for i in range(n):
            c = tests[i]
            child_result = c.accept(self)
            test.append(child_result)

            c = exprs[i + 1]
            child_result = c.accept(self)
            expr.append(child_result)

        left = exprs[0].accept(self)

        return Compare(left, test, expr)

    # Visit a parse tree produced by Python3Parser#comp_op.
    def visitComp_op(self, ctx: Python3Parser.Comp_opContext):
        op = self.visitChildren(ctx)
        if isinstance(op, list):
            op = ' '.join(op)
        clazz = operators[op]

        return clazz()


    # Visit a parse tree produced by Python3Parser#expr.
    def visitExpr(self, ctx: Python3Parser.ExprContext):
        if ctx.atom_expr() is not None:
            return ctx.atom_expr().accept(self)

        if ctx.getChildCount() == 1:
            return self.visitChildren(ctx)

        exprs = ctx.expr()
        if len(exprs) > 1:
            left = ctx.getChild(0).accept(self)
            op_sign = ctx.getChild(1).accept(self)
            op = operators.get(op_sign)()
            right = ctx.getChild(2).accept(self)

            return BinOp(left, op, right)

        children = list(ctx.getChildren())
        expr = children.pop()
        operand = expr.accept(self)
        while len(children) > 0:
            op_sign = children.pop().accept(self)
            op = operators.get('unary').get(op_sign)()
            operand = UnaryOp(op, operand)

        return operand

    # Visit a parse tree produced by Python3Parser#atom_expr.
    def visitAtom_expr(self, ctx: Python3Parser.Atom_exprContext):
        ret = ctx.atom().accept(self)

        trailers = ctx.trailer()
        for i in range(len(trailers)):
            trail = trailers[i].accept(self)

            if isinstance(trail, Call):
                trail.func = ret
                ret = trail
            else:
                trail.value = ret
                ret = trail

        return ret

    @staticmethod
    def replace_escaped_chars(string):
        # Define a dictionary mapping escaped characters to their corresponding values
        escape_dict = {
            "\\n": "\n",
            "\\r": "\r",
            "\\t": "\t",
            "\\\\": "\\",
            "\\'": "'",
            '\\"': '"'
            # Add more escape sequences here as needed
        }
        # Create a regular expression pattern that matches any escaped character
        escape_pattern = re.compile("|".join(re.escape(key) for key in escape_dict.keys()))
        # Replace all escaped characters with their corresponding values
        return escape_pattern.sub(lambda match: escape_dict[match.group()], string)

    @staticmethod
    def transform_string_to_byte(input_str):
        try:
            # Use eval to interpret the input string as a Python literal
            value = eval(input_str)

            # Check if the value is a bytes-like object (bytes or bytearray)
            if isinstance(value, (bytes, bytearray)):
                # Convert the value to a formatted byte string
                formatted_bytes = b"".join([bytes([byte]) for byte in value])
                return formatted_bytes

            raise ValueError("Input string is not a valid bytes literal.")
        except Exception as e:
            raise ValueError("Error transforming the input string to a byte string.") from e

    @staticmethod
    def convert_escape_sequence(input_string):
        # Decode the string using 'unicode_escape' codec
        output_string = codecs.decode(input_string, 'unicode_escape')
        return output_string

    def cleanup_string(self, string):
        # remove potential '\' at the end of each line
        regex = r"\\\n"
        string = re.sub(regex, "", string, 0, re.MULTILINE)

        if string.startswith('"""') or string.startswith("'''"):
            string = string[3:-3]
            string = self.replace_escaped_chars(string)
        elif string.startswith('"') or string.startswith("'"):
            string = string[1:-1]
            if "\\x" in string:
                string = self.convert_escape_sequence(string)
            string = self.replace_escaped_chars(string)
        elif string.startswith('b'):
            string = self.transform_string_to_byte(string.encode())
        elif string.startswith('r'):
            string = string[2:-1]

        return string

    # Visit a parse tree produced by Python3Parser#atom.
    def visitAtom(self, ctx: Python3Parser.AtomContext):
        if ctx.name() is not None:
            return Name(ctx.name().accept(self), self.context)

        if ctx.NUMBER() is not None:
            num = ctx.NUMBER().accept(self).lower()
            if '.' in num or 'e' in num:
                return Constant(float(num))
            base = 10
            if len(num) > 2 and num[0] == '0':
                b = num[1]
                if b == 'b':
                    base = 2
                elif b == 'o':
                    base = 8
                elif b == 'x':
                    base = 16
            return Constant(int(num, base))

        if len(ctx.STRING()) > 0:
            if len(ctx.STRING()) == 1:
                string = ctx.STRING(0).accept(self)
                string = self.cleanup_string(string)
            else:
                strings = [self.cleanup_string(s.accept(self)) for s in ctx.STRING()]
                string = ''.join(strings)

            return Constant(string)

        if ctx.ELLIPSIS() is not None:
            return Constant(...)

        if ctx.NONE() is not None:
            return Constant(None)

        if ctx.TRUE() is not None:
            return Constant(True)

        if ctx.FALSE() is not None:
            return Constant(False)

        if ctx.OPEN_PAREN() is not None:
            if ctx.testlist_comp() is not None:
                val = ctx.testlist_comp().accept(self)
                if isinstance(val, List):
                    val = val.elts
                elif isinstance(val, ListComp):
                    return GeneratorExp(elt=val.elt, generators=val.generators)
            elif ctx.yield_expr() is not None:
                val = ctx.yield_expr().accept(self)
            else:
                val = []
            if isinstance(val, list):
                return Tuple(elts=val, ctx=self.context)
            return val

        if ctx.OPEN_BRACK() is not None:
            val = ctx.testlist_comp().accept(self) if ctx.testlist_comp() is not None \
                else List(elts=[], ctx=self.context)
            if not isinstance(val, List) and not isinstance(val, ListComp):
                val = List(elts=[val], ctx=self.context)
            return val

        if ctx.OPEN_BRACE() is not None:
            val = ctx.dictorsetmaker().accept(self) if ctx.dictorsetmaker() is not None \
                else Dict(keys=[], values=[])
            return val

        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#testlist_comp.
    def visitTestlist_comp(self, ctx: Python3Parser.Testlist_compContext):
        if ctx.comp_for() is not None:
            comp = ctx.comp_for().accept(self)
            elt = ctx.getChild(0).accept(self)
            return ListComp(elt=elt, generators=comp)
        vals = self.visitChildren(ctx)
        if isinstance(vals, list):
            vals = list(filter(lambda x: x != ',', vals))
            return List(elts=vals, ctx=self.context)
        return vals

    # Visit a parse tree produced by Python3Parser#trailer.
    def visitTrailer(self, ctx: Python3Parser.TrailerContext):
        prev_ctx = self.context
        self.context = Load()
        if ctx.subscriptlist() is not None:
            val = ctx.subscriptlist().accept(self)
            return Subscript(value=None, slice=val, ctx=self.context)

        if ctx.name() is not None:
            val = ctx.name().accept(self)
            return Attribute(value=None, attr=val, ctx=self.context)

        if ctx.arglist() is not None:
            allargs = ctx.arglist().accept(self)

            # Filter args and keywords
            keywords = list(filter(lambda x: isinstance(x, keyword), allargs))
            args = list(filter(lambda x: x not in keywords, allargs))

            return Call(args=args, keywords=keywords)

        return Call(args=[], keywords=[])

    # Visit a parse tree produced by Python3Parser#subscriptlist.
    def visitSubscriptlist(self, ctx: Python3Parser.SubscriptlistContext):
        prev_ctx = self.context
        self.context = Load()
        if ctx.getChildCount() > 1:
            subscriptlist = list(map(lambda x: x.accept(self), ctx.subscript_()))
            self.context = prev_ctx
            return Tuple(subscriptlist, self.context)

        subscript = ctx.subscript_(0).accept(self)
        self.context = prev_ctx
        return subscript

    # Visit a parse tree produced by Python3Parser#subscript.
    def visitSubscript_(self, ctx: Python3Parser.Subscript_Context):
        if ctx.COLON() is not None:
            lower = None
            step = ctx.sliceop().accept(self) if ctx.sliceop() is not None else None

            if ctx.getChild(0) == ctx.test(0):
                lower = ctx.test(0).accept(self)
                upper = ctx.test(1).accept(self) if len(ctx.test()) > 1 else None
            else:
                upper = ctx.test(0).accept(self) if len(ctx.test()) > 0 else None

            return Slice(lower=lower, upper=upper, step=step)

        return self.visitChildren(ctx)


    # Visit a parse tree produced by Python3Parser#exprlist.
    def visitExprlist(self, ctx: Python3Parser.ExprlistContext):
        vals = self.visitChildren(ctx)
        if isinstance(vals, list):
            vals = list(filter(lambda x: x != ',', vals))
            return Tuple(elts=vals, ctx=self.context)
        return vals

    # Visit a parse tree produced by Python3Parser#testlist.
    def visitTestlist(self, ctx: Python3Parser.TestlistContext):
        vals = list(map(lambda x: x.accept(self), ctx.test()))
        return Tuple(vals, self.context) if len(vals) > 1 else vals[0]

    # Visit a parse tree produced by Python3Parser#dictorsetmaker.
    def visitDictorsetmaker(self, ctx: Python3Parser.DictorsetmakerContext):
        if len(ctx.COLON()) > 0:
            # we have a dict
            if ctx.comp_for() is not None:
                # we have a dict comprehension
                comp = ctx.comp_for().accept(self)
                keys = ctx.test(0).accept(self)
                values = ctx.test(1).accept(self)
                return DictComp(key=keys, value=values, generators=comp)

            tests = list(map(lambda x: x.accept(self), ctx.test()))
            keys = tests[::2]
            values = tests[1::2]
            return Dict(keys=keys, values=values)

        # we have a set
        if ctx.comp_for() is not None:
            # we have a set comprehension
            comp = ctx.comp_for().accept(self)
            elt = ctx.test(0).accept(self)
            return SetComp(elt=elt, generators=comp)

        vals = self.visitChildren(ctx)
        if not isinstance(vals, list):
            vals = [vals]
        else:
            vals = list(filter(lambda x: x != ',', vals))
        return Set(elts=vals)

    # Visit a parse tree produced by Python3Parser#classdef.
    def visitClassdef(self, ctx: Python3Parser.ClassdefContext):
        if ctx.name() is not None:
            name = ctx.name().accept(self)
        elif ctx.simple_hole() is not None:
            name = ctx.simple_hole().accept(self)
        else:
            name = ctx.var_hole().accept(self)
        args = ctx.arglist()
        args = args.accept(self) if args is not None else []
        body = ctx.block().accept(self)
        return ClassDef(name, args, [], body, [])

    # Visit a parse tree produced by Python3Parser#arglist.
    def visitArglist(self, ctx: Python3Parser.ArglistContext):
        return list(map(lambda x: x.accept(self), ctx.argument()))

    # Visit a parse tree produced by Python3Parser#argument.
    def visitArgument(self, ctx: Python3Parser.ArgumentContext):
        if ctx.STAR() is not None:
            return Starred(value=ctx.test(0).accept(self), ctx=self.context)

        if ctx.POWER() is not None:
            return keyword(value=ctx.test(0).accept(self))

        if ctx.ASSIGN() is not None:
            key = ctx.test(0).accept(self)
            key = key.id if isinstance(key, Name) else key.value
            return keyword(arg=key, value=ctx.test(1).accept(self))

        if ctx.comp_for() is not None:
            generator = ctx.comp_for().accept(self)
            elt = ctx.test(0).accept(self)
            return GeneratorExp(elt=elt, generators=generator)

        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_iter.
    def visitComp_iter(self, ctx: Python3Parser.Comp_iterContext):
        vals = self.visitChildren(ctx)
        return vals

    # Visit a parse tree produced by Python3Parser#comp_for.
    def visitComp_for(self, ctx: Python3Parser.Comp_forContext):
        target = ctx.exprlist().accept(self)
        iter_val = ctx.or_test().accept(self)
        is_async = 1 if ctx.ASYNC() is not None else 0

        ret = []
        ifs = []
        next_comp = ctx.comp_iter()
        if next_comp is not None:
            next_comp = next_comp.accept(self)
            for comp in next_comp:
                if isinstance(comp, comprehension):
                    ret.append(comp)
                else:
                    ifs.append(comp)
        return [comprehension(target=target, iter=iter_val, ifs=ifs, is_async=is_async)] + ret

    # Visit a parse tree produced by Python3Parser#comp_if.
    def visitComp_if(self, ctx: Python3Parser.Comp_ifContext):
        test = ctx.test_nocond().accept(self)
        next_comp = ctx.comp_iter().accept(self) if ctx.comp_iter() is not None else []

        return [test] + next_comp

    # Visit a parse tree produced by Python3Parser#yield_expr.
    def visitYield_expr(self, ctx: Python3Parser.Yield_exprContext):
        if ctx.yield_arg() is not None:
            return ctx.yield_arg().accept(self)
        return Yield(None)

    # Visit a parse tree produced by Python3Parser#yield_arg.
    def visitYield_arg(self, ctx: Python3Parser.Yield_argContext):
        if ctx.FROM() is not None:
            return YieldFrom(ctx.test().accept(self))
        return Yield(ctx.testlist().accept(self))

    def visitTerminal(self, node):
        txt = node.getText()
        if txt.isspace():
            return None
        return txt

    def visitHole_type(self, ctx:Python3Parser.Hole_typeContext):
        return list(map(lambda x: x.accept(self), ctx.name()))

    # Visit a parse tree produced by Python3Parser#simple_hole.
    def visitSimple_hole(self, ctx: Python3Parser.Simple_holeContext):
        types = None
        if ctx.hole_type() is not None:
            types = ctx.hole_type().accept(self)
        hole = SimpleHole(types)
        set_lineno(hole, ctx)
        return hole

    # Visit a parse tree produced by Python3Parser#double_hole.
    def visitDouble_hole(self, ctx: Python3Parser.Double_holeContext):
        types = None
        if ctx.hole_type() is not None:
            types = ctx.hole_type().accept(self)
        hole = DoubleHole(types)
        set_lineno(hole, ctx)
        return hole

    def visitVar_hole(self, ctx: Python3Parser.Var_holeContext):
        types = None
        if ctx.hole_type() is not None:
            types = ctx.hole_type().accept(self)
        name = ctx.name().accept(self)
        hole = VarHole(name, types)
        set_lineno(hole, ctx)
        return hole

    def visitSimple_compound_hole(self, ctx: Python3Parser.Simple_compound_holeContext):
        types = None
        if ctx.hole_type() is not None:
            types = ctx.hole_type().accept(self)
        body = ctx.block().accept(self)
        hole = CompoundHole(body, types)
        set_lineno(hole, ctx)
        return hole

    def visitMultiple_compound_hole(self, ctx: Python3Parser.Multiple_compound_holeContext):
        types = None
        if ctx.hole_type() is not None:
            types = ctx.hole_type().accept(self)
        body = ctx.block().accept(self)
        hole = MultipleCompoundHole(body, types)
        set_lineno(hole, ctx)
        return hole

    def visitStrict_mode(self, ctx: Python3Parser.Strict_modeContext):
        body = self.visitChildren(ctx)
        hole = StrictMode(body, True)
        set_lineno(hole, ctx)

        end_hole = StrictMode(None, False)
        set_lineno(hole, ctx)
        return [hole, end_hole]


del Python3Parser
