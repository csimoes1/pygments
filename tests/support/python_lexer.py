# pygments.lexers.python (as CustomLexer) for test_cmdline.py

from pygments_tldr.lexers import PythonLexer


class CustomLexer(PythonLexer):
    name = 'PythonLexerWrapper'


class LexerWrapper(CustomLexer):
    name = 'PythonLexerWrapperWrapper'
