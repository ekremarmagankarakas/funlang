from llvmlite import ir, binding
import llvmlite.binding as llvm
from src.token import TokenType, KeywordType
from src.ast_nodes import NumberNode, BinaryOperationNode, ListNode, FunctionCallNode, StringNode, VariableDeclarationNode, VariableAccessNode, VariableAssignmentNode, IfNode, UnaryOperationNode, ForNode, WhileNode, BreakNode, ContinueNode


class CodeGenerator:
  def __init__(self):
    # Initialize LLVM
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    # Create a new module
    self.module = ir.Module(name="funlang_module")

    # Set target triple
    target = llvm.Target.from_default_triple()
    self.module.triple = target.triple

    # Symbol tables
    self.global_vars = {}
    self.local_vars = {}
    self.functions = {}
    
    # Loop context stack for break/continue
    self.loop_stack = []

    # Setup types
    self.int_type = ir.IntType(64)
    self.float_type = ir.DoubleType()
    self.char_ptr_type = ir.IntType(8).as_pointer()
    self.bool_type = ir.IntType(1)

    # Declare double pow(double, double)
    pow_type = ir.FunctionType(
        self.float_type, [self.float_type, self.float_type])
    self.pow_func = ir.Function(self.module, pow_type, name="pow")

    # Declare printf function
    printf_func_type = ir.FunctionType(
        ir.IntType(32), [self.char_ptr_type], var_arg=True)
    self.printf_func = ir.Function(
        self.module, printf_func_type, name="printf")

    # Create main function
    func_type = ir.FunctionType(self.int_type, [])
    self.main_func = ir.Function(self.module, func_type, name="main")

    # Entry block
    entry_block = self.main_func.append_basic_block(name="entry")
    self.builder = ir.IRBuilder(entry_block)

  def generate(self, ast_node):
    # Handle ListNode wrapper from parser
    if isinstance(ast_node, ListNode):
      last_result = None
      for stmt in ast_node.element_nodes:
        # Process supported node types
        if isinstance(stmt, (NumberNode, BinaryOperationNode, FunctionCallNode, VariableDeclarationNode, VariableAccessNode, VariableAssignmentNode, IfNode, UnaryOperationNode, ForNode, WhileNode, BreakNode, ContinueNode)):
          last_result = self.visit(stmt)
    else:
      last_result = self.visit(ast_node)

    # Return 0 from main
    if not self.builder.block.is_terminated:
      self.builder.ret(ir.Constant(self.int_type, 0))

    return str(self.module)

  def visit(self, node):
    method_name = f"visit_{type(node).__name__}"
    visitor = getattr(self, method_name, self.generic_visit)
    return visitor(node)

  def generic_visit(self, node):
    raise Exception(f"No visit_{type(node).__name__} method defined")

  def visit_NumberNode(self, node):
    if isinstance(node.tok.value, int):
      return ir.Constant(self.int_type, node.tok.value)
    else:
      return ir.Constant(self.float_type, float(node.tok.value))

  def visit_StringNode(self, node):
    # Create a global string constant
    string_val = node.tok.value + '\0'  # Null terminate
    string_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(
        string_val)), bytearray(string_val.encode('utf-8')))
    string_global = ir.GlobalVariable(
        self.module, string_const.type, name=f"str_{len(self.module.globals)}")
    string_global.initializer = string_const
    string_global.global_constant = True

    # Get pointer to the string
    return self.builder.gep(string_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

  def visit_FunctionCallNode(self, node):
    if node.name.tok.value == "print":
      return self.handle_print_call(node)
    else:
      raise Exception(
          f"Function '{node.name.tok.value}' not supported in codegen yet")

  def handle_print_call(self, node):
    if len(node.args) != 1:
      raise Exception("print() expects exactly one argument")

    arg = self.visit(node.args[0])

    # Handle different argument types
    if arg.type == self.int_type:
      # Print integer with format "%ld\n"
      fmt_str = "%ld\n\0"
      fmt_const = ir.Constant(ir.ArrayType(ir.IntType(
          8), len(fmt_str)), bytearray(fmt_str.encode('utf-8')))
      fmt_global = ir.GlobalVariable(
          self.module, fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      fmt_global.initializer = fmt_const
      fmt_global.global_constant = True
      fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(
          ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

      self.builder.call(self.printf_func, [fmt_ptr, arg])
    elif arg.type == self.float_type:
      # Print float with format "%.6f\n"
      fmt_str = "%.6f\n\0"
      fmt_const = ir.Constant(ir.ArrayType(ir.IntType(
          8), len(fmt_str)), bytearray(fmt_str.encode('utf-8')))
      fmt_global = ir.GlobalVariable(
          self.module, fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      fmt_global.initializer = fmt_const
      fmt_global.global_constant = True
      fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(
          ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

      self.builder.call(self.printf_func, [fmt_ptr, arg])
    elif arg.type == self.char_ptr_type:
      # Print string with format "%s\n"
      fmt_str = "%s\n\0"
      fmt_const = ir.Constant(ir.ArrayType(ir.IntType(
          8), len(fmt_str)), bytearray(fmt_str.encode('utf-8')))
      fmt_global = ir.GlobalVariable(
          self.module, fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      fmt_global.initializer = fmt_const
      fmt_global.global_constant = True
      fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(
          ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

      self.builder.call(self.printf_func, [fmt_ptr, arg])
    elif arg.type == self.bool_type:
      # Print boolean as integer (0 or 1)
      arg = self.builder.zext(arg, self.int_type)  # zero-extend to i64

      # Then print as integer
      fmt_str = "%ld\n\0"
      fmt_const = ir.Constant(ir.ArrayType(ir.IntType(
          8), len(fmt_str)), bytearray(fmt_str.encode('utf-8')))
      fmt_global = ir.GlobalVariable(
          self.module, fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      fmt_global.initializer = fmt_const
      fmt_global.global_constant = True
      fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(
          ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])

      self.builder.call(self.printf_func, [fmt_ptr, arg])
    else:
      raise Exception(f"Cannot print type: {arg.type}")

    # Return void/null
    return ir.Constant(self.int_type, 0)

  def visit_VariableDeclarationNode(self, node):
    var_name = node.tok.value
    value = self.visit(node.value)

    # Allocate space for the variable in the entry block
    with self.builder.goto_entry_block():
      var_ptr = self.builder.alloca(value.type, name=var_name)

    # Store the value
    self.builder.store(value, var_ptr)

    # Keep track of the variable
    self.local_vars[var_name] = var_ptr

    return value

  def visit_VariableAccessNode(self, node):
    var_name = node.tok.value

    if var_name not in self.local_vars:
      raise Exception(f"Variable '{var_name}' not defined")

    var_ptr = self.local_vars[var_name]
    return self.builder.load(var_ptr, name=var_name)

  def visit_VariableAssignmentNode(self, node):
    var_name = node.tok.value
    value = self.visit(node.value)

    if var_name not in self.local_vars:
      raise Exception(f"Variable '{var_name}' not defined")

    var_ptr = self.local_vars[var_name]
    self.builder.store(value, var_ptr)

    return value

  def visit_BinaryOperationNode(self, node):
    left = self.visit(node.left)
    right = self.visit(node.right)

    # Type promotion if needed
    if left.type != right.type:
      if left.type == self.int_type and right.type == self.float_type:
        left = self.builder.sitofp(left, self.float_type)
      elif left.type == self.float_type and right.type == self.int_type:
        right = self.builder.sitofp(right, self.float_type)

    result_type = left.type

    if result_type == self.int_type:
      if node.op.type == TokenType.PLUS:
        return self.builder.add(left, right)
      elif node.op.type == TokenType.MINUS:
        return self.builder.sub(left, right)
      elif node.op.type == TokenType.MULTIPLY:
        return self.builder.mul(left, right)
      elif node.op.type == TokenType.DIVIDE:
        return self.builder.sdiv(left, right)
      elif node.op.type == TokenType.POWER:
        left = self.builder.sitofp(left, self.float_type)
        right = self.builder.sitofp(right, self.float_type)
        result = self.builder.call(self.pow_func, [left, right])
        return self.builder.fptosi(result, self.int_type)
      elif node.op.type == TokenType.EE:
        return self.builder.icmp_signed("==", left, right)
      elif node.op.type == TokenType.NE:
        return self.builder.icmp_signed("!=", left, right)
      elif node.op.type == TokenType.LT:
        return self.builder.icmp_signed("<", left, right)
      elif node.op.type == TokenType.GT:
        return self.builder.icmp_signed(">", left, right)
      elif node.op.type == TokenType.LTE:
        return self.builder.icmp_signed("<=", left, right)
      elif node.op.type == TokenType.GTE:
        return self.builder.icmp_signed(">=", left, right)

    elif result_type == self.float_type:
      if node.op.type == TokenType.PLUS:
        return self.builder.fadd(left, right)
      elif node.op.type == TokenType.MINUS:
        return self.builder.fsub(left, right)
      elif node.op.type == TokenType.MULTIPLY:
        return self.builder.fmul(left, right)
      elif node.op.type == TokenType.DIVIDE:
        return self.builder.fdiv(left, right)
      elif node.op.type == TokenType.POWER:
        return self.builder.call(self.pow_func, [left, right])
      elif node.op.type == TokenType.EE:
        return self.builder.fcmp_ordered("==", left, right)
      elif node.op.type == TokenType.NE:
        return self.builder.fcmp_ordered("!=", left, right)
      elif node.op.type == TokenType.LT:
        return self.builder.fcmp_ordered("<", left, right)
      elif node.op.type == TokenType.GT:
        return self.builder.fcmp_ordered(">", left, right)
      elif node.op.type == TokenType.LTE:
        return self.builder.fcmp_ordered("<=", left, right)
      elif node.op.type == TokenType.GTE:
        return self.builder.fcmp_ordered(">=", left, right)

    if node.op.type == KeywordType.AND:
      return self.builder.and_(self._to_boolean(left), self._to_boolean(right))
    elif node.op.type == KeywordType.OR:
      return self.builder.or_(self._to_boolean(left), self._to_boolean(right))

    raise Exception(f"Unsupported binary operation: {node.op.type}")

  def _to_boolean(self, value):
    if value.type == self.bool_type:
      return value
    elif value.type == self.int_type:
      return self.builder.icmp_signed("!=", value, ir.Constant(self.int_type, 0))
    elif value.type == self.float_type:
      return self.builder.fcmp_ordered("!=", value, ir.Constant(self.float_type, 0.0))
    else:
      raise Exception(f"Cannot convert {value.type} to boolean")

  def visit_UnaryOperationNode(self, node):
    operand = self.visit(node.right)

    if node.op.type == KeywordType.NOT:
      operand_bool = self._to_boolean(operand)
      return self.builder.not_(operand_bool)

    elif node.op.type == TokenType.MINUS:
      if operand.type == self.int_type:
        return self.builder.neg(operand)
      elif operand.type == self.float_type:
        return self.builder.fneg(operand)
      else:
        raise Exception(f"Unary '-' not supported for type {operand.type}")

    raise Exception(f"Unsupported unary operator: {node.op.type}")

  def visit_IfNode(self, node):
    # Handle multiple elif cases
    current_block = self.builder.block
    merge_block = self.main_func.append_basic_block('if_merge')
    
    # Process all if/elif cases
    for i, (condition_node, body_statements) in enumerate(node.cases):
      # Create blocks for this condition
      then_block = self.main_func.append_basic_block(f'if_then_{i}')
      next_block = self.main_func.append_basic_block(f'if_next_{i}') if i < len(node.cases) - 1 or node.else_case else merge_block
      
      # Generate condition
      condition = self.visit(condition_node)
      
      # Convert condition to boolean if needed
      condition_bool = self._to_boolean(condition)
      
      # Branch based on condition
      self.builder.cbranch(condition_bool, then_block, next_block)
      
      # Generate then block
      self.builder.position_at_end(then_block)
      for stmt in body_statements:
        self.visit(stmt)
      
      # Jump to merge block if not terminated
      if not self.builder.block.is_terminated:
        self.builder.branch(merge_block)
      
      # Continue with next condition if there are more cases
      if i < len(node.cases) - 1 or node.else_case:
        self.builder.position_at_end(next_block)
    
    # Handle else case if present
    if node.else_case:
      for stmt in node.else_case:
        self.visit(stmt)
      
      # Jump to merge block if not terminated
      if not self.builder.block.is_terminated:
        self.builder.branch(merge_block)
    
    # Continue with merge block
    self.builder.position_at_end(merge_block)
    
    return ir.Constant(self.int_type, 0)

  def visit_ForNode(self, node):
    # Generate start, end, and step values
    start_val = self.visit(node.start)
    end_val = self.visit(node.end)
    step_val = self.visit(node.step) if node.step else ir.Constant(self.int_type, 1)
    
    # Ensure all values are integers
    if start_val.type != self.int_type:
      start_val = self.builder.fptosi(start_val, self.int_type) if start_val.type == self.float_type else start_val
    if end_val.type != self.int_type:
      end_val = self.builder.fptosi(end_val, self.int_type) if end_val.type == self.float_type else end_val
    if step_val.type != self.int_type:
      step_val = self.builder.fptosi(step_val, self.int_type) if step_val.type == self.float_type else step_val
    
    # Allocate loop variable
    loop_var_ptr = self.builder.alloca(self.int_type, name=node.var_name.value)
    self.builder.store(start_val, loop_var_ptr)
    
    # Save old variable if it exists
    old_var = self.local_vars.get(node.var_name.value)
    self.local_vars[node.var_name.value] = loop_var_ptr
    
    # Create basic blocks
    loop_cond_block = self.main_func.append_basic_block('for_cond')
    loop_body_block = self.main_func.append_basic_block('for_body')
    loop_incr_block = self.main_func.append_basic_block('for_incr') 
    loop_end_block = self.main_func.append_basic_block('for_end')
    
    # Push loop context for break/continue
    self.loop_stack.append({
      'continue_block': loop_incr_block,
      'break_block': loop_end_block
    })
    
    # Jump to condition check
    self.builder.branch(loop_cond_block)
    
    # Loop condition block
    self.builder.position_at_end(loop_cond_block)
    current_val = self.builder.load(loop_var_ptr, name=node.var_name.value)
    condition = self.builder.icmp_signed('<', current_val, end_val)
    self.builder.cbranch(condition, loop_body_block, loop_end_block)
    
    # Loop body block
    self.builder.position_at_end(loop_body_block)
    for stmt in node.body:
      self.visit(stmt)
    
    # Jump to increment block if not terminated
    if not self.builder.block.is_terminated:
      self.builder.branch(loop_incr_block)
    
    # Loop increment block
    self.builder.position_at_end(loop_incr_block)
    current_val = self.builder.load(loop_var_ptr, name=node.var_name.value)
    incremented_val = self.builder.add(current_val, step_val)
    self.builder.store(incremented_val, loop_var_ptr)
    self.builder.branch(loop_cond_block)
    
    # Loop end block
    self.builder.position_at_end(loop_end_block)
    
    # Pop loop context
    self.loop_stack.pop()
    
    # Restore old variable or remove from scope
    if old_var:
      self.local_vars[node.var_name.value] = old_var
    else:
      del self.local_vars[node.var_name.value]
    
    return ir.Constant(self.int_type, 0)

  def visit_WhileNode(self, node):
    # Create basic blocks
    loop_cond_block = self.main_func.append_basic_block('while_cond')
    loop_body_block = self.main_func.append_basic_block('while_body')
    loop_end_block = self.main_func.append_basic_block('while_end')
    
    # Push loop context for break/continue
    self.loop_stack.append({
      'continue_block': loop_cond_block,
      'break_block': loop_end_block
    })
    
    # Jump to condition check
    self.builder.branch(loop_cond_block)
    
    # Loop condition block
    self.builder.position_at_end(loop_cond_block)
    condition = self.visit(node.condition)
    
    # Convert condition to boolean if needed
    condition_bool = self._to_boolean(condition)
    
    # Branch based on condition
    self.builder.cbranch(condition_bool, loop_body_block, loop_end_block)
    
    # Loop body block
    self.builder.position_at_end(loop_body_block)
    for stmt in node.body:
      self.visit(stmt)
    
    # Jump back to condition check if not terminated
    if not self.builder.block.is_terminated:
      self.builder.branch(loop_cond_block)
    
    # Loop end block
    self.builder.position_at_end(loop_end_block)
    
    # Pop loop context
    self.loop_stack.pop()
    
    return ir.Constant(self.int_type, 0)

  def visit_BreakNode(self, node):
    # Check if we're inside a loop
    if not self.loop_stack:
      raise Exception("Break statement not inside a loop")
    
    # Get the current loop's break block
    current_loop = self.loop_stack[-1]
    break_block = current_loop['break_block']
    
    # Jump to the break block
    self.builder.branch(break_block)
    
    return ir.Constant(self.int_type, 0)

  def visit_ContinueNode(self, node):
    # Check if we're inside a loop
    if not self.loop_stack:
      raise Exception("Continue statement not inside a loop")
    
    # Get the current loop's continue block  
    current_loop = self.loop_stack[-1]
    continue_block = current_loop['continue_block']
    
    # Jump to the continue block
    self.builder.branch(continue_block)
    
    return ir.Constant(self.int_type, 0)
