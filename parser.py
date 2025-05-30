from ast_nodes import Program, FunctionDeclarationNode, PrintStatementNode, VariableAccessNode, VariableDeclarationNode, BinaryOperationNode, NumberNode, ExpressionStatementNode, FunctionCallNode, UnaryOperationNode, IfNode
from token import Token, KEYWORDS, SYMBOLS, TT_EOF, TT_INT, TT_FLOAT, TT_STRING, TT_IDENT, TT_PLUS, TT_MINUS, TT_MULTIPLY, TT_DIVIDE, TT_POWER, TT_LPAREN, TT_RPAREN, TT_LBRACE, TT_RBRACE, TT_LBRACKET, TT_RBRACKET, TT_COMMA, TT_SEMICOLON, TT_EQUALS, TK_FUN, TK_YELL, TK_VAR, TT_EQUALS, TT_EE, TT_NE, TT_LT, TT_GT, TT_GTE, TT_LTE, TK_NOT, TK_OR, TK_AND, TK_IF, TK_ELIF, TK_ELSE
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

  def expect(self, expectee, error_msg):
    if self.current_token.type == expectee:
      tok = self.current_token
      self.advance()
      return tok
    return IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, error_msg)

  def parse(self):
    res = ParseResult()
    if self.current_token.type == TK_FUN:
      functions = []
      while self.current_token.type != TT_EOF:
        func = res.register(self.parse_function())
        if res.error:
          return res
        functions.append(func)
      return res.success(Program(functions))
    else:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      return res.success(expr)

  def parse_function(self):
    res = ParseResult()
    if (err := self.expect(TK_FUN, "Expected 'fun' keyword")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)
    func_name = self.expect(TT_IDENT, "Expected function name")
    if isinstance(func_name, IllegalSyntaxError):
      return res.failure(func_name)

    if (err := self.expect(TT_LPAREN, "Expected '('")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    params = []
    if self.current_token.type != TT_RPAREN:
      ident = self.expect(TT_IDENT, "Expected parameter")
      if isinstance(ident, IllegalSyntaxError):
        return res.failure(ident)
      params.append(ident.value)

      while self.current_token.type == TT_COMMA:
        self.advance()
        ident = self.expect(TT_IDENT, "Expected parameter after ','")
        if isinstance(ident, IllegalSyntaxError):
          return res.failure(ident)
        params.append(ident.value)

    if (err := self.expect(TT_RPAREN, "Expected ')'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    if (err := self.expect(TT_LBRACE, "Expected '{'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    body = []
    while self.current_token.type != TT_RBRACE:
      stmt = res.register(self.parse_statement())
      if res.error:
        return res
      body.append(stmt)

    if (err := self.expect(TT_RBRACE, "Expected '}'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    return res.success(FunctionDeclarationNode(func_name.value, params, body))

  def parse_statement(self):
    res = ParseResult()
    if self.current_token.type == TK_YELL:
      self.advance()
      if (err := self.expect(TT_LPAREN, "Expected '('")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if (err := self.expect(TT_RPAREN, "Expected ')' after expression")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      if (err := self.expect(TT_SEMICOLON, "Expected ';' after expression")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      return res.success(PrintStatementNode(expr))

    expr = res.register(self.parse_expression())
    if res.error:
      return res
    if (err := self.expect(TT_SEMICOLON, "Expected ';' after expression")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)
    return res.success(ExpressionStatementNode(expr))

  def parse_expression(self):
    res = ParseResult()
    if self.current_token.type == TK_VAR:
      self.advance()
      var_name = self.current_token
      if (err := self.expect(TT_IDENT, "Expected 'IDENT' after variable declaration")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      if (err := self.expect(TT_EQUALS, "Expected '=' after variable name")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
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
    if self.current_token.type == TK_NOT:
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
    return self.power()

  def power(self):
    res = ParseResult()
    left = res.register(self.parse_atom())
    if res.error:
      return res
    while self.current_token and self.current_token.type == TT_POWER:
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_atom(self):
    res = ParseResult()
    tok = self.current_token
    if self.current_token.type in (TT_INT, TT_FLOAT):
      self.advance()
      return res.success(NumberNode(tok))
    elif self.current_token.type == TT_IDENT:
      self.advance()
      return res.success(VariableAccessNode(tok))
    elif self.current_token.type == TT_LPAREN:
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if (err := self.expect(TT_RPAREN, "Expected ')'")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      return res.success(expr)
    elif self.current_token.type == TK_IF:
      if_expr = res.register(self.parse_if_expression())
      if res.error:
        return res
      return res.success(if_expr)
    return res.failure(IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"Unexpected token: {self.current_token.type}"))

  def parse_if_expression(self):
    res = ParseResult()
    cases = []
    else_case = []
    if (err := self.expect(TK_IF, "Expected 'if' keyword")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    condition = res.register(self.parse_expression())
    if res.error:
      return res

    if (err := self.expect(TT_LBRACE, "Expected '{' after 'if' condition")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    expressions = []
    while self.current_token.type != TT_RBRACE:
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      expressions.append(expr)

    if (err := self.expect(TT_RBRACE, "Expected '}' after 'if' block")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)
    cases.append((condition, expressions))

    while self.current_token.type == TK_ELIF:
      self.advance()
      condition = res.register(self.parse_expression())
      if res.error:
        return res

      if (err := self.expect(TT_LBRACE, "Expected '{' after 'elif' condition")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)

      expressions = []
      while self.current_token.type != TT_RBRACE:
        expr = res.register(self.parse_expression())
        if res.error:
          return res
        expressions.append(expr)

      if (err := self.expect(TT_RBRACE, "Expected '}' after 'elif' block")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      cases.append((condition, expressions))

    if self.current_token.type == TK_ELSE:
      self.advance()
      if (err := self.expect(TT_LBRACE, "Expected '{' after 'else' keyword")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)

      while self.current_token.type != TT_RBRACE:
        expr = res.register(self.parse_expression())
        if res.error:
          return res
        else_case.append(expr)

      if (err := self.expect(TT_RBRACE, "Expected '}' after 'else' block")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)

    return res.success(IfNode(cases, else_case))
