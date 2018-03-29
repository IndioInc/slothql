# Quick start
some bla bla bla about the lib


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
# {'data': OrderedDict([('hello', 'world')])}
```
