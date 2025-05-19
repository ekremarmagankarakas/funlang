from lexer import Lexer

code = "fun greet(x) { yell(x + 2); }"
lexer = Lexer("<stdin>", code)
tokens, error = lexer.tokenizer()

if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)


multiline_test = '''
fun main()
{ yell(x + 2); }
'''
lexer = Lexer("<stdin>", multiline_test)
tokens, error = lexer.tokenizer()

if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)


error_test = "fun main() { yell(@); }"
lexer = Lexer("<stdin>", error_test)
tokens, error = lexer.tokenizer()

if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)

multiline_error = '''
fun main()
{ yell(@); }
'''

lexer = Lexer("<stdin>", multiline_error)
tokens, error = lexer.tokenizer()
if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)


multiline_error2 = '''
fun main()
{
greet(x + 2);
yell(@);
}
'''

lexer = Lexer("<stdin>", multiline_error2)
tokens, error = lexer.tokenizer()
if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)


unterminated_string = '"fun main() { yell("Hello"); }'
lexer = Lexer("<stdin>", unterminated_string)
tokens, error = lexer.tokenizer()
if error:
  print(error.as_string())
else:
  print("Tokens:", tokens)
