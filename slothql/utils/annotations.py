import functools
import typing as t


def _validate_nested(value, annotation) -> bool:
    if t.Union is annotation.__origin__:
        return any(is_valid_type(value, i) for i in annotation.__args__)

    if list is annotation.__origin__:
        item_type, = annotation.__args__
        return isinstance(value, list) and all(
            is_valid_type(i, item_type) for i in value
        )

    if set is annotation.__origin__:
        item_type, = annotation.__args__
        return isinstance(value, set) and all(
            is_valid_type(i, item_type) for i in value
        )

    if tuple is annotation.__origin__:
        return (
            isinstance(value, tuple)
            and len(value) == len(annotation.__args__)
            and all(
                is_valid_type(i, i_type)
                for i, i_type in zip(value, annotation.__args__)
            )
        )

    if dict is annotation.__origin__:
        key_type, value_type = annotation.__args__
        return isinstance(value, dict) and all(
            is_valid_type(k, key_type) and is_valid_type(v, value_type)
            for k, v in value.items()
        )

    if type is annotation.__origin__:
        type_, = annotation.__args__
        return isinstance(value, type) and issubclass(value, type_)

    raise NotImplementedError(
        f"validate is not implemented for {repr(annotation.__origin__)}"
    )


def is_valid_type(value, annotation) -> bool:
    if (
        annotation is t.Any
        or annotation is t.List
        and isinstance(value, list)
        or annotation is t.Set
        and isinstance(value, set)
        or annotation is t.Tuple
        and isinstance(value, tuple)
        or annotation is t.Dict
        and isinstance(value, dict)
    ):
        return True

    if isinstance(annotation, t._GenericAlias):
        return _validate_nested(value, annotation)

    if annotation in (str, bool, int, float, list, set, tuple, type(None)):
        return isinstance(value, annotation)

    if isinstance(annotation, type):
        return isinstance(value, annotation)

    raise NotImplementedError(f"validate is not implemented for {repr(annotation)}")


def validate_call(func: t.Callable) -> t.Callable:
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapped
