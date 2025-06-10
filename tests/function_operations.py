from tests.test_base import test

function_test = "fun add(a, b) { a + b; }; add(2, 3)"
assert test(function_test).elements[1].elements[0].value == 5
