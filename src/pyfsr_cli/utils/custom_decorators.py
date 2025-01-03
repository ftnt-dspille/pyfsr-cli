from functools import wraps


def requires_client(f):
    """Decorator to initialize client only for commands that need it"""

    @wraps(f)
    def wrapper(ctx, *args, **kwargs):
        if ctx.obj.client is None:
            ctx.obj.init_client()
        return f(ctx, *args, **kwargs)

    return wrapper
