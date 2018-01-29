from graphql.language import ast

from ..selections import selections_to_dict


def test_get_selections_to_dict():
    selections = [
        ast.Field(name='foo'),
        ast.Field(name='nested', selection_set=ast.SelectionSet([
            ast.Field(name='bar'),
            ast.Field(name='more_nested', selection_set=ast.SelectionSet(selections=[
                ast.Field(name='baz'),
            ]))
        ]))
    ]

    assert {'foo': None, 'nested': {'bar': None, 'more_nested': {'baz': None}}} == selections_to_dict(selections)
