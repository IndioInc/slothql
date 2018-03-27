import json
from urllib.parse import urlencode

import pytest
from unittest import mock

from django.core.exceptions import ValidationError
from django.core.handlers.wsgi import WSGIRequest
from django.test import RequestFactory

import slothql
from slothql.operation import OperationSyntaxError

from ..request import get_operation_from_request


class TestGetOperation:
    rf = RequestFactory()
    data = {'query': 'query { hello }'}
    operation = slothql.Operation.from_dict(data)

    @pytest.mark.parametrize('value', (
            rf.get('', data=data),
            rf.post('', data=data),
            rf.post('', data=urlencode(data), content_type='application/x-www-form-urlencoded'),
            rf.post('', data=json.dumps(data), content_type='application/graphql'),
            rf.post('', data=json.dumps(data), content_type='application/json'),
    ))
    def test_query_from_request__valid(self, value: WSGIRequest):
        assert self.operation == get_operation_from_request(value)

    @pytest.mark.parametrize('content_type, message', (
            (rf.post('', data=data, content_type=''), 'content-type not specified'),
            (rf.post('', data=data, content_type='text/html'), f'Unsupported content-type text/html'),
    ))
    def test_query_from_request__invalid(self, content_type, message):
        with pytest.raises(ValidationError) as exc_info:
            assert self.operation == get_operation_from_request(content_type)
        assert message in str(exc_info.value)

    @mock.patch('slothql.operation.Operation.from_raw_json', side_effect=OperationSyntaxError('mocked exception'))
    def test_query_from_request__post_invalid_json(self, from_raw_json):
        request = self.rf.post('', data='{"query": "hello"}', content_type='application/json')
        with pytest.raises(ValidationError) as exc_info:
            get_operation_from_request(request)
        assert 'mocked exception' in str(exc_info.value)
