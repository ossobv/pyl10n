#!/usr/bin/env python
# vim: set ts=8 sw=4 sts=4 et:
#=======================================================================
# Copyright (C) 2008, OSSO B.V.
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
import __builtin__, os, cPickle as pickle, sys

#
# IMPLEMENTED:
#
# Most functions behave very or exactly similarly to their locale.* counterpart.
#
# Globals modification:
# * setlocale() <= application wide locale setting: use nl_NL instead of nl_NL.utf-8!
# * setlocalefunc() <= uses a callable should return a string (for django this would be
#   lambda: to_locale(get_language()))
#
# The following functions take an optional callable so you don't have to call
# setlocalefunc():
# * localeconv() <= works as intended
# * localeconvext() <= loads all available locale categories into a dictionary
# * format() <= limited to a single format specified (e.g. '%08d')
# * currency() <= works as intended
# * str() <= calls format with %f

#
# NOT IMPLEMENTED:
#
# * Must be implemented: atof, atoi, 
# * Will be replaced: DAY_1 etc.. will be replaced with a time formatting function.
# * Should be implemented: address/telephone formatting functions
# * Won't be implemented any time soon: strcoll, strxfrm, format_string.
#

#
# BUGS:
#
# * Exception handling in _get_category is not properly done yet.
#
# * The locale_path is 'hardcoded' as relative to __file__.
#
# * The standard is unclear about how to handle [np]_sep_by_space for international
#   symbols. We assume that the space is an optional fourth character in int_curr_symbol.
#
# * format(...monetary=True) gets handled by currency(). This means that your format string
#   will be ignored.
#
# * string.letters is not modified when calling setlocale(). (In fact, no CTYPE/COLLATE
#   locale settings are used.)
#

#
# PYTHON BUGS:
#
# * Python is inconsistent with stripping or not stripping trailing zeroes from lists.
#
# * Python does not honor mon_grouping for monetary values.
#

_locale_path = os.path.join(os.path.dirname(__file__), '..', 'locale')
_current_lang_callable = lambda: 'C'

def setlocale(language):
    setlocalefunc(lambda: language)

def setlocalefunc(callable):
    global _current_lang_callable
    _current_lang_callable = callable

def localeconv(callable=None):
    language = _get_language(callable)
    ret = {}
    ret.update(_get_category(language, 'LC_MONETARY'))
    ret.update(_get_category(language, 'LC_NUMERIC'))
    # We've removed trailing zeroes at generation time
    assert 0 not in ret['grouping'] and 0 not in ret['mon_grouping']
    return ret

def localeconvext(callable=None):
    language = _get_language(callable)
    ret = {}
    for category in ('LC_ADDRESS', 'LC_MEASUREMENT', 'LC_MONETARY', 'LC_NAME', \
            'LC_NUMERIC', 'LC_PAPER', 'LC_TELEPHONE', 'LC_TIME'):
        ret[category] = _get_category(language, category)
    return ret

def format(format, val, grouping=False, monetary=False, callable=None):
    if monetary:
        assert format == u'%f'
        return currency(val, False, grouping, callable=callable)
        
    assert len(format) and format[0] == u'%'
    conv = localeconv(callable)

    ret = format % val
    if u'e' in ret or u'E' in ret: # we're looking at exponents.. blame the user
        return ret
    return _group_and_decimal(ret, grouping, conv['decimal_point'], \
            conv['thousands_sep'], conv['grouping'])

