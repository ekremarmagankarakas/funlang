# run.py
import os
from src.token import BuiltInFunctionType as BT
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction
from src.codegen import CodeGenerator
from src.config import LanguageConfig


def create_global_symbol_table(config):
    """Create a global symbol table with builtin functions using custom names from config"""
    symbol_table = SymbolTable()
    
    # Get custom builtin names from config
    builtin_names = config.config['builtins']
    
    # Register builtin functions with their custom names
    symbol_table.set(builtin_names['print'], BuiltInFunction("print"))
    symbol_table.set(builtin_names['clear'], BuiltInFunction("clear"))
    symbol_table.set(builtin_names['is_string'], BuiltInFunction("is_string"))
    symbol_table.set(builtin_names['is_number'], BuiltInFunction("is_number"))
    symbol_table.set(builtin_names['is_fun'], BuiltInFunction("is_fun"))
    symbol_table.set(builtin_names['is_list'], BuiltInFunction("is_list"))
    symbol_table.set(builtin_names['len'], BuiltInFunction("len"))
    symbol_table.set(builtin_names['to_string'], BuiltInFunction("to_string"))
    symbol_table.set(builtin_names['to_int'], BuiltInFunction("to_int"))
    symbol_table.set(builtin_names['to_float'], BuiltInFunction("to_float"))
    symbol_table.set(builtin_names['to_list'], BuiltInFunction("to_list"))
    symbol_table.set(builtin_names['typeof'], BuiltInFunction("typeof"))
    symbol_table.set(builtin_names['elos'], BuiltInFunction("elos"))
    
    # Register constants
    symbol_table.set("null", Number(0))
    symbol_table.set("false", Number(0))
    symbol_table.set("true", Number(1))
    
    return symbol_table


def run(file_name, source, config=None):
    """Run FunLang code with optional custom configuration"""
    if config is None:
        config = LanguageConfig()
    
    lexer = Lexer(file_name, source, config)
    tokens, error = lexer.tokenizer()
    if error:
        return None, None, None, error

    parser = Parser(tokens, config)
    ast = parser.parse()
    if ast.error:
        return None, None, tokens, ast.error

    interpreter = Interpreter()
    context = Context("<program>")
    # Create symbol table with custom builtin names
    context.symbol_table = create_global_symbol_table(config)
    result = interpreter.visit(ast.node, context)

    return result.value, ast.node, tokens, result.error


def compile_to_llvm(file_name, source, config=None):
    """Compile FunLang code to LLVM IR with optional custom configuration"""
    if config is None:
        config = LanguageConfig()
    
    lexer = Lexer(file_name, source, config)
    tokens, error = lexer.tokenizer()
    if error:
        return None, None, None, error

    parser = Parser(tokens, config)
    ast = parser.parse()
    if ast.error:
        return None, None, tokens, ast.error

    codegen = CodeGenerator()
    try:
        llvm_ir = codegen.generate(ast.node)
        return llvm_ir, ast.node, tokens, None
    except Exception as e:
        return None, ast.node, tokens, f"Code generation error: {str(e)}"


def compile_file(file_path, config=None):
    """Compile a FunLang file with optional custom configuration"""
    if not file_path.endswith('.fl'):
        return None, None, None, "File must have a .fl extension"

    try:
        with open(file_path, 'r') as file:
            source = file.read()

        file_name = os.path.basename(file_path)
        return compile_to_llvm(file_name, source, config)
    except FileNotFoundError:
        return None, None, None, f"File '{file_path}' not found"
    except Exception as e:
        return None, None, None, f"Error reading file: {str(e)}"


def build_executable(file_path, config=None):
    """Build an executable from a FunLang file with optional custom configuration"""
    import subprocess

    if not file_path.endswith('.fl'):
        return None, "File must have a .fl extension"

    try:
        llvm_ir, ast, tokens, error = compile_file(file_path, config)
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

        clang_result = subprocess.run(['clang', obj_file, '-o', exe_file, '-lm'],
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


def run_file(file_path, config=None):
    """Run a FunLang file with optional custom configuration"""
    if not file_path.endswith('.fl'):
        return None, None, None, "File must have a .fl extension"

    try:
        with open(file_path, 'r') as file:
            source = file.read()

        file_name = os.path.basename(file_path)
        return run(file_name, source, config)
    except FileNotFoundError:
        return None, None, None, f"File '{file_path}' not found"
    except Exception as e:
        return None, None, None, f"Error reading file: {str(e)}"
