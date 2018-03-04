from graphql.type.typemap import GraphQLTypeMap


class TypeMap(GraphQLTypeMap):
    def __init__(self, types, *, auto_camelcase: bool = False):
        self.auto_camelcase = auto_camelcase
        super().__init__(types)

    def to_camelcase(self):
        pass

    def update(self, data: dict, **kwargs):
        super().update(data, **kwargs)

    @classmethod
    def reducer(cls, type_map, of_type):
        return super().reducer(map=type_map, type=of_type)
