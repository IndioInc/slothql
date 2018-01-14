import json


def is_magic_name(name: str) -> bool:
    return name.startswith('__') and name.endswith('__')


def get_object_attributes(obj) -> dict:
    return {name: getattr(obj, name) for name in dir(obj) if not is_magic_name(name)}


def query_from_raw_json(data: str) -> str:
    try:
        json_query = json.loads(data)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    if not isinstance(json_query, dict):
        raise ValueError('GraphQL queries must a dictionary')

    if 'query' not in json_query:
        raise ValueError('"query" not not found in json object')
    return json_query['query']
