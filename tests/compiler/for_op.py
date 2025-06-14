import os
from tests.compiler.base import compile_test, run_compiled_code

for_test = "for i=0, 6 { var j = i; }; print(j);"

for_tests = (
    f"{for_test}\n"
)

expected_for_output = (
    "5\n"
)

llvm_ir_for = compile_test(for_tests)
compiled_for_output, compile_for_error = run_compiled_code(llvm_ir_for)
assert compiled_for_output == expected_for_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
