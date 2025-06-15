import math
import os
from src.error import RuntimeError
from src.token import TokenType as TT, KeywordType as TK


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

  def copy(self):
    copy = Number(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __repr__(self):
    return str(self.value)


Number.null = Number(0)
Number.false = Number(0)
Number.true = Number(1)
Number.math_PI = Number(math.pi)


class String(Value):
  def __init__(self, value):
    super().__init__()
    self.value = value

  def added_to(self, other):
    if isinstance(other, String):
      return String(self.value + other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def multiplied_by(self, other):
    if isinstance(other, Number):
      return String(self.value * other.value).set_context(self.context), None
    else:
      return None, Value.illegal_operation(self, other)

  def copy(self):
    copy = String(self.value)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __repr__(self):
    return self.value


class List(Value):
  def __init__(self, elements):
    super().__init__()
    self.elements = elements

  def added_to(self, other):
    new_list = self.copy()
    new_list.elements.append(other)
    return new_list, None

  def multiplied_by(self, other):
    if isinstance(other, List):
      new_list = self.copy()
      new_list.elements.extend(other.elements)
      return new_list, None
    else:
      return None, Value.illegal_operation(self, other)

  def subtracted_by(self, other):
    if isinstance(other, Number):
      new_list = self.copy()
      try:
        new_list.elements.pop(other.value)
        return new_list, None
      except:
        return None, RuntimeError(other.pos_start, other.pos_end, 'Out of bounds', self.context)
    else:
      return None, Value.illegal_operation(self, other)

  def divided_by(self, other):
    if isinstance(other, Number):
      try:
        return self.elements[other.value], None
      except:
        return None, RuntimeError(other.pos_start, other.pos_end, 'Out of bounds', self.context)
    else:
      return None, Value.illegal_operation(self, other)

  def copy(self):
    copy = List(self.elements)
    copy.set_pos(self.pos_start, self.pos_end)
    copy.set_context(self.context)
    return copy

  def __repr__(self):
    return f'[{", ".join([str(x) for x in self.elements])}]'


class BaseFunction(Value):
  def __init__(self, name):
    super().__init__()
    self.name = name or "<anonymous>"

  def generate_new_context(self):
    new_context = Context(self.name, self.context, self.pos_start)
    new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)
    return new_context

  def check_args(self, arg_names, args):
    res = InterpreterResult()
    if len(args) > len(arg_names):
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"{len(args) - len(arg_names)} too many args passed into '{self.name}'",
          self.context
      ))
    if len(args) < len(arg_names):
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"{len(arg_names) - len(args)} too few args passed into '{self.name}'",
          self.context
      ))
    return res.success(None)

  def populate_args(self, arg_names, args, exec_ctx):
    for i in range(len(args)):
      arg_name = arg_names[i]
      arg_value = args[i]
      arg_value.set_context(exec_ctx)
      exec_ctx.symbol_table.set(arg_name, arg_value)

  def check_and_populate_args(self, arg_names, args, exec_ctx):
    res = InterpreterResult()
    res.register(self.check_args(arg_names, args))
    if res.should_return():
      return res
    self.populate_args(arg_names, args, exec_ctx)
    return res.success(None)


