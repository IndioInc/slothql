import json

from typing import NamedTuple

from slothql.utils.case import camelcase_to_snake


class InvalidOperation(RuntimeError):
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
        data = {camelcase_to_snake(k): v for k, v in data.items()}
        if not data.get('query'):
            raise InvalidOperation('"query" not found in json object')
        if 'variables' in data and isinstance(data['variables'], str):
            try:
                data['variables'] = json.loads(data['variables'])
            except ValueError as e:
                raise InvalidOperation(f'Could not parse variables `{repr(data["variables"])}`. {e}')
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
            raise InvalidOperation(f'Invalid JSON: {e}')

        if not isinstance(json_query, dict):
            raise InvalidOperation('GraphQL queries must a dictionary')

        return cls.serialize(json_query)
