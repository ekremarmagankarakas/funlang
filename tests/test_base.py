from lexer import Lexer
from parser import Parser
from interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction
from token import BuiltInFunctionType as BT

global_symbol_table = SymbolTable()
global_symbol_table.set(BT.PRINT.value, BuiltInFunction("print"))
global_symbol_table.set(BT.CLEAR.value, BuiltInFunction("clear"))
global_symbol_table.set(BT.IS_STRING.value, BuiltInFunction("is_string"))
global_symbol_table.set(BT.IS_NUMBER.value, BuiltInFunction("is_number"))
global_symbol_table.set(BT.IS_FUN.value, BuiltInFunction("is_fun"))
global_symbol_table.set(BT.IS_LIST.value, BuiltInFunction("is_list"))
global_symbol_table.set(BT.LEN.value, BuiltInFunction("len"))
global_symbol_table.set(BT.TO_STRING.value, BuiltInFunction("to_string"))
global_symbol_table.set(BT.TO_INT.value, BuiltInFunction("to_int"))
global_symbol_table.set(BT.TO_FLOAT.value, BuiltInFunction("to_float"))
global_symbol_table.set(BT.TO_LIST.value, BuiltInFunction("to_list"))
global_symbol_table.set("null", Number(0))
global_symbol_table.set("false", Number(0))
global_symbol_table.set("true", Number(1))


def test(source):
  file_name = '<stdin>'
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    print(f"Lexer error: {error.as_string()}")
    return False

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error:
    print(f"Parser error: {ast.error.as_string()}")
    return False

  interpreter = Interpreter()
  context = Context("<program>")
  context.symbol_table = global_symbol_table
  result = interpreter.visit(ast.node, context)

  if result.error:
    print(f"Interpreter error: {result.error.as_string()}")
    return False

  return result.value
