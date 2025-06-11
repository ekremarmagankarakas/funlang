from ast_nodes import Program, FunctionDeclarationNode, VariableAccessNode, VariableDeclarationNode, BinaryOperationNode, NumberNode, FunctionCallNode, UnaryOperationNode, IfNode, ForNode, WhileNode, StringNode, ListNode, BreakNode, ContinueNode, ReturnNode
from token import Token, TokenType as TT, KeywordType as TK
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
    statements = res.register(self.parse_statements())
    if res.error:
      return res
    return res.success(statements)

  def parse_statements(self):
    res = ParseResult()
    statements = []
    pos_start = self.current_token.pos_start.copy()

    while self.current_token.type == TT.SEMICOLON:
      self.advance()

    statement = res.register(self.parse_statement())
    if res.error:
      return res
    statements.append(statement)

    while self.current_token and self.current_token.type != TT.EOF and self.current_token.type != TT.RBRACE:
      if self.match(TT.SEMICOLON):
        self.advance()
      else:
        statement = res.register(self.parse_statement())
        if res.error:
          return res
        statements.append(statement)

    pos_end = statements[-1].pos_end.copy() if statements else pos_start.copy()
    return res.success(ListNode(statements, pos_start, pos_end))

  def parse_statement(self):
    res = ParseResult()
    if self.match(TK.BREAK):
      self.advance()
      if not self.match(TT.SEMICOLON):
        return res.failure(self.err("Expected ';' after 'break' statement"))
      self.advance()
      return res.success(BreakNode(self.current_token.pos_start, self.current_token.pos_end))
    elif self.match(TK.CONTINUE):
      self.advance()
      if not self.match(TT.SEMICOLON):
        return res.failure(self.err("Expected ';' after 'continue' statement"))
      self.advance()
      return res.success(ContinueNode(self.current_token.pos_start, self.current_token.pos_end))
    elif self.match(TK.RETURN):
      pos_start = self.current_token.pos_start.copy()
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if not self.match(TT.SEMICOLON):
        return res.failure(self.err("Expected ';' after 'return' statement"))
      pos_end = self.current_token.pos_end.copy()
      self.advance()
      return res.success(ReturnNode(expr, pos_start, pos_end))

    expr = res.register(self.parse_expression())
    if res.error:
      return res
    return res.success(expr)

  def parse_expression(self):
    res = ParseResult()
    if self.match(TK.VAR):
      self.advance()
      var_name = self.current_token
      if not self.match(TT.IDENT):
        return res.failure(self.err("Expected 'IDENT' after variable declaration"))
      self.advance()
      if not self.match(TT.EQUALS):
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
      while self.current_token and self.current_token.type in (TK.AND, TK.OR):
        op = self.current_token
        self.advance()
        right = res.register(self.parse_comparison_expression())
        if res.error:
          return res
        left = BinaryOperationNode(left, op, right)
      return res.success(left)

  def parse_comparison_expression(self):
    res = ParseResult()
    if self.match(TK.NOT):
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
      while self.current_token and self.current_token.type in (TT.EQUALS, TT.EE, TT.NE, TT.LT, TT.GT, TT.GTE, TT.LTE):
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
    while self.current_token and self.current_token.type in (TT.PLUS, TT.MINUS):
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
    while self.current_token and self.current_token.type in (TT.MULTIPLY, TT.DIVIDE):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_factor(self):
    res = ParseResult()
    if self.current_token.type in (TT.PLUS, TT.MINUS):
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
    while self.current_token and self.match(TT.POWER):
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

    if self.match(TT.LPAREN):
      self.advance()
      args = []

      if self.match(TT.RPAREN):
        self.advance()
      else:
        args.append(res.register(self.parse_expression()))
        if res.error:
          return res

        while self.match(TT.COMMA):
          self.advance()
          args.append(res.register(self.parse_expression()))
          if res.error:
            return res

        if not self.match(TT.RPAREN):
          res.failure(self.err("Expected ')'"))
        self.advance()

      return res.success(FunctionCallNode(atom, args))
    return res.success(atom)

  def parse_atom(self):
    res = ParseResult()
    tok = self.current_token
    if self.current_token.type in (TT.INT, TT.FLOAT):
      self.advance()
      return res.success(NumberNode(tok))
    elif self.current_token.type == TT.STRING:
      self.advance()
      return res.success(StringNode(tok))
    elif self.match(TT.IDENT):
      self.advance()
      return res.success(VariableAccessNode(tok))
    elif self.match(TT.LPAREN):
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if not self.match(TT.RPAREN):
        res.failure(self.err("Expected ')'"))
      self.advance()
      return res.success(expr)
    elif self.match(TT.LBRACKET):
      list_expr = res.register(self.parse_list_expression())
      if res.error:
        return res
      return res.success(list_expr)
    elif self.match(TK.IF):
      if_expr = res.register(self.parse_if_expression())
      if res.error:
        return res
      return res.success(if_expr)
    elif self.match(TK.FOR):
      for_expr = res.register(self.parse_for_expression())
      if res.error:
        return res
      return res.success(for_expr)
    elif self.match(TK.WHILE):
      while_expr = res.register(self.parse_while_expression())
      if res.error:
        return res
      return res.success(while_expr)
    elif self.match(TK.FUN):
      function_declaration = res.register(self.parse_function())
      if res.error:
        return res
      return res.success(function_declaration)
    return res.failure(IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"Unexpected token: {self.current_token.type}"))

  def parse_list_expression(self):
    res = ParseResult()
    element_nodes = []
    pos_start = self.current_token.pos_start.copy()

    if not self.match(TT.LBRACKET):
      res.failure(self.err("Expected '['"))
    self.advance()

    if self.match(TT.RBRACKET):
      pos_end = self.current_token.pos_end.copy()
      self.advance()
    else:
      element_nodes.append(res.register(self.parse_expression()))
      if res.error:
        return res

      while self.match(TT.COMMA):
        self.advance()
        element_nodes.append(res.register(self.parse_expression()))
        if res.error:
          return res

      if not self.match(TT.RBRACKET):
        res.failure(self.err("Expected ']'"))
      pos_end = self.current_token.pos_end.copy()
      self.advance()

    return res.success(ListNode(element_nodes, pos_start, pos_end))

  def parse_if_expression(self):
    res = ParseResult()
    cases = []
    else_case = []
    if not self.match(TK.IF):
      res.failure(self.err("Expected 'if' keyword"))
    self.advance()

    condition = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT.LBRACE):
      res.failure(self.err("Expected '{' after 'if' condition"))
    self.advance()

    expressions = []
    statements = res.register(self.parse_statements())
    if res.error:
      return res
    expressions = statements.element_nodes

    if not self.match(TT.RBRACE):
      res.failure(self.err("Expected '}' after 'if' block"))
    self.advance()

    cases.append((condition, expressions))

    while self.match(TK.ELIF):
      self.advance()
      condition = res.register(self.parse_expression())
      if res.error:
        return res

      if not self.match(TT.LBRACE):
        res.failure(self.err("Expected '{' after 'elif' condition"))
      self.advance()

      expressions = []
      statements = res.register(self.parse_statements())
      if res.error:
        return res
      expressions = statements.element_nodes

      if not self.match(TT.RBRACE):
        res.failure(self.err("Expected '}' after 'elif' block"))
      self.advance()

      cases.append((condition, expressions))

    if self.match(TK.ELSE):
      self.advance()

      if not self.match(TT.LBRACE):
        res.failure(self.err("Expected '{' after 'else' keyword"))
      self.advance()

      statements = res.register(self.parse_statements())
      if res.error:
        return res
      else_case = statements.element_nodes

      if not self.match(TT.RBRACE):
        res.failure(self.err("Expected '}' after 'else' block"))
      self.advance()

    return res.success(IfNode(cases, else_case))

  def parse_for_expression(self):
    res = ParseResult()

    if not self.match(TK.FOR):
      res.failure(self.err("Expected 'for' keyword"))
    self.advance()

    if not self.match(TT.IDENT):
      res.failure(self.err("Expected variable name after 'for' keyword"))
    var_name = self.current_token
    self.advance()

    if not self.match(TT.EQUALS):
      res.failure(self.err("Expected '=' after variable name"))
    self.advance()

    start = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT.COMMA):
      res.failure(self.err("Expected ',' after start value"))
    self.advance()

    end = res.register(self.parse_expression())
    if res.error:
      return res

    if self.match(TT.COMMA):
      self.advance()
      step = res.register(self.parse_expression())
      if res.error:
        return res
    else:
      step = None

    if not self.match(TT.LBRACE):
      res.failure(self.err("Expected '{' after 'for' loop definition"))
    self.advance()

    body = []
    statements = res.register(self.parse_statements())
    if res.error:
      return res
    body = statements.element_nodes

    if not self.match(TT.RBRACE):
      res.failure(self.err("Expected '}' after 'for' loop body"))
    self.advance()

    return res.success(ForNode(var_name, start, end, step, body))

  def parse_while_expression(self):
    res = ParseResult()

    if not self.match(TK.WHILE):
      res.failure(self.err("Expected 'while' keyword"))
    self.advance()

    condition = res.register(self.parse_expression())
    if res.error:
      return res

    if not self.match(TT.LBRACE):
      res.failure(self.err("Expected '{' after 'while' condition"))
    self.advance()

    body = []
    statements = res.register(self.parse_statements())
    if res.error:
      return res
    body = statements.element_nodes

    if not self.match(TT.RBRACE):
      res.failure(self.err("Expected '}' after 'while' loop body"))
    self.advance()

    return res.success(WhileNode(condition, body))

  def parse_function(self):
    res = ParseResult()
    if not self.match(TK.FUN):
      return res.failure(self.err("Expected 'fun' keyword"))
    self.advance()

    if not self.match(TT.IDENT):
      return res.failure(self.err("Expected function name"))
    func_name = self.current_token
    self.advance()

    if not self.match(TT.LPAREN):
      return res.failure(self.err("Expected '('"))
    self.advance()

    params = []
    if not self.match(TT.RPAREN):
      if not self.match(TT.IDENT):
        return res.failure(self.err("Expected parameter"))
      params.append(self.current_token)
      self.advance()

      while self.match(TT.COMMA):
        self.advance()
        if not self.match(TT.IDENT):
          return res.failure(self.err("Expected parameter after ','"))
        params.append(self.current_token)
        self.advance()

    if not self.match(TT.RPAREN):
      return res.failure(self.err("Expected ')'"))
    self.advance()

    if not self.match(TT.LBRACE):
      return res.failure(self.err("Expected '{'"))
    self.advance()

    body = []
    statements = res.register(self.parse_statements())
    if res.error:
      return res
    body = statements.element_nodes

    if not self.match(TT.RBRACE):
      return res.failure(self.err("Expected '}'"))
    self.advance()

    return res.success(FunctionDeclarationNode(func_name, params, body))
