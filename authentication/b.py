def login(*args, **kwargs):
    def decorator(fun):
        def wrapper(*args, **kwargs):
            return fun(*args, **kwargs)
        return wrapper
    return decorator

@login()
def t0(c):
    return c

print(t0(100))