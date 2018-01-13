import os

import pytest
from unittest import mock

from .. import template


@pytest.fixture()
def template_file(tmpdir_factory):
    file = tmpdir_factory.mktemp('templates').join('file.html')
    file.write('content')
    return file


def test_resolve_path(template_file):
    template_dir = os.path.dirname(template_file)
    base_dir = os.path.dirname(template_dir)
    with mock.patch('slothql.config.BASE_DIR', base_dir):
        with mock.patch('slothql.config.TEMPLATE_DIRS', [os.path.basename(template_dir)]):
            path = template.resolve_path('file.html')
    assert path == f'{base_dir}/{os.path.basename(template_dir)}/file.html' and os.path.exists(path)


def test_get_template_string(template_file):
    with mock.patch.object(template, 'resolve_path', return_value=template_file) as resolve_path:
        assert 'content' == template.get_template_string('file.html')
    resolve_path.assert_called_once_with('file.html')
