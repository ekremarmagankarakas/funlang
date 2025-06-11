#!/usr/bin/env python3
import sys
from run import run_file, run


def main():
  # No arguments - run the shell
  if len(sys.argv) == 1:
    print("FunLang Shell - Type 'exit' to quit")
    while True:
      source = input('funlang > ')
      if source.lower() == 'exit':
        break

      result, ast, tokens, error = run('<stdin>', source)

      if error:
        print(error.as_string())
      else:
        print("Result:", result)

  # Run a file
  elif len(sys.argv) == 2:
    file_path = sys.argv[1]
    result, ast, tokens, error = run_file(file_path)

    if error:
      if isinstance(error, str):
        print(f"Error: {error}")
      else:
        print(error.as_string())
      sys.exit(1)

    if result is not None:
      print(result)

  # Invalid usage
  else:
    print("Usage: python main.py [file.fl]")
    sys.exit(1)


if __name__ == "__main__":
  main()

