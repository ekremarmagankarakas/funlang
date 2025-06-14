from tests.interpreter.test_base import test

while_test = "var j = 0; var i = 0; while i!=6 { j = i; i = i + 1 }; j;"

while_test_result = test(while_test)
assert while_test_result.elements[-1].value == 5

