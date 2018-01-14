import django
from django.conf import settings


def pytest_configure():
    settings.configure()
    django.setup()
