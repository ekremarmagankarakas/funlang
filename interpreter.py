from error import DivisionByZeroError


class Number:
  def __init__(self, value):
    self.value = value
    self.set_pos()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value)
    return None

  def subtracted_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value)
    return None

  def multiplied_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value)
    return None

  def divided_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None
      return Number(self.value / other.value)
    return None

  def __repr__(self):
    return f"Number({self.value})"


class Interpreter:
  def visit(self, node):
    method_name = 'visit_' + type(node).__name__
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node)

  def generic_visit(self, node):
    raise Exception('No visit_{} method'.format(type(node).__name__))

  def visit_NumberNode(self, node):
    return Number(node.tok.value).set_pos(node.pos_start, node.pos_end)

  def visit_BinaryOperationNode(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)

    if isinstance(left, Number) and isinstance(right, Number):
      if node.op.type == 'PLUS':
        return left.added_to(right)
      elif node.op.type == 'MINUS':
        return left.subtracted_by(right)
      elif node.op.type == 'MULTIPLY':
        return left.multiplied_by(right)
      elif node.op.type == 'DIVIDE':
        result = left.divided_by(right)
        if result is None:
          return DivisionByZeroError(
              node.pos_start, node.pos_end, "Division by zero")
        return result.set_pos(node.pos_start, node.pos_end)
    return None

  def visit_UnaryOperationNode(self, node):
    right = self.visit(node.right)
    if isinstance(right, Number):
      if node.op.type == 'MINUS':
        return Number(-right.value).set_pos(node.pos_start, node.pos_end)
    return None
