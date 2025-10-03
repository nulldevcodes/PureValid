import re
from collections.abc import Iterable

def is_iterable(obj):
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes))

def flatten_list(nested_list):
    for item in nested_list:
        if is_iterable(item):
            yield from flatten_list(item)
        else:
            yield item

def check_regex(value, pattern):
    return bool(re.match(pattern, value))

def to_list(value):
    if isinstance(value, list):
        return value
    if is_iterable(value):
        return list(value)
    return [value]
