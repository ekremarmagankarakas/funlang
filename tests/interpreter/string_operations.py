from tests.interpreter.test_base import test

str_add_test = 'var s = "hi"; var r = s + " there"; r'
str_add_test_result = test(str_add_test)
assert str_add_test_result.elements[-1].value == "hi there"

str_add_test2 = 'var s = "hi"; var r = " there"; var sr = s + r; sr'
str_add_test2_result = test(str_add_test2)
assert str_add_test2_result.elements[-1].value == "hi there"

str_mult_test = 'var s = "hi"; s = s * 3; s'
str_mult_test_result = test(str_mult_test)
assert str_mult_test_result.elements[-1].value == "hihihi"
