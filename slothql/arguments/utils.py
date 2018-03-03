from graphql.language import ast
from typing import Union

ScalarValueTypes = (ast.BooleanValue, ast.IntValue, ast.FloatValue, ast.StringValue, ast.EnumValue)


def parse_argument(value: ast.Value) -> Union[int, bool, str, dict, list]:
    if isinstance(value, ScalarValueTypes):
        return value.value
    elif isinstance(value, ast.ObjectValue):
        return {field.name.value: parse_argument(field.value) for field in value.fields}
    elif isinstance(value, ast.ListValue):
        return [parse_argument(value) for value in value.values]
    else:
        raise NotImplementedError(f'Unsupported Value type: {repr(value)}')
