from lexer import Lexer

code = "fun greet(x) { yell(x + 2); }"


lexer = Lexer(code)
tokens = lexer.tokenizer()
print("Tokens:", tokens)
