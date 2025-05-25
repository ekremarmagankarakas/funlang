from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context


def run(file_name, source):
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    return None, None, None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error:
    return None, None, None, ast.error

  interpreter = Interpreter()
  context = Context("<program>")
  result = interpreter.visit(ast.node, context)

  return result.value, ast.node, tokens, result.error
