from tests.test_base import test

var_test = "var x = 5; x"
var_test_result = test(var_test)
assert var_test_result.elements[-1].value == 5

var_test2 = "var x = 5; var y = 10; x + y"
var_test2_result = test(var_test2)
assert var_test2_result.elements[-1].value == 15

var_test3 = "var x = 4; x = 10; x"
var_test3_result = test(var_test3)
assert var_test3_result.elements[-1].value == 10

var_test4 = "var int x = 5; x"
var_test4_result = test(var_test4)
assert var_test4_result.elements[-1].value == 5

var_test5 = 'var string x = "Hello"; x'
var_test5_result = test(var_test5)
assert var_test5_result.elements[-1].value == "Hello"

var_test6 = "var list x = [1, 2, 3]; x"
var_test6_elements = test(var_test6).elements[0].elements
var_test_6_elements_format = [
    list_element.value for list_element in var_test6_elements]
assert var_test_6_elements_format == [1, 2, 3]

var_test7 = "var float x = 3.14; x"
var_test7_result = test(var_test7)
assert var_test7_result.elements[-1].value == 3.14

