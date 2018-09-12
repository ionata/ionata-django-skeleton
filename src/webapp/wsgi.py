import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webapp.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Dev')

# pylint: disable=wrong-import-position
from configurations.wsgi import get_wsgi_application  # type: ignore # noqa

application = get_wsgi_application()
