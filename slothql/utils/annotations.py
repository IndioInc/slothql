import typing


def _validate_nested(value, annotation) -> bool:
    if typing.Union is annotation.__origin__:
        return any(validate(value, i) for i in annotation.__args__)

    if list is annotation.__origin__:
        item_type, = annotation.__args__
        return isinstance(value, list) and all(validate(i, item_type) for i in value)

    if set is annotation.__origin__:
        item_type, = annotation.__args__
        return isinstance(value, set) and all(validate(i, item_type) for i in value)

    if tuple is annotation.__origin__:
        return (
            isinstance(value, tuple)
            and len(value) == len(annotation.__args__)
            and all(
                validate(i, i_type) for i, i_type in zip(value, annotation.__args__)
            )
        )

    if dict is annotation.__origin__:
        key_type, value_type = annotation.__args__
        return isinstance(value, dict) and all(
            validate(k, key_type) and validate(v, value_type) for k, v in value.items()
        )

    if type is annotation.__origin__:
        type_, = annotation.__args__
        return isinstance(value, type) and issubclass(value, type_)

    raise NotImplementedError(
        f"validate is not implemented for {repr(annotation.__origin__)}"
    )


def validate(value, annotation) -> bool:
    if (
        annotation is typing.Any
        or annotation is typing.List
        and isinstance(value, list)
        or annotation is typing.Set
        and isinstance(value, set)
        or annotation is typing.Tuple
        and isinstance(value, tuple)
        or annotation is typing.Dict
        and isinstance(value, dict)
    ):
        return True

    if isinstance(annotation, typing._GenericAlias):
        return _validate_nested(value, annotation)

    if annotation in (str, bool, int, float, list, set, tuple, type(None)):
        return isinstance(value, annotation)

    if isinstance(annotation, type):
        return isinstance(value, annotation)

    raise NotImplementedError(f"validate is not implemented for {repr(annotation)}")
