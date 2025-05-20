from lexer import Lexer
from parser import Parser


def run(file_name, source):
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    return None, error
  # return tokens, None

  parser = Parser(tokens)
  ast = parser.parse()

  return ast, None
