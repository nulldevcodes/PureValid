class ValidationError(Exception):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field
    def __str__(self):
        return f"{self.field + ': ' if self.field else ''}{super().__str__()}"

class ValidationErrors(Exception):
    def __init__(self, errors=None):
        self.errors = errors or []
    def add(self, error):
        self.errors.append(error)
    def __bool__(self):
        return bool(self.errors)
    def __str__(self):
        msgs = [str(e) for e in self.errors]
        return f"{len(self.errors)} validation error(s): " + "; ".join(msgs)
