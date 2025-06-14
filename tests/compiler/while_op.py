import os
from tests.compiler.base import compile_test, run_compiled_code

while_test = "var j = 0; var i = 0; while i!=6 { j = i; i = i + 1 }; print(j);"

while_tests = (
    f"{while_test}\n"
)

expected_while_output = (
    "5\n"
)

llvm_ir_while = compile_test(while_tests)
compiled_while_output, compile_while_error = run_compiled_code(llvm_ir_while)
assert compiled_while_output == expected_while_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
