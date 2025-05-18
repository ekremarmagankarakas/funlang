class Program:
  def __init__(self, functions):
    self.functions = functions

  def __repr__(self):
    return f"Program(functions={self.functions})"


class FunctionDeclaration:
  def __init__(self, name, params, body):
    self.name = name
    self.params = params
    self.body = body

  def __repr__(self):
    return f"FunctionDeclaration(name={self.name}, params={self.params}, body={self.body})"


class FunctionCall:
  def __init__(self, name, args):
    self.name = name
    self.args = args

  def __repr__(self):
    return f"FunctionCall(name={self.name}, args={self.args})"


class ExpressionStatement:
  def __init__(self, expression):
    self.expression = expression

  def __repr__(self):
    return f"ExpressionStatement(expression={self.expression})"


class PrintStatement:
  def __init__(self, expression):
    self.expression = expression

  def __repr__(self):
    return f"PrintStatement(expression={self.expression})"


class Variable:
  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return f"Variable(name={self.name})"


class Number:
  def __init__(self, value):
    self.value = value

  def __repr__(self):
    return f"Number(value={self.value})"


class BinaryOperation:
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right

  def __repr__(self):
    return f"BinaryOperation({self.left} {self.op} {self.right})"
