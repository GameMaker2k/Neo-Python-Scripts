import sys

def var_dump(var, indent=0):
    """Equivalent of PHP's var_dump for Python 2 and 3."""
    spacing = ' ' * indent
    if isinstance(var, (list, tuple, set, dict)):
        if isinstance(var, dict):
            print('{}Dict({})'.format(spacing, len(var)))
            for key, value in var.items():
                print('{}  [{}]:'.format(spacing, repr(key)))
                var_dump(value, indent + 4)
        else:
            print('{}{}({})'.format(spacing, type(var).__name__, len(var)))
            for item in var:
                var_dump(item, indent + 4)
    elif isinstance(var, str):
        if sys.version_info[0] < 3:  # Python 2
            print('{}str: "{}"'.format(spacing, var.encode('utf-8')))
        else:  # Python 3
            print('{}str: "{}"'.format(spacing, var))
    elif isinstance(var, (int, float, bool)):
        print('{}{}: {}'.format(spacing, type(var).__name__, var))
    elif var is None:
        print('{}None'.format(spacing))
    else:
        print('{}{}: {}'.format(spacing, type(var).__name__, repr(var)))

# Example usage:
var_dump({"name": "John", "age": 30, "scores": [10, 20, 30], "is_active": True})
