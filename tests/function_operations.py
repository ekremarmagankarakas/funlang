from tests.test_base import test

function_test = "fun add(a, b) { a + b; }; add(2, 3)"
assert test(function_test).elements[-1].value == 5

function_return_test = """
fun add(a, b) {
    return a + b;
}

var result = add(5, 3);
result
"""
assert test(function_return_test).elements[-1].value == 8

function_return_test2 = """
fun max(a, b) {
    if (a > b) {
        return a;
    }
    return b;
}

var result = max(10, 5);
result
"""
assert test(function_return_test2).elements[-1].value == 10

var_function_test2 = "var f = fun(x) { return x * 2; }; f(4)"
assert test(var_function_test2).elements[-1].value == 8

