from tests.test_base import test

for_test = "var j = 0; for i=0, 6 { var j = i; }; j"
#assert test(for_test).elements[0].value == 5

for_test2 = "for i=0, 6 { var j = i; }; j"
#assert test(for_test2).elements[0].value == 5
