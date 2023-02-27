# book_latex.py
# -*- coding: utf-8 -*-
#
# This file is part of LilyPond, the GNU music typesetter.
#
# Copyright (C) 2010 Reinhold Kainhofer <reinhold@kainhofer.com>,
#               2020--2020 Han-Wen Nienhuys <hanwen@xs4all.nl>
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


import os
import re
import subprocess
import sys
import tempfile

import book_base
import book_snippets
import lilylib as ly

progress = ly.progress
warning = ly.warning
error = ly.error
debug = ly.debug_output


# Recognize special sequences in the input.
#
#   (?P<name>regex) -- Assign result of REGEX to NAME.
#   *? -- Match non-greedily.
#   (?!...) -- Match if `...' doesn't match next (without consuming
#              the string).
#
#   (?m) -- Multiline regex: Make ^ and $ match at each line.
#   (?s) -- Make the dot match all characters including newline.
#   (?x) -- Ignore whitespace in patterns.
# See book_base.BookOutputFormat for  possible keys
Latex_snippet_res = {
    'include':
    r'''(?smx)
          ^[^%\n]*?
          (?P<match>
          \\input\s*{
           (?P<filename>\S+?)
          })''',

    'lilypond':
    r'''(?smx)
          ^[^%\n]*?
          (?P<match>
          \\lilypond\s*(
          \[
           \s*(?P<options>.*?)\s*
          \])?\s*{
           (?P<code>.*?)
          })''',

    'lilypond_block':
    r'''(?smx)
          ^[^%\n]*?
          (?P<match>
          \\begin\s*(?P<env>{lilypond}\s*)?(
          \[
           \s*(?P<options>.*?)\s*
          \])?(?(env)|\s*{lilypond})
           (?P<code>.*?)
          ^[^%\n]*?
          \\end\s*{lilypond})''',

    'lilypond_file':
    r'''(?smx)
          ^[^%\n]*?
          (?P<match>
          \\lilypondfile\s*(
          \[
           \s*(?P<options>.*?)\s*
          \])?\s*\{
           (?P<filename>\S+?)
          })''',

    'musicxml_file':
    r'''(?smx)
          ^[^%\n]*?
          (?P<match>
          \\musicxmlfile\s*(
          \[
           \s*(?P<options>.*?)\s*
          \])?\s*\{
           (?P<filename>\S+?)
          })''',

    'singleline_comment':
    r'''(?mx)
          ^.*?
          (?P<match>
           (?P<code>
           %.*$\n+))''',

    'verb':
    r'''(?mx)
          ^[^%\n]*?
          (?P<match>
           (?P<code>
           \\verb(?P<del>.)
            .*?
           (?P=del)))''',

    'verbatim':
    r'''(?msx)
          ^[^%\n]*?
          (?P<match>
           (?P<code>
           \\begin\s*{verbatim}
            .*?
           \\end\s*{verbatim}))''',

    'lilypondversion':
    r'''(?smx)
          (?P<match>
          \\lilypondversion)[^a-zA-Z]''',
}

Latex_output = {
    book_snippets.FILTER: r'''\begin{lilypond}[%(options)s]
%(code)s
\end{lilypond}''',

    book_snippets.OUTPUT: r'''{%%
\parindent 0pt
\noindent
\ifx\preLilyPondExample \undefined
\else
  \expandafter\preLilyPondExample
\fi
\def\lilypondbook{}%%
\input{%(base)s-systems.tex}
\ifx\postLilyPondExample \undefined
\else
  \expandafter\postLilyPondExample
\fi
}''',

    book_snippets.PRINTFILENAME: r'''\texttt{%(filename)s}
\linebreak
''',

    book_snippets.QUOTE: r'''\begin{quote}
%(str)s
\end{quote}''',

    book_snippets.VERBATIM: r'''\noindent
\begin{verbatim}%(verb)s\end{verbatim}
''',

    book_snippets.VERSION: r'''%(program_version)s''',
}


###
# Retrieve dimensions from LaTeX
LATEX_INSPECTION_DOCUMENT = r'''
\nonstopmode
%(preamble)s
\begin{document}
\typeout{textwidth=\the\textwidth}
\typeout{columnsep=\the\columnsep}
\makeatletter\if@twocolumn\typeout{columns=2}\fi\makeatother
\end{document}
'''

# Do we need anything else besides `textwidth'?


