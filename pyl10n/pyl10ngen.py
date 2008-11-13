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
import itertools, os, re

#
# BUGS:
#
# * Comment might be legal further on the line, but its not used often (only 3 out of 226 files do that).
#   E.g.: Language file as_IN corrupt: unexpected data: IGNORE;IGNORE;IGNORE;%... (%...)
#
# * We only use the CATEGORIES defined below, and not LC_CTYPE/LC_COLLATE.. they are complicated and beyond the scope
#   of the fix, right now.
#
# * I suspect that the copy keyword in a category tells us that you should only read that category from the copied
#   file. Currently it reads everything from copied files (and uses loop_check to fix infinite recursion).
#
# * There is an 'include' keyword. We don't use it yet.
#
# * We strip trailing zeroes from a list (e.g. mon_grouping 3;3;0 becomes [3,3]). This is not a bug but a deviation
#   from the C-documentation.
#


# Read only these categories.. set to None to read all.
CATEGORIES = ('LC_ADDRESS', 'LC_MEASUREMENT', 'LC_MONETARY', 'LC_NAME', 'LC_NUMERIC', 'LC_PAPER', 'LC_TELEPHONE', 'LC_TIME')

class ParseException(Exception):
    pass

def parse_args(string, escape_char):
    re_nextarg = re.compile(r'(\s*(LC_[A-Z]+|[A-Za-z_:-]+|"[^"]*"|-?[0-9]+|<[0-9A-Za-z_-]+>|<[0-9A-Za-z_-]+>..<[0-9A-Za-z_-]+>|\(<[0-9A-Za-z_-]+>,<[0-9A-Za-z_-]+>\))\s*)')
    ret = []

    i = 0
    while True:
        m = re_nextarg.match(string, i)
        if not m:
            raise ParseException, 'Unexpected data: \'\'\'%s<-- HERE -->%s\'\'\'' % (string[:i], string[i:])
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
                ret[i] = unicode(ret[i][1:-1].replace(escape_char * 2, escape_char))
                j = 0
                while j < len(ret[i]):
                    if ret[i][j] == '<' and ret[i][j+1] == 'U' and ret[i][j+6] == '>':
                        ret[i] = ret[i][0:j] + unichr(int(ret[i][j+2:j+6], 16)) + ret[i][j+7:]
                    j += 1
            except UnicodeDecodeError:
                ret[i] = 'Someone put illegal non-ASCII here!'
        # else: <U0123> or <U01234567>
        # else: <U0123>..<U4567>
        # else: <TREMA>

    return ret
    

def parse_libc_localedata(filename, loop_check = None):
    # Trap infinite recursion
    loop_check = loop_check or []
    if filename in loop_check:
        return {}
    loop_check.append(filename)

    # The result
    ret = {}

    input = open(filename, 'rb')
    comment_char, escape_char = '#', '\\'
    category = None
    state = None
    multiline_buffer = False
    
    re_cat = re.compile(r'^(LC_[A-Z]+)$', re.DOTALL)
    re_stmt = re.compile(r'^([A-Za-z_]+)\s+(.*?)$', re.DOTALL)
    re_comment_s = r'^Comment.*$'
    re_comment = re.compile(re_comment_s.replace('Comment', comment_char*(int(comment_char=='\\')+1)))
    re_multiline_s = r'(^|[^Escape]|EscapeEscape)*Escape$'
    re_multiline = re.compile(re_multiline_s.replace('Escape', escape_char*(int(escape_char=='\\')+1)))

    for line in itertools.chain(input, ('\n',)): # append extra line to complete work
        # Ignore extra whitespace
        line = line.strip()
        # Ignore comments (escape char on EOL does not "work")
        if re_comment.match(line):
            continue
        # If previous line was multiline, append
        if multiline_buffer != False:
            line = multiline_buffer + line.strip()
        # If line matches multiline, set multiline_buffer and restart
        if re_multiline.match(line):
            multiline_buffer = line[:-len(escape_char)].strip() # strip that one too..
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
            if keyword == 'END' and args == category: # e.g. "END LC_NUMERIC"
                category = None
            # Skip over categories that we're not interested in
            elif category != None and (CATEGORIES != None and category not in CATEGORIES):
                pass
            # Switch comment character
            elif keyword == 'comment_char':
                comment_char = args
                re_comment = re.compile(re_comment_s.replace('Comment', comment_char*(int(comment_char=='\\')+1)))
            # Switch escape character
            elif keyword == 'escape_char':
                escape_char = args
                re_multiline = re.compile(re_multiline_s.replace('Escape', escape_char*(int(escape_char=='\\')+1)))
            # Load other file
            elif keyword == 'copy':
                recurse_data = parse_libc_localedata(
                    os.path.join(os.path.dirname(filename), parse_args(args, escape_char)[0]),
                    loop_check
                )
                # Merge inner file data
                for recurse_cat in recurse_data:
                    if recurse_cat not in ret:
                        ret[recurse_cat] = {}
                    ret[recurse_cat].update(recurse_data[recurse_cat])
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
                    # Trim tailing zeroes from lists (see locale.localeconv() output)
                    while len(args) >= 1 and args[-1] == 0:
                        args.pop()
                ret[category][keyword] = args
        # No match
        else:
            # Skip over uninteresting categories
            if category != None and (CATEGORIES != None and category not in CATEGORIES):
                pass
            # We don't do defines
            elif keyword == 'else' or keyword == 'endif':
                pass
            # And we don't do order start and end.
            elif keyword == 'order_end':
                pass
            # We don't do anything with non-statements, really ;)
            else:
                pass
                #print '(unmatched: %s)' % (line,)
   
    # Purge empty categories
    for key in ret.keys():
        if len(ret[key]) == 0:
            del ret[key]
    return ret


if __name__ == '__main__':
    import cPickle as pickle, re, os, sys
    file_match = re.compile(r'^[a-z]+_[A-Z]+$')
    locale_source = '/usr/share/i18n/locales'
    locale_destination = os.path.join(os.path.dirname(__file__), 'locale')

    in_languages = []
    for file in os.listdir(locale_source):
        if file_match.match(file):
            in_languages.append(file)
    in_languages.sort()

#    in_languages = ['csb_PL']
#
#    print parse_args('"<U003B>"', '/')
#    import sys
#    sys.exit(1)
    
    print 'Processing languages...'
    for language in in_languages:
        sys.stdout.write('\r%s\r%s' % (' ' * 16, language))
        sys.stdout.flush()
        try:
            locale_info = parse_libc_localedata(os.path.join(locale_source, language))
            try: os.mkdir(os.path.join(locale_destination, language))
            except OSError: pass

            for category in locale_info:
                destination = open(os.path.join(locale_destination, language, category), 'wb')
                pickle.dump(locale_info[category], destination, pickle.HIGHEST_PROTOCOL)

        except ParseException, e:
            sys.stdout.write('\n')
            sys.stderr.write('Language file %s corrupt: %s\n' % (language, e))

    print '\r%s\r...done' % (' ' * 16,)
