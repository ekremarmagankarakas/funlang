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
