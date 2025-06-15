from src.lexer import Lexer
from src.parser import Parser

source = "fun int add(a, b) { return a + b; }; var result = add(2, 3); result;"
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
