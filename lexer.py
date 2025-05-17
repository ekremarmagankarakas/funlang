class Token:
  def __init__(self, type_, value=None, line=1, column=1):
    self.type = type_
    self.value = value
    self.line = line
    self.column = column

  def __repr__(self):
    if self.value is not None:
      return f"{self.type}({repr(self.value)})"
    return self.type


class Lexer:
  def __init__(self, source):
    self.source = source
    self.pos = 0
    self.keywords = {
        "fun": "FUN",
        "yell": "YELL",
        "doubt": "DOUBT",
        "maybe": "MAYBE",
    }
    self.token_map = {
        '+': "PLUS",
        '-': "MINUS",
        '*': "MULTIPLY",
        '/': "DIVIDE",
        '(': "LPAREN",
        ')': "RPAREN",
        '{': "LBRACE",
        '}': "RBRACE",
        '[': "LBRACKET",
        ']': "RBRACKET",
        ';': "SEMICOLON",
        ',': "COMMA",
    }

  def advance_pos(self):
    self.pos += 1

  def read_identifier(self):
    identifier = ""
    while self.pos < len(self.source) and not self.source[self.pos].isspace() and self.source[self.pos] not in self.token_map:
      identifier += self.source[self.pos]
      self.advance_pos()
    if identifier in self.keywords:
      return Token(self.keywords[identifier], identifier)
    else:
      return Token("IDENT", identifier)

  def read_number(self):
    num = ""
    while self.pos < len(self.source) and self.source[self.pos].isdigit():
      num += self.source[self.pos]
      self.advance_pos()
    return Token("NUMBER", int(num))

  def read_string(self):
    self.advance_pos()
    string = ""
    while self.pos < len(self.source) and self.source[self.pos] != '"':
      string += self.source[self.pos]
      self.advance_pos()
    self.advance_pos()
    return Token("STRING", string)

  def tokenizer(self):
    tokens = []
    while self.pos < len(self.source):
      char = self.source[self.pos]

      if char.isspace():
        self.advance_pos()
        continue
      elif char.isalpha():
        tokens.append(self.read_identifier())
      elif char.isdigit():
        tokens.append(self.read_number())
      elif char == '"':
        tokens.append(self.read_string())
      else:
        if char in self.token_map:
          tokens.append(Token(self.token_map[char], char))
          self.advance_pos()
        else:
          raise Exception(f"Unexpected Character: {char}")

    tokens.append(Token("EOF"))
    return tokens
