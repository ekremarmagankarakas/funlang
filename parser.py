from ast_nodes import Program, FunctionDeclarationNode, PrintStatementNode, VariableNode, BinaryOperationNode, NumberNode, ExpressionStatementNode, FunctionCallNode, UnaryOperationNode
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
    if self.current_token.type == "FUN":
      functions = []
      while self.current_token.type != "EOF":
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
    if (err := self.expect("FUN", "Expected 'fun' keyword")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)
    func_name = self.expect("IDENT", "Expected function name")
    if isinstance(func_name, IllegalSyntaxError):
      return res.failure(func_name)

    if (err := self.expect("LPAREN", "Expected '('")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    params = []
    if self.current_token.type != "RPAREN":
      ident = self.expect("IDENT", "Expected parameter")
      if isinstance(ident, IllegalSyntaxError):
        return res.failure(ident)
      params.append(ident.value)

      while self.current_token.type == "COMMA":
        self.advance()
        ident = self.expect("IDENT", "Expected parameter after ','")
        if isinstance(ident, IllegalSyntaxError):
          return res.failure(ident)
        params.append(ident.value)

    if (err := self.expect("RPAREN", "Expected ')'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    if (err := self.expect("LBRACE", "Expected '{'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    body = []
    while self.current_token.type != "RBRACE":
      stmt = res.register(self.parse_statement())
      if res.error:
        return res
      body.append(stmt)

    if (err := self.expect("RBRACE", "Expected '}'")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)

    return res.success(FunctionDeclarationNode(func_name.value, params, body))

  def parse_statement(self):
    res = ParseResult()
    if self.current_token.type == "YELL":
      self.advance()
      if (err := self.expect("LPAREN", "Expected '('")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if (err := self.expect("RPAREN", "Expected ')' after expression")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      if (err := self.expect("SEMICOLON", "Expected ';' after expression")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      return res.success(PrintStatementNode(expr))

    expr = res.register(self.parse_expression())
    if res.error:
      return res
    if (err := self.expect("SEMICOLON", "Expected ';' after expression")) and isinstance(err, IllegalSyntaxError):
      return res.failure(err)
    return res.success(ExpressionStatementNode(expr))

  def parse_expression(self):
    res = ParseResult()
    left = res.register(self.parse_term())
    if res.error:
      return res
    while self.current_token and self.current_token.type in ("PLUS", "MINUS"):
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
    while self.current_token and self.current_token.type in ("MULTIPLY", "DIVIDE"):
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_factor(self):
    res = ParseResult()
    if self.current_token.type in ("PLUS", "MINUS"):
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
    while self.current_token and self.current_token.type == "POWER":
      op = self.current_token
      self.advance()
      right = res.register(self.parse_factor())
      if res.error:
        return res
      left = BinaryOperationNode(left, op, right)
    return res.success(left)

  def parse_atom(self):
    res = ParseResult()
    if self.current_token.type in ("INT", "FLOAT"):
      tok = self.current_token
      self.advance()
      return res.success(NumberNode(tok))
    elif self.current_token.type == "LPAREN":
      self.advance()
      expr = res.register(self.parse_expression())
      if res.error:
        return res
      if (err := self.expect("RPAREN", "Expected ')'")) and isinstance(err, IllegalSyntaxError):
        return res.failure(err)
      return res.success(expr)
    return res.failure(IllegalSyntaxError(self.current_token.pos_start, self.current_token.pos_end, f"Unexpected token: {self.current_token.type}"))

  def parse_primary(self):
    res = ParseResult()
    tok = self.current_token
    if tok.type == "IDENT":
      self.advance()
      if self.current_token.type == "LPAREN":
        self.advance()
        args = []
        if self.current_token.type != "RPAREN":
          arg = res.register(self.parse_expression())
          if res.error:
            return res
          args.append(arg)
          while self.current_token.type == "COMMA":
            self.advance()
            arg = res.register(self.parse_expression())
            if res.error:
              return res
            args.append(arg)
        if (err := self.expect("RPAREN", "Expected ')' after function arguments")) and isinstance(err, IllegalSyntaxError):
          return res.failure(err)
        return res.success(FunctionCallNode(tok.value, args))
      return res.success(VariableNode(tok.value))
    elif tok.type in ("INT", "FLOAT"):
      self.advance()
      return res.success(NumberNode(tok))
    return res.failure(IllegalSyntaxError(tok.pos_start, tok.pos_end, f"Unexpected token: {tok.type}"))
