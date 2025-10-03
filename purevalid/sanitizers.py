import html
from collections.abc import Mapping
from .utils import is_iterable

def sanitize_string(value, trim=True, escape_html=False, lower=False, upper=False):
    if not isinstance(value, str):
        raise TypeError("sanitize_string expects a string input")
    result = value
    if trim:
        result = result.strip()
    if escape_html:
        result = html.escape(result)
    if lower:
        result = result.lower()
    if upper:
        result = result.upper()
    return result

def sanitize_list(lst, sanitizer, *args, **kwargs):
    if not isinstance(lst, list):
        raise TypeError("sanitize_list expects a list")
    return [sanitizer(item, *args, **kwargs) for item in lst]

def sanitize_dict(dct, sanitizer, *args, keys=None, **kwargs):
    if not isinstance(dct, Mapping):
        raise TypeError("sanitize_dict expects a dict-like object")
    result = {}
    for k, v in dct.items():
        if keys is None or k in keys:
            if isinstance(v, str):
                result[k] = sanitizer(v, *args, **kwargs)
            elif is_iterable(v) and not isinstance(v, (str, bytes)):
                if isinstance(v, list):
                    result[k] = sanitize_list(v, sanitizer, *args, **kwargs)
                elif isinstance(v, Mapping):
                    result[k] = sanitize_dict(v, sanitizer, *args, **kwargs)
                else:
                    result[k] = v
            else:
                result[k] = v
        else:
            result[k] = v
    return result
