import os
from tests.compiler.base import compile_test, run_compiled_code

''' Builtin Operations Tests '''
len_test = 'var l = [1, 2, 3]; print(len(l));'
typeof_test = 'var n = 42; print(typeof(n));'
typeof_test2 = 'var s = "Hello"; print(typeof(s));'
typeof_test3 = 'var l = [1, 2, 3]; print(typeof(l));'
# typeof_test4 = 'var f = fun(x) { return x; }; print(typeof(f));'

builtin_tests = (
    f"{len_test}\n"
    f"{typeof_test}\n"
    f"{typeof_test2}\n"
    f"{typeof_test3}\n"
    # f"{typeof_test4}\n"
)

expected_builtin_output = (
    "3\n"          # len([1, 2, 3])
    "int\n"       # typeof(42)
    "string\n"    # typeof("Hello")
    "list\n"      # typeof([1, 2, 3])
    # "function\n"  # typeof(fun(x) { return x; })
)

llvm_ir_builtin = compile_test(builtin_tests)
compiled_builtin_output, compile_builtin_error = run_compiled_code(llvm_ir_builtin)
assert compiled_builtin_output == expected_builtin_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")
