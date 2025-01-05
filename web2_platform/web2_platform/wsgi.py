"""
WSGI config for web2_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web2_platform.settings')

# Initialize Django WSGI application early to ensure the app is loaded
application = get_wsgi_application()
