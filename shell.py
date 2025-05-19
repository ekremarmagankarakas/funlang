import lexer

while True:
  source = input('funlang > ')
  if source == 'exit':
    break
  tokens, error = lexer.run('<stdin>', source)
  if error:
    print(error.as_string())
  else:
    print("Tokens:", tokens)
