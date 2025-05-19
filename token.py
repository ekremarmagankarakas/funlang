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
