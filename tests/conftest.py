"""
    Generated lexer tests
    ~~~~~~~~~~~~~~~~~~~~~

    Checks that lexers output the expected tokens for each sample
    under snippets/ and examplefiles/.

    After making a change, rather than updating the samples manually,
    run `pytest --update-goldens <changed file>`.

    To add a new sample, create a new file matching this pattern.
    The directory must match the alias of the lexer to be used.
    Populate only the input, then just `--update-goldens`.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pathlib import Path

import pytest

import pygments_tldr.lexers
from pygments_tldr.token import Error


def pytest_addoption(parser):
    parser.addoption('--update-goldens', action='store_true',
                     help='reset golden master benchmarks')


class LexerTestItem(pytest.Item):
    def __init__(self, name, parent):
        super().__init__(name, parent)
        self.lexer = Path(str(self.fspath)).parent.name
        self.actual = None

    @classmethod
    def _prettyprint_tokens(cls, tokens):
        for tok, val in tokens:
            if tok is Error and not cls.allow_errors:
                raise ValueError(f'generated Error token at {val!r}')
            yield f'{val!r:<13} {str(tok)[6:]}'
            if val.endswith('\n'):
                yield ''

    def runtest(self):
        lexer = pygments_tldr.lexers.get_lexer_by_name(self.lexer)
        tokens = list(lexer.get_tokens(self.input))
        self.actual = '\n'.join(self._prettyprint_tokens(tokens)).rstrip('\n') + '\n'
        if self.config.getoption('--update-goldens'):
            # Make sure the new golden output corresponds to the input.
            output = ''.join(val for (tok, val) in tokens)
            preproc_input = lexer._preprocess_lexer_input(self.input) # remove BOMs etc.
            assert output == preproc_input
        else:
            # Make sure the output is the expected golden output
            assert self.actual == self.expected

    def _test_file_rel_path(self):
        return Path(str(self.fspath)).relative_to(Path(__file__).parent.parent)

    def _prunetraceback(self, excinfo):
        excinfo.traceback = excinfo.traceback.cut(__file__).filter()

    def repr_failure(self, excinfo):
        if isinstance(excinfo.value, AssertionError):
            if self.config.getoption('--update-goldens'):
                message = (
                    f'The tokens produced by the "{self.lexer}" lexer '
                    'do not add up to the input.'
                )
            else:
                rel_path = self._test_file_rel_path()
                message = (
                    f'The tokens produced by the "{self.lexer}" lexer differ from the '
                    f'expected ones in the file "{rel_path}".\n'
                    f'Run `tox -- {Path(*rel_path.parts[:2])} --update-goldens` to update it.'
                )
            diff = str(excinfo.value).split('\n', 1)[-1]
            return message + '\n\n' + diff
        else:
            return pytest.Item.repr_failure(self, excinfo)

    def reportinfo(self):
        return self.fspath, None, str(self._test_file_rel_path())

    def maybe_overwrite(self):
        if self.actual is not None and self.config.getoption('--update-goldens'):
            self.overwrite()


class LexerSeparateTestItem(LexerTestItem):
    allow_errors = False

    def __init__(self, name, parent):
        super().__init__(name, parent)

        self.input = self.fspath.read_text('utf-8')
        output_path = self.fspath + '.output'
        if output_path.check():
            self.expected = output_path.read_text(encoding='utf-8')
        else:
            self.expected = ''

    def overwrite(self):
        output_path = self.fspath + '.output'
        output_path.write_text(self.actual, encoding='utf-8')


class LexerInlineTestItem(LexerTestItem):
    allow_errors = True

    def __init__(self, name, parent):
        super().__init__(name, parent)

        content = self.fspath.read_text('utf-8')
        content, _, self.expected = content.partition('\n---tokens---\n')
        if content.startswith('---input---\n'):
            content = '\n' + content
        self.comment, _, self.input = content.rpartition('\n---input---\n')
        if not self.input.endswith('\n'):
            self.input += '\n'
        self.comment = self.comment.strip()

    def overwrite(self):
        with self.fspath.open('w', encoding='utf-8') as f:
            f.write(self.comment)
            if self.comment:
                f.write('\n\n')
            f.write('---input---\n')
            f.write(self.input)
            f.write('\n---tokens---\n')
            f.write(self.actual)


def pytest_runtest_teardown(item, nextitem):
    if isinstance(item, LexerTestItem):
        item.maybe_overwrite()
