class Program:
  def __init__(self, functions):
    self.functions = functions

  def __repr__(self):
    return f"Program(functions={self.functions})"


class FunctionDeclarationNode:
  def __init__(self, name, params, body):
    self.name = name
    self.params = params
    self.body = body

  def __repr__(self):
    return f"FunctionDeclaration(name={self.name}, params={self.params}, body={self.body})"


class FunctionCallNode:
  def __init__(self, name, args):
    self.name = name
    self.args = args

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


class VariableNode:
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return f"Variable(name={self.name})"


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
