from tests.interpreter.test_base import test

list_test = "[]"
assert test(list_test).elements[0].elements == []

list_test2 = "[2]"
list_test2_elements = test(list_test2).elements[0].elements
list_test2_elements_format = [
    list_element.value for list_element in list_test2_elements]
assert list_test2_elements_format == [2]

list_test3 = "[3, 4]"
list_test3_elements = test(list_test3).elements[0].elements
list_test3_elements_format = [
    list_element.value for list_element in list_test3_elements]
assert list_test3_elements_format == [3, 4]

list_add_test = "[3, 2] + 4"
list_add_test_elements = test(list_add_test).elements[0].elements
list_add_test_elements_format = [
    list_element.value for list_element in list_add_test_elements]
assert list_add_test_elements_format == [3, 2, 4]

list_subtract_test = "[3, 4, 2] - 1"
list_subtract_test_elements = test(list_subtract_test).elements[0].elements
list_subtract_test_elements_format = [
    list_element.value for list_element in list_subtract_test_elements]
assert list_subtract_test_elements_format == [3, 2]

list_multiply_test = "[3, 4] * [5, 6]"
list_multiply_test_elements = test(list_multiply_test).elements[0].elements
list_multiply_test_elements_format = [
    list_element.value for list_element in list_multiply_test_elements]
assert list_multiply_test_elements_format == [3, 4, 5, 6]

list_divided_test = "[3, 4] / 0"
assert test(list_divided_test).elements[0].value == 3

list_types = "var list l = int [1, 2, 3]; l;"
list_types_elements = test(list_types).elements[0].elements
list_types_elements_format = [
    list_element.value for list_element in list_types_elements]
assert list_types_elements_format == [1, 2, 3]

list_types2 = "var list l = float [1.0, 2.0, 3.0]; l;"
list_types2_elements = test(list_types2).elements[0].elements
list_types2_elements_format = [
    list_element.value for list_element in list_types2_elements]
assert list_types2_elements_format == [1.0, 2.0, 3.0]

list_types3 = "var list l = string [\"a\", \"b\", \"c\"]; l;"
list_types3_elements = test(list_types3).elements[0].elements
list_types3_elements_format = [
    list_element.value for list_element in list_types3_elements]
assert list_types3_elements_format == ["a", "b", "c"]

list_type_mismatch = "var list l = int [1, 2, 3]; l + \"a\";"
try:
    test(list_type_mismatch)
except Exception as e:
    assert "Type Mismatch" in str(e)

multiple_list_types = "var list l = [1, 2.0, \"3\"]; l;"
multiple_list_types_elements = test(multiple_list_types).elements[0].elements
multiple_list_types_elements_format = [
    list_element.value for list_element in multiple_list_types_elements]
assert multiple_list_types_elements_format == [1, 2.0, "3"]
