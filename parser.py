from ast_nodes import Program, FunctionDeclarationNode, PrintStatementNode, VariableAccessNode, VariableDeclarationNode, BinaryOperationNode, NumberNode, ExpressionStatementNode, FunctionCallNode, UnaryOperationNode, IfNode, ForNode, WhileNode, StringNode, ListNode
from token import Token, KEYWORDS, SYMBOLS, TT_EOF, TT_INT, TT_FLOAT, TT_STRING, TT_IDENT, TT_PLUS, TT_MINUS, TT_MULTIPLY, TT_DIVIDE, TT_POWER, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE, TT_LBRACKET, TT_RBRACKET, TT_COMMA, TT_SEMICOLON, TT_EQUALS, TK_FUN, TK_YELL, TK_VAR, TT_EQUALS, TT_EE, TT_NE, TT_LT, TT_GT, TT_GTE, TT_LTE, TK_NOT, TK_OR, TK_AND, TK_IF, TK_ELIF, TK_ELSE, TK_FOR, TK_WHILE
from error import IllegalSyntaxError


class ParseResult:
  def __init__(self):
    self.error = None
    self.node = None

  def register(self, res):
    if isinstance(res, ParseResult):
      if res.error:
        self.error = res.error
      return res.node
    return res

  def success(self, node):
    self.node = node
    return self

  def failure(self, error):
    self.error = error
    return self


