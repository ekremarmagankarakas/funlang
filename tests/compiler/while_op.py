import os
from tests.compiler.base import compile_test, run_compiled_code

while_test = "var j = 0; var i = 0; while i!=6 { j = i; i = i + 1 }; print(j);"
while_break_test = "var j = 0; var i = 0; while i!=6 { if i == 3 { break; }; j = i; i = i + 1 }; print(j);"
while_continue_test = "var j = 0; var i = 0; while i!=6 { i = i + 1; if i == 3 { continue; }; j = i; }; print(j);"

while_tests = (
    f"{while_test}\n"
    f"{while_break_test}\n"
    f"{while_continue_test}\n"
)

expected_while_output = (
    "5\n"
    "2\n"
    "6\n"
)

llvm_ir_while = compile_test(while_tests)
compiled_while_output, compile_while_error = run_compiled_code(llvm_ir_while)
assert compiled_while_output == expected_while_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
