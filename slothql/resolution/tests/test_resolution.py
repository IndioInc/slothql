from graphql.language import ast

import slothql


def test_selections_from_ast():
    selections = [
        ast.Field(ast.Name(value="foo"), arguments=[]),
        ast.Field(
            ast.Name(value="nested"),
            arguments=[],
            selection_set=ast.SelectionSet(
                [
                    ast.Field(ast.Name(value="bar"), arguments=[]),
                    ast.Field(
                        ast.Name(value="more_nested"),
                        arguments=[],
                        selection_set=ast.SelectionSet(
                            selections=[ast.Field(ast.Name(value="baz"), arguments=[])]
                        ),
                    ),
                ]
            ),
        ),
    ]

    assert [
        slothql.Selection(field_name="foo"),
        slothql.Selection(
            field_name="nested",
            selections=[
                slothql.Selection(field_name="bar"),
                slothql.Selection(
                    field_name="more_nested",
                    selections=[slothql.Selection(field_name="baz")],
                ),
            ],
        ),
    ] == list(slothql.Selection.from_ast_fields(selections))


def test_selection_arguments():
    selections = [
        ast.Field(
            ast.Name("field"),
            arguments=[
                ast.Argument(
                    ast.Name(value="filter"),
                    ast.ObjectValue(
                        fields=[
                            ast.ObjectField(
                                ast.Name("foo"),
                                ast.ObjectValue(
                                    fields=[
                                        ast.ObjectField(
                                            ast.Name("bar"), ast.IntValue(1)
                                        )
                                    ]
                                ),
                            ),
                            ast.ObjectField(ast.Name("baz"), ast.StringValue("baz")),
                        ]
                    ),
                )
            ],
        )
    ]
    assert [
        slothql.Selection(
            field_name="field",
            selections=None,
            filters=[
                slothql.FilterExpression(path="foo.bar", value=1),
                slothql.FilterExpression(path="baz", value="baz"),
            ],
        )
    ] == list(slothql.Selection.from_ast_fields(selections))