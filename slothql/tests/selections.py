from graphql.language import ast

from ..selections import Selection


def test_selections_from_ast():
    selections = [
        ast.Field(name='foo'),
        ast.Field(name='nested', selection_set=ast.SelectionSet([
            ast.Field(name='bar'),
            ast.Field(name='more_nested', selection_set=ast.SelectionSet(selections=[
                ast.Field(name='baz'),
            ])),
        ])),
    ]

    assert frozenset((
        Selection(field_name='foo'),
        Selection(field_name='nested', selections=frozenset((
            Selection(field_name='bar'),
            Selection(field_name='more_nested', selections=frozenset((
                Selection(field_name='baz'),
            ))),
        ))),
    )) == Selection.from_ast(selections)
