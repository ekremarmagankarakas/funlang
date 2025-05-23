from lexer import Lexer
from parser import Parser


def run(file_name, source):
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    return None, None, error

  parser = Parser(tokens)
  result = parser.parse()

  return result.node, tokens, result.error
