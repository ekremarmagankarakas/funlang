from tests.test_base import test

for_test = "for i=0, 6 { var j = i; }; j"
assert test(for_test).elements[-1].value == 5

for_test2 = "for i=0, 6 { if i == 3 { break; } }; i"
assert test(for_test2).elements[-1].value == 3

for_test3 = "var l = []; for i=0, 6 { if i == 3 { continue;}; l + i}; l"
for_test3_elements = test(for_test3).elements[-1].elements
for_test3_format = [
    list_element.value for list_element in for_test3_elements]
assert for_test3_format == [0, 1, 2, 4, 5]
