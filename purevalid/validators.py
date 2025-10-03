import re
from functools import wraps
from inspect import signature
from .errors import ValidationError, ValidationErrors
from .utils import is_iterable, check_regex, to_list
from .type_utils import type_name

def _validate_type(value, expected_type):
    if not isinstance(value, expected_type):
        raise ValidationError(
            f"Expected type '{type_name(expected_type)}', got '{type_name(value)}'")

def _validate_range(value, min_value=None, max_value=None):
    if (min_value is not None and value < min_value) or \
       (max_value is not None and value > max_value):
        raise ValidationError(f"Value {value} out of range [{min_value}, {max_value}]")

def _validate_length(value, min_len=None, max_len=None):
    length = len(value)
    if (min_len is not None and length < min_len) or \
       (max_len is not None and length > max_len):
        raise ValidationError(f"Length {length} out of bounds [{min_len}, {max_len}]")

def _validate_regex(value, pattern):
    if not check_regex(value, pattern):
        raise ValidationError(f"Value '{value}' does not match pattern '{pattern}'")

def _validate_membership(value, allowed):
    if value not in allowed:
        raise ValidationError(f"Value '{value}' not in allowed set {allowed}")

def _validate_custom(value, validator):
    try:
        result = validator(value)
        if result is False:
            raise ValidationError(f"Custom validation failed for value '{value}'")
    except ValidationError as ve:
        raise ve
    except Exception as e:
        raise ValidationError(f"Error in custom validator: {e}")

def validate(**rules):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sig = signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            errors = ValidationErrors()
            for arg_name, rule in rules.items():
                if arg_name not in bound.arguments:
                    errors.add(ValidationError(f"Missing argument '{arg_name}'", field=arg_name))
                    continue
                value = bound.arguments[arg_name]

                try:
                    if isinstance(rule, dict):
                        if 'type' in rule:
                            _validate_type(value, rule['type'])
                        if 'min' in rule or 'max' in rule:
                            _validate_range(value, rule.get('min'), rule.get('max'))
                        if 'min_len' in rule or 'max_len' in rule:
                            _validate_length(value, rule.get('min_len'), rule.get('max_len'))
                        if 'regex' in rule:
                            _validate_regex(value, rule['regex'])
                        if 'allowed' in rule:
                            _validate_membership(value, to_list(rule['allowed']))
                        if 'custom' in rule:
                            _validate_custom(value, rule['custom'])
                    elif isinstance(rule, type):
                        _validate_type(value, rule)
                    elif callable(rule):
                        _validate_custom(value, rule)
                    else:
                        errors.add(ValidationError(f"Invalid rule type for '{arg_name}'", field=arg_name))
                except ValidationError as ve:
                    errors.add(ValidationError(str(ve), field=arg_name))

            if errors:
                raise errors
            return func(*args, **kwargs)
        return wrapper
    return decorator
