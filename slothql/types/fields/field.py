import functools
import typing as t

import graphql

from slothql import types
from slothql.types.base import LazyType, resolve_lazy_type, BaseType

from .. import mixins
from .resolver import (
    get_resolver,
    Resolver,
    PartialResolver,
    ResolveArgs,
    is_valid_resolver,
)


class Field:
    __slots__ = (
        "description",
        "many",
        "null",
        "_type",
        "_resolver",
        "source",
        "parent",
        "name",
        "filterable",
    )

    def __init__(
        self,
        of_type: t.Union[LazyType, str],
        *,
        resolver: PartialResolver = None,
        description: str = None,
        source: str = None,
        many: bool = False,
        null: bool = True,
        name: str = None,
        parent=None,
        filterable=True,
    ):
        self._type = of_type

        assert resolver is None or is_valid_resolver(
            resolver
        ), f"Resolver has to be callable, but got {resolver}"
        self._resolver = resolver

        assert description is None or isinstance(
            description, str
        ), f"description needs to be of type str, not {description}"
        self.description = description

        assert source is None or isinstance(
            source, str
        ), f"source= has to be of type str, not {source}"
        self.source = source

        assert many is None or isinstance(
            many, bool
        ), f"many= has to be of type bool, not {many}"
        self.many = many

        assert null is None or isinstance(
            null, bool
        ), f"null= has to be of type bool, not {null}"
        self.null = null

        self.name = name
        self.parent = parent

        assert isinstance(
            filterable, bool
        ), f"Invalid value `{filterable}` for argument `filterable`"
        self.filterable = filterable

    @classmethod
    def reinstantiate(cls, field: "Field", name: str, parent: BaseType):
        assert isinstance(
            field, Field
        ), f"field has to be of type {repr(Field)}, not {repr(field)}"
        return cls(
            of_type=field._type,
            resolver=field._resolver,
            description=field.description,
            source=field.source,
            many=field.many,
            filterable=field.filterable,
            name=name,
            parent=parent,
        )

    @property
    def of_type(self) -> t.Type[BaseType]:
        if self._type == "self":
            resolved_type = self.parent
        else:
            resolved_type = resolve_lazy_type(self._type)
        if issubclass(resolved_type, types.Object):
            resolved_type.validate_field(self, resolved_type)
        return resolved_type

    @property
    def resolver(self) -> Resolver:
        resolver = get_resolver(self, self._resolver)
        assert resolver is None or callable(
            resolver
        ), f"resolver needs to be callable, not {resolver}"
        return functools.partial(self.resolve, resolver)

    @property
    def arguments(self) -> t.Optional:
        if issubclass(self.of_type, types.Object) and self.filterable:
            return {
                "filter": self.of_type.filter_class,
                # 'pagination': {},  # TODO
                # 'ordering': {},  # TODO
            }
        return {}

    def resolve(
        self, resolver: t.Optional[Resolver], obj, info: graphql.ResolveInfo, **kwargs
    ):
        resolved = (resolver or self.resolve_field)(obj, info, kwargs)
        if issubclass(self.of_type, mixins.Resolvable):
            return self.of_type.resolve(resolved, info, kwargs, self.many)
        return resolved

    def get_internal_name(self, name: str) -> str:
        return self.source or name

    def resolve_field(self, obj, info: graphql.ResolveInfo, args: ResolveArgs):
        if obj is None:
            return None
        name = self.get_internal_name(info.field_name)
        if isinstance(obj, dict):
            value = obj.get(name)
        else:
            value = getattr(obj, name, None)
        return value

    def __eq__(self, other: "class"):
        if not isinstance(other, Field):
            raise ValueError(
                f"slothql.Field can only be compared with other slothql.Field instances, not {other}"
            )
        return other.name == other.name and other.parent == other.parent

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
