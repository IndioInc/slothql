import enum
import itertools
import typing as t

import graphql
from graphql.language import ast


@enum.unique
class FilterOperator(enum.Enum):
    EQUALS = "eq"


FilterPrimitive = t.Union[int, bool, float, str]


class FilterExpression(t.NamedTuple):
    path: str
    value: t.Optional["FilterPrimitive"]
    operator: FilterOperator = FilterOperator.EQUALS.value

    @classmethod
    def from_object_value(
        cls, object_value: ast.ObjectValue
    ) -> t.Iterable["FilterExpression"]:
        for field in object_value.fields:
            if isinstance(field.value, ast.ObjectValue):
                yield from (
                    FilterExpression(
                        path=f"{field.name.value}.{expression.path}",
                        value=expression.value,
                        operator=expression.operator,
                    )
                    for expression in cls.from_object_value(field.value)
                )
            elif isinstance(field.value, ast.IntValue):
                yield FilterExpression(
                    path=field.name.value, value=int(field.value.value)
                )
            elif isinstance(field.value, ast.FloatValue):
                yield FilterExpression(
                    path=field.name.value, value=float(field.value.value)
                )
            elif isinstance(field.value, ast.BooleanValue):
                yield FilterExpression(
                    path=field.name.value, value=bool(field.value.value)
                )
            elif isinstance(field.value, ast.StringValue):
                yield FilterExpression(
                    path=field.name.value, value=str(field.value.value)
                )
            else:
                raise NotImplementedError(field)


class Selection(t.NamedTuple):
    field_name: str
    selections: t.Optional[t.List["Selection"]] = None
    filters: t.Optional[t.List[FilterExpression]] = None

    @classmethod
    def from_ast_field(
        cls, ast_field: t.Union[ast.Field, ast.InlineFragment]
    ) -> t.Iterable["Selection"]:
        if isinstance(ast_field, ast.Field):
            filter_object = next(
                (a.value for a in ast_field.arguments if a.name.value == "filter"), None
            )
            yield Selection(
                field_name=ast_field.name.value,
                selections=(
                    ast_field.selection_set
                    and list(cls.from_ast_fields(ast_field.selection_set.selections))
                ),
                filters=(
                    filter_object
                    and list(FilterExpression.from_object_value(filter_object))
                ),
            )
        elif isinstance(ast_field, ast.InlineFragment):
            yield from cls.from_ast_fields(ast_field.selection_set.selections)
        else:
            raise ValueError(
                f"{cls.from_ast_field.__name__}: Unexpected ast_field: {ast_field}"
            )

    @classmethod
    def from_ast_fields(
        cls, ast_fields: t.Iterable[ast.Field]
    ) -> t.Iterable["Selection"]:
        yield from itertools.chain(*(cls.from_ast_field(field) for field in ast_fields))


class ResolveInfo(t.NamedTuple):
    field_name: str
    selection: Selection

    @classmethod
    def from_info(cls, info: graphql.ResolveInfo) -> "ResolveInfo":
        return ResolveInfo(
            field_name=info.field_name,
            selection=next(
                s
                for s in Selection.from_ast_fields(info.field_asts)
                if s.field_name == info.field_name
            ),
        )
