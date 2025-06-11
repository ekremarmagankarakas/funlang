from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number

global_symbol_table = SymbolTable()
global_symbol_table.set("null", Number(0))
global_symbol_table.set("false", Number(0))
global_symbol_table.set("true", Number(1))


def test(source):
  file_name = '<stdin>'
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    print(f"Lexer error: {error}")
    return False

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error:
    print(f"Parser error: {ast.error}")
    return False

  interpreter = Interpreter()
  context = Context("<program>")
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  if result.error:
    print(f"Interpreter error: {result.error}")
    return False

  return result.value
