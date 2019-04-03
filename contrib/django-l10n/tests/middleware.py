from django.conf import settings
from django.test import TestCase
from django.utils import translation


class LanguageSelectTest(TestCase):
    ACCEPT_LANGUAGE = 'sv, en-gb;q=0.7, nl-nl;q=0.8'

    def setUp(self, **kwargs):
        # Store settings that we mess with
        self.SETTINGS_LANGUAGE_CODE = settings.LANGUAGE_CODE
        try: self.SETTINGS_LANGUAGE_CODES = settings.LANGUAGE_CODES
        except AttributeError: self.SETTINGS_LANGUAGE_CODES = ()

    def tearDown(self):
        # Restore messed with settings
        settings.LANGUAGE_CODE = self.SETTINGS_LANGUAGE_CODE
        settings.LANGUAGE_CODES = self.SETTINGS_LANGUAGE_CODES

    def test_single_language(self):
        if hasattr(settings, 'LANGUAGE_CODES'):
            settings.LANGUAGE_CODES = ()
        settings.LANGUAGE_CODE = 'sv'

        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE=self.ACCEPT_LANGUAGE)

        # The middleware should be disabled because of the single language,
        # ergo it does not set Content-Language. However someone else might.
        language = response._headers.get('content-language', (None, ''))[1]
        self.assertTrue(language == '' or language == 'sv')
        self.assertEquals(translation.get_language(), 'sv')

    def test_select_default_language(self):
        settings.LANGUAGE_CODES = ('da', 'es', 'fr')
        settings.LANGUAGE_CODE = 'unused'

        response = self.client.get('/')
        self.assertEquals(response._headers.get('content-language', (None, ''))[1], 'da')

    def test_select_fallback_language(self):
        settings.LANGUAGE_CODES = ('da', 'es', 'fr')
        settings.LANGUAGE_CODE = 'unused'

        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE=self.ACCEPT_LANGUAGE)
        self.assertEquals(response._headers.get('content-language', (None, ''))[1], 'da')

    def test_select_second_language(self):
        settings.LANGUAGE_CODES = ('da', 'en', 'fr')
        settings.LANGUAGE_CODE = 'unused'

        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE=self.ACCEPT_LANGUAGE)
        self.assertEquals(response._headers.get('content-language', (None, ''))[1], 'en')
