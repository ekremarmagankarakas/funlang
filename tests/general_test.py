from lexer import Lexer
from parser import Parser

code = "fun greet(x) { yell(x + 2); }"

functioncall = "fun main() { greet(7); }"

lexer = Lexer(code)
tokens = lexer.tokenizer()
print("Tokens:", tokens)

parser = Parser(tokens)
program = parser.parse()
print("Parsed Program:", program)
