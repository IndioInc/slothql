import json

from typing import NamedTuple


class OperationSyntaxError(RuntimeError):
    pass


class Operation(NamedTuple):
    query: str
    variables: dict
    operation_name: str

    @classmethod
    def from_string(cls, string: str) -> 'class':
        return cls.from_dict(cls.from_raw_json(string))

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**cls.serialize(data))

    @classmethod
    def serialize(cls, data: dict) -> dict:
        assert isinstance(data, dict), f'Expected data to of instance dict, got {data}'
        if not data.get('query'):
            raise OperationSyntaxError('"query" not found in json object')
        return {
            'query': data['query'],
            'variables': data.get('variables'),
            'operation_name': data.get('operation_name'),
        }

    @classmethod
    def from_raw_json(cls, data: str) -> dict:
        try:
            json_query = json.loads(data)
        except json.JSONDecodeError as e:
            raise OperationSyntaxError(f'Invalid JSON: {e}')

        if not isinstance(json_query, dict):
            raise OperationSyntaxError('GraphQL queries must a dictionary')

        return cls.serialize(json_query)
