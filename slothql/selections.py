import typing as t

import graphql
from graphql.language import ast

from .types.fields.filter import Filter

Selections = t.Dict[str, t.Optional[dict]]


class Selection(t.NamedTuple):
    field_name: str
    filter = Filter.SKIP
    selections: t.FrozenSet['Selection'] = None

    @classmethod
    def from_ast(cls, ast_fields: t.Iterable[ast.Field]) -> t.FrozenSet['Selection']:
        return frozenset(
            Selection(
                field_name=field.name.value,
                selections=field.selection_set and cls.from_ast(field.selection_set.selections),
            ) for field in ast_fields
        )


def get_selections(info: graphql.ResolveInfo) -> t.FrozenSet[Selection]:
    return Selection.from_ast(info.field_asts[0].selection_set.selections)
