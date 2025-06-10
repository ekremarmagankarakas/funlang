from tests.test_base import test

for_test = "for i=0, 6 { var j = i; }; j"
assert test(for_test).elements[-1].value == 5
