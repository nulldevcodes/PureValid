from .errors import ValidationError, ValidationErrors
from .utils import to_list

class Schema:
    def __init__(self, schema_dict):
        self.schema = schema_dict

    def validate(self, data):
        errors = ValidationErrors()
        for key, rule in self.schema.items():
            if key not in data:
                errors.add(ValidationError(f"Missing key '{key}'", field=key))
                continue
            value = data[key]
            try:
                if isinstance(rule, dict):
                    if 'type' in rule:
                        if not isinstance(value, rule['type']):
                            raise ValidationError(f"Expected type '{rule['type'].__name__}' for key '{key}', got '{type(value).__name__}'")
                    if 'allowed' in rule:
                        allowed = to_list(rule['allowed'])
                        if value not in allowed:
                            raise ValidationError(f"Value '{value}' not in allowed set for key '{key}'")
                    if 'custom' in rule and callable(rule['custom']):
                        valid = rule['custom'](value)
                        if valid is False:
                            raise ValidationError(f"Custom validation failed for key '{key}'")
                elif callable(rule):
                    valid = rule(value)
                    if valid is False:
                        raise ValidationError(f"Custom validation failed for key '{key}'")
                else:
                    raise ValidationError(f"Invalid rule for key '{key}'")
            except ValidationError as ve:
                errors.add(ve)
        if errors:
            raise errors

def validate_schema(schema, data):
    if not isinstance(schema, Schema):
        raise TypeError("schema must be an instance of Schema")
    schema.validate(data)
