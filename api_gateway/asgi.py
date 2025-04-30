"""
ASGI config for api_gateway project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api_gateway.settings")

application = get_asgi_application()


# TODO evaluate this configuration, maybe we should remove this and configure nginx to serve these static files
from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler


application = ASGIStaticFilesHandler(application)
