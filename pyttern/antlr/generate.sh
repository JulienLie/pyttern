python transformGrammar.py
echo "Generating lexer and parser"
antlr4 -Dlanguage=Python3 -visitor *.g4
echo "Done!"