from error import RuntimeError
from token import Token, KEYWORDS, SYMBOLS, TT_EOF, TT_INT, TT_FLOAT, TT_STRING, TT_IDENT, TT_PLUS, TT_MINUS, TT_MULTIPLY, TT_DIVIDE, TT_POWER, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE, TT_LBRACKET, TT_RBRACKET, TT_COMMA, TT_SEMICOLON, TT_EQUALS, TK_FUN, TK_YELL, TK_VAR, TT_EQUALS, TT_EE, TT_NE, TT_LT, TT_GT, TT_GTE, TT_LTE, TK_NOT, TK_OR, TK_AND, TK_IF, TK_ELSE


class Value:
  def __init__(self):
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
    return None, self.illegal_operation(other)

  def subtracted_by(self, other):
    return None, self.illegal_operation(other)

  def multiplied_by(self, other):
    return None, self.illegal_operation(other)

  def divided_by(self, other):
    return None, self.illegal_operation(other)

  def powered_by(self, other):
    return None, self.illegal_operation(other)

  def comparison_equals(self, other):
    return None, self.illegal_operation(other)

  def comparison_not_equals(self, other):
    return None, self.illegal_operation(other)

  def comparison_less_than(self, other):
    return None, self.illegal_operation(other)

  def comparison_greater_than(self, other):
    return None, self.illegal_operation(other)

  def comparison_less_than_or_equals(self, other):
    return None, self.illegal_operation(other)

  def comparison_greater_than_or_equals(self, other):
    return None, self.illegal_operation(other)

  def anded_with(self, other):
    return None, self.illegal_operation(other)

  def ored_with(self, other):
    return None, self.illegal_operation(other)

  def notted(self):
    return None, self.illegal_operation()

  def execute(self, args):
    return InterpreterResult().failure(self.illegal_operation())

  def copy(self):
    raise Exception('No copy method defined')

  def illegal_operation(self, other=None):
    if not other:
      other = self
    return RuntimeError(
        self.pos_start, other.pos_end,
        'Illegal operation',
        self.context
    )


