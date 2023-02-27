# This file is part of LilyPond, the GNU music typesetter.
#
# Copyright (C) 1998--2020 Han-Wen Nienhuys <hanwen@xs4all.nl>
#                Jan Nieuwenhuizen <janneke@gnu.org>
#
# LilyPond is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# LilyPond is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with LilyPond.  If not, see <http://www.gnu.org/licenses/>.

import __main__
import codecs
import gettext
import glob
import optparse
import os
import re
import shutil
import sys
import time

sys.stdin = codecs.getreader('utf8')(sys.stdin.detach())
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())

# Lilylib globals.
program_name = os.path.basename(sys.argv[0])

# Logging framework: We have the following output functions:
#    error
#    warning
#    progress
#    debug

# TODO: use the standard logging module

loglevels = {"NONE": 0, "ERROR": 1, "WARN": 2,
             "BASIC": 3, "PROGRESS": 4, "INFO": 5, "DEBUG": 6}

loglevel = loglevels["PROGRESS"]


def set_loglevel(l):
    global loglevel
    newlevel = loglevels.get(l, -1)
    if newlevel > 0:
        debug_output(_("Setting loglevel to %s") % l)
        loglevel = newlevel
    else:
        error(_("Unknown or invalid loglevel '%s'") % l)


def handle_loglevel_option(option, opt_str, value, parser, *args):
    if value:
        set_loglevel(value)
    elif args:
        set_loglevel(args[0])


def is_loglevel(l):
    global loglevel
    return loglevel >= loglevels[l]


def is_verbose():
    return is_loglevel("DEBUG")


def print_logmessage(level, s, fullmessage=True, newline=True):
    if is_loglevel(level):
        if fullmessage:
            s = program_name + ": " + s + "\n"
        elif newline:
            s += '\n'
        sys.stderr.write(s)
        sys.stderr.flush()


def error(s):
    print_logmessage("ERROR", _("error: %s") % s)


def warning(s):
    print_logmessage("WARN", _("warning: %s") % s)


def progress(s, fullmessage=False, newline=True):
    print_logmessage("PROGRESS", s, fullmessage, newline)


def debug_output(s, fullmessage=False, newline=True):
    print_logmessage("DEBUG", s, fullmessage, newline)


def strip_extension(f, ext):
    (p, e) = os.path.splitext(f)
    if e == ext:
        e = ''
    return p + e


class NonDentedHeadingFormatter (optparse.IndentedHelpFormatter):
    def format_heading(self, heading):
        if heading:
            return heading[0].upper() + heading[1:] + ':\n'
        return ''

    def format_option_strings(self, option):
        sep = ' '
        if option._short_opts and option._long_opts:
            sep = ','

        metavar = ''
        if option.takes_value():
            metavar = '=%s' % option.metavar or option.dest.upper()

        return "%3s%s %s%s" % (" ".join(option._short_opts),
                               sep,
                               " ".join(option._long_opts),
                               metavar)

    # Only use one level of indentation (even for groups and nested groups),
    # since we don't indent the headeings, either
    def indent(self):
        self.current_indent = self.indent_increment
        self.level += 1

    def dedent(self):
        self.level -= 1
        if self.level <= 0:
            self.current_indent = ''
            self.level = 0

    def format_usage(self, usage):
        return _("Usage: %s") % usage + '\n'

    def format_description(self, description):
        return description


class NonEmptyOptionParser (optparse.OptionParser):
    "A subclass of OptionParser that gobbles empty string arguments."

    def parse_args(self, args=None, values=None):
        options, args = optparse.OptionParser.parse_args(self, args, values)
        return options, [_f for _f in args if _f]


def get_option_parser(*args, **kwargs):
    p = NonEmptyOptionParser(*args, **kwargs)
    p.formatter = NonDentedHeadingFormatter()
    p.formatter.set_parser(p)
    return p
