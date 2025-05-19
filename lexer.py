class Token:
  def __init__(self, type_, value=None):
    self.type = type_
    self.value = value

  def __repr__(self):
    if self.value is not None:
      return f"{self.type}({repr(self.value)})"
    return self.type


class Error:
  def __init__(self, pos_start, pos_end, error_name, details):
    self.pos_start = pos_start
    self.pos_end = pos_end
    self.error_name = error_name
    self.details = details

  def as_string(self):
    return f"{self.error_name}: {self.details}\nFile {self.pos_start.file_name}, line {self.pos_start.line + 1}, column {self.pos_start.column + 1}"


class IllegalCharError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, "Illegal Character", details)


class Position:
  def __init__(self, index, line, column, file_name, file_text):
    self.index = index
    self.line = line
    self.column = column
    self.file_name = file_name
    self.file_text = file_text

  def advance(self, current_char=None):
    self.index += 1
    self.column += 1
    if current_char == '\n':
      self.line += 1
      self.column = 0
    return self

  def copy(self):
    return Position(self.index, self.line, self.column, self.file_name, self.file_text)


class Lexer:
  def __init__(self, file_name, source):
    self.source = source
    self.pos = Position(-1, 0, -1, file_name, source)
    self.current_char = None
    self.advance()
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

  def advance(self):
    self.pos.advance(self.source[self.pos.index])
    self.current_char = self.source[self.pos.index] if self.pos.index < len(
        self.source) else None

  def read_identifier(self):
    identifier = ""
    while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
      identifier += self.current_char
      self.advance()
    if identifier in self.keywords:
      return Token(self.keywords[identifier], identifier)
    else:
      return Token("IDENT", identifier)

  def read_number(self):
    num = ""
    while self.current_char is not None and self.current_char.isdigit():
      num += self.current_char
      self.advance()
    return Token("NUMBER", int(num))

  def read_string(self):
    self.advance()
    string = ""
    while self.current_char is not None and self.current_char != '"':
      string += self.current_char
      self.advance()

    if self.current_char != '"':
      return IllegalCharError(
          self.pos.copy(), self.pos.copy(), "Unterminated string literal")

    self.advance()
    return Token("STRING", string)

  def tokenizer(self):
    tokens = []
    while self.current_char is not None:

      if self.current_char.isspace():
        self.advance()
        continue
      elif self.current_char.isalpha():
        tokens.append(self.read_identifier())
      elif self.current_char.isdigit():
        tokens.append(self.read_number())
      elif self.current_char == '"':
        read_string = self.read_string()
        if isinstance(read_string, IllegalCharError):
          return [], read_string
        else:
          tokens.append(read_string)
      elif self.current_char in self.token_map:
        tokens.append(
            Token(self.token_map[self.current_char], self.current_char))
        self.advance()
      else:
        return [], IllegalCharError(self.pos.copy(), self.pos.copy(), self.current_char)

    tokens.append(Token("EOF"))
    return tokens, None
