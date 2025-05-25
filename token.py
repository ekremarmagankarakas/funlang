class Token:
  def __init__(self, type_, value=None, pos_start=None, pos_end=None):
    self.type = type_
    self.value = value
    self.pos_start = pos_start.copy() if pos_start else None
    self.pos_end = pos_end.copy() if pos_end else None

  def __repr__(self):
    if self.value is not None:
      return f"{self.type}({repr(self.value)})"
    return self.type


TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_STRING = "STRING"
TT_IDENT = "IDENT"

TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MULTIPLY = "MULTIPLY"
TT_DIVIDE = "DIVIDE"
TT_POWER = "POWER"

TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
TT_LBRACE = "LBRACE"
TT_RBRACE = "RBRACE"
TT_LBRACKET = "LBRACKET"
TT_RBRACKET = "RBRACKET"
TT_COMMA = "COMMA"
TT_SEMICOLON = "SEMICOLON"
TT_EQUALS = "EQUALS"

TT_EOF = "EOF"

TK_FUN = "FUN"
TK_YELL = "YELL"
TK_DOUBT = "DOUBT"
TK_MAYBE = "MAYBE"
TK_VAR = "VAR"

SYMBOLS = {
    '+': TT_PLUS,
    '-': TT_MINUS,
    '*': TT_MULTIPLY,
    '/': TT_DIVIDE,
    '^': TT_POWER,
    '(': TT_LPAREN,
    ')': TT_RPAREN,
    '{': TT_LBRACE,
    '}': TT_RBRACE,
    '[': TT_LBRACKET,
    ']': TT_RBRACKET,
    ';': TT_SEMICOLON,
    ',': TT_COMMA,
    '=': TT_EQUALS,
}

KEYWORDS = {
    "fun": TK_FUN,
    "yell": TK_YELL,
    "doubt": TK_DOUBT,
    "maybe": TK_MAYBE,
    "var": TK_VAR,
}
