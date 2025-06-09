from error import IllegalCharError
from token import Token, TokenType as TT, KeywordType as TK


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
    if identifier in TK._value2member_map_:
      return Token(TK[identifier.upper()], identifier)
    else:
      return Token(TT.IDENT, identifier, pos_start, self.pos)

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
      return Token(TT.INT, int(num), pos_start, self.pos)
    else:
      return Token(TT.FLOAT, float(num), pos_start, self.pos)

  def read_string(self):
    self.advance()
    string = ""
    pos_start = self.pos.copy()
    escape_character = False

    escape_characters = {
        'n': '\n',
        't': '\t'
    }

    while self.current_char is not None and self.current_char != '"' or escape_character:
      if escape_character:
        string += escape_characters.get(self.current_char, self.current_char)
      else:
        if self.current_char == '\\':
          escape_character = True
        string += self.current_char
      self.advance()
      escape_character = False

    if self.current_char != '"':
      return IllegalCharError(
          self.pos.copy(), self.pos.copy(), "Unterminated string literal")

    self.advance()
    return Token(TT.STRING, string, pos_start, self.pos)

  def read_not_equals(self):
    self.advance()
    pos_start = self.pos.copy()
    if self.current_char == '=':
      self.advance()
      return Token(TT.NE, '!=', pos_start, self.pos)
    return IllegalCharError(pos_start, self.pos.copy(), "Expected '=' after '!'")

  def read_equals(self):
    self.advance()
    pos_start = self.pos.copy()
    if self.current_char == '=':
      self.advance()
      return Token(TT.EE, '==', pos_start, self.pos)
    return Token(TT.EQUALS, '=', pos_start, self.pos)

  def read_less_than(self):
    self.advance()
    pos_start = self.pos.copy()
    if self.current_char == '=':
      self.advance()
      return Token(TT.LTE, '<=', pos_start, self.pos)
    return Token(TT.LT, '<', pos_start, self.pos)

  def read_greater_than(self):
    self.advance()
    pos_start = self.pos.copy()
    if self.current_char == '=':
      self.advance()
      return Token(TT.GTE, '>=', pos_start, self.pos)
    return Token(TT.GT, '>', pos_start, self.pos)

  def read_arrow_or_less_than(self):
    self.advance()
    pos_start = self.pos.copy()
    if self.current_char == '>':
      self.advance()
      return Token(TT.ARROW, '->', pos_start, self.pos)
    return Token(TT.MINUS, '-', pos_start, self.pos)

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
        tokens.append(read_string)
      elif self.current_char == '!':
        read_not_equals = self.read_not_equals()
        if isinstance(read_not_equals, IllegalCharError):
          return [], read_not_equals
        tokens.append(read_not_equals)
      elif self.current_char == '=':
        read_equals = self.read_equals()
        if isinstance(read_equals, IllegalCharError):
          return [], read_equals
        tokens.append(read_equals)
      elif self.current_char == '<':
        read_less_than = self.read_less_than()
        if isinstance(read_less_than, IllegalCharError):
          return [], read_less_than
        tokens.append(read_less_than)
      elif self.current_char == '>':
        read_greater_than = self.read_greater_than()
        if isinstance(read_greater_than, IllegalCharError):
          return [], read_greater_than
        tokens.append(read_greater_than)
      elif self.current_char == '-':
        read_arrow_or_less_than = self.read_arrow_or_less_than()
        if isinstance(read_arrow_or_less_than, IllegalCharError):
          return [], read_arrow_or_less_than
        tokens.append(read_arrow_or_less_than)
      elif self.current_char in TT._value2member_map_:
        pos_start = self.pos.copy()
        tokens.append(
            Token(TT._value2member_map_[self.current_char], self.current_char, pos_start, self.pos))
        self.advance()
      else:
        return [], IllegalCharError(self.pos.copy(), self.pos.copy(), self.current_char)

    tokens.append(Token(TT.EOF))
    return tokens, None
