class Program:
    def __init__(self, functions):
        self.functions = functions

    def __repr__(self):
        return f"Program(functions={self.functions})"


class FunctionDeclarationNode:
    def __init__(self, name, params, body, return_type=None):
        self.name = name
        self.args = params
        self.body = body
        self.return_type = return_type

        if self.name:
            self.pos_start = self.name.pos_start
        elif len(self.args) > 0:
            self.pos_start = self.args[0].pos_start
        else:
            self.pos_start = self.body[0].pos_start

        self.pos_end = self.body[-1].pos_start

    def __repr__(self):
        return f"FunctionDeclaration(name={self.name}, params={self.args}, body={self.body}, return_type={self.return_type})"


class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name
        self.args = args

        self.pos_start = self.name.pos_start

        if len(self.args) > 0:
            self.pos_end = self.args[-1].pos_end
        else:
            self.pos_end = self.name.pos_end

    def __repr__(self):
        return f"FunctionCall(name={self.name}, args={self.args})"


class VariableDeclarationNode:
    def __init__(self, type_tok, tok, value):
        self.type_tok = type_tok
        self.tok = tok
        self.value = value

        self.pos_start = type_tok.pos_start if type_tok else tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"VariableDeclaration(type={self.type_tok.value if self.type_tok else None}, name={self.tok.value}, value={self.value})"


class VariableAssignmentNode:
    def __init__(self, tok, value):
        self.tok = tok
        self.value = value

        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"VariableAssignment(name={self.tok.value}, value={self.value})"


class VariableAccessNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"VariableAccess(name={self.tok.value})"


class NumberNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"Number(value={self.tok})"


class StringNode:
    def __init__(self, tok):
        self.tok = tok

        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end

    def __repr__(self):
        return f"String(value={self.tok})"


class BinaryOperationNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

        self.pos_start = left.pos_start
        self.pos_end = right.pos_end

    def __repr__(self):
        return f"BinaryOperation({self.left} {self.op} {self.right})"


class UnaryOperationNode:
    def __init__(self, op, right):
        self.op = op
        self.right = right

        self.pos_start = op.pos_start
        self.pos_end = right.pos_end

    def __repr__(self):
        return f"UnaryOperation({self.op} {self.right})"


class IfNode:
    def __init__(self, cases, else_case=None):
        self.cases = cases
        self.else_case = else_case if else_case is not None else []

        self.pos_start = cases[0][0].pos_start
        if self.else_case:
            self.pos_end = self.else_case[-1].pos_end
        else:
            self.pos_end = cases[-1][1][-1].pos_end

        def __repr__(self):
            return f"IfNode(cases={self.cases}, else_case={self.else_case})"


class ForNode:
    def __init__(self, var_name, start, end, step, body):
        self.var_name = var_name
        self.start = start
        self.end = end
        self.step = step
        self.body = body

        self.pos_start = start.pos_start
        self.pos_end = body[-1].pos_end

    def __repr__(self):
        return f"ForNode(var_name={self.var_name}, start={self.start}, end={self.end}, step={self.step}, body={self.body})"


class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

        self.pos_start = condition.pos_start
        self.pos_end = body[-1].pos_end

    def __repr__(self):
        return f"WhileNode(condition={self.condition}, body={self.body})"


class ListNode:
    def __init__(self, type_tok, element_nodes, pos_start, pos_end):
        self.type_tok = type_tok
        self.element_nodes = element_nodes

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"ListNode(tok_type={self.type_tok}, elements={self.element_nodes})"


class ReturnNode:
    def __init__(self, node_to_return, pos_start, pos_end):
        self.node_to_return = node_to_return

        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return f"ReturnNode(value={self.node_to_return})"


class BreakNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "BreakNode()"


class ContinueNode:
    def __init__(self, pos_start, pos_end):
        self.pos_start = pos_start
        self.pos_end = pos_end

    def __repr__(self):
        return "ContinueNode()"