def get_latex_textwidth(source, global_options):
    # default value
    textwidth = 550.0

    m = re.search(r'''(?P<preamble>\\begin\s*{document})''', source)
    if m is None:
        warning(_("cannot find \\begin{document} in LaTeX document"))
        return textwidth

    preamble = source[:m.start(0)]
    latex_document = LATEX_INSPECTION_DOCUMENT % {'preamble': preamble}

    (handle, tmpfile) = tempfile.mkstemp('.tex')
    tmpfileroot = os.path.splitext(tmpfile)[0]
    tmpfileroot = os.path.split(tmpfileroot)[1]
    auxfile = tmpfileroot + '.aux'
    logfile = tmpfileroot + '.log'

    tmp_handle = os.fdopen(handle, 'w')
    tmp_handle.write(latex_document)
    tmp_handle.close()

    progress(_("Running `%s' on file `%s' to detect default page settings.\n")
             % (global_options.latex_program, tmpfile))
    cmd = '%s %s' % (global_options.latex_program, tmpfile)
    debug("Executing: %s\n" % cmd)
    run_env = os.environ.copy()
    run_env['LC_ALL'] = 'C'
    run_env['TEXINPUTS'] = os.path.pathsep.join(
                             (global_options.input_dir,
                              run_env.get('TEXINPUTS', '')))

    # unknown why this is necessary
    universal_newlines = True
    if sys.platform == 'mingw32':
        universal_newlines = False
        # use os.system to avoid weird sleep() problems on
        # GUB's python 2.4.2 on mingw
        # make file to write to
        output_dir = tempfile.mkdtemp()
        output_filename = os.path.join(output_dir, 'output.txt')
        # call command
        cmd += " > %s" % output_filename
        oldtexinputs = os.environ.get('TEXINPUTS')
        os.environ['TEXINPUTS'] = run_env['TEXINPUTS']
        returncode = os.system(cmd)
        if oldtexinputs:
            os.environ['TEXINPUTS'] = oldtexinputs
        else:
            del os.environ['TEXINPUTS']
        parameter_string = open(output_filename, encoding="utf8").read()
        if returncode != 0:
            warning(_("Unable to auto-detect default settings:\n"))
        # clean up
        os.remove(output_filename)
        os.rmdir(output_dir)
    else:
        proc = subprocess.Popen(cmd,
                                env=run_env,
                                universal_newlines=universal_newlines,
                                shell=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (parameter_string, error_string) = proc.communicate()
        if proc.returncode != 0:
            warning(_("Unable to auto-detect default settings:\n%s")
                    % error_string)
    os.unlink(tmpfile)
    if os.path.exists(auxfile):
        os.unlink(auxfile)
    if os.path.exists(logfile):
        parameter_string = open(logfile, encoding="utf8").read()
        os.unlink(logfile)

    columns = 0
    m = re.search('columns=([0-9.]+)', parameter_string)
    if m:
        columns = int(m.group(1))

    columnsep = 0
    m = re.search('columnsep=([0-9.]+)pt', parameter_string)
    if m:
        columnsep = float(m.group(1))

    m = re.search('textwidth=([0-9.]+)pt', parameter_string)
    if m:
        textwidth = float(m.group(1))
    else:
        warning(_("cannot detect textwidth from LaTeX"))
        return textwidth

    debug('Detected values:')
    debug('  columns = %s' % columns)
    debug('  columnsep = %s' % columnsep)
    debug('  textwidth = %s' % textwidth)

    if m and columns:
        textwidth = (textwidth - columnsep) / columns
        debug('Adjusted value:')
        debug('  textwidth = %s' % textwidth)

    return textwidth


def modify_preamble(chunk):
    s = chunk.replacement_text()
    if (re.search(r"\\begin *{document}", s)
            and not re.search("{graphic[sx]", s)):
        s = re.sub(r"\\begin{document}",
                     r"\\usepackage{graphics}" + '\n'
                     + r"\\begin{document}",
                     s)
        chunk.override_text = s


class BookLatexOutputFormat (book_base.BookOutputFormat):
    def __init__(self):
        book_base.BookOutputFormat.__init__(self)
        self.format = "latex"
        self.default_extension = ".tex"
        self.snippet_res = Latex_snippet_res
        self.output = Latex_output
        self.handled_extensions = ['.latex', '.lytex', '.tex']
        self.image_formats = "ps"
        self.snippet_option_separator = r'\s*,\s*'

    def process_options(self, global_options):
        self.process_options_pdfnotdefault(global_options)

    def get_line_width(self, source):
        textwidth = get_latex_textwidth(source, self.global_options)
        return '%.0f\\pt' % textwidth

    def input_fullname(self, input_filename):
        # Use kpsewhich if available, otherwise fall back to the default:
        try:
            input_fullname = subprocess.run(['kpsewhich', input_filename],
                                            check=True,
                                            stdout=subprocess.PIPE).stdout.decode('utf-8')

            input_fullname = input_fullname.strip("\n")

        except (subprocess.CalledProcessError, FileNotFoundError):
            input_fullname = book_base.BookOutputFormat.input_fullname(
                self,
                input_filename)

        return input_fullname

    def process_chunks(self, chunks):
        for c in chunks:
            if (c.is_plain() and
                    re.search(r"\\begin *{document}", c.replacement_text())):
                modify_preamble(c)
                break
        return chunks

    def snippet_output(self, basename, snippet):
        s = ''
        rep = snippet.get_replacements()
        rep['base'] = basename.replace('\\', '/')
        rep['filename'] = os.path.basename(snippet.filename).replace('\\', '/')
        rep['ext'] = snippet.ext
        if book_snippets.PRINTFILENAME in snippet.option_dict:
            s += self.output[book_snippets.PRINTFILENAME] % rep
        if book_snippets.VERBATIM in snippet.option_dict:
            rep['verb'] = snippet.verb_ly()
            s += self.output[book_snippets.VERBATIM] % rep

        s += self.output[book_snippets.OUTPUT] % rep

        # todo: maintain breaks
        if 0:
            breaks = snippet.ly().count("\n")
            s += "".ljust(breaks, "\n").replace("\n", "%\n")

        if book_snippets.QUOTE in snippet.option_dict:
            s = self.output[book_snippets.QUOTE] % {'str': s}

        return s


book_base.register_format(BookLatexOutputFormat())
