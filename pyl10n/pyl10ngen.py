#!/usr/bin/env python
# vim: set ts=8 sw=4 sts=4 et:
# ======================================================================
# Copyright (C) 2008-2016 Walter Doekes (wdoekes) at OSSO B.V.
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
# ======================================================================


# INTRODUCTION
# ============
# Pyl10n is a thread-safe /locale module/ replacement. Pyl10ngen
# converts libc-supplied locale sources files to pickled python files
# usable by pyl10n.
#
# Parsing the libc locale files has been pure guesswork. So sometimes
# the results may not be what the original author intended. See the BUGS
# / NOTES section for a couple of questions that remain.


# QUICK HOWTO
# ===========
# You shouldn't need to run this file. Preconverted languages files can
# be found where these python files are distributed:
# http://code.osso.nl/projects/pyl10n/


# BUGS / NOTES
# ============
#  * Comments might be legal further on the line, but its not used
#    often (only 3 out of 226 files do that).
#    Example: Language file as_IN corrupt: unexpected data:
#     \_ IGNORE;IGNORE;IGNORE;%... (%...)
#  * We only use the categories defines in the CATEGORIES list and not
#    LC_CTYPE/LC_COLLATE.. they are complicated and beyond the scope of
#    pyl10ns intentions right now.
#  * The copy keyword in a category tells us that you should only read
#    that category from the copied file.
#  * There is an 'include' keyword. We don't use it yet.
#  * We strip trailing zeroes from a list (e.g. mon_grouping 3;3;0
#    becomes [3,3]). This is not a bug but a deviation from the
#    C-documentation.

from __future__ import unicode_literals

import itertools
import os
import re

import six

# Read only these categories.. set to None to read all.
CATEGORIES = ('LC_ADDRESS', 'LC_MEASUREMENT', 'LC_MONETARY',
              'LC_NAME', 'LC_NUMERIC', 'LC_PAPER', 'LC_TELEPHONE',
              'LC_TIME')


class ParseException(Exception):
    pass


def parse_args(string, escape_char):
    re_nextarg = re.compile(r'(\s*(%s)\s*)' % '|'.join([
        r'LC_[A-Z]+', r'[A-Za-z_:-]+', r'"[^"]*"', r'-?[0-9]+',
        r'<[0-9A-Za-z_-]+>', r'<[0-9A-Za-z_-]+>..<[0-9A-Za-z_-]+>',
        r'\(<[0-9A-Za-z_-]+>,<[0-9A-Za-z_-]+>\)'
    ]))
    ret = []

    i = 0
    while True:
        m = re_nextarg.match(string, i)
        if not m:
            raise ParseException(
                'Unexpected data: \'\'\'%s<-- HERE -->%s\'\'\'' %
                (string[:i], string[i:]))
        ret.append(m.group(2))
        i = m.end(1)
        if i < len(string) and string[i] == ';':
            i += 1
            continue
        break

    for i in range(len(ret)):
        if ret[i].isdigit() or ret[i][0] == '-' and ret[i][1:].isdigit():
            ret[i] = int(ret[i])
        elif ret[i][0] == '"':
            try:
                ret[i] = six.text_type(ret[i][1:-1].replace(escape_char * 2,
                                                            escape_char))
                j = 0
                while j < len(ret[i]):
                    if (ret[i][j] == '<' and ret[i][j + 1] == 'U' and
                            ret[i][j + 6] == '>'):
                        ret[i] = (ret[i][0:j] +
                                  six.unichr(
                                      int(ret[i][(j + 2):(j + 6)], 16)) +
                                  ret[i][(j + 7):])
                    j += 1
            except UnicodeDecodeError:
                ret[i] = 'Someone put illegal non-ASCII here!'
        # else: <U0123> or <U01234567>
        # else: <U0123>..<U4567>
        # else: <TREMA>

    return ret


