from tests.interpreter.test_base import test

addition_test = "4 + 3"
assert test(addition_test).elements[0].value == 7

remove_test = "5 - 2"
assert test(remove_test).elements[0].value == 3

multiply_test = "3 * 5"
assert test(multiply_test).elements[0].value == 15

divide_test = "21 / 3"
assert test(divide_test).elements[0].value == 7

powered_test = "3 ^ 2"
assert test(powered_test).elements[0].value == 9

comparison_equals_test = "3 == 3"
comparison_equals_test2 = "3 == 4"
assert test(comparison_equals_test).elements[0].value == 1
assert test(comparison_equals_test2).elements[0].value == 0

comparison_not_equals_test = "3 != 4"
comparison_not_equals_test2 = "3 != 3"
assert test(comparison_not_equals_test).elements[0].value == 1
assert test(comparison_not_equals_test2).elements[0].value == 0

comparison_less_than_test = "3 < 4"
comparison_less_than_test2 = "3 < 3"
comparison_less_than_test3 = "3 < 2"
assert test(comparison_less_than_test).elements[0].value == 1
assert test(comparison_less_than_test2).elements[0].value == 0
assert test(comparison_less_than_test3).elements[0].value == 0

comparison_greater_than_test = "4 > 3"
comparison_greater_than_test2 = "4 > 4"
comparison_greater_than_test3 = "4 > 5"
assert test(comparison_greater_than_test).elements[0].value == 1
assert test(comparison_greater_than_test2).elements[0].value == 0
assert test(comparison_greater_than_test3).elements[0].value == 0

comparison_less_than_or_equals_test = "3 <= 4"
comparison_less_than_or_equals_test2 = "3 <= 3"
comparison_less_than_or_equals_test3 = "3 <= 2"
assert test(comparison_less_than_or_equals_test).elements[0].value == 1
assert test(comparison_less_than_or_equals_test2).elements[0].value == 1
assert test(comparison_less_than_or_equals_test3).elements[0].value == 0

comparison_greater_than_or_equals_test = "3 >= 2"
comparison_greater_than_or_equals_test2 = "3 >= 3"
comparison_greater_than_or_equals_test3 = "3 >= 4"
assert test(comparison_greater_than_or_equals_test).elements[0].value == 1
assert test(comparison_greater_than_or_equals_test2).elements[0].value == 1
assert test(comparison_greater_than_or_equals_test3).elements[0].value == 0

anded_with_test = "2 and 3"
assert test(anded_with_test).elements[0].value == 3

ored_with_test = "0 or 4"
assert test(ored_with_test).elements[0].value == 4

notted_test = "not 0"
notted_test2 = "not 1"
notted_test3 = "not 2"
assert test(notted_test).elements[0].value == 1
assert test(notted_test2).elements[0].value == 0
assert test(notted_test3).elements[0].value == 0

negative_test = "-5"
negative_test2 = "var x = -5; x;"
negative_test3 = "-2 * 3"
assert test(negative_test).elements[0].value == -5
assert test(negative_test2).elements[0].value == -5
assert test(negative_test3).elements[0].value == -6
