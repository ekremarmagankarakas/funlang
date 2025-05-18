from lexer import Lexer
from parser import Parser

code = "fun greet(x) { yell(x + 2); }"


lexer = Lexer(code)
tokens = lexer.tokenizer()
print("Tokens:", tokens)

parser = Parser(tokens)
program = parser.parse()
print("Parsed Program:", program)
