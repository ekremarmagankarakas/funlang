from ast_nodes import Program, FunctionDeclaration, PrintStatement, Variable, BinaryOperation, Number, ExpressionStatement, FunctionCall, UnaryOperation


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
    raise SyntaxError(f"{error_msg} at token {self.current_token}")

  def parse(self):
    if self.current_token.type == "FUN":
      functions = []
      while self.current_token.type != "EOF":
        functions.append(self.parse_function())
      return Program(functions)
    else:
      return self.parse_expression()

  def parse_function(self):
    self.expect("FUN", "Expected 'fun' keyword")
    func_name = self.expect("IDENT", "Expected function name")
    self.expect("LPAREN", "Expected '('")
    params = []

    if self.current_token.type != "RPAREN":
      param = self.expect("IDENT", "Expected parameter")
      params.append(param.value)

      while self.current_token.type == "COMMA":
        self.advance()
        param = self.expect("IDENT", "Expected parameter after ','")
        params.append(param.value)

    self.expect("RPAREN", "Expected ')'")
    self.expect("LBRACE", "Expected '{'")

    body = []
    while self.current_token.type != "RBRACE":
      body.append(self.parse_statement())

    self.expect("RBRACE", "Expected '}'")
    return FunctionDeclaration(func_name.value, params, body)

  def parse_statement(self):
    tok = self.current_token
    if tok.type == "YELL":
      self.advance()
      self.expect("LPAREN", "Expected '('")
      expression = self.parse_expression()
      self.expect("RPAREN", "Expected ')' after expression")
      self.expect("SEMICOLON", "Expected ';' after expression")
      return PrintStatement(expression)

    expression = self.parse_expression()
    self.expect("SEMICOLON", "Expected ';' after expression")
    return ExpressionStatement(expression)

  def parse_expression(self):
    left = self.parse_term()
    while self.current_token.type in ("PLUS", "MINUS"):
      op = self.current_token.value
      self.advance()
      right = self.parse_term()
      left = BinaryOperation(left, op, right)
    return left

  def parse_term(self):
    left = self.parse_factor()
    while self.current_token.type in ("MULTIPLY", "DIVIDE"):
      op = self.current_token.value
      self.advance()
      right = self.parse_factor()
      left = BinaryOperation(left, op, right)
    return left

  def parse_factor(self):
    if self.current_token.type == "MINUS":
      self.advance()
      right = self.parse_factor()
      return UnaryOperation("-", right)
    return self.parse_primary()

  def parse_primary(self):
    tok = self.current_token
    if tok.type == "IDENT":
      self.advance()
      if self.current_token.type == "LPAREN":
        self.advance()
        args = []
        if self.current_token.type != "RPAREN":
          arg = self.parse_expression()
          args.append(arg)
          while self.current_token.type == "COMMA":
            self.advance()
            arg = self.parse_expression()
            args.append(arg)
        self.expect("RPAREN", "Expected ')' after function arguments")
        return FunctionCall(tok.value, args)
      return Variable(tok.value)
    elif tok.type == "INT" or tok.type == "FLOAT":
      self.advance()
      return Number(tok.value)
    else:
      raise SyntaxError(f"Unexpected type encountered: {tok.type}")
