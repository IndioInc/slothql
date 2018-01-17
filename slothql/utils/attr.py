import inspect


def is_magic_name(name: str) -> bool:
    return name.startswith('__') and name.endswith('__')


def get_attrs(obj) -> dict:
    return {name: getattr(obj, name) for name in dir(obj) if not is_magic_name(name)}


def get_attr_fields(obj) -> dict:
    return {
        name: getattr(obj, name) for name in dir(obj)
        if not is_magic_name(name)
           and not inspect.ismethod(getattr(obj, name))
           and not inspect.isfunction(getattr(obj, name))
    }
