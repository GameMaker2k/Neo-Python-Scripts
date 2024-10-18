import sys

def print_r(var, indent=0):
    """Equivalent of PHP's print_r for Python 2 and 3."""
    spacing = ' ' * indent
    if isinstance(var, dict):
        print('{}{{'.format(spacing))
        for key, value in var.items():
            print('{}  [{}] => '.format(spacing, repr(key)))
            print_r(value, indent + 4)
        print('{}}}'.format(spacing))
    elif isinstance(var, (list, tuple, set)):
        print('{}{}'.format(spacing, type(var).__name__))
        print('{}['.format(spacing))
        for item in var:
            print_r(item, indent + 4)
        print('{}]'.format(spacing))
    elif isinstance(var, str):
        if sys.version_info[0] < 3:  # Python 2
            print('{}"{}"'.format(spacing, var.encode('utf-8')))
        else:  # Python 3
            print('{}"{}"'.format(spacing, var))
    elif isinstance(var, (int, float, bool)):
        print('{}{}'.format(spacing, var))
    elif var is None:
        print('{}None'.format(spacing))
    else:
        print('{}{}'.format(spacing, repr(var)))

# Example usage:
print_r({"name": "John", "age": 30, "scores": [10, 20, 30], "is_active": True})
