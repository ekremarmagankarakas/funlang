class Program:
  def __init__(self, functions):
    self.functions = functions

  def __repr__(self):
    return f"Program(functions={self.functions})"


class FunctionDeclarationNode:
  def __init__(self, name, params, body):
    self.name = name
    self.args = params
    self.body = body

    if self.name:
      self.pos_start = self.name.pos_start
    elif len(self.args) > 0:
      self.pos_start = self.args[0].pos_start
    else:
      self.pos_start = self.body[0].pos_start

    self.pos_end = self.body[-1].pos_start

  def __repr__(self):
    return f"FunctionDeclaration(name={self.name}, params={self.args}, body={self.body})"


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


class ExpressionStatementNode:
  def __init__(self, expression):
    self.expression = expression

  def __repr__(self):
    return f"ExpressionStatement(expression={self.expression})"


class PrintStatementNode:
  def __init__(self, expression):
    self.expression = expression

  def __repr__(self):
    return f"PrintStatement(expression={self.expression})"


class VariableDeclarationNode:
  def __init__(self, tok, value):
    self.tok = tok
    self.value = value

    self.pos_start = tok.pos_start
    self.pos_end = tok.pos_end

  def __repr__(self):
    return f"VariableDeclaration(name={self.tok.value}, value={self.value})"


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
