from error import RuntimeError
from token import Token, KEYWORDS, SYMBOLS, TT_EOF, TT_INT, TT_FLOAT, TT_STRING, TT_IDENT, TT_PLUS, TT_MINUS, TT_MULTIPLY, TT_DIVIDE, TT_POWER, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE, TT_LBRACKET, TT_RBRACKET, TT_COMMA, TT_SEMICOLON, TT_EQUALS, TK_FUN, TK_YELL, TK_DOUBT, TK_MAYBE, TK_VAR


class Number:
  def __init__(self, value):
    self.value = value
    self.set_pos()
    self.set_context()

  def set_pos(self, pos_start=None, pos_end=None):
    self.pos_start = pos_start
    self.pos_end = pos_end
    return self

  def set_context(self, context=None):
    self.context = context
    return self

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    return None

  def subtracted_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    return None

  def multiplied_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    return None

  def divided_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RuntimeError(
            self.pos_start, other.pos_end,
            "Division by zero",
            self.context,
        )
      return Number(self.value / other.value).set_context(self.context), None
    return None

  def powered_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    return None

  def __repr__(self):
    return str(self.value)


class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None


class SymbolTable:
  def __init__(self):
    self.symbols = {}
    self.parent = None

  def get(self, name):
    value = self.symbols.get(name, None)
    if value is None and self.parent:
      return self.parent.get(name)
    return value

  def set(self, name, value):
    self.symbols[name] = value

  def remove(self, name):
    del self.symbols[name]


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
  def visit(self, node, context):
    method_name = 'visit_' + type(node).__name__
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node, context)

  def generic_visit(self, node, context):
    raise Exception('No visit_{} method'.format(type(node).__name__))

  def visit_NumberNode(self, node, context):
    return InterpreterResult().success(
        Number(node.tok.value).set_context(
            context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_VariableAccessNode(self, node, context):
    res = InterpreterResult()
    var_name = node.tok.value
    value = context.symbol_table.get(var_name)
    if value is None:
      return res.failure(RuntimeError(
          node.pos_start, node.pos_end,
          f"Variable '{var_name}' not defined",
          context,
      ))
    return res.success(value)

  def visit_VariableDeclarationNode(self, node, context):
    res = InterpreterResult()
    var_name = node.tok.value
    value = res.register(self.visit(node.value, context))
    if res.error:
      return res
    if context.symbol_table.get(var_name) is not None:
      return res.failure(RuntimeError(
          node.pos_start, node.pos_end,
          f"Variable '{var_name}' already defined",
          context,
      ))
    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinaryOperationNode(self, node, context):
    res = InterpreterResult()
    left = res.register(self.visit(node.left, context))
    if res.error:
      return res
    right = res.register(self.visit(node.right, context))
    if res.error:
      return res

    if isinstance(left, Number) and isinstance(right, Number):
      if node.op.type == TT_PLUS:
        result, error = left.added_to(right)
      elif node.op.type == TT_MINUS:
        result, error = left.subtracted_by(right)
      elif node.op.type == TT_MULTIPLY:
        result, error = left.multiplied_by(right)
      elif node.op.type == TT_DIVIDE:
        result, error = left.divided_by(right)
      elif node.op.type == TT_POWER:
        result, error = left.powered_by(right)

      if error:
        return res.failure(error)
      else:
        return res.success(result.set_pos(node.pos_start, node.pos_end))
    return None

  def visit_UnaryOperationNode(self, node, context):
    res = InterpreterResult()
    right = res.register(self.visit(node.right, context))
    if res.error:
      return res
    error = None
    if isinstance(right, Number):
      if node.op.type == TT_MINUS:
        number, error = right.multiplied_by(Number(-1))
      elif node.op.type == TT_PLUS:
        number, error = right.added_to(Number(0))
      if error:
        return res.failure(error)
      else:
        return res.success(number.set_pos(node.pos_start, node.pos_end))
    return None
