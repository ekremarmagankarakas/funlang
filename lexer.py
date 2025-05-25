from error import IllegalCharError
from token import Token


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
        '^': "POWER",
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
    pos_start = self.pos.copy()
    while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
      identifier += self.current_char
      self.advance()
    if identifier in self.keywords:
      return Token(self.keywords[identifier], identifier)
    else:
      return Token("IDENT", identifier, pos_start, self.pos)

  def read_number(self):
    num = ""
    dot_count = 0
    pos_start = self.pos.copy()
    while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
      if self.current_char == '.':
        if dot_count == 1:
          break
        dot_count += 1
      num += self.current_char
      self.advance()
    if dot_count == 0:
      return Token("INT", int(num), pos_start, self.pos)
    else:
      return Token("FLOAT", float(num), pos_start, self.pos)

  def read_string(self):
    self.advance()
    string = ""
    pos_start = self.pos.copy()
    while self.current_char is not None and self.current_char != '"':
      string += self.current_char
      self.advance()

    if self.current_char != '"':
      return IllegalCharError(
          self.pos.copy(), self.pos.copy(), "Unterminated string literal")

    self.advance()
    return Token("STRING", string, pos_start, self.pos)

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
        pos_start = self.pos.copy()
        tokens.append(
            Token(self.token_map[self.current_char], self.current_char, pos_start, self.pos))
        self.advance()
      else:
        return [], IllegalCharError(self.pos.copy(), self.pos.copy(), self.current_char)

    tokens.append(Token("EOF"))
    return tokens, None