class Function(BaseFunction):
  def __init__(self, name, body, arg_names, return_type=None):
    super().__init__(name)
    self.body = body
    self.arg_names = arg_names
    self.return_type = return_type

  def execute(self, args):
    res = InterpreterResult()
    interpreter = Interpreter()
    exec_ctx = self.generate_new_context()

    res.register(self.check_and_populate_args(self.arg_names, args, exec_ctx))
    if res.should_return():
      return res

    values = []
    for body_node in self.body:
      value = res.register(interpreter.visit(body_node, exec_ctx))
      if res.func_return_value:
        # Validate return type if function has explicit return type
        if self.return_type:
          return_value = res.func_return_value
          expected_type_name = self.return_type.value
          actual_type_name = self.get_value_type_name(return_value)
          
          # Check for type compatibility
          if not self.is_type_compatible(actual_type_name, expected_type_name):
            return res.failure(RuntimeError(
              return_value.pos_start, return_value.pos_end,
              f"Type mismatch: function declared to return '{expected_type_name}' but trying to return '{actual_type_name}'",
              exec_ctx
            ))
        
        return res.success(res.func_return_value)
      if res.should_return():
        return res
      values.append(value)

    return res.success(values[-1] if values else Number.null)

  def get_value_type_name(self, value):
    """Get the type name of a value for type checking"""
    if isinstance(value, Number):
      if isinstance(value.value, int):
        return "int" 
      elif isinstance(value.value, float):
        return "float"
    elif isinstance(value, String):
      return "string"
    elif isinstance(value, List):
      return "list"
    return "unknown"
  
  def is_type_compatible(self, actual_type, expected_type):
    """Check if the actual type is compatible with the expected type"""
    if actual_type == expected_type:
      return True
    
    # Allow automatic conversions for compatible types
    compatible_conversions = {
      ("int", "float"): True,
      ("float", "int"): True,
    }
    
    return compatible_conversions.get((actual_type, expected_type), False)

  def copy(self):
    copy = Function(self.name, self.body, self.arg_names, self.return_type)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<function {self.name}>"


