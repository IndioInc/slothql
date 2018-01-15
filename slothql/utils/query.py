import json


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
