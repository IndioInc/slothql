import graphql


class ListMixin:
    def __init__(self, **kwargs):
        assert 'type' in kwargs, f'ListMixin requires "type" kwarg, kwargs={kwargs}'

        self.many = kwargs.pop('many', False)
        assert isinstance(self.many, bool), f'many has to be of type bool, not {self.many}'
        if self.many:
            kwargs.update(type=graphql.GraphQLList(kwargs.get('type')))
        super().__init__(**kwargs)