class BuiltInFunction(BaseFunction):
  def __init__(self, name):
    super().__init__(name)

  def execute(self, args):
    res = InterpreterResult()
    exec_ctx = self.generate_new_context()

    method_name = f'execute_{self.name}'
    method = getattr(self, method_name, self.no_visit_method)

    res.register(self.check_and_populate_args(
        method.arg_names, args, exec_ctx))
    if res.should_return():
      return res

    return_value = res.register(method(exec_ctx))
    if res.should_return():
      return res
    return res.success(return_value)

  def no_visit_method(self, node, context):
    raise Exception(f'No execute_{self.name} method defined')

  def copy(self):
    copy = BuiltInFunction(self.name)
    copy.set_context(self.context)
    copy.set_pos(self.pos_start, self.pos_end)
    return copy

  def __repr__(self):
    return f"<built-in function {self.name}>"

  def execute_print(self, exec_ctx):
    print(str(exec_ctx.symbol_table.get('value')))
    return InterpreterResult().success(Number.null)
  execute_print.arg_names = ['value']

  def execute_clear(self, exec_ctx):
    os.system('cls' if os.name == 'nt' else 'cls')
    return InterpreterResult().success(Number.null)
  execute_clear.arg_names = []

  def execute_is_number(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), Number)
    return InterpreterResult().success(Number.true if is_number else Number.false)
  execute_is_number.arg_names = ["value"]

  def execute_is_string(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), String)
    return InterpreterResult().success(Number.true if is_number else Number.false)
  execute_is_string.arg_names = ["value"]

  def execute_is_list(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), List)
    return InterpreterResult().success(Number.true if is_number else Number.false)
  execute_is_list.arg_names = ["value"]

  def execute_is_fun(self, exec_ctx):
    is_number = isinstance(exec_ctx.symbol_table.get("value"), BaseFunction)
    return InterpreterResult().success(Number.true if is_number else Number.false)
  execute_is_fun.arg_names = ["value"]

  def execute_len(self, exec_ctx):
    list_ = exec_ctx.symbol_table.get("list")

    if not isinstance(list_, List):
      return InterpreterResult().failure(RuntimeError(
          self.pos_start, self.pos_end,
          "Argument must be list",
          exec_ctx
      ))

    return InterpreterResult().success(Number(len(list_.elements)))
  execute_len.arg_names = ["list"]

  def execute_to_string(self, exec_ctx):
    value = exec_ctx.symbol_table.get("value")
    return InterpreterResult().success(String(str(value)))
  execute_to_string.arg_names = ["value"]

  def execute_to_int(self, exec_ctx):
    value = exec_ctx.symbol_table.get("value")
    res = InterpreterResult()
    
    try:
      if isinstance(value, Number):
        return res.success(Number(int(value.value)))
      elif isinstance(value, String):
        try:
          return res.success(Number(int(value.value)))
        except ValueError:
          return res.failure(RuntimeError(
              self.pos_start, self.pos_end,
              f"Cannot convert '{value.value}' to an integer",
              exec_ctx
          ))
      else:
        return res.failure(RuntimeError(
            self.pos_start, self.pos_end,
            f"Cannot convert {type(value).__name__} to an integer",
            exec_ctx
        ))
    except Exception as e:
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"Error converting to integer: {str(e)}",
          exec_ctx
      ))
  execute_to_int.arg_names = ["value"]

  def execute_to_float(self, exec_ctx):
    value = exec_ctx.symbol_table.get("value")
    res = InterpreterResult()
    
    try:
      if isinstance(value, Number):
        return res.success(Number(float(value.value)))
      elif isinstance(value, String):
        try:
          return res.success(Number(float(value.value)))
        except ValueError:
          return res.failure(RuntimeError(
              self.pos_start, self.pos_end,
              f"Cannot convert '{value.value}' to a float",
              exec_ctx
          ))
      else:
        return res.failure(RuntimeError(
            self.pos_start, self.pos_end,
            f"Cannot convert {type(value).__name__} to a float",
            exec_ctx
        ))
    except Exception as e:
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"Error converting to float: {str(e)}",
          exec_ctx
      ))
  execute_to_float.arg_names = ["value"]

  def execute_to_list(self, exec_ctx):
    value = exec_ctx.symbol_table.get("value")
    res = InterpreterResult()
    
    try:
      if isinstance(value, List):
        return res.success(value)
      elif isinstance(value, String):
        elements = [String(char) for char in value.value]
        return res.success(List(elements).set_context(exec_ctx))
      else:
        return res.success(List([value]).set_context(exec_ctx))
    except Exception as e:
      return res.failure(RuntimeError(
          self.pos_start, self.pos_end,
          f"Error converting to list: {str(e)}",
          exec_ctx
      ))
  execute_to_list.arg_names = ["value"]

  def execute_typeof(self, exec_ctx):
    value = exec_ctx.symbol_table.get("value")
    if isinstance(value, Number):
      if isinstance(value.value, int):
        type_name = "int"
      elif isinstance(value.value, float):
        type_name = "float"
      else:
        type_name = "number"
    elif isinstance(value, String):
      type_name = "string"
    elif isinstance(value, List):
      type_name = "list"
    elif isinstance(value, BaseFunction):
      type_name = "function"
    else:
      type_name = "unknown"
    
    return InterpreterResult().success(String(type_name))
  execute_typeof.arg_names = ["value"]

  def execute_elos(self, exec_ctx):
    print("I love my wife, Elos!")
    return InterpreterResult().success(Number.null)
  execute_elos.arg_names = []


class Context:
  def __init__(self, display_name, parent=None, parent_entry_pos=None):
    self.display_name = display_name
    self.parent = parent
    self.parent_entry_pos = parent_entry_pos
    self.symbol_table = None

  def __repr__(self):
    return f'{self.display_name}, {self.parent}, {self.parent_entry_pos}, {self.symbol_table}'


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

  def __repr__(self):
    return f'{self.symbols}, {self.parent}'


