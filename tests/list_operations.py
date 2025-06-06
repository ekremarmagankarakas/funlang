from tests.test_base import test

list_test = "[]"
assert test(list_test).elements == []

list_test2 = "[2]"
list_test2_elements = test(list_test2).elements
list_test2_elements_format = [
    list_element.value for list_element in list_test2_elements]
assert list_test2_elements_format == [2]

list_test3 = "[3, 4]"
list_test3_elements = test(list_test3).elements
list_test3_elements_format = [
    list_element.value for list_element in list_test3_elements]
assert list_test3_elements_format == [3, 4]

list_add_test = "[3, 2] + 4"
list_add_test_elements = test(list_add_test).elements
list_add_test_elements_format = [
    list_element.value for list_element in list_add_test_elements]
assert list_add_test_elements_format == [3, 2, 4]

list_subtract_test = "[3, 4, 2] - 1"
list_subtract_test_elements = test(list_subtract_test).elements
list_subtract_test_elements_format = [
    list_element.value for list_element in list_subtract_test_elements]
assert list_subtract_test_elements_format == [3, 2]

list_multiply_test = "[3, 4] * [5, 6]"
list_multiply_test_elements = test(list_multiply_test).elements
list_multiply_test_elements_format = [
    list_element.value for list_element in list_multiply_test_elements]
assert list_multiply_test_elements_format == [3, 4, 5, 6]

list_divided_test = "[3, 4] / 0"
assert test(list_divided_test).value == 3
