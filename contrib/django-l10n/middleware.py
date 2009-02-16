from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
from django.utils.cache import patch_vary_headers
from django.utils import translation
from django.utils.translation import get_language
import pyl10n as locale
# Or alternately, if you've installed pyl10n in the django l10n dir:
#import l10n.pyl10n as locale, l10n.pyl10n.pyl10n_core as locale_config, os
#locale_config._locale_path = os.path.join(os.path.dirname(__file__), '..', 'locale')


class L10nMiddleware(object):
    """
    This is an updated version of django's very simple middleware
    that parses a request and decides what translation object to
    install in the current thread context. This allows pages to be
    dynamically translated to the language the user desires.

    The difference with django.middleware.locale.LocaleMiddleware
    is that this one checks settings.LANGUAGE_CODES for valid
    languages.

    Also, it sets the pyl10n locale for the current thread.
    """

    def __init__(self):
        if not hasattr(settings, 'LANGUAGE_CODES') or len(settings.LANGUAGE_CODES) == 0:
            locale.setlocale(settings.LANGUAGE_CODE) # this is en-us by default
            raise MiddlewareNotUsed('A fixed language code was set. Not using Accept-Language headers.')
        locale.setlocalefunc(translation.get_language)

    def process_request(self, request):
        # get_language_from_request returns a two-letter language code (en, nl, sv, etc..)
        language = translation.get_language_from_request(request)
        if language not in settings.LANGUAGE_CODES:
            language = settings.LANGUAGE_CODES[0]
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
