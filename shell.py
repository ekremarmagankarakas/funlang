from run import run as run_shell

while True:
  source = input('funlang > ')
  if source == 'exit':
    break

  interpreter, ast, tokens, error = run_shell('<stdin>', source)

  if error:
    print(error.as_string())

  print("Tokens:", tokens)
  print("AST:", ast)
  print("Result:", interpreter)
