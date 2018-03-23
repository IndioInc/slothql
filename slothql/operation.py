import json

from typing import NamedTuple


def from_raw_json(data: str) -> dict:
    try:
        json_query = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    if not isinstance(json_query, dict):
        raise ValueError('GraphQL queries must a dictionary')

    if 'query' not in json_query:
        raise ValueError('"query" not found in json object')
    return json_query


class Operation(NamedTuple):
    query: str
    variables: dict
    operation_name: str

    @classmethod
    def from_string(cls, string: str) -> 'class':
        return cls.from_dict(from_raw_json(string))

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            query=data.get('query'),
            variables=data.get('variables'),
            operation_name=data.get('operationName') or data.get('operation_name'),
        )