class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = -1
    self.current_token = None
    self.advance()

  def advance(self):
    self.pos += 1
    if self.pos < len(self.tokens):
      self.current_token = self.tokens[self.pos]
    else:
      self.current_token = None

  def match(self, match_token):
    return self.current_token.type == match_token

  def err(self, err_msg):
    return IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, err_msg)

  def parse(self):
    res = ParseResult()
    expr = res.register(self.parse_expression())
    if res.error:
      return res
    return res.success(expr)

  def parse_function(self):
    res = ParseResult()
    if not self.match(TK_FUN):
      return res.failure(self.err("Expected 'fun' keyword"))
    self.advance()

    if not self.match(TT_IDENT):
      return res.failure(self.err("Expected function name"))
    func_name = self.current_token
    self.advance()

    if not self.match(TT_LPAREN):
      return res.failure(self.err("Expected '('"))
    self.advance()

    params = []
    if not self.match(TT_RPAREN):
      if not self.match(TT_IDENT):
        return res.failure(self.err("Expected parameter"))
      params.append(self.current_token)
      self.advance()

      while self.match(TT_COMMA):
        self.advance()
        if not self.match(TT_IDENT):
          return res.failure(self.err("Expected parameter after ','"))
        params.append(self.current_token)
        self.advance()

    if not self.match(TT_RPAREN):
      return res.failure(self.err("Expected ')'"))
    self.advance()

    if not self.match(TT_LBRACE):
      return res.failure(self.err("Expected '{'"))
    self.advance()

    body = []
    while self.current_token.type != TT_RBRACE:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      body.append(expr)

    if not self.match(TT_RBRACE):
      return res.failure(self.err("Expected '}'"))
    self.advance()

    return res.success(FunctionDeclarationNode(func_name, params, body))

  def parse_expression(self):
    res = ParseResult()
    if self.match(TK_VAR):
      self.advance()
      var_name = self.current_token
      if not self.match(TT_IDENT):
        return res.failure(self.err("Expected 'IDENT' after variable declaration"))
      self.advance()
      if not self.match(TT_EQUALS):
        res.failure(self.err("Expected '=' after variable name"))
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      return res.success(VariableDeclarationNode(var_name, expr))
    else:
      left = res.register(self.parse_comparison_expression())
      if res.error:
        return res
      while self.current_token and self.current_token.type in (TK_AND, TK_OR):
        op = self.current_token
        self.advance()
        right = res.register(self.parse_comparison_expression())
        if res.error:
          return res
        left = BinaryOperationNode(left, op, right)
      return res.success(left)

  def parse_comparison_expression(self):
    res = ParseResult()
    if self.match(TK_NOT):
      op_token = self.current_token
      self.advance()
      node = res.register(self.parse_comparison_expression())
      if res.error:
        return res
      return res.success(UnaryOperationNode(op_token, node))
    else:
      left = res.register(self.parse_arithmetic_expression())
      if res.error:
        return res
      while self.current_token and self.current_token.type in (TT_EQUALS, TT_EE, TT_NE, TT_LT, TT_GT, TT_GTE, TT_LTE):
        op = self.current_token
        self.advance()
        right = res.register(self.parse_arithmetic_expression())
        if res.error:
          return res
        left = BinaryOperationNode(left, op, right)
      return res.success(left)

  def parse_arithmetic_expression(self):
    res = ParseResult()
    left = res.register(self.parse_term())
    if res.error:
      return res
    while self.current_token and self.current_token.type in (TT_PLUS, TT_MINUS):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_term())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_term(self):
    res = ParseResult()
    left = res.register(self.parse_factor())
    if res.error:
      return res
    while self.current_token and self.current_token.type in (TT_MULTIPLY, TT_DIVIDE):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_factor(self):
    res = ParseResult()
    if self.current_token.type in (TT_PLUS, TT_MINUS):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      return res.success(UnaryOperationNode(op, right))
    return self.parse_power()

  def parse_power(self):
    res = ParseResult()
    left = res.register(self.parse_call())
    if res.error:
      return res
    while self.current_token and self.match(TT_POWER):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_call(self):
    res = ParseResult()
    atom = res.register(self.parse_atom())
    if res.error:
      return res

    if self.match(TT_LPAREN):
      self.advance()
      args = []

      if self.match(TT_RPAREN):
        self.advance()
      else:
        args.append(res.register(self.parse_expression()))
        if res.error:
          return res

        while self.match(TT_COMMA):
          self.advance()
          args.append(res.register(self.parse_expression()))
          if res.error:
            return res

        if not self.match(TT_RPAREN):
          res.failure(self.err("Expected ')'"))
        self.advance()

      return res.success(FunctionCallNode(atom, args))
    return res.success(atom)

  def parse_atom(self):
    res = ParseResult()
    tok = self.current_token
    if self.current_token.type in (TT_INT, TT_FLOAT):
      self.advance()
      return res.success(NumberNode(tok))
    elif self.current_token.type in TT_STRING:
      self.advance()
      return res.success(StringNode(tok))
    elif self.match(TT_IDENT):
      self.advance()
      return res.success(VariableAccessNode(tok))
    elif self.match(TT_LPAREN):
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if not self.match(TT_RPAREN):
        res.failure(self.err("Expected ')'"))
      self.advance()
      return res.success(expr)
    elif self.match(TT_LBRACKET):
      list_expr = res.register(self.parse_list_expression())
      if res.error:
        return res
      return res.success(list_expr)
    elif self.match(TK_IF):
      if_expr = res.register(self.parse_if_expression())
      if res.error:
        return res
      return res.success(if_expr)
    elif self.match(TK_FOR):
      for_expr = res.register(self.parse_for_expression())
      if res.error:
        return res
      return res.success(for_expr)
    elif self.match(TK_WHILE):
      while_expr = res.register(self.parse_while_expression())
      if res.error:
        return res
      return res.success(while_expr)
    elif self.match(TK_FUN):
      function_declaration = res.register(self.parse_function())
      if res.error:
        return res
      return res.success(function_declaration)
    return res.failure(IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"Unexpected token: {self.current_token.type}"))

  def parse_list_expression(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_token.pos_start.copy()

    if not self.match(TT_LBRACKET):
      res.failure(self.err("Expected '['"))
    self.advance()

    if self.match(TT_RBRACKET):
      pos_end = self.current_token.pos_end.copy()
      self.advance()
    else:
      element_nodes.append(res.register(self.parse_expression()))
      if res.error:
        return res

      while self.match(TT_COMMA):
        self.advance()
        element_nodes.append(res.register(self.parse_expression()))
        if res.error:
          return res

      if not self.match(TT_RBRACKET):
        res.failure(self.err("Expected ']'"))
      pos_end = self.current_token.pos_end.copy()
      self.advance()

    return res.success(ListNode(element_nodes, pos_start, pos_end))

  def parse_if_expression(self):
    res = ParseResult()
    cases = []
    else_case = []
    if not self.match(TK_IF):
      res.failure(self.err("Expected 'if' keyword"))
    self.advance()

    condition = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT_LBRACKET):
      res.failure(self.err("Expected '['"))
    self.advance()

    if not self.match(TT_LBRACE):
      res.failure(self.err("Expected '{' after 'if' condition"))
    self.advance()

    expressions = []
    while self.current_token.type != TT_RBRACE:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      expressions.append(expr)

    if not self.match(TT_RBRACE):
      res.failure(self.err("Expected '}' after 'if' block"))
    self.advance()

    cases.append((condition, expressions))

    while self.match(TK_ELIF):
      self.advance()
      condition = res.register(self.parse_expression())
      if res.error:
        return res

      if not self.match(TT_LBRACE):
        res.failure(self.err("Expected '{' after 'elif' condition"))
      self.advance()

      expressions = []
      while self.current_token.type != TT_RBRACE:
        expr = res.register(self.parse_expression())
        if res.error:
          return res
        expressions.append(expr)

      if not self.match(TT_RBRACE):
        res.failure(self.err("Expected '}' after 'elif' block"))
      self.advance()

      cases.append((condition, expressions))

    if self.match(TK_ELSE):
      self.advance()

      if not self.match(TT_LBRACE):
        res.failure(self.err("Expected '{' after 'else' keyword"))
      self.advance()

      while self.current_token.type != TT_RBRACE:
        expr = res.register(self.parse_expression())
        if res.error:
          return res
        else_case.append(expr)

      if not self.match(TT_RBRACE):
        res.failure(self.err("Expected '}' after 'else' block"))
      self.advance()

    return res.success(IfNode(cases, else_case))

  def parse_for_expression(self):
    res = ParseResult()

    if not self.match(TK_FOR):
      res.failure(self.err("Expected 'for' keyword"))
    self.advance()

    if not self.match(TT_IDENT):
      res.failure(self.err("Expected variable name after 'for' keyword"))
    var_name = self.current_token
    self.advance()

    if not self.match(TT_EQUALS):
      res.failure(self.err("Expected '=' after variable name"))
    self.advance()

    start = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT_COMMA):
      res.failure(self.err("Expected ',' after start value"))
    self.advance()

    end = res.register(self.parse_expression())
    if res.error:
      return res

    if self.match(TT_COMMA):
      self.advance()
      step = res.register(self.parse_expression())
      if res.error:
        return res
    else:
      step = None

    if not self.match(TT_LBRACE):
      res.failure(self.err("Expected '{' after 'for' loop definition"))
    self.advance()

    body = []
    while self.current_token.type != TT_RBRACE:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      body.append(expr)

    if not self.match(TT_RBRACE):
      res.failure(self.err("Expected '}' after 'for' loop body"))
    self.advance()

    return res.success(ForNode(var_name, start, end, step, body))

  def parse_while_expression(self):
    res = ParseResult()

    if not self.match(TK_WHILE):
      res.failure(self.err("Expected 'while' keyword"))
    self.advance()

    condition = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT_LBRACE):
      res.failure(self.err("Expected '{' after 'while' condition"))
    self.advance()

    body = []
    while self.current_token.type != TT_RBRACE:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      body.append(expr)

    if not self.match(TT_RBRACE):
      res.failure(self.err("Expected '}' after 'while' loop body"))
    self.advance()

    return res.success(WhileNode(condition, body))
