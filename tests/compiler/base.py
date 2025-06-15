import subprocess
from src.parser import Parser
from src.lexer import Lexer
from src.codegen import CodeGenerator


def run_compiled_code(llvm_ir):
    with open('temp.ll', 'w') as f:
        f.write(llvm_ir)

    subprocess.run(['llc', '-filetype=obj', 'temp.ll', '-o', 'temp.o'])
    subprocess.run(['clang', 'temp.o', '-o', 'temp_executable', '-lm'])

    result = subprocess.run(['./temp_executable'],
                            capture_output=True, text=True)
    return result.stdout.strip(), result.stderr


def compile_test(source):
    lexer = Lexer("<stdin>", source)
    tokens, error = lexer.tokenizer()
    if error:
        raise Exception(f"Lexer error: {error.as_string()}")

    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        raise Exception(f"Parser error: {ast.error.as_string()}")

    codegen = CodeGenerator()
    llvm_ir = codegen.generate(ast.node)
    return llvm_ir
