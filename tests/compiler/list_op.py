import os
from tests.compiler.base import compile_test, run_compiled_code

list_creation_test = "var mylist = [1, 2, 3]; print(mylist);"
empty_list_test = "var empty = []; print(empty);"
single_element_test = "var single = [42]; print(single);"

list_function_test = """
fun list createNumbers() {
    return [10, 20, 30];
}

var result = createNumbers();
print(result);
"""

list_return_test = """
fun list getEmpty() {
    return [];
}

var empty = getEmpty();
print(empty);
"""

list_operations_test = """
var list1 = [1, 2, 3];
print(list1);

var list2 = list1 + 4;
print(list2);

var list3 = [5, 6];
var list4 = list2 * list3;
print(list4);

var list5 = list4 - 2;
print(list5);

var element = list5 / 1;
print(element);

var empty = [];
var list6 = empty + 10;
print(list6);

var single = [42];
var empty_again = single - 0;
print(empty_again);
"""


edge_cases_test = """
var big_list = [10, 20, 30, 40, 50];
var first = big_list / 0;
var last = big_list / 4;
print(first);
print(last);

var middle_removed = big_list - 2;
print(middle_removed);

var first_removed = big_list - 0;
print(first_removed);

var last_removed = big_list - 4;
print(last_removed);
"""

string_list_test = """
var string_list = ["apple", "banana", "cherry"];
print(string_list);
"""

list_tests = (
    f"{list_creation_test}\n"
    f"{empty_list_test}\n"
    f"{single_element_test}\n"
    f"{list_function_test}\n"
    f"{list_return_test}\n"
    f"{list_operations_test}\n"
    f"{edge_cases_test}\n"
)

expected_list_output = (
    "[1, 2, 3]\n"      # mylist
    "[]\n"             # empty
    "[42]\n"           # single
    "[10, 20, 30]\n"   # createNumbers()
    "[]\n"             # getEmpty()
    "[1, 2, 3]\n"      # list1
    "[1, 2, 3, 4]\n"   # list2
    "[1, 2, 3, 4, 5, 6]\n"  # list4
    "[1, 2, 4, 5, 6]\n"      # list5
    "2\n"              # element
    "[10]\n"           # list6
    "[]\n"             # empty_again
    "10\n"             # first
    "50\n"             # last
    "[10, 20, 40, 50]\n"  # middle_removed
    "[20, 30, 40, 50]\n"  # first_removed
    "[10, 20, 30, 40]\n"   # last_removed
)

llvm_ir_list = compile_test(list_tests)
actual_list_output, error = run_compiled_code(llvm_ir_list)

assert actual_list_output.strip() == expected_list_output.strip()

# Clean up
os.remove("temp.ll")
os.remove("temp.o")
os.remove("temp_executable")


list_type_error_test = """
fun int shouldFail() {
    return [1, 2, 3];
}
"""

try:
  compile_test(list_type_error_test)
except Exception as e:
  assert str(
      e) == "Type mismatch: function declared to return 'int' but trying to return 'list'"

