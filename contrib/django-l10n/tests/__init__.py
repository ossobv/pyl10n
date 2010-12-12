from django.conf import settings
from project.l10n.tests.middleware import *


# Make sure the middleware is loaded if we're going to test it.
if 'project.l10n.middleware.L10nMiddleware' not in settings.MIDDLEWARE_CLASSES:
    settings.MIDDLEWARE_CLASSES += ('project.l10n.middleware.L10nMiddleware',)
