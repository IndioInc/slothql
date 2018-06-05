from graphql.language import ast

from ..selections import Selection


def test_selections_from_ast():
    selections = [
        ast.Field(ast.Name(value='foo')),
        ast.Field(ast.Name(value='nested'), selection_set=ast.SelectionSet([
            ast.Field(ast.Name(value='bar')),
            ast.Field(ast.Name(value='more_nested'), selection_set=ast.SelectionSet(selections=[
                ast.Field(ast.Name(value='baz')),
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
