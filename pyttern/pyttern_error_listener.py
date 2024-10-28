"""
This module contains the Python3ErrorListener class.
"""

from antlr4.error.ErrorListener import ErrorListener


class Python3ErrorListener(ErrorListener):
    """
    Python3ErrorListener class is responsible for handling syntax errors in the input pyttern file.
    """
    def __init__(self, output):
        self.output = output
        self._symbol = ''
        self._line = -1

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        """
        Syntax error handler.
        """
        new_msg = f"Syntax error at {line}:{column} ({offendingSymbol.text}) : {msg}\n"
        print(new_msg, end='')
        if self._line == -1:
            self.output.write(msg)
            self._symbol = offendingSymbol.text
            self._line = line
            stack = recognizer.getRuleInvocationStack()
            stack.reverse()

    @property
    def symbol(self):
        """Symbol getter."""
        return self._symbol

    @property
    def line(self):
        """Line getter."""
        return self._line
