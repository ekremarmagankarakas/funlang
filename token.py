class Token:
  def __init__(self, type_, value=None):
    self.type = type_
    self.value = value

  def __repr__(self):
    if self.value is not None:
      return f"{self.type}({repr(self.value)})"
    return self.type
