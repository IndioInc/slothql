import dataclasses
import typing as t

from slothql import resolution
from .base import BaseType, BaseMeta, BaseOptions
from .mixins import FieldMetaMixin
from .fields import Field
from .fields.filter import Filter


@dataclasses.dataclass()
class ObjectOptions(BaseOptions):
    fields: t.Dict[str, Field] = dataclasses.field(default_factory=dict)
    filter_class: t.Optional[t.Type[Filter]] = None


class ObjectMeta(FieldMetaMixin, BaseMeta):
    _meta: ObjectOptions
    __slots__ = ()

    def __new__(
        mcs,
        name,
        bases,
        attrs: dict,
        options_class: t.Type[ObjectOptions] = ObjectOptions,
        **kwargs,
    ):
        cls: t.Type[Object] = super().__new__(
            mcs, name, bases, attrs, options_class, **kwargs
        )
        if (
            not hasattr(cls, "is_type_of")
            or cls._meta.abstract
            and cls._meta.name is "Object"
        ):
            cls.is_type_of = None
        assert (
            cls._meta.abstract or cls._meta.fields
        ), f'"{name}" has to provide some fields, or use "class Meta: abstract = True"'
        return cls

    @property
    def filter_class(cls) -> t.Type[Filter]:
        if not cls._meta.filter_class:
            cls._meta.filter_class = cls.get_filter_class()
        return cls._meta.filter_class

    def get_filter_class(cls) -> t.Type[Filter]:
        return Filter.create_class(
            cls._meta.name + "Filter",
            fields={
                name: Field(
                    of_type=(
                        lambda field=field: field.of_type.filter_class
                        if issubclass(field.of_type, Object)
                        else field.of_type
                    ),
                    many=field.many,
                    null=field.null,
                    source=field.source,
                )
                for name, field in cls._meta.fields.items()
                if field.filterable
            },
        )

    @classmethod
    def validate_field(mcs, field: Field, of_type: t.Type[BaseType]):
        pass


class Object(resolution.Resolvable, BaseType, metaclass=ObjectMeta):
    _meta: ObjectOptions

    class Meta:
        abstract = True

    @classmethod
    def resolve(
        cls, resolver: resolution.Resolver, obj, info, args: dict, field
    ) -> t.Iterable:
        resolved = resolver(obj, info, args)
        if cls._meta.filter_class:
            return cls._meta.filter_class(**args.get("filter", {})).apply(resolved)
        return resolved

    @classmethod
    def is_type_of(cls, obj, info) -> bool:
        """
        This acts only as a template.
        It will be overwritten to None by the metaclass, if not implemented
        """
        pass