def currency(val, symbol=True, grouping=False, international=False, callable=None):
    conv = localeconv(callable)
    neg = val < 0
    val = abs(val)

    if neg:
        symbol_before = bool(conv['n_cs_precedes'])
        sign = conv['negative_sign']
        sep_by_space = bool(conv['n_sep_by_space'])
        positioning = conv['n_sign_posn']
    else:
        symbol_before = bool(conv['p_cs_precedes'])
        sign = conv['positive_sign']
        sep_by_space = bool(conv['p_sep_by_space'])
        positioning = conv['p_sign_posn']

    if international:
        symbol_char = conv['int_curr_symbol']
        fractionals = int(conv['int_frac_digits'])
        if len(symbol_char) > 3:
            space_between_symbol_value = symbol_char[3]
        else:
            space_between_symbol_value = ''
        symbol_char = symbol_char[0:3]
    else:
        symbol_char = conv['currency_symbol']
        fractionals = int(conv['frac_digits'])
        space_between_symbol_value = ('', ' ')[sep_by_space]

    ret = (u'%%.%if' % fractionals) % val
    ret = _group_and_decimal(ret, grouping, conv['mon_decimal_point'], \
            conv['mon_thousands_sep'], conv['mon_grouping'])

    if not symbol:
        if positioning == 0:
            return u'(%s%s%s)' % (ret,)
        elif positioning == 1 or positioning == 3 or positioning == 127:
            return u'%s%s' % (sign, ret)
        elif positioning == 2 or positioning == 4:
            return u'%s%s' % (ret, sign)
        assert False
        
    if symbol_before:
        args = [symbol_char, space_between_symbol_value, ret]
    else:
        args = [ret, space_between_symbol_value, symbol_char]

    if positioning == 0:
        ret = u'(%s%s%s)' % tuple(args)
    else:
        if positioning == 1 or (positioning == 3 and symbol_before) or positioning == 127:
            args.insert(0, sign)
        elif positioning == 2 or (positioning == 4 and not symbol_before):
            args.append(sign)
        elif positioning == 3:
            args.insert(2, sign)
        elif positioning == 4:
            args.insert(1, sign)
        else:
            assert False
        ret = u'%s%s%s%s' % tuple(args)

    return ret

def str(val, callable=None):
    return format('%s', val, callable=callable)

def _get_category(language, category):
    try:
        data = open(os.path.join(_locale_path, language, category), 'rb')
        ret = pickle.load(data)
        assert type(ret) == dict
        return ret
    except Exception, e:
        print type(e), e
        return {}

def _get_language(callable = None):
    global _current_lang_callable
    callable = callable or _current_lang_callable
    return _current_lang_callable()

def _group(val, group_char, group_list):
    if val[0] not in '0123456789':
        sign = val[0]
        val = val[1:]
    else:
        sign = ''

    ret = []
    i = len(val)
    # group_list defines grouping from right to left
    group = 127
    for group in group_list:
        if i <= 0 or group == 127: # CHAR_MAX => no more grouping
            break
        # append next group to list
        ret.insert(0, val[max(0,i-group):i])
        i -= group
    # continue with last value from group_list
    while i > 0:
        ret.insert(0, val[max(0,i-group):i])
        i -= group
    # concat and return
    return sign + group_char.join(ret)
    
def _group_and_decimal(val, grouping, decimal_char, group_char, group_list):
    if grouping:
        if u'.' in val:
            left, right = val.split(u'.')
            return u'%s%s%s' % (_group(left, group_char, group_list), decimal_char, right)
        else:
            return _group(val, group_char, group_list)
    return val.replace(u'.', decimal_char)

if __name__ == '__main__':
    import locale
    for lang in ('nl_NL', 'en_US'):
        print u'**** %s ****\n' % (lang,)
        locale.setlocale(locale.LC_MONETARY, lang + '.utf-8')
        locale.setlocale(locale.LC_NUMERIC, lang + '.utf-8')
        setlocale(lang)

        print u'%24s|%24s' % ('[locale]', '[pyl10n]')
        lconv = locale.localeconv()
        pconv = localeconv()
        keys = lconv.keys()
        keys.sort()
        for k in keys:
            print u'%24s|%24s <= %s' % (__builtin__.str(lconv[k]).decode('utf-8'), pconv[k], k)
        print

        print '%24s|%24s' % ('[locale]', '[pyl10n]')

        print '%24s|%24s' % (locale.str(-3.1415), str(-3.1415))
        for val in (0.7, -0.7, 1234567.89, -1234567.89):
            for monetary in (False, True):
                lval = locale.format('%f', val, True, monetary).decode('utf-8')
                pval = format('%f', val, True, monetary)
                print '%24s|%24s' % (lval, pval)
        for val in (0.7, -0.7, 1234567.89, -1234567.89):
            for intl in (False, True):
                lval = locale.currency(val, True, True, intl).decode('utf-8')
                pval = currency(val, True, True, intl)
                print '%24s|%24s' % (lval, pval)
        print

        print 'All available locale data:\n  ', localeconvext()
        print

