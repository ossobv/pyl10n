#!/usr/bin/env python
# vim: set ts=8 sw=4 sts=4 et:
#=======================================================================
# Copyright (C) 2008,2009, Walter Doekes (wdoekes) at OSSO B.V.
# This file is part of Pyl10n.
#
# Pyl10n is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyl10n is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pyl10n.  If not, see <http://www.gnu.org/licenses/>.
#=======================================================================


import os
try: import cPickle as pickle
except: import pickle
_locale_path = os.path.join(os.path.dirname(__file__), '..', 'locale')
_current_locale_callable = lambda: 'C'


def setlocale(locale):
    setlocalefunc(lambda: locale)

def setlocalefunc(callable):
    global _current_lang_callable
    _current_lang_callable = callable

def localeconv(locale=None):
    locale = locale or _get_locale()
    ret = {}
    ret.update(_get_category(locale, 'LC_MONETARY'))
    ret.update(_get_category(locale, 'LC_NUMERIC'))
    # We've removed trailing zeroes at generation time
    assert 0 not in ret['grouping'] and 0 not in ret['mon_grouping']
    return ret

def localeconv_by_category(category, locale=None):
    locale = locale or _get_locale()
    assert category in ('LC_ADDRESS', 'LC_MEASUREMENT', 'LC_MONETARY', \
            'LC_NAME', 'LC_NUMERIC', 'LC_PAPER', 'LC_TELEPHONE', 'LC_TIME')
    return _get_category(locale, category)

def _get_category(locale, category):
    try:
        data = open(os.path.join(_locale_path, locale, category), 'rb')
        ret = pickle.load(data)
        assert type(ret) == dict
        return ret
    except Exception, e:
        from sys import stderr
        print >> stderr, type(e), e
        return {}

def _get_locale():
    global _current_lang_callable
    return _current_lang_callable()

def pyl10n_core_test():
    # FIXME: create tests :)
    pass
