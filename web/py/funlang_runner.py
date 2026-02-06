import io
import os
import sys

from src.config import LanguageConfig
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, Context, SymbolTable, Number, BuiltInFunction


def _create_global_symbol_table(config):
    symbol_table = SymbolTable()
    builtin_names = config.config["builtins"]

    symbol_table.set(builtin_names["print"], BuiltInFunction("print"))
    symbol_table.set(builtin_names["clear"], BuiltInFunction("clear"))
    symbol_table.set(builtin_names["is_string"], BuiltInFunction("is_string"))
    symbol_table.set(builtin_names["is_number"], BuiltInFunction("is_number"))
    symbol_table.set(builtin_names["is_fun"], BuiltInFunction("is_fun"))
    symbol_table.set(builtin_names["is_list"], BuiltInFunction("is_list"))
    symbol_table.set(builtin_names["len"], BuiltInFunction("len"))
    symbol_table.set(builtin_names["to_string"], BuiltInFunction("to_string"))
    symbol_table.set(builtin_names["to_int"], BuiltInFunction("to_int"))
    symbol_table.set(builtin_names["to_float"], BuiltInFunction("to_float"))
    symbol_table.set(builtin_names["to_list"], BuiltInFunction("to_list"))
    symbol_table.set(builtin_names["typeof"], BuiltInFunction("typeof"))
    symbol_table.set(builtin_names["elos"], BuiltInFunction("elos"))

    symbol_table.set("null", Number(0))
    symbol_table.set("false", Number(0))
    symbol_table.set("true", Number(1))

    return symbol_table


def eval_funlang(source, config_path=None):
    """Evaluate FunLang source code.

    Returns a dict: {stdout: str, result: str|None, error: str|None}
    """

    os.environ["FUNLANG_BROWSER"] = "1"

    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = buf
    try:
        config = LanguageConfig(config_path) if config_path else LanguageConfig()

        lexer = Lexer("<stdin>", source, config)
        tokens, error = lexer.tokenizer()
        if error:
            err_str = error if isinstance(error, str) else error.as_string()
            return {"stdout": buf.getvalue(), "result": None, "error": err_str}

        parser = Parser(tokens, config)
        ast = parser.parse()
        if ast.error:
            err_str = ast.error if isinstance(ast.error, str) else ast.error.as_string()
            return {"stdout": buf.getvalue(), "result": None, "error": err_str}

        interpreter = Interpreter()
        context = Context("<program>")
        context.symbol_table = _create_global_symbol_table(config)
        result = interpreter.visit(ast.node, context)

        if result.error:
            err_str = (
                result.error
                if isinstance(result.error, str)
                else result.error.as_string()
            )
            return {"stdout": buf.getvalue(), "result": None, "error": err_str}

        result_value = result.value
        result_str = None if result_value is None else str(result_value)
        return {"stdout": buf.getvalue(), "result": result_str, "error": None}
    finally:
        sys.stdout = old_stdout


# Make it easy to grab from JS via pyodide.globals.get(...)
__all__ = ["eval_funlang"]
