from tests.interpreter.test_base import test

var_test = "var x = 5"
var_test_result = test(var_test)
assert var_test_result.elements[-1].value == 5

var_test2 = "var x = 5.0"
var_test2_result = test(var_test2)
assert var_test2_result.elements[-1].value == 5.0

var_test3 = "var x = 5; to_float(x)"
var_test3_result = test(var_test3)
assert var_test3_result.elements[-1].value == 5.0

var_test4 = "var x = 5.0; to_int(x)"
var_test4_result = test(var_test4)
assert var_test4_result.elements[-1].value == 5

var_test5 = "var x = 5; to_string(x)"
var_test5_result = test(var_test5)
assert var_test5_result.elements[-1].value == "5"

var_test6 = "var x = 5.0; to_string(x)"
var_test6_result = test(var_test6)
assert var_test6_result.elements[-1].value == "5.0"

var_test7 = 'var str = "hello"; to_list(str)'
var_test7_result = test(var_test7)
var_test7_result_tolist = [element.value for element in var_test7_result.elements[-1].elements]
assert var_test7_result_tolist == ['h', 'e', 'l', 'l', 'o']
