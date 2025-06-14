import os
from src.token import BuiltInFunctionType as BT
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction
from src.codegen import CodeGenerator

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
global_symbol_table.set(BT.TYPEOF.value, BuiltInFunction("typeof"))
global_symbol_table.set(BT.ELOS.value, BuiltInFunction("elos"))
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


def compile_to_llvm(file_name, source):
  lexer = Lexer(file_name, source)
  tokens, error = lexer.tokenizer()
  if error:
    return None, None, None, error

  parser = Parser(tokens)
  ast = parser.parse()
  if ast.error:
    return None, None, tokens, ast.error

  codegen = CodeGenerator()
  try:
    llvm_ir = codegen.generate(ast.node)
    return llvm_ir, ast.node, tokens, None
  except Exception as e:
    return None, ast.node, tokens, f"Code generation error: {str(e)}"


def compile_file(file_path):
  if not file_path.endswith('.fl'):
    return None, None, None,

  try:
    with open(file_path, 'r') as file:
      source = file.read()

    file_name = os.path.basename(file_path)
    return compile_to_llvm(file_name, source)
  except FileNotFoundError:
    return None, None, None, f"File '{file_path}' not found"
  except Exception as e:
    return None, None, None, f"Error reading file: {str(e)}"


def build_executable(file_path):
  import subprocess
  
  if not file_path.endswith('.fl'):
    return None,
  
  try:
    llvm_ir, ast, tokens, error = compile_file(file_path)
    if error:
      return None, error
    
    base_name = file_path.replace('.fl', '')
    ll_file = f"{base_name}.ll"
    obj_file = f"{base_name}.o"
    exe_file = base_name
    
    with open(ll_file, 'w') as f:
      f.write(llvm_ir)
    
    llc_result = subprocess.run(['llc', '-filetype=obj', ll_file, '-o', obj_file], 
                               capture_output=True, text=True)
    if llc_result.returncode != 0:
      return None, f"LLC error: {llc_result.stderr}"
    
    clang_result = subprocess.run(['clang', obj_file, '-o', exe_file], 
                                 capture_output=True, text=True)
    if clang_result.returncode != 0:
      return None, f"Clang error: {clang_result.stderr}"
    
    os.remove(ll_file)
    os.remove(obj_file)
    
    return exe_file, None
    
  except FileNotFoundError:
    return None, f"File '{file_path}' not found"
  except Exception as e:
    return None, f"Build error: {str(e)}"


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
