from tests.test_base import test

is_string_test = 'var s = "Hello, World!"; is_string(s);'
is_string_test2 = 'var s = 123; is_string(s);'
assert test(is_string_test).elements[-1].value == 1
assert test(is_string_test2).elements[-1].value == 0

is_number_test = 'var n = 42; is_number(n);'
is_number_test2 = 'var n = "Not a number"; is_number(n);'
assert test(is_number_test).elements[-1].value == 1
assert test(is_number_test2).elements[-1].value == 0

is_list_test = 'var l = [1, 2, 3]; is_list(l);'
is_list_test2 = 'var l = "Not a list"; is_list(l);'
assert test(is_list_test).elements[-1].value == 1
assert test(is_list_test2).elements[-1].value == 0

is_fun_test = 'var f = fun(x) { return x; }; is_fun(f);'
is_fun_test2 = 'var f = 42; is_fun(f);'
assert test(is_fun_test).elements[-1].value == 1
assert test(is_fun_test2).elements[-1].value == 0
