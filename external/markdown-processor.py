"""
    The Pygments Markdown Preprocessor
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This fragment is a Markdown_ preprocessor that renders source code
    to HTML via Pygments.  To use it, invoke Markdown like so::

        import markdown

        html = markdown.markdown(someText, extensions=[CodeBlockExtension()])

    This uses CSS classes by default, so use
    ``pygmentize -S <some style> -f html > pygments.css``
    to create a stylesheet to be added to the website.

    You can then highlight source code in your markdown markup::

        [sourcecode:lexer]
        some code
        [/sourcecode]

    .. _Markdown: https://pypi.python.org/pypi/Markdown

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension

from pygments_tldr import highlight
from pygments_tldr.formatters import HtmlFormatter
from pygments_tldr.lexers import get_lexer_by_name, TextLexer


# Options
# ~~~~~~~

# Set to True if you want inline CSS styles instead of classes
INLINESTYLES = False


class CodeBlockPreprocessor(Preprocessor):

    pattern = re.compile(r'\[sourcecode:(.+?)\](.+?)\[/sourcecode\]', re.S)

    formatter = HtmlFormatter(noclasses=INLINESTYLES)

    def run(self, lines):
        def repl(m):
            try:
                lexer = get_lexer_by_name(m.group(1))
            except ValueError:
                lexer = TextLexer()
            code = highlight(m.group(2), lexer, self.formatter)
            code = code.replace('\n\n', '\n&nbsp;\n').replace('\n', '<br />')
            return f'\n\n<div class="code">{code}</div>\n\n'
        joined_lines = "\n".join(lines)
        joined_lines = self.pattern.sub(repl, joined_lines)
        return joined_lines.split("\n")

class CodeBlockExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.preprocessors.add('CodeBlockPreprocessor', CodeBlockPreprocessor(), '_begin')
