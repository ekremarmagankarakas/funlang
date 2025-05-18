from ast_nodes import Program, FunctionDeclaration, PrintStatement, Variable, BinaryOperation, Number


class Parser:
  def __init__(self, tokens):
    self.tokens = tokens
    self.pos = 0

  def advance_pos(self):
    self.pos += 1

  def expect(self, expectee, error_msg):
    if self.tokens[self.pos].type == expectee:
      tok = self.tokens[self.pos]
      self.advance_pos()
      return tok
    raise SyntaxError(f"{error_msg} at token {self.tokens[self.pos]}")

  def parse(self):
    functions = []
    while self.tokens[self.pos].type != "EOF":
      functions.append(self.parse_function())
    return Program(functions)

  def parse_function(self):
    self.expect("FUN", "Expected 'fun' keyword")
    func_name = self.expect("IDENT", "Expected function name")
    self.expect("LPAREN", "Expected '('")
    params = []

    if self.tokens[self.pos].type != "RPAREN":
      param = self.expect("IDENT", "Expected parameter")
      params.append(param.value)

      while self.tokens[self.pos].type == "COMMA":
        self.advance_pos()
        param = self.expect("IDENT", "Expected parameter after ','")

    self.expect("RPAREN", "Expected ')'")
    self.expect("LBRACE", "Expected '{'")

    body = []
    while self.tokens[self.pos].type != "RBRACE":
      body.append(self.parse_statement())
      self.advance_pos()

    self.expect("RBRACE", "Expected '}'")
    return FunctionDeclaration(func_name.value, params, body)

  def parse_statement(self):
    if self.tokens[self.pos].type == "YELL":
      self.advance_pos()
      self.expect("LPAREN", "Expected '('")
      expression = self.parse_expression()
      self.expect("RPAREN", "Expected ')' after expression")
      return PrintStatement(expression)

  def parse_expression(self):
    left = self.parse_primary()
    while self.tokens[self.pos].type == "PLUS":
      op = self.tokens[self.pos].value
      self.advance_pos()
      right = self.parse_primary()
      left = BinaryOperation(left, op, right)
    return left

  def parse_primary(self):
    tok = self.tokens[self.pos]
    if tok.type == "IDENT":
      self.advance_pos()
      return Variable(tok.value)
    elif tok.type == "NUMBER":
      self.advance_pos()
      return Number(tok.value)
    else:
      raise SyntaxError(f"Unexpected type encountered: {tok.type}")
