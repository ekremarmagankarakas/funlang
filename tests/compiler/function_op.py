import os
from tests.compiler.base import compile_test, run_compiled_code

return_test = "fun int add(a, b) { return a + b; }; var result = add(2, 3); print(result);"
return_test2 = "fun float divide(a, b) { return 5.0 / 2.0; }; var result = divide(10, 4); print(result);"
return_test3 = "fun int multiply(a, b) { return a * b; }; var result = multiply(3, 4); print(result);"

function_test = "fun addi(a, b) { return a + b; }; var result = addi(2, 3); print(result);"

function_return_test = """
fun add2(a, b) {
    return a + b;
}

var result = add2(5, 3);
print(result);
"""

function_return_test2 = """
fun mymax(a, b) {
    if (a > b) {
        return a;
    }
    return b;
}

var result = mymax(10, 5);
print(result);
"""

# var_function_test2 = "var f = fun(x) { return x * 2; }; var result = f(4); print(result);"

function_tests = (
    f"{function_test}\n"
    f"{function_return_test}\n"
    f"{function_return_test2}\n"
    # f"{var_function_test2}\n"
    f"{return_test}\n"
    f"{return_test2}\n"
    f"{return_test3}\n"
)

expected_function_output = (
    "5\n"          # add(2, 3)
    "8\n"          # add(5, 3)
    "10\n"         # max(10, 5)
    # "8\n"          # f(4)
    "5\n"          # add(2, 3)
    "2.500000\n"   # divide result as float
    "12\n"         # multiply(3, 4)
)

llvm_ir_function = compile_test(function_tests)
compiled_function_output, compile_function_error = run_compiled_code(llvm_ir_function)
assert compiled_function_output == expected_function_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
