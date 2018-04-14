# Quick start

## Installation
```bash
pip install slothql
```

## Defining schema
```python
import slothql

class Query(slothql.Object):
    hello = slothql.String(resolver=lambda: 'world')

schema = slothql.Schema(query=Query)

slothql.gql(schema=schema, query='query { hello }')
# output: {'data': {'hello', 'world'}}
```
