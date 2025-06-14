import os
from tests.compiler.base import compile_test, run_compiled_code

''' arithmetic operations tests '''
arithmetic_test = "var x = 5; print(x + 3);"
addition_test = "print(4 + 3);"
remove_test = "print(5 - 2);"
multiply_test = "print(3 * 5);"
divide_test = "print(21 / 3);"
powered_test = "print(3 ^ 2);"
comparison_equals_test = "print(3 == 3);"
comparison_equals_test2 = "print(3 == 4);"
comparison_not_equals_test = "print(3 != 4);"
comparison_not_equals_test2 = "print(3 != 3);"
comparison_less_than_test = "print(3 < 4);"
comparison_less_than_test2 = "print(3 < 3);"
comparison_less_than_test3 = "print(3 < 2);"
comparison_greater_than_test = "print(4 > 3);"
comparison_greater_than_test2 = "print(4 > 4);"
comparison_greater_than_test3 = "print(4 > 5);"
comparison_less_than_or_equals_test = "print(3 <= 4);"
comparison_less_than_or_equals_test2 = "print(3 <= 3);"
comparison_less_than_or_equals_test3 = "print(3 <= 2);"
comparison_greater_than_or_equals_test = "print(3 >= 2);"
comparison_greater_than_or_equals_test2 = "print(3 >= 3);"
comparison_greater_than_or_equals_test3 = "print(3 >= 4);"
anded_with_test = "print(2 and 3);"
ored_with_test = "print(0 or 4);"
notted_test = "print(not 0);"
notted_test2 = "print(not 1);"
notted_test3 = "print(not 2);"

arith_tests = (f"{arithmetic_test}\n"
               f"{addition_test}\n"
               f"{remove_test}\n"
               f"{multiply_test}\n"
               f"{divide_test}\n"
               # f"{powered_test}\n"
               # f"{comparison_equals_test}\n"
               # f"{comparison_equals_test2}\n"
               # f"{comparison_not_equals_test}\n"
               # f"{comparison_not_equals_test2}\n"
               # f"{comparison_less_than_test}\n"
               # f"{comparison_less_than_test2}\n"
               # f"{comparison_less_than_test3}\n"
               # f"{comparison_greater_than_test}\n"
               # f"{comparison_greater_than_test2}\n"
               # f"{comparison_greater_than_test3}\n"
               # f"{comparison_less_than_or_equals_test}\n"
               # f"{comparison_less_than_or_equals_test2}\n"
               # f"{comparison_less_than_or_equals_test3}\n"
               # f"{comparison_greater_than_or_equals_test}\n"
               # f"{comparison_greater_than_or_equals_test2}\n"
               # f"{comparison_greater_than_or_equals_test3}\n"
               # f"{anded_with_test}\n"
               # f"{ored_with_test}\n"
               # f"{notted_test}\n"
               # f"{notted_test2}\n"
               # f"{notted_test3}"
               )

expected_arith_output = (
    "8\n"   # var x = 5; print(x + 3);
    "7\n"   # 4 + 3
    "3\n"   # 5 - 2
    "15\n"  # 3 * 5
    "7\n"   # 21 / 3
    # "9\n"   # 3 ^ 2   (power)
    # "1\n"   # 3 == 3
    # "0\n"   # 3 == 4
    # "1\n"   # 3 != 4
    # "0\n"   # 3 != 3
    # "1\n"   # 3 < 4
    # "0\n"   # 3 < 3
    # "0\n"   # 3 < 2
    # "1\n"   # 4 > 3
    # "0\n"   # 4 > 4
    # "0\n"   # 4 > 5
    # "1\n"   # 3 <= 4
    # "1\n"   # 3 <= 3
    # "0\n"   # 3 <= 2
    # "1\n"   # 3 >= 2
    # "1\n"   # 3 >= 3
    # "0\n"   # 3 >= 4
    # "1\n"   # 2 and 3      (both truthy)
    # "1\n"   # 0 or 4       (one truthy)
    # "1\n"   # not 0        (true)
    # "0\n"   # not 1        (false)
    # "0\n"   # not 2        (false)
)


llvm_ir_arith = compile_test(arith_tests)
compiled_arith_output, compile_arith_error = run_compiled_code(llvm_ir_arith)
assert compiled_arith_output == expected_arith_output.strip()
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")


