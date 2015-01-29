PYL10N
------

Pyl10n is a localization (l10n) library for python, written in 2008-2010.

BEWARE: This is old code, migrated to git. Previously, this was found at:
https://code.osso.nl/projects/pyl10n


SUMMARY
-------

Pyl10n intends to replace the standard locale module which is not thread safe
(locale.setlocale() updates the entire process' locale settings). Pyl10n allows
you to supply the language setting at conversion function call time or through
a callback function that allows you to have a thread-specific language. E.g.
for Django you could pass `django.utils.translation.get_language` which gets
the currently selected language.

Its a complement to `gettext` solutions that do not depend on process-wide language settings.


PORTABILITY
-----------

Pyl10n has been tested with python 2.5 through 2.7 on Debian/Ubuntu Linux systems.


LIMITATIONS
-----------

As of this writing, it is not complete yet. It does implement `format()` and
`currency()` correctly (see http://bugs.python.org/issue1222 ) and it has
most of the time formatting support that `strftime(3)` specifies.

In the near future (ha ha) it will support address formatting functions.

Look at the lists of finished and unfinished functions in the source.
