from lexer import Lexer

source = "not 0"
file_name = "tests/lexer_test.py"
lexer = Lexer(file_name, source)
tokens, error = lexer.tokenizer()

if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)

