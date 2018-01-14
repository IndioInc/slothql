from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest

from slothql import utils


def get_query_from_request(request: WSGIRequest) -> str:
    if request.method == 'GET':
        return request.GET.get('query', '')

    if not request.content_type:
        raise ValidationError('content-type not specified')

    if request.content_type == 'application/graphql':
        return request.body.decode()
    elif request.content_type == 'application/json':
        try:
            return utils.query_from_raw_json(request.body.decode('utf-8'))
        except ValueError as e:
            raise ValidationError(str(e))
    elif request.content_type in ('application/x-www-form-urlencoded', 'multipart/form-data'):
        return request.POST.get('query', '')
    raise ValidationError(f'Unsupported content-type {request.content_type}')
