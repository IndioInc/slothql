import dataclasses
import inspect
import typing as t

from slothql.utils import get_attr_fields, annotations


@dataclasses.dataclass()
class BaseOptions:
    parent: t.Any
    name: str
    abstract: bool = False
    description: t.Optional[str] = None

    def __post_init__(self):
        for field in dataclasses.fields(self):  # type: dataclasses.Field
            assert annotations.is_valid_type(getattr(self, field.name), field.type), (
                f"`{field.name} = {getattr(self, field.name)}`"
                f" does not match type annotation `{field.type.__name__}`"
            )


class BaseMeta(type):
    def __new__(
        mcs,
        name: str,
        bases: t.Tuple[type],
        attrs: dict,
        options_class: t.Type[BaseOptions] = BaseOptions,
        **kwargs,
    ):
        assert "Meta" not in attrs or inspect.isclass(
            attrs["Meta"]
        ), "attribute Meta has to be a class"
        cls: BaseMeta = super().__new__(mcs, name, bases, attrs)
        base_option = cls.merge_options(*mcs.get_options_bases(bases))
        meta_attrs = get_attr_fields(attrs["Meta"]) if "Meta" in attrs else {}

        option_fields = {field.name for field in dataclasses.fields(options_class)}
        for attr_name, value in meta_attrs.items():
            if attr_name not in option_fields:
                raise AttributeError(
                    f"Meta received an unexpected attribute `{attr_name} = {value}`"
                )
        cls._meta = options_class(
            **cls.merge_options(
                base_option, cls.get_option_attrs(name, base_option, attrs, meta_attrs)
            )
        )
        return cls

    def get_option_attrs(
        cls, name: str, base_attrs: dict, attrs: dict, meta_attrs: dict
    ) -> dict:
        defaults = {
            "parent": cls,
            "name": meta_attrs.get("name") or name,
            "abstract": meta_attrs.get("abstract", False),
        }
        return {**meta_attrs, **defaults}

    def merge_options(cls, *options: dict) -> dict:
        result = {}
        for option_set in options:
            for name, value in option_set.items():
                result[name] = cls.merge_field(result.get(name), value)
        return result

    @classmethod
    def get_options_bases(mcs, bases: t.Tuple[type]) -> t.Iterable[dict]:
        yield from (
            dataclasses.asdict(base._meta)
            for base in reversed(bases)
            if issubclass(base, BaseType)
        )

    @classmethod
    def merge_field(mcs, old, new):
        if isinstance(new, dict):
            return {**(old or {}), **new}
        return new


class BaseType(metaclass=BaseMeta):
    _meta: BaseOptions

    @staticmethod
    def __new__(cls, *more, **kwargs):
        assert (
            not cls._meta.abstract
        ), f"Abstract type {cls.__name__} can not be instantiated"
        return super().__new__(cls)

    def __init__(self) -> None:
        raise RuntimeError(
            f"`{self.__class__.__name__}` initialization is not supported"
        )

    def __repr__(self):
        return self.__class__.__name__


LazyType = t.Union[t.Type[BaseType], t.Callable]


def resolve_lazy_type(lazy_type: LazyType) -> t.Type[BaseType]:
    resolved = lazy_type() if inspect.isfunction(lazy_type) else lazy_type
    assert inspect.isclass(resolved) and issubclass(
        resolved, BaseType
    ), f'"lazy_type" needs to inherit from BaseType or be a lazy reference, not {lazy_type}'
    return resolved
