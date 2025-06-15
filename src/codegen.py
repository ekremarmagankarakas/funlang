from llvmlite import ir, binding
import llvmlite.binding as llvm
from src.token import TokenType, KeywordType
from src.ast_nodes import NumberNode, BinaryOperationNode, ListNode, FunctionCallNode, StringNode, VariableDeclarationNode, VariableAccessNode, VariableAssignmentNode, IfNode, UnaryOperationNode, ForNode, WhileNode, BreakNode, ContinueNode, FunctionDeclarationNode, ReturnNode


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
    
    # Function context for tracking current function
    self.current_function = None
    self.function_stack = []

    # Setup types
    self.int_type = ir.IntType(64)
    self.float_type = ir.DoubleType()
    self.char_ptr_type = ir.IntType(8).as_pointer()
    self.bool_type = ir.IntType(1)
    
    # List type: struct containing length and pointer to elements
    # For simplicity, all list elements are i64 (can hold int, float as bits, or pointer)
    self.list_element_type = self.int_type
    self.list_type = ir.LiteralStructType([self.int_type, self.list_element_type.as_pointer()])

    # Declare double pow(double, double)
    pow_type = ir.FunctionType(
        self.float_type, [self.float_type, self.float_type])
    self.pow_func = ir.Function(self.module, pow_type, name="pow")

    # Declare printf function
    printf_func_type = ir.FunctionType(
        ir.IntType(32), [self.char_ptr_type], var_arg=True)
    self.printf_func = ir.Function(
        self.module, printf_func_type, name="printf")
    
    # Declare malloc and free for dynamic list allocation
    malloc_func_type = ir.FunctionType(self.char_ptr_type, [self.int_type])
    self.malloc_func = ir.Function(self.module, malloc_func_type, name="malloc")
    
    free_func_type = ir.FunctionType(ir.VoidType(), [self.char_ptr_type])
    self.free_func = ir.Function(self.module, free_func_type, name="free")

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
        if isinstance(stmt, (NumberNode, BinaryOperationNode, ListNode, FunctionCallNode, VariableDeclarationNode, VariableAccessNode, VariableAssignmentNode, IfNode, UnaryOperationNode, ForNode, WhileNode, BreakNode, ContinueNode, FunctionDeclarationNode, ReturnNode)):
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

  def visit_ListNode(self, node):
    # Create list with elements
    num_elements = len(node.element_nodes)
    
    # Allocate memory for list elements
    if num_elements > 0:
      # Allocate array for elements
      element_size = ir.Constant(self.int_type, 8)  # 8 bytes per element (i64)
      array_size = self.builder.mul(ir.Constant(self.int_type, num_elements), element_size)
      elements_ptr = self.builder.call(self.malloc_func, [array_size])
      elements_ptr = self.builder.bitcast(elements_ptr, self.list_element_type.as_pointer())
      
      # Store each element
      for i, element_node in enumerate(node.element_nodes):
        element_val = self.visit(element_node)
        
        # Convert element to i64 if needed
        if element_val.type == self.float_type:
          element_val = self.builder.bitcast(element_val, self.int_type)
        elif element_val.type == self.bool_type:
          element_val = self.builder.zext(element_val, self.int_type)
        
        # Store element at index i
        element_ptr = self.builder.gep(elements_ptr, [ir.Constant(self.int_type, i)])
        self.builder.store(element_val, element_ptr)
    else:
      # Empty list
      elements_ptr = ir.Constant(self.list_element_type.as_pointer(), None)
    
    # Create list structure
    list_struct = ir.Constant(self.list_type, ir.Undefined)
    list_struct = self.builder.insert_value(list_struct, ir.Constant(self.int_type, num_elements), 0)
    list_struct = self.builder.insert_value(list_struct, elements_ptr, 1)
    
    return list_struct

  def visit_FunctionCallNode(self, node):
    # Extract function name
    func_name = node.name.tok.value if hasattr(node.name, 'tok') else node.name.value
    
    # Handle built-in functions
    if func_name == "print":
      return self.handle_print_call(node)
    
    # Handle user-defined functions
    if func_name in self.functions:
      func = self.functions[func_name]
      
      # Generate arguments
      args = []
      for arg_node in node.args:
        arg_val = self.visit(arg_node)
        # Keep lists as-is, convert other types to int64 for simplicity
        if arg_val.type == self.list_type:
          args.append(arg_val)
        elif arg_val.type == self.float_type:
          arg_val = self.builder.fptosi(arg_val, self.int_type)
          args.append(arg_val)
        elif arg_val.type == self.bool_type:
          arg_val = self.builder.zext(arg_val, self.int_type)
          args.append(arg_val)
        else:
          args.append(arg_val)
      
      # Check argument count
      if len(args) != len(func.args):
        raise Exception(f"Function '{func_name}' expects {len(func.args)} arguments, got {len(args)}")
      
      # Call function
      return self.builder.call(func, args)
    
    else:
      raise Exception(f"Function '{func_name}' not defined")

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
    elif arg.type == self.list_type:
      # Print list with format "[element1, element2, ...]\n"
      # Extract list length and elements pointer
      list_length = self.builder.extract_value(arg, 0)
      elements_ptr = self.builder.extract_value(arg, 1)
      
      # Print opening bracket
      fmt_str = "[\0"
      fmt_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt_str)), bytearray(fmt_str.encode('utf-8')))
      fmt_global = ir.GlobalVariable(self.module, fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      fmt_global.initializer = fmt_const
      fmt_global.global_constant = True
      fmt_ptr = self.builder.gep(fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
      self.builder.call(self.printf_func, [fmt_ptr])
      
      # Create loop to print elements
      current_func = self.current_function if self.current_function else self.main_func
      loop_start = current_func.append_basic_block('print_list_loop')
      loop_body = current_func.append_basic_block('print_list_body')
      loop_end = current_func.append_basic_block('print_list_end')
      
      # Create loop counter
      with self.builder.goto_entry_block():
        counter_ptr = self.builder.alloca(self.int_type, name="list_print_counter")
      self.builder.store(ir.Constant(self.int_type, 0), counter_ptr)
      
      self.builder.branch(loop_start)
      
      # Loop condition
      self.builder.position_at_end(loop_start)
      counter = self.builder.load(counter_ptr)
      condition = self.builder.icmp_signed('<', counter, list_length)
      self.builder.cbranch(condition, loop_body, loop_end)
      
      # Loop body - print element
      self.builder.position_at_end(loop_body)
      counter = self.builder.load(counter_ptr)
      
      # Print comma separator if not first element
      zero = ir.Constant(self.int_type, 0)
      is_first = self.builder.icmp_signed('==', counter, zero)
      comma_block = current_func.append_basic_block('print_comma')
      no_comma_block = current_func.append_basic_block('no_comma')
      self.builder.cbranch(is_first, no_comma_block, comma_block)
      
      # Print comma
      self.builder.position_at_end(comma_block)
      comma_str = ", \0"
      comma_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(comma_str)), bytearray(comma_str.encode('utf-8')))
      comma_global = ir.GlobalVariable(self.module, comma_const.type, name=f"fmt_{len(self.module.globals)}")
      comma_global.initializer = comma_const  
      comma_global.global_constant = True
      comma_ptr = self.builder.gep(comma_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
      self.builder.call(self.printf_func, [comma_ptr])
      self.builder.branch(no_comma_block)
      
      # Print element
      self.builder.position_at_end(no_comma_block)
      counter = self.builder.load(counter_ptr)
      element_ptr = self.builder.gep(elements_ptr, [counter])
      element_val = self.builder.load(element_ptr)
      
      # Print element as integer
      elem_fmt_str = "%ld\0"
      elem_fmt_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(elem_fmt_str)), bytearray(elem_fmt_str.encode('utf-8')))
      elem_fmt_global = ir.GlobalVariable(self.module, elem_fmt_const.type, name=f"fmt_{len(self.module.globals)}")
      elem_fmt_global.initializer = elem_fmt_const
      elem_fmt_global.global_constant = True
      elem_fmt_ptr = self.builder.gep(elem_fmt_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
      self.builder.call(self.printf_func, [elem_fmt_ptr, element_val])
      
      # Increment counter
      counter = self.builder.load(counter_ptr)
      next_counter = self.builder.add(counter, ir.Constant(self.int_type, 1))
      self.builder.store(next_counter, counter_ptr)
      self.builder.branch(loop_start)
      
      # Print closing bracket and newline
      self.builder.position_at_end(loop_end)
      close_str = "]\n\0"
      close_const = ir.Constant(ir.ArrayType(ir.IntType(8), len(close_str)), bytearray(close_str.encode('utf-8')))
      close_global = ir.GlobalVariable(self.module, close_const.type, name=f"fmt_{len(self.module.globals)}")
      close_global.initializer = close_const
      close_global.global_constant = True
      close_ptr = self.builder.gep(close_global, [ir.Constant(ir.IntType(32), 0), ir.Constant(ir.IntType(32), 0)])
      self.builder.call(self.printf_func, [close_ptr])
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

    # Handle list operations
    if left.type == self.list_type or right.type == self.list_type:
      return self.handle_list_operation(node.op.type, left, right)

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

  def handle_list_operation(self, op_type, left, right):
    """Handle list-specific binary operations"""
    if op_type == TokenType.PLUS:
      # list + element -> append element to list
      if left.type == self.list_type and right.type != self.list_type:
        return self.list_append(left, right)
      else:
        raise Exception("List + operation requires list on left and element on right")
    
    elif op_type == TokenType.MULTIPLY:
      # list * list -> concatenate lists
      if left.type == self.list_type and right.type == self.list_type:
        return self.list_concatenate(left, right)
      else:
        raise Exception("List * operation requires two lists")
    
    elif op_type == TokenType.MINUS:
      # list - index -> remove element at index
      if left.type == self.list_type and right.type == self.int_type:
        return self.list_remove_at_index(left, right)
      else:
        raise Exception("List - operation requires list on left and integer index on right")
    
    elif op_type == TokenType.DIVIDE:
      # list / index -> access element at index
      if left.type == self.list_type and right.type == self.int_type:
        return self.list_access_at_index(left, right)
      else:
        raise Exception("List / operation requires list on left and integer index on right")
    
    else:
      raise Exception(f"Unsupported list operation: {op_type}")

  def list_append(self, list_val, element):
    """Append an element to a list (returns new list)"""
    # Extract current list info
    current_length = self.builder.extract_value(list_val, 0)
    current_elements = self.builder.extract_value(list_val, 1)
    
    # Calculate new length
    new_length = self.builder.add(current_length, ir.Constant(self.int_type, 1))
    
    # Allocate memory for new list
    element_size = ir.Constant(self.int_type, 8)  # 8 bytes per element
    new_array_size = self.builder.mul(new_length, element_size)
    new_elements_ptr = self.builder.call(self.malloc_func, [new_array_size])
    new_elements_ptr = self.builder.bitcast(new_elements_ptr, self.list_element_type.as_pointer())
    
    # Copy existing elements if any
    zero = ir.Constant(self.int_type, 0)
    has_elements = self.builder.icmp_signed('>', current_length, zero)
    
    current_func = self.current_function if self.current_function else self.main_func
    copy_block = current_func.append_basic_block('copy_elements')
    append_block = current_func.append_basic_block('append_element')
    
    self.builder.cbranch(has_elements, copy_block, append_block)
    
    # Copy existing elements
    self.builder.position_at_end(copy_block)
    # Simple loop to copy elements
    counter_ptr = self.builder.alloca(self.int_type, name="copy_counter")
    self.builder.store(zero, counter_ptr)
    
    copy_loop = current_func.append_basic_block('copy_loop')
    copy_body = current_func.append_basic_block('copy_body')
    self.builder.branch(copy_loop)
    
    # Copy loop condition
    self.builder.position_at_end(copy_loop)
    counter = self.builder.load(counter_ptr)
    copy_condition = self.builder.icmp_signed('<', counter, current_length)
    self.builder.cbranch(copy_condition, copy_body, append_block)
    
    # Copy loop body
    self.builder.position_at_end(copy_body)
    counter = self.builder.load(counter_ptr)
    
    # Load from old array
    old_element_ptr = self.builder.gep(current_elements, [counter])
    old_element = self.builder.load(old_element_ptr)
    
    # Store to new array
    new_element_ptr = self.builder.gep(new_elements_ptr, [counter])
    self.builder.store(old_element, new_element_ptr)
    
    # Increment counter
    next_counter = self.builder.add(counter, ir.Constant(self.int_type, 1))
    self.builder.store(next_counter, counter_ptr)
    self.builder.branch(copy_loop)
    
    # Append new element
    self.builder.position_at_end(append_block)
    
    # Convert element to i64 if needed
    converted_element = element
    if element.type == self.float_type:
      converted_element = self.builder.bitcast(element, self.int_type)
    elif element.type == self.bool_type:
      converted_element = self.builder.zext(element, self.int_type)
    
    # Store new element at the end
    last_index = self.builder.sub(new_length, ir.Constant(self.int_type, 1))
    last_element_ptr = self.builder.gep(new_elements_ptr, [last_index])
    self.builder.store(converted_element, last_element_ptr)
    
    # Create new list struct
    new_list = ir.Constant(self.list_type, ir.Undefined)
    new_list = self.builder.insert_value(new_list, new_length, 0)
    new_list = self.builder.insert_value(new_list, new_elements_ptr, 1)
    
    return new_list

  def list_concatenate(self, left_list, right_list):
    """Concatenate two lists (returns new list)"""
    # Extract list info
    left_length = self.builder.extract_value(left_list, 0)
    left_elements = self.builder.extract_value(left_list, 1)
    right_length = self.builder.extract_value(right_list, 0)
    right_elements = self.builder.extract_value(right_list, 1)
    
    # Calculate total length
    total_length = self.builder.add(left_length, right_length)
    
    # Allocate memory for new list
    element_size = ir.Constant(self.int_type, 8)
    new_array_size = self.builder.mul(total_length, element_size)
    new_elements_ptr = self.builder.call(self.malloc_func, [new_array_size])
    new_elements_ptr = self.builder.bitcast(new_elements_ptr, self.list_element_type.as_pointer())
    
    # Copy left list elements
    zero = ir.Constant(self.int_type, 0)
    current_func = self.current_function if self.current_function else self.main_func
    
    # Copy left elements
    left_counter_ptr = self.builder.alloca(self.int_type, name="left_copy_counter")
    self.builder.store(zero, left_counter_ptr)
    
    left_copy_loop = current_func.append_basic_block('left_copy_loop')
    left_copy_body = current_func.append_basic_block('left_copy_body')
    right_copy_start = current_func.append_basic_block('right_copy_start')
    
    self.builder.branch(left_copy_loop)
    
    # Left copy loop
    self.builder.position_at_end(left_copy_loop)
    left_counter = self.builder.load(left_counter_ptr)
    left_condition = self.builder.icmp_signed('<', left_counter, left_length)
    self.builder.cbranch(left_condition, left_copy_body, right_copy_start)
    
    self.builder.position_at_end(left_copy_body)
    left_counter = self.builder.load(left_counter_ptr)
    
    left_element_ptr = self.builder.gep(left_elements, [left_counter])
    left_element = self.builder.load(left_element_ptr)
    
    new_element_ptr = self.builder.gep(new_elements_ptr, [left_counter])
    self.builder.store(left_element, new_element_ptr)
    
    next_left_counter = self.builder.add(left_counter, ir.Constant(self.int_type, 1))
    self.builder.store(next_left_counter, left_counter_ptr)
    self.builder.branch(left_copy_loop)
    
    # Copy right elements
    self.builder.position_at_end(right_copy_start)
    right_counter_ptr = self.builder.alloca(self.int_type, name="right_copy_counter")
    self.builder.store(zero, right_counter_ptr)
    
    right_copy_loop = current_func.append_basic_block('right_copy_loop')
    right_copy_body = current_func.append_basic_block('right_copy_body')
    concat_end = current_func.append_basic_block('concat_end')
    
    self.builder.branch(right_copy_loop)
    
    self.builder.position_at_end(right_copy_loop)
    right_counter = self.builder.load(right_counter_ptr)
    right_condition = self.builder.icmp_signed('<', right_counter, right_length)
    self.builder.cbranch(right_condition, right_copy_body, concat_end)
    
    self.builder.position_at_end(right_copy_body)
    right_counter = self.builder.load(right_counter_ptr)
    
    right_element_ptr = self.builder.gep(right_elements, [right_counter])
    right_element = self.builder.load(right_element_ptr)
    
    # Calculate position in new array (left_length + right_counter)
    new_index = self.builder.add(left_length, right_counter)
    new_element_ptr = self.builder.gep(new_elements_ptr, [new_index])
    self.builder.store(right_element, new_element_ptr)
    
    next_right_counter = self.builder.add(right_counter, ir.Constant(self.int_type, 1))
    self.builder.store(next_right_counter, right_counter_ptr)
    self.builder.branch(right_copy_loop)
    
    # Create new list struct
    self.builder.position_at_end(concat_end)
    new_list = ir.Constant(self.list_type, ir.Undefined)
    new_list = self.builder.insert_value(new_list, total_length, 0)
    new_list = self.builder.insert_value(new_list, new_elements_ptr, 1)
    
    return new_list

  def list_remove_at_index(self, list_val, index):
    """Remove element at index from list (returns new list)"""
    # Extract list info
    current_length = self.builder.extract_value(list_val, 0)
    current_elements = self.builder.extract_value(list_val, 1)
    
    # Check bounds
    zero = ir.Constant(self.int_type, 0)
    index_valid = self.builder.and_(
      self.builder.icmp_signed('>=', index, zero),
      self.builder.icmp_signed('<', index, current_length)
    )
    
    current_func = self.current_function if self.current_function else self.main_func
    valid_block = current_func.append_basic_block('index_valid')
    error_block = current_func.append_basic_block('index_error')
    
    self.builder.cbranch(index_valid, valid_block, error_block)
    
    # Handle error case - for now just return original list
    self.builder.position_at_end(error_block)
    # In a real implementation, we'd throw an exception here
    # For now, just return the original list
    self.builder.branch(valid_block)
    
    # Valid index case
    self.builder.position_at_end(valid_block)
    
    # Calculate new length
    new_length = self.builder.sub(current_length, ir.Constant(self.int_type, 1))
    
    # Allocate memory for new list (if new_length > 0)
    has_elements = self.builder.icmp_signed('>', new_length, zero)
    
    alloc_block = current_func.append_basic_block('allocate_new')
    empty_block = current_func.append_basic_block('return_empty')
    copy_start = current_func.append_basic_block('copy_start')
    
    self.builder.cbranch(has_elements, alloc_block, empty_block)
    
    # Allocate new array
    self.builder.position_at_end(alloc_block)
    element_size = ir.Constant(self.int_type, 8)
    new_array_size = self.builder.mul(new_length, element_size)
    new_elements_ptr = self.builder.call(self.malloc_func, [new_array_size])
    new_elements_ptr = self.builder.bitcast(new_elements_ptr, self.list_element_type.as_pointer())
    self.builder.branch(copy_start)
    
    # Return empty list
    self.builder.position_at_end(empty_block)
    empty_ptr = ir.Constant(self.list_element_type.as_pointer(), None)
    self.builder.branch(copy_start)
    
    # Copy elements (skipping the one at index)
    self.builder.position_at_end(copy_start)
    elements_ptr = self.builder.phi(self.list_element_type.as_pointer())
    elements_ptr.add_incoming(new_elements_ptr, alloc_block)
    elements_ptr.add_incoming(empty_ptr, empty_block)
    
    # Copy before index and after index separately
    src_counter_ptr = self.builder.alloca(self.int_type, name="src_counter")
    dst_counter_ptr = self.builder.alloca(self.int_type, name="dst_counter")
    self.builder.store(zero, src_counter_ptr)
    self.builder.store(zero, dst_counter_ptr)
    
    copy_loop = current_func.append_basic_block('copy_loop')
    copy_body = current_func.append_basic_block('copy_body')
    skip_element = current_func.append_basic_block('skip_element')
    copy_element = current_func.append_basic_block('copy_element')
    remove_end = current_func.append_basic_block('remove_end')
    
    self.builder.branch(copy_loop)
    
    # Copy loop condition
    self.builder.position_at_end(copy_loop)
    src_counter = self.builder.load(src_counter_ptr)
    copy_condition = self.builder.icmp_signed('<', src_counter, current_length)
    self.builder.cbranch(copy_condition, copy_body, remove_end)
    
    # Copy body - check if this is the index to skip
    self.builder.position_at_end(copy_body)
    src_counter = self.builder.load(src_counter_ptr)
    is_skip_index = self.builder.icmp_signed('==', src_counter, index)
    self.builder.cbranch(is_skip_index, skip_element, copy_element)
    
    # Skip this element
    self.builder.position_at_end(skip_element)
    src_counter = self.builder.load(src_counter_ptr)
    next_src = self.builder.add(src_counter, ir.Constant(self.int_type, 1))
    self.builder.store(next_src, src_counter_ptr)
    self.builder.branch(copy_loop)
    
    # Copy this element
    self.builder.position_at_end(copy_element)
    src_counter = self.builder.load(src_counter_ptr)
    dst_counter = self.builder.load(dst_counter_ptr)
    
    src_element_ptr = self.builder.gep(current_elements, [src_counter])
    src_element = self.builder.load(src_element_ptr)
    
    dst_element_ptr = self.builder.gep(elements_ptr, [dst_counter])
    self.builder.store(src_element, dst_element_ptr)
    
    next_src = self.builder.add(src_counter, ir.Constant(self.int_type, 1))
    next_dst = self.builder.add(dst_counter, ir.Constant(self.int_type, 1))
    self.builder.store(next_src, src_counter_ptr)
    self.builder.store(next_dst, dst_counter_ptr)
    self.builder.branch(copy_loop)
    
    # Create new list struct
    self.builder.position_at_end(remove_end)
    new_list = ir.Constant(self.list_type, ir.Undefined)
    new_list = self.builder.insert_value(new_list, new_length, 0)
    new_list = self.builder.insert_value(new_list, elements_ptr, 1)
    
    return new_list

  def list_access_at_index(self, list_val, index):
    """Access element at index from list (returns element value)"""
    # Extract list info
    list_length = self.builder.extract_value(list_val, 0)
    list_elements = self.builder.extract_value(list_val, 1)
    
    # Check bounds
    zero = ir.Constant(self.int_type, 0)
    index_valid = self.builder.and_(
      self.builder.icmp_signed('>=', index, zero),
      self.builder.icmp_signed('<', index, list_length)
    )
    
    current_func = self.current_function if self.current_function else self.main_func
    valid_block = current_func.append_basic_block('access_valid')
    error_block = current_func.append_basic_block('access_error')
    end_block = current_func.append_basic_block('access_end')
    
    self.builder.cbranch(index_valid, valid_block, error_block)
    
    # Valid access
    self.builder.position_at_end(valid_block)
    element_ptr = self.builder.gep(list_elements, [index])
    element_value = self.builder.load(element_ptr)
    self.builder.branch(end_block)
    
    # Error case - return 0
    self.builder.position_at_end(error_block)
    error_value = ir.Constant(self.int_type, 0)
    self.builder.branch(end_block)
    
    # Return result
    self.builder.position_at_end(end_block)
    result = self.builder.phi(self.int_type)
    result.add_incoming(element_value, valid_block)
    result.add_incoming(error_value, error_block)
    
    return result

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
    # Use current function context instead of always using main_func
    current_func = self.current_function if self.current_function else self.main_func
    merge_block = current_func.append_basic_block('if_merge')
    
    # Process all if/elif cases
    for i, (condition_node, body_statements) in enumerate(node.cases):
      # Create blocks for this condition
      then_block = current_func.append_basic_block(f'if_then_{i}')
      next_block = current_func.append_basic_block(f'if_next_{i}') if i < len(node.cases) - 1 or node.else_case else merge_block
      
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
    current_func = self.current_function if self.current_function else self.main_func
    loop_cond_block = current_func.append_basic_block('for_cond')
    loop_body_block = current_func.append_basic_block('for_body')
    loop_incr_block = current_func.append_basic_block('for_incr') 
    loop_end_block = current_func.append_basic_block('for_end')
    
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
    current_func = self.current_function if self.current_function else self.main_func
    loop_cond_block = current_func.append_basic_block('while_cond')
    loop_body_block = current_func.append_basic_block('while_body')
    loop_end_block = current_func.append_basic_block('while_end')
    
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

  def visit_FunctionDeclarationNode(self, node):
    # Extract function name
    func_name = node.name.value if hasattr(node.name, 'value') else str(node.name)
    
    # Determine return type based on declaration
    return_type = self.int_type  # default
    if node.return_type:
      if node.return_type.type == KeywordType.INT_TYPE:
        return_type = self.int_type
      elif node.return_type.type == KeywordType.FLOAT_TYPE:
        return_type = self.float_type
      elif node.return_type.type == KeywordType.STRING_TYPE:
        return_type = self.char_ptr_type
      elif node.return_type.type == KeywordType.LIST_TYPE:
        return_type = self.list_type
    
    # Create function type - for simplicity, all parameters are int64
    param_types = [self.int_type] * len(node.args)
    func_type = ir.FunctionType(return_type, param_types)
    
    # Create function
    func = ir.Function(self.module, func_type, func_name)
    # Store return type information for validation
    func._funlang_return_type = node.return_type
    self.functions[func_name] = func
    
    # Save current context
    old_builder = self.builder
    old_function = self.current_function
    old_local_vars = self.local_vars.copy()
    
    # Set new context
    self.current_function = func
    self.local_vars = {}
    
    # Create entry block
    entry_block = func.append_basic_block('entry')
    self.builder = ir.IRBuilder(entry_block)
    
    # Add parameters to local variables
    for i, param in enumerate(node.args):
      param_name = param.value if hasattr(param, 'value') else str(param)
      # Allocate space for parameter
      param_ptr = self.builder.alloca(self.int_type, name=param_name)
      # Store the parameter value
      self.builder.store(func.args[i], param_ptr)
      # Add to local variables
      self.local_vars[param_name] = param_ptr
    
    # Generate function body
    return_value = None
    for stmt in node.body:
      result = self.visit(stmt)
      if isinstance(stmt, ReturnNode):
        return_value = result
        break
    
    # If no explicit return, return 0
    if not self.builder.block.is_terminated:
      if return_value is None:
        # Return appropriate default based on function return type
        if func.return_value.type == self.int_type:
          return_value = ir.Constant(self.int_type, 0)
        elif func.return_value.type == self.float_type:
          return_value = ir.Constant(self.float_type, 0.0)
        elif func.return_value.type == self.char_ptr_type:
          return_value = ir.Constant(self.char_ptr_type, None)
        elif func.return_value.type == self.list_type:
          # Return empty list
          empty_list = ir.Constant(self.list_type, ir.Undefined)
          empty_list = self.builder.insert_value(empty_list, ir.Constant(self.int_type, 0), 0)  # length = 0
          empty_list = self.builder.insert_value(empty_list, ir.Constant(self.list_element_type.as_pointer(), None), 1)  # elements = null
          return_value = empty_list
        else:
          return_value = ir.Constant(self.int_type, 0)
      self.builder.ret(return_value)
    
    # Restore previous context
    self.builder = old_builder
    self.current_function = old_function
    self.local_vars = old_local_vars
    
    return func

  def visit_ReturnNode(self, node):
    # Generate return value
    if node.node_to_return:
      return_val = self.visit(node.node_to_return)
      
      # Get expected return type from current function
      expected_type = self.current_function.return_value.type
      
      # Validate return type if function has explicit return type
      if hasattr(self.current_function, '_funlang_return_type') and self.current_function._funlang_return_type:
        # Get the expected type token
        expected_type_token = self.current_function._funlang_return_type
        
        # Check if the return value type matches expected type
        def get_value_type_name(llvm_type):
          if llvm_type == self.int_type:
            return "int"
          elif llvm_type == self.float_type:
            return "float"
          elif llvm_type == self.char_ptr_type:
            return "string"
          elif llvm_type == self.list_type:
            return "list"
          else:
            return str(llvm_type)
        
        expected_type_name = expected_type_token.value
        actual_type_name = get_value_type_name(return_val.type)
        
        # Allow automatic conversions for compatible types
        compatible_conversions = {
          ("int", "float"): True,
          ("float", "int"): True, 
          ("bool", "int"): True,
          ("bool", "float"): True,
        }
        
        if actual_type_name != expected_type_name:
          if (actual_type_name, expected_type_name) not in compatible_conversions:
            raise Exception(f"Type mismatch: function declared to return '{expected_type_name}' but trying to return '{actual_type_name}'")
      
      # Convert return value to expected type if needed
      if return_val.type != expected_type:
        if expected_type == self.int_type:
          if return_val.type == self.float_type:
            return_val = self.builder.fptosi(return_val, self.int_type)
          elif return_val.type == self.bool_type:
            return_val = self.builder.zext(return_val, self.int_type)
        elif expected_type == self.float_type:
          if return_val.type == self.int_type:
            return_val = self.builder.sitofp(return_val, self.float_type)
          elif return_val.type == self.bool_type:
            bool_as_int = self.builder.zext(return_val, self.int_type)
            return_val = self.builder.sitofp(bool_as_int, self.float_type)
    else:
      # Return appropriate default based on function return type
      expected_type = self.current_function.return_value.type
      if expected_type == self.int_type:
        return_val = ir.Constant(self.int_type, 0)
      elif expected_type == self.float_type:
        return_val = ir.Constant(self.float_type, 0.0)
      elif expected_type == self.char_ptr_type:
        return_val = ir.Constant(self.char_ptr_type, None)
      elif expected_type == self.list_type:
        # Return empty list
        empty_list = ir.Constant(self.list_type, ir.Undefined)
        empty_list = self.builder.insert_value(empty_list, ir.Constant(self.int_type, 0), 0)  # length = 0
        empty_list = self.builder.insert_value(empty_list, ir.Constant(self.list_element_type.as_pointer(), None), 1)  # elements = null
        return_val = empty_list
      else:
        return_val = ir.Constant(self.int_type, 0)
    
    # Generate return instruction
    self.builder.ret(return_val)
    
    return return_val
