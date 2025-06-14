from tests.interpreter.test_base import test

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

len_test = 'var l = [1, 2, 3]; len(l);'
assert test(len_test).elements[-1].value == 3

typeof_test = 'var n = 42; typeof(n);'
typeof_test2 = 'var s = "Hello"; typeof(s);'
typeof_test3 = 'var l = [1, 2, 3]; typeof(l);'
typeof_test4 = 'var f = fun(x) { return x; }; typeof(f);'
assert test(typeof_test).elements[-1].value == 'int'
assert test(typeof_test2).elements[-1].value == 'string'
assert test(typeof_test3).elements[-1].value == 'list'
assert test(typeof_test4).elements[-1].value == 'function'

typeof_with_types_test = "var int n = 42; typeof(n);"
typeof_with_types_test2 = 'var string s = "Hello"; typeof(s);'
typeof_with_types_test3 = "var list l = [1, 2, 3]; typeof(l);"
assert test(typeof_with_types_test).elements[-1].value == 'int'
assert test(typeof_with_types_test2).elements[-1].value == 'string'
assert test(typeof_with_types_test3).elements[-1].value == 'list'
