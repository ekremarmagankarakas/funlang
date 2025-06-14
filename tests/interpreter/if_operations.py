from tests.interpreter.test_base import test

if_test = "var case = 0; if case == 0 { var a = 0; } elif case == 1 { var a = 1; } else { var a = 2; }; a"
assert test(if_test).elements[0].value == 0

elif_test = "var case = 1; if case == 0 { var a = 0; } elif case == 1 { var a = 1; } else { var a = 2; }; a"
assert test(elif_test).elements[0].value == 1

else_test = "var case = 2; if case == 0 { var a = 0; } elif case == 1 { var a = 1; } else { var a = 2; }; a"
assert test(else_test).elements[0].value == 2