class InterpreterResult:
  def __init__(self):
    self.reset()

  def reset(self):
    self.value = None
    self.error = None
    self.func_return_value = None
    self.loop_should_continue = False
    self.loop_should_break = False

  def register(self, res):
    self.error = res.error
    self.func_return_value = res.func_return_value
    self.loop_should_continue = res.loop_should_continue
    self.loop_should_break = res.loop_should_break
    return res.value

  def success(self, value):
    self.reset()
    self.value = value
    return self

  def success_return(self, value):
    self.reset()
    self.func_return_value = value
    return self

  def success_continue(self):
    self.reset()
    self.loop_should_continue = True
    return self

  def success_break(self):
    self.reset()
    self.loop_should_break = True
    return self

  def failure(self, error):
    self.reset()
    self.error = error
    return self

  def should_return(self):
    return (
        self.error or
        self.func_return_value or
        self.loop_should_continue or
        self.loop_should_break
    )


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

  def visit_StringNode(self, node, context):
    return InterpreterResult().success(
        String(node.tok.value).set_context(
            context).set_pos(node.pos_start, node.pos_end)
    )

  def visit_ListNode(self, node, context):
    res = InterpreterResult()
    elements = []

    for element_node in node.element_nodes:
      elements.append(res.register(self.visit(element_node, context)))
      if res.should_return():
        return res

    return res.success(List(elements).set_context(context).set_pos(node.pos_start, node.pos_end))

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
    value = value.copy().set_context(context).set_pos(node.pos_start, node.pos_end)
    return res.success(value)

  def visit_VariableDeclarationNode(self, node, context):
    res = InterpreterResult()
    var_name = node.tok.value
    value = res.register(self.visit(node.value, context))
    if res.should_return():
      return res
    
    if node.type_tok:
      expected_type = node.type_tok.value
      if not self.type_matches(value, expected_type):
        return res.failure(RuntimeError(
          node.pos_start, node.pos_end,
          f"Type mismatch: expected {expected_type}, got {self.get_type_name(value)}",
          context
        ))
    
    context.symbol_table.set(var_name, value)
    return res.success(value)
  
  def type_matches(self, value, expected_type):
    if expected_type == "int":
      return isinstance(value, Number) and isinstance(value.value, int)
    elif expected_type == "float":
      return isinstance(value, Number) and isinstance(value.value, float)
    elif expected_type == "string":
      return isinstance(value, String)
    elif expected_type == "list":
      return isinstance(value, List)
    return True
  
  def get_type_name(self, value):
    if isinstance(value, Number):
      if isinstance(value.value, int):
        return "int"
      elif isinstance(value.value, float):
        return "float"
    elif isinstance(value, String):
      return "string"
    elif isinstance(value, List):
      return "list"
    return "unknown"

  def visit_VariableAssignmentNode(self, node, context):
    res = InterpreterResult()
    var_name = node.tok.value
    value = res.register(self.visit(node.value, context))
    if res.should_return():
      return res

    existing_value = context.symbol_table.get(var_name)
    if existing_value is None:
      return res.failure(RuntimeError(
          node.pos_start, node.pos_end,
          f"Variable '{var_name}' not defined",
          context,
      ))

    context.symbol_table.set(var_name, value)
    return res.success(value)

  def visit_BinaryOperationNode(self, node, context):
    res = InterpreterResult()
    left = res.register(self.visit(node.left, context))
    if res.should_return():
      return res
    right = res.register(self.visit(node.right, context))
    if res.should_return():
      return res

    error = None
    result = None
    if node.op.type == TT.PLUS:
      result, error = left.added_to(right)
    elif node.op.type == TT.MINUS:
      result, error = left.subtracted_by(right)
    elif node.op.type == TT.MULTIPLY:
      result, error = left.multiplied_by(right)
    elif node.op.type == TT.DIVIDE:
      result, error = left.divided_by(right)
    elif node.op.type == TT.POWER:
      result, error = left.powered_by(right)
    elif node.op.type == TT.EE:
      result, error = left.comparison_equals(right)
    elif node.op.type == TT.NE:
      result, error = left.comparison_not_equals(right)
    elif node.op.type == TT.LT:
      result, error = left.comparison_less_than(right)
    elif node.op.type == TT.GT:
      result, error = left.comparison_greater_than(right)
    elif node.op.type == TT.LTE:
      result, error = left.comparison_less_than_or_equals(right)
    elif node.op.type == TT.GTE:
      result, error = left.comparison_greater_than_or_equals(right)
    elif node.op.type == TK.AND:
      result, error = left.anded_with(right)
    elif node.op.type == TK.OR:
      result, error = left.ored_with(right)

    if error:
      return res.failure(error)
    else:
      return res.success(result.set_pos(node.pos_start, node.pos_end))

  def visit_UnaryOperationNode(self, node, context):
    res = InterpreterResult()
    right = res.register(self.visit(node.right, context))
    if res.should_return():
      return res
    error = None
    if isinstance(right, Number):
      if node.op.type == TT.MINUS:
        number, error = right.multiplied_by(Number(-1))
      elif node.op.type == TT.PLUS:
        number, error = right.added_to(Number(0))
      elif node.op.type == TK.NOT:
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
      if res.should_return():
        return res
      if isinstance(condition_value, Number) and condition_value.value != 0:
        for expr in expressions:
          value = res.register(self.visit(expr, context))
          if res.should_return():
            return res
        return res.success(value.set_pos(node.pos_start, node.pos_end))
    if node.else_case:
      for expr in node.else_case:
        value = res.register(self.visit(expr, context))
        if res.should_return():
          return res
      return res.success(value.set_pos(node.pos_start, node.pos_end))
    return res.success(None)

  def visit_ForNode(self, node, context):
    res = InterpreterResult()
    start_value = res.register(self.visit(node.start, context))
    if res.should_return():
      return res
    end_value = res.register(self.visit(node.end, context))
    if res.should_return():
      return res
    if node.step:
      step_value = res.register(self.visit(node.step, context))
      if res.should_return():
        return res
    else:
      step_value = Number(1)

    context.symbol_table.set(node.var_name.value, start_value)

    current_value = start_value.value
    end_value = end_value.value
    step_value = step_value.value

    while (step_value > 0 and current_value < end_value) or (step_value < 0 and current_value > end_value):
      should_continue = False

      for expr in node.body:
        res.register(self.visit(expr, context))
        if res.loop_should_continue:
          res.loop_should_continue = False
          should_continue = True
          break
        if res.loop_should_break:
          break
        if res.should_return():
          return res

      if res.loop_should_break:
        break

      current_value += step_value
      context.symbol_table.set(node.var_name.value, Number(current_value))

    return res.success(None)

  def visit_WhileNode(self, node, context):
    res = InterpreterResult()
    while True:
      condition_value = res.register(self.visit(node.condition, context))
      if res.should_return():
        return res
      if isinstance(condition_value, Number) and condition_value.value == 0:
        break
      for expr in node.body:
        res.register(self.visit(expr, context))
        if res.loop_should_continue:
          continue
        if res.loop_should_break:
          break
        if res.should_return():
          return res

      if res.loop_should_break:
        break

      if res.loop_should_continue:
        res.loop_should_continue = False

    return res.success(None)

  def visit_FunctionDeclarationNode(self, node, context):
    res = InterpreterResult()

    func_name = node.name.value if node.name else None
    body_node = node.body
    arg_names = [arg_name.value for arg_name in node.args]
    func_value = Function(func_name, body_node, arg_names, node.return_type).set_context(
        context).set_pos(node.pos_start, node.pos_end)

    if node.name:
      context.symbol_table.set(func_name, func_value)

    return res.success(func_value)

  def visit_ReturnNode(self, node, context):
    res = InterpreterResult()

    value = res.register(self.visit(node.node_to_return, context))
    if res.should_return():
      return res

    return res.success_return(value)

  def visit_BreakNode(self, node, context):
    return InterpreterResult().success_break()

  def visit_ContinueNode(self, node, context):
    return InterpreterResult().success_continue()

  def visit_FunctionCallNode(self, node, context):
    res = InterpreterResult()
    args = []

    value_to_call = res.register(self.visit(node.name, context))
    if res.should_return():
      return res

    for arg_node in node.args:
      args.append(res.register(self.visit(arg_node, context)))
      if res.should_return():
        return res

    return_value = res.register(value_to_call.execute(args))
    if res.should_return():
      return res
    return_value = return_value.copy().set_context(
        context).set_pos(node.pos_start, node.pos_end)
    return res.success(return_value)
