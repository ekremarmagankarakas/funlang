from error import RuntimeError


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
      return Number(self.value + other.value), None
    return None

  def subtracted_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value), None
    return None

  def multiplied_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value), None
    return None

  def divided_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RuntimeError(
            self.pos_start, other.pos_end,
            "Division by zero",
        )
      return Number(self.value / other.value), None
    return None

  def __repr__(self):
    return f"Number({self.value})"


class InterpreterResult:
  def __init__(self):
    self.value = None
    self.error = None

  def register(self, res):
    if res.error:
      self.error = res.error
    return res.value

  def success(self, value):
    self.value = value
    return self

  def failure(self, error):
    self.error = error
    return self


class Interpreter:
  def visit(self, node):
    method_name = 'visit_' + type(node).__name__
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node)

  def generic_visit(self, node):
    raise Exception('No visit_{} method'.format(type(node).__name__))

  def visit_NumberNode(self, node):
    return InterpreterResult().success(
        Number(node.tok.value).set_pos(node.pos_start, node.pos_end)
    )

  def visit_BinaryOperationNode(self, node):
    res = InterpreterResult()
    left = res.register(self.visit(node.left))
    if res.error:
      return res
    right = res.register(self.visit(node.right))
    if res.error:
      return res

    if isinstance(left, Number) and isinstance(right, Number):
      if node.op.type == 'PLUS':
        result, error = left.added_to(right)
      elif node.op.type == 'MINUS':
        result, error = left.subtracted_by(right)
      elif node.op.type == 'MULTIPLY':
        result, error = left.multiplied_by(right)
      elif node.op.type == 'DIVIDE':
        result, error = left.divided_by(right)

      if error:
        return res.failure(error)
      else:
        return res.success(result.set_pos(node.pos_start, node.pos_end))
    return None

  def visit_UnaryOperationNode(self, node):
    res = InterpreterResult()
    right = res.register(self.visit(node.right))
    if res.error:
      return res
    error = None
    if isinstance(right, Number):
      if node.op.type == 'MINUS':
        number, error = right.multiplied_by(Number(-1))
      elif node.op.type == 'PLUS':
        number, error = right.added_to(Number(0))
      if error:
        return res.failure(error)
      else:
        return res.success(number.set_pos(node.pos_start, node.pos_end))
    return None
