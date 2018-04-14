# Fields

### slothql.Field
Base class for all fields
*

* **many**: bool = False
  one or many objects

  ```python
  class Query(slothql.Object):
      field = slothql.String(resolver=lambda: 'hello, world')
      fields = slothql.String(many=True, resolver=lambda: ['hello', 'world'])
  ```
* **default**: Any = None
  value to return, when field resolves to None
  ```python
  ```
## Scalars

### slothql.Integer

### slothql.Float

### slothql.String

### slothql.Boolean

### slothql.ID