class Number(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, Number):
      return Number(self.value + other.value).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def subtracted_by(self, other):
    if isinstance(other, Number):
      return Number(self.value - other.value).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def multiplied_by(self, other):
    if isinstance(other, Number):
      return Number(self.value * other.value).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def divided_by(self, other):
    if isinstance(other, Number):
      if other.value == 0:
        return None, RuntimeError(
            self.pos_start, other.pos_end,
            "Division by zero",
            self.context,
        )
      return Number(self.value / other.value).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def powered_by(self, other):
    if isinstance(other, Number):
      return Number(self.value ** other.value).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_equals(self, other):
    if isinstance(other, Number):
      return Number(int(self.value == other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_not_equals(self, other):
    if isinstance(other, Number):
      return Number(int(self.value != other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_less_than(self, other):
    if isinstance(other, Number):
      return Number(int(self.value < other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_greater_than(self, other):
    if isinstance(other, Number):
      return Number(int(self.value > other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_less_than_or_equals(self, other):
    if isinstance(other, Number):
      return Number(int(self.value <= other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def comparison_greater_than_or_equals(self, other):
    if isinstance(other, Number):
      return Number(int(self.value >= other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def anded_with(self, other):
    if isinstance(other, Number):
      return Number(int(self.value and other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def ored_with(self, other):
    if isinstance(other, Number):
      return Number(int(self.value or other.value)).set_context(self.context), None
    return None, Value.illegal_operation(self, other)

  def notted(self):
    return Number(1 if self.value == 0 else 0).set_context(self.context), None

  def __repr__(self):
    return str(self.value)


class Function(Value):
  def __init__(self, name, body, args):
    super().__init__()
    self.name = name or "<anonymous>"
    self.body = body
    self.args = args

  def execute(self, args):
    res = InterpreterResult()
    interpreter = Interpreter()
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

    if len(args) > len(self.args):
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"{len(args) - len(self.args)} too many args passed into '{self.name}'",
          self.context
      ))

    if len(args) < len(self.args):
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"{len(self.args) - len(args)} too few args passed into '{self.name}'",
          self.context
      ))

    for i in range(len(args)):
      arg_name = self.args[i]
      arg_value = args[i]
      arg_value.set_context(new_context)
      new_context.symbol_table.set(arg_name, arg_value)

    for i in range(len(self.body)):
      value = res.register(interpreter.visit(self.body[i], new_context))
    if res.error:
      return res
    return res.success(value)

  def __repr__(self):
    return f"<function {self.name}>"


class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None


class SymbolTable:
  def __init__(self, parent=None):
    self.symbols = {}
    self.parent = parent

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

    error = None
    result = None
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
    elif node.op.type == TT_EE:
      result, error = left.comparison_equals(right)
    elif node.op.type == TT_NE:
      result, error = left.comparison_not_equals(right)
    elif node.op.type == TT_LT:
      result, error = left.comparison_less_than(right)
    elif node.op.type == TT_GT:
      result, error = left.comparison_greater_than(right)
    elif node.op.type == TT_LTE:
      result, error = left.comparison_less_than_or_equals(right)
    elif node.op.type == TT_GTE:
      result, error = left.comparison_greater_than_or_equals(right)
    elif node.op.type == TK_AND:
      result, error = left.anded_with(right)
    elif node.op.type == TK_OR:
      result, error = left.ored_with(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

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
      elif node.op.type == TK_NOT:
        number, error = right.notted()
      if error:
        return res.failure(error)
      else:
        return res.success(number.set_pos(node.pos_start, node.pos_end))
    return None

  def visit_IfNode(self, node, context):
    res = InterpreterResult()
    for condition, expressions in node.cases:
      condition_value = res.register(self.visit(condition, context))
      if res.error:
        return res
      if isinstance(condition_value, Number) and condition_value.value != 0:
        for expr in expressions:
          value = res.register(self.visit(expr, context))
          if res.error:
            return res
        return res.success(value.set_pos(node.pos_start, node.pos_end))
    if node.else_case:
      for expr in node.else_case:
        value = res.register(self.visit(expr, context))
        if res.error:
          return res
      return res.success(value.set_pos(node.pos_start, node.pos_end))
    return res.success(None)

  def visit_ForNode(self, node, context):
    res = InterpreterResult()
    start_value = res.register(self.visit(node.start, context))
    if res.error:
      return res
    end_value = res.register(self.visit(node.end, context))
    if res.error:
      return res
    if node.step:
      step_value = res.register(self.visit(node.step, context))
      if res.error:
        return res
    else:
      step_value = Number(1)

    context.symbol_table.set(node.var_name.value, start_value)

    current_value = start_value.value
    end_value = end_value.value
    step_value = step_value.value

    while (step_value > 0 and current_value < end_value) or (step_value < 0 and current_value > end_value):
      for expr in node.body:
        res.register(self.visit(expr, context))
        if res.error:
          return res
      current_value += step_value
      context.symbol_table.set(node.var_name.value, Number(current_value))

    return res.success(None)

  def visit_WhileNode(self, node, context):
    res = InterpreterResult()
    while True:
      condition_value = res.register(self.visit(node.condition, context))
      if res.error:
        return res
      if isinstance(condition_value, Number) and condition_value.value == 0:
        break
      for expr in node.body:
        res.register(self.visit(expr, context))
        if res.error:
          return res
    return res.success(None)

  def visit_FunctionDeclarationNode(self, node, context):
    res = InterpreterResult()

    func_name = node.name.value if node.name else None
    body_node = node.body
    arg_names = [arg_name.value for arg_name in node.args]
    func_value = Function(func_name, body_node, arg_names).set_context(
        context).set_pos(node.pos_start, node.pos_end)

    if node.name:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_FunctionCallNode(self, node, context):
    res = InterpreterResult()
    args = []

    value_to_call = res.register(self.visit(node.name, context))
    if res.error:
      return res

    for arg_node in node.args:
      args.append(res.register(self.visit(arg_node, context)))
      if res.error:
        return res

    return_value = res.register(value_to_call.execute(args))
    if res.error:
      return res
    return res.success(return_value)
