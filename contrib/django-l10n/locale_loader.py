from django.conf import settings as _s
import pyl10n as locale

# If this file is loaded twice, you'll have issues
# as you'll get two copies of the locale module with
# different module-specific globals.
# Therefore, make sure you use the same "module path"
# in middleware.py (or implicitly through
# MIDDLEWARE_CLASSES) as in templatestags/l10n.py
# to load the locale_loader.
if len(_s.LOCALE_PATHS) != 0:
    locale.setlocalepath(_s.LOCALE_PATHS[0])
