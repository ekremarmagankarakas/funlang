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


class IllegalSyntaxError(Error):
  def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, "Illegal Syntax", details)


class RuntimeError(Error):
  def __init__(self, pos_start, pos_end, details, context):
    super().__init__(pos_start, pos_end, "Runtime Error", details)
    self.context = context

  def as_string(self):
    result = self.generate_traceback()
    result += f"{self.error_name}: {self.details}\n"
    result += f"File {self.pos_start.file_name}, line {self.pos_start.line + 1}, column {self.pos_start.column + 1}"
    return result

  def generate_traceback(self):
    result = ""
    pos = self.pos_start
    context = self.context
    while context:
      result += f"  File {pos.file_name}, line {pos.line + 1}, in {context.display_name}\n"
      pos = context.parent_entry_pos
      context = context.parent
    return "Traceback (most recent call last):\n" + result
