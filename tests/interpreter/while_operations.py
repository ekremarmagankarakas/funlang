from tests.interpreter.test_base import test

while_test = "var j = 0; var i = 0; while i!=6 { j = i; i = i + 1 }; j;"
while_break_test = "var j = 0; var i = 0; while i!=6 { if i == 3 { break; }; j = i; i = i + 1 }; j;"
while_continue_test = "var j = 0; var i = 0; while i!=6 { i = i + 1; if i == 3 { continue; }; j = i; }; j;"

while_test_result = test(while_test)
assert while_test_result.elements[-1].value == 5

while_break_test_result = test(while_break_test)
assert while_break_test_result.elements[-1].value == 2

while_continue_test_result = test(while_continue_test)
assert while_continue_test_result.elements[-1].value == 6
