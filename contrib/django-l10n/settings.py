# Add/set these in your settings.py

# Select the available languages
LANGUAGE_CODE = 'en' # the django tests require this to be 'en'
LANGUAGE_CODES = ('en', 'nl') # comment this out to force use of LANGUAGE_CODE
LOCALE_PATHS = ('%s/locale' % DJANGO_DIR,)

# Add the http-accept-language reading middleware
MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('project.l10n.middleware.L10nMiddleware',)

# Add the app to the installed apps to allow tests
INSTALLED_APPS = INSTALLED_APPS + ('project.l10n.middleware',)
