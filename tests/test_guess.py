"""
    Pygments basic API tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from pathlib import Path

import pytest

from pygments_tldr.lexers import (
    _fn_matches,
    find_lexer_class_by_name,
    get_lexer_by_name,
    guess_lexer,
)
from pygments_tldr.lexers.basic import CbmBasicV2Lexer
from pygments_tldr.lexers.ecl import ECLLexer

TESTDIR = Path(__file__).resolve().parent


def get_input(lexer, filename):
    return Path(TESTDIR, 'examplefiles', lexer, filename).read_text(encoding='utf-8')


@pytest.mark.skip(reason="This is identified as T-SQL")
def test_guess_lexer_fsharp():
    lx = guess_lexer(get_input('fsharp', 'Deflate.fs'))
    assert lx.__class__.__name__ == 'FSharpLexer'


def test_guess_lexer_brainfuck():
    lx = guess_lexer('>>[-]<<[->>+<<]')
    assert lx.__class__.__name__ == 'BrainfuckLexer'


def test_guess_lexer_singularity():
    lx = guess_lexer(get_input('singularity', 'Singularity'))
    assert lx.__class__.__name__ == 'SingularityLexer'


@pytest.mark.skip(reason="This is identified as MIME")
def test_guess_lexer_matlab():
    lx = guess_lexer(r'A \ B')
    assert lx.__class__.__name__ == 'OctaveLexer'


@pytest.mark.skip(reason="This is identified as Python")
def test_guess_lexer_hybris():
    lx = guess_lexer(get_input('hybris', 'hybris_File.hy'))
    assert lx.__class__.__name__ == 'HybrisLexer'


def test_guess_lexer_forth():
    lx = guess_lexer(get_input('forth', 'demo.frt'))
    assert lx.__class__.__name__ == 'ForthLexer'


def test_guess_lexer_modula2():
    lx = guess_lexer(get_input('modula2', 'modula2_test_cases.def'))
    assert lx.__class__.__name__ == 'Modula2Lexer'


def test_guess_lexer_unicon():
    lx = guess_lexer(get_input('unicon', 'example.icn'))
    assert lx.__class__.__name__ == 'UcodeLexer'


def test_guess_lexer_ezhil():
    lx = guess_lexer(get_input('ezhil', 'ezhil_primefactors.n'))
    assert lx.__class__.__name__ == 'EzhilLexer'


def test_guess_lexer_gdscript():
    lx = guess_lexer(get_input('gdscript', 'gdscript_example.gd'))
    assert lx.__class__.__name__ == 'GDScriptLexer'


def test_guess_lexer_gap():
    lx = guess_lexer(get_input('gap', 'example.gd'))
    assert lx.__class__.__name__ == 'GAPLexer'
    lx = guess_lexer(get_input('gap', 'example.gi'))
    assert lx.__class__.__name__ == 'GAPLexer'


def test_guess_lexer_easytrieve():
    lx = guess_lexer(get_input('easytrieve', 'example.ezt'))
    assert lx.__class__.__name__ == 'EasytrieveLexer'
    lx = guess_lexer(get_input('easytrieve', 'example.mac'))
    assert lx.__class__.__name__ == 'EasytrieveLexer'


def test_guess_lexer_jcl():
    lx = guess_lexer(get_input('jcl', 'example.jcl'))
    assert lx.__class__.__name__ == 'JclLexer'


def test_guess_lexer_rexx():
    lx = guess_lexer(get_input('rexx', 'example.rexx'))
    assert lx.__class__.__name__ == 'RexxLexer'


def test_easytrieve_can_guess_from_text():
    lx = get_lexer_by_name('easytrieve')
    assert lx.analyse_text('MACRO')
    assert lx.analyse_text('\nMACRO')
    assert lx.analyse_text(' \nMACRO')
    assert lx.analyse_text(' \n MACRO')
    assert lx.analyse_text('*\nMACRO')
    assert lx.analyse_text('*\n *\n\n \n*\n MACRO')


def test_rexx_can_guess_from_text():
    lx = get_lexer_by_name('rexx')
    assert lx.analyse_text('/* */') == pytest.approx(0.01)
    assert lx.analyse_text('''/* Rexx */
            say "hello world"''') == pytest.approx(1.0)
    val = lx.analyse_text('/* */\n'
                          'hello:pRoceduRe\n'
                          '  say "hello world"')
    assert val > 0.5
    val = lx.analyse_text('''/* */
            if 1 > 0 then do
                say "ok"
            end
            else do
                say "huh?"
            end''')
    assert val > 0.2
    val = lx.analyse_text('''/* */
            greeting = "hello world!"
            parse value greeting "hello" name "!"
            say name''')
    assert val > 0.2


def test_guess_cmake_lexer_from_header():
    headers = [
        "CMAKE_MINIMUM_REQUIRED(VERSION 2.6 FATAL_ERROR)",
        "cmake_minimum_required(version 3.13)  # CMake version check",
        " CMAKE_MINIMUM_REQUIRED\t( VERSION 2.6 FATAL_ERROR ) ",
    ]
    for header in headers:
        code = '\n'.join([
            header,
            'project(example)',
            'set(CMAKE_CXX_STANDARD 14)',
            'set(SOURCE_FILES main.cpp)',
            'add_executable(example ${SOURCE_FILES})',
        ])
        lexer = guess_lexer(code)
        assert lexer.__class__.__name__ == 'CMakeLexer', \
            f"header must be detected as CMake: {header!r}"


def test_guess_c_lexer():
    code = '''
    #include <stdio.h>
    #include <stdlib.h>

    int main(void);

    int main(void) {
        uint8_t x = 42;
        uint8_t y = x + 1;

        /* exit 1 for success! */
        return 1;
    }
    '''
    lexer = guess_lexer(code)
    assert lexer.__class__.__name__ == 'CLexer'

def test_guess_carbon_lexer():
    code = '''
    package Sorting api;

    abstract class C {
      var a: i32;
    }

    base class B {
      var value_b: i32;
    }

    impl JustX as X {}
    '''
    lexer = guess_lexer(code)
    assert lexer.__class__.__name__ == 'CarbonLexer'

def test_cbmbasicv2_analyse_text():
    text = "10 PRINT \"PART 1\""
    res = CbmBasicV2Lexer.analyse_text(text)
    assert res == 0.2


def test_ecl_analyze_text():
    text = r"""
            STRING  ABC -> size32_t lenAbc, const char * abc;
            """
    res = ECLLexer.analyse_text(text)
    assert res == 0.01


def iter_fixture_dir(sub_dir):
    """Returns the sub-directories in any of the examplefiles/"snippets" fixture directory."""
    for dir in Path(TESTDIR, sub_dir).iterdir():
        # Only keep directories that are not special.
        if (
            dir.is_dir()
            and not dir.name.startswith("__")
            and not dir.name.startswith(".")
        ):
            yield dir


@pytest.mark.parametrize("sub_dir", ["examplefiles", "snippets"])
def test_lexer_fixtures(sub_dir):
    """Check that example files and snippets fixtures are in a directory named after a lexer alias."""
    for dir in iter_fixture_dir(sub_dir):
        assert find_lexer_class_by_name(
            dir.name
        ), f"Alias {dir.name} not found in pygments"


def all_example_files():
    example_files = []
    for dir in iter_fixture_dir("examplefiles"):
        for f in dir.iterdir():
            if f.is_file() and f.suffix != ".output":
                # XXX Skip the srcinfo directory, whose example files are not strictly named ".SRCINFO".
                marks = []
                if dir.name == "srcinfo":
                    marks = [
                        pytest.mark.skip(
                            reason="Example file not strictly named '.SRCINFO'"
                        )
                    ]

                example_files.append(
                    pytest.param(f, id=f"{f.parent.name}/{f.name}", marks=marks)
                )

    return example_files


@pytest.mark.parametrize("example_file", all_example_files())
def test_filename_matching(example_file):
    """Check that each example file is correctly identified by its lexer from its filename pattern."""
    # Example files are stored in subdirectories named after the lexer alias.
    alias = example_file.parent.name
    klass = find_lexer_class_by_name(alias)

    # If the class defines no filename patterns, we can't check anything.
    if not klass.filenames:
        return

    matches = []
    for pattern in klass.filenames:
        if _fn_matches(example_file.name, pattern):
            matches.append(pattern)

    assert matches, f"No {klass.filenames} patterns matches {example_file.name!r}"
