PYL10N
------

Pyl10n is a localization (l10n) library for python, written in 2008-2010.

BEWARE: This is old code, migrated to git. Previously, this was found at:
https://code.osso.nl/projects/pyl10n


SUMMARY
-------

Pyl10n intends to replace the standard locale module which is not thread
safe (locale.setlocale() updates the entire process' locale settings).
Pyl10n allows you to supply the language setting at conversion function
call time or through a callback function that allows you to have a
thread-specific language. E.g.  for Django you could pass
``django.utils.translation.get_language`` which gets the currently
selected language.

Its a complement to `gettext` solutions that do not depend on
process-wide language settings.


PORTABILITY
-----------

Pyl10n has been tested with python 2.5 through 2.7 on Debian/Ubuntu
Linux systems. It's been known to work with Python 3 as well.

Python support before 2.7 cannot be guaranteed. Python support for 3 is
not well tested.


TODO
----

The generated locale files should be packaged separately so you don't
need to fetch them when using pyl10n with only a handful of selected
languages.


EXAMPLE
-------

Import pyl10n as locale:

.. code-block:: pycon

    >>> import pyl10n as locale

Hardcode the current thread locale.

.. code-block:: pycon

    >>> locale.setlocale('nl_NL')
    >>> print(locale.currency(12345.67))
    € 12345,67

Usually you'll want to set a function that returns the current thread
locale.

.. code-block:: pycon

    >>> getlocale = lambda: 'en_US'
    >>> locale.setlocalefunc(getlocale)
    >>> print(locale.format('%f', 12345.67, True, True))
    12,345.67

If you're using your own locale files, you may set up the path like this:

.. code-block:: console

    $ ls path/to/locale/en/ -1p
    LC_ADDRESS
    LC_MEASUREMENT
    LC_MESSAGES/
    LC_MONETARY
    LC_NAME
    LC_NUMERIC
    LC_PAPER
    LC_TELEPHONE
    LC_TIME

.. code-block:: pycon

    >>> locale.setlocalepath('path/to/locale')
    >>> locale.setlocale('en')
    >>> locale.teldom2string((31, 50, 1234567))
    '(50) 1234567'
    >>> locale.setlocale('sv')
    >>> locale.teldom2string((31, 50, 1234567))
    '050-1234567'

The data files are stored/read using pickle.


TESTS
-----

A quick selftest can be run:

.. code-block:: shell

    $ python -c 'from pyl10n import selftest; selftest()'
    ...

Differences between the locale output and the pyl10n output *may* be
attributed to an alternate/earlier source of locale date, or to custom
adjustments (improvements) by me (to the Dutch or English locale files).


LIMITATIONS
-----------

As of this writing, it is not complete yet. It does implement
``format()`` and ``currency()`` correctly (see
http://bugs.python.org/issue1222 ) and it has most of the time
formatting support that ``strftime(3)`` specifies.

In the near future (ha ha) it will support address formatting functions.

Look at the lists of finished and unfinished functions in the source.
