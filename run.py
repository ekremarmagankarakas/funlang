from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction

global_symbol_table = SymbolTable()
global_symbol_table.set("print", BuiltInFunction("print"))
global_symbol_table.set("null", Number(0))
global_symbol_table.set("false", Number(0))
global_symbol_table.set("true", Number(1))


def run(file_name, source):
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    return None, None, None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error:
    return None, None, tokens, ast.error

  interpreter = Interpreter()
  context = Context("<program>")
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  return result.value, ast.node, tokens, result.error
