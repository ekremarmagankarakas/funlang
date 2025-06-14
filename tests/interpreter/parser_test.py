from lexer import Lexer
from parser import Parser

source = "not 0"
file_name = "tests/lexer_test.py"
lexer = Lexer(file_name, source)
tokens, error = lexer.tokenizer()
if error:
  print(error.as_string())

parser = Parser(tokens)
ast = parser.parse()
if ast.error:
  print(ast.error.as_string())
else:
  print("AST:", ast.node)