def parse_libc_localedata(filename, cache):
    if filename in cache:
        return cache[filename]
    cache[filename] = None  # catch broken recursion: will fail on .get access

    # The result
    ret = {}

    input = open(filename, 'rb')
    comment_char, escape_char = '#', '\\\\'
    category = None
    multiline_buffer = False

    re_cat_s = r'^(LC_[A-Z]+)(\s*Comment\s+.*)?$'
    re_cat = re.compile(re_cat_s.replace('Comment', comment_char), re.DOTALL)
    re_stmt = re.compile(r'^([A-Za-z_]+)\s+(.*?)$', re.DOTALL)
    re_comment_s = r'^Comment(\s+.*)?$'
    re_comment = re.compile(
        re_comment_s.replace('Comment', comment_char))
    re_midcomment_s = r'^(([^"]|"[^"]*")+)Comment.*(Escape)$'
    re_midcomment = re.compile(
        re_midcomment_s.replace(
            'Comment', comment_char).replace('Escape', escape_char))
    re_multiline_s = r'(^|[^Escape]|EscapeEscape)*Escape$'
    re_multiline = re.compile(
        re_multiline_s.replace('Escape',
                               escape_char * (int(escape_char == '\\') + 1)))

    for line in itertools.chain(input, ('\n',)):  # append LF to complete work
        # Treat as utf-8, ignore whitespace
        line = line.decode('utf-8').strip()
        # Drop trailing comments
        comm = re_midcomment.match(line)
        if comm:
            line = comm.group(1).rstrip() + comm.group(3)
        # Ignore comments (escape char on EOL does not "work")
        if re_comment.match(line):
            continue
        # If previous line was multiline, append
        if multiline_buffer:
            line = multiline_buffer + line.lstrip()
        # If line matches multiline, set multiline_buffer and restart
        if re_multiline.match(line):
            multiline_buffer = line[:-len(escape_char)]
            continue
        multiline_buffer = False

        # Ignore empty lines
        if line == '':
            pass
        # Check categories
        elif re_cat.match(line):
            m = re_cat.match(line)
            category = m.group(1)
            ret[category] = {}
        # Check statements
        elif re_stmt.match(line):
            m = re_stmt.match(line)
            keyword, args = m.group(1), m.group(2)
            # Special case where we close a category
            if keyword == 'END' and args == category:  # e.g. "END LC_NUMERIC"
                category = None
            # Skip over categories that we're not interested in
            elif (category is not None and
                    (CATEGORIES is not None and category not in CATEGORIES)):
                pass
            # Switch comment character
            elif keyword == 'comment_char':
                comment_char = args
                if args == '\\':
                    comment_char = '\\\\'
                re_cat = re.compile(
                    re_cat_s.replace('Comment', comment_char), re.DOTALL)
                re_comment = re.compile(
                    re_comment_s.replace('Comment', comment_char))
                re_midcomment = re.compile(
                    re_midcomment_s.replace(
                        'Comment', comment_char).replace(
                            'Escape', escape_char))
            # Switch escape character
            elif keyword == 'escape_char':
                escape_char = args
                if args == '\\':
                    escape_char = '\\\\'
                re_multiline = re.compile(
                    re_multiline_s.replace('Escape', escape_char))
                re_midcomment = re.compile(
                    re_midcomment_s.replace(
                        'Comment', comment_char).replace(
                            'Escape', escape_char))
            # Load other file
            elif keyword == 'copy':
                new_filename = os.path.join(
                    os.path.dirname(filename),
                    parse_args(args, escape_char)[0])
                recurse_data = parse_libc_localedata(new_filename, cache)
                if recurse_data is None:
                    raise ParseException(
                        'recursion during copy from %s to %s' % (
                            new_filename, filename))
                # Merge inner file data
                for copy_cat in (category,) if category else recurse_data:
                    if copy_cat not in ret:
                        ret[copy_cat] = {}
                    ret[copy_cat].update(recurse_data.get(copy_cat, {}))
            # Wow.. we even have defines...
            elif keyword == 'ifdef' or keyword == 'define':
                pass
            # Order start and end? Forget it...
            elif keyword == 'order_start':
                pass
            # Args.. store them
            else:
                assert args != ''
                args = parse_args(args, escape_char)
                # One-sized lists are not lists
                if len(args) == 1:
                    args = args[0]
                # Lists stay lists (even when empty)
                else:
                    # Trim tailing zeroes from lists (see
                    # locale.localeconv() output).
                    while len(args) >= 1 and args[-1] == 0:
                        args.pop()
                ret[category][keyword] = args
        # No match
        else:
            # Skip over uninteresting categories
            if (category is not None and
                    (CATEGORIES is not None and category not in CATEGORIES)):
                pass
            # We don't do defines
            elif keyword == 'else' or keyword == 'endif':
                pass
            # And we don't do order start and end.
            elif keyword == 'order_end':
                pass
            # We don't do anything with non-statements, really ;)
            else:
                # print('(unmatched: %s)' % (line,))
                pass

    # Purge empty categories
    for key in ret.keys():
        if len(ret[key]) == 0:
            del ret[key]

    cache[filename] = ret
    return ret


def get_libc_sources(locale_path='/usr/share/i18n/locales'):
    file_match = re.compile(r'^[a-z]+_[A-Z]+$')

    sources = []
    for file in os.listdir(locale_path):
        if file_match.match(file):
            sources.append((file, os.path.join(locale_path, file)))
    sources.sort()
    return sources


def convert_all_libc_locales(src_path, dst_path):
    import json
    import sys

    languages = get_libc_sources(src_path)
#    languages = [('csb_PL', os.path.join(src_path, 'csb_PL'))]
#    print parse_args('"<U003B>"', '/')
#    sys.exit(1)

    print('Processing languages...')
    cache = {}
    for languagecode, filename in languages:
        # if languagecode != 'uk_UA':
        #     continue
        sys.stdout.write('\r%s\r%s' % (' ' * 16, languagecode))
        sys.stdout.flush()
        try:
            localedata = parse_libc_localedata(filename, cache)
            if localedata is None:
                raise ParseException('broken recursion?')
        except ParseException as e:
            sys.stdout.write('\n')
            sys.stderr.write('Language file %s corrupt: %s\n' % (
                filename, e))
        else:
            try:
                os.mkdir(os.path.join(dst_path, languagecode))
            except OSError:
                pass
            for category in localedata:
                dst_file = open(os.path.join(dst_path, languagecode, category),
                                'wb')
                json.dump(
                    obj=localedata[category], fp=dst_file,
                    sort_keys=True, separators=(',', ':'))
                dst_file.close()

    print('\r%s\r...done' % (' ' * 16,))


if __name__ == '__main__':
    convert_all_libc_locales(
        '/usr/share/i18n/locales',
        os.path.join(os.path.dirname(__file__), 'locale')
    )
