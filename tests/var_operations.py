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
