import os

from slothql import config
from .exceptions import TemplateNotFound


def resolve_path(template: str) -> str:
    for template_dir in config.TEMPLATE_DIRS:
        path = os.path.join(config.BASE_DIR, template_dir, template)
        if os.path.exists(path):
            return path
    raise TemplateNotFound(template)


def get_template_string(path: str):
    with open(resolve_path(path), 'r') as file:
        return file.read()
