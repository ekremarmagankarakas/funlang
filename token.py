from enum import Enum


class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value
    self.pos_start = pos_start.copy() if pos_start else None
    self.pos_end = pos_end.copy() if pos_end else None

  def __repr__(self):
    if self.value is not None:
      return f"{self.type.name}({repr(self.value)})"
    return self.type.name


class TokenType(Enum):
  INT = "INT"
  FLOAT = "FLOAT"
  STRING = "STRING"
  IDENT = "IDENT"

  PLUS = "+"
  MINUS = "-"
  MULTIPLY = "*"
  DIVIDE = "/"
  POWER = "^"

  LPAREN = "("
  RPAREN = ")"
  LBRACE = "{"
  RBRACE = "}"
  LBRACKET = "["
  RBRACKET = "]"
  COMMA = ","
  SEMICOLON = ";"

  EQUALS = "="
  EE = "EE"
  NE = "NE"
  LT = "LT"
  GT = "GT"
  GTE = "GTE"
  LTE = "LTE"

  EOF = "EOF"


class KeywordType(Enum):
  FUN = "fun"
  VAR = "var"
  AND = "and"
  OR = "or"
  NOT = "not"
  IF = "if"
  ELIF = "elif"
  ELSE = "else"
  FOR = "for"
  WHILE = "while"
  RETURN = "return"
  BREAK = "break"
  CONTINUE = "continue"

class BuiltInFunctionType(Enum):
  PRINT = "print"
