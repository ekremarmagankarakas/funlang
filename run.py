import os
from token import BuiltInFunctionType as BT
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction

global_symbol_table = SymbolTable()
global_symbol_table.set(BT.PRINT.value, BuiltInFunction("print"))
global_symbol_table.set(BT.CLEAR.value, BuiltInFunction("clear"))
global_symbol_table.set(BT.IS_STRING.value, BuiltInFunction("is_string"))
global_symbol_table.set(BT.IS_NUMBER.value, BuiltInFunction("is_number"))
global_symbol_table.set(BT.IS_FUN.value, BuiltInFunction("is_fun"))
global_symbol_table.set(BT.IS_LIST.value, BuiltInFunction("is_list"))
global_symbol_table.set(BT.LEN.value, BuiltInFunction("len"))
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


def run_file(file_path):
  if not file_path.endswith('.fl'):
    return None, None, None, "File must have a .fl extension"
  
  try:
    with open(file_path, 'r') as file:
      source = file.read()
    
    file_name = os.path.basename(file_path)
    return run(file_name, source)
  except FileNotFoundError:
    return None, None, None, f"File '{file_path}' not found"
  except Exception as e:
    return None, None, None, f"Error reading file: {str(e)}"
