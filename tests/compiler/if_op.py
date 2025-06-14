import os
from tests.compiler.base import compile_test, run_compiled_code

''' If Operations Tests '''
if_test = "var a = 3; var case = 0; if case == 0 { a = 0; } elif case == 1 { a = 1; } else { a = 2; }; print(a)"
elif_test = "var a = 3; var case = 1; if case == 0 { a = 0; } elif case == 1 { a = 1; } else { a = 2; }; print(a)"
else_test = "var a = 3; var case = 2; if case == 0 { a = 0; } elif case == 1 { a = 1; } else { a = 2; }; print(a)"

if_tests = (
    f"{if_test}\n"
    f"{elif_test}\n"
    f"{else_test}\n"
)

expected_if_output = (
    "0\n"
    "1\n"
    "2\n"
)

llvm_ir_if = compile_test(if_tests)
compiled_if_output, compile_if_error = run_compiled_code(llvm_ir_if)
assert compiled_if_output == expected_if_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
