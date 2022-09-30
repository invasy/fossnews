"""Meta definitions."""


class Singleton(type):
    """
    Singleton metaclass.

    Example:

    .. code-block:: python

        class Foo(metaclass=Singleton):
            pass
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Create or return singleton instance."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


def bind_to(cls, name: str = None):
    """
    Class decorator that adds a new method to the class.

    :param cls: class to add a method to.
    :param name: method name.
    :return: decorator.
    """
    def wrapper(f):
        setattr(cls, name if name is not None else f.__name__, f)
        return f

    return wrapper
