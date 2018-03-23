from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest

from slothql.operation import Operation


def get_operation_from_request(request: WSGIRequest) -> Operation:
    if request.method == 'GET':
        return Operation.from_dict(request.GET)

    if not request.content_type:
        raise ValidationError('content-type not specified')

    if request.content_type in ('application/graphql', 'application/json', 'multipart/form-data'):
        try:
            return Operation.from_string(request.body.decode())
        except ValueError as e:
            raise ValidationError(str(e))
    elif request.content_type in ('application/x-www-form-urlencoded',):
        return Operation.from_dict(request.POST)
    raise ValidationError(f'Unsupported content-type {request.content_type}')
