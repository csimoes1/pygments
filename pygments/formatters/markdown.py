"""
Pygments Markdown Formatter

A formatter for Pygments that outputs Markdown-formatted code with syntax highlighting
using fenced code blocks and optional inline styling.
"""

from pygments.formatter import Formatter
from pygments.token import (
    Token, Whitespace, Error, Other, Keyword, Name, Literal, String,
    Number, Punctuation, Operator, Comment, Generic
)
from pygments.util import get_bool_opt, get_int_opt, get_list_opt


class MarkdownFormatter(Formatter):
    """
    Format tokens as Markdown code blocks with optional syntax highlighting.

    This formatter outputs code in GitHub-flavored Markdown format using fenced
    code blocks (```). It supports various options for customization including
    language specification, line numbers, and inline formatting.

    Options accepted:

    `lang` : string
        The language identifier to use in the fenced code block.
        If not specified, attempts to detect from lexer name.

    `linenos` : bool
        Turn on line numbers. (default: False)

    `linenostart` : integer
        The line number for the first line (default: 1)

    `hl_lines` : list of integers
        Specify a list of lines to be highlighted with comments.

    `full` : bool
        Generate a complete Markdown document with title and metadata.
        (default: False)

    `title` : string
        Title for the document when `full` is True. (default: '')

    `inline_styles` : bool
        Use inline Markdown formatting for syntax highlighting instead of
        just the fenced code block. (default: False)

    `fence_char` : string
        Character to use for fencing. Either '`' or '~'. (default: '`')

    `fence_count` : integer
        Number of fence characters to use. Must be at least 3. (default: 3)

    `highlight_functions` : bool
        Add special highlighting for function/method signatures using
        Markdown callouts or emphasis. (default: True)

    `function_style` : string
        Style for function highlighting. Options: 'callout', 'emphasis', 'heading'.
        - 'callout': Use > blockquote style
        - 'emphasis': Use **bold** formatting
        - 'heading': Use ### heading style
        (default: 'emphasis')
    """

    name = 'Markdown'
    aliases = ['markdown', 'md']
    filenames = ['*.md', '*.markdown']

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # Basic options
        self.lang = options.get('lang', '')
        self.linenos = get_bool_opt(options, 'linenos', False)
        self.linenostart = get_int_opt(options, 'linenostart', 1)
        self.hl_lines = set(get_list_opt(options, 'hl_lines', []))
        self.inline_styles = get_bool_opt(options, 'inline_styles', False)

        # Markdown-specific options
        self.fence_char = options.get('fence_char', '`')
        if self.fence_char not in ('`', '~'):
            self.fence_char = '`'

        self.fence_count = get_int_opt(options, 'fence_count', 3)
        if self.fence_count < 3:
            self.fence_count = 3

        # Function highlighting options
        self.highlight_functions = get_bool_opt(options, 'highlight_functions', True)
        self.function_style = options.get('function_style', 'emphasis')
        if self.function_style not in ('callout', 'emphasis', 'heading'):
            self.function_style = 'emphasis'

        # Auto-detect language if not specified
        if not self.lang and hasattr(self, 'lexer'):
            if hasattr(self.lexer, 'aliases') and self.lexer.aliases:
                self.lang = self.lexer.aliases[0]
            elif hasattr(self.lexer, 'name'):
                self.lang = self.lexer.name.lower()

    def _get_markdown_style(self, ttype):
        """
        Convert Pygments token types to Markdown inline formatting.
        Returns a tuple of (prefix, suffix) strings.
        """
        if not self.inline_styles:
            return ('', '')

        # Map token types to Markdown formatting
        style_map = {
            # Comments - italic
            Comment: ('*', '*'),
            Comment.Single: ('*', '*'),
            Comment.Multiline: ('*', '*'),
            Comment.Preproc: ('*', '*'),
            Comment.PreprocFile: ('*', '*'),
            Comment.Special: ('*', '*'),

            # Keywords - bold
            Keyword: ('**', '**'),
            Keyword.Constant: ('**', '**'),
            Keyword.Declaration: ('**', '**'),
            Keyword.Namespace: ('**', '**'),
            Keyword.Pseudo: ('**', '**'),
            Keyword.Reserved: ('**', '**'),
            Keyword.Type: ('**', '**'),

            # Strings - no special formatting (already in code block)
            String: ('', ''),
            String.Backtick: ('', ''),
            String.Char: ('', ''),
            String.Doc: ('', ''),
            String.Double: ('', ''),
            String.Escape: ('', ''),
            String.Heredoc: ('', ''),
            String.Interpol: ('', ''),
            String.Other: ('', ''),
            String.Regex: ('', ''),
            String.Single: ('', ''),
            String.Symbol: ('', ''),

            # Names - no special formatting
            Name: ('', ''),
            Name.Attribute: ('', ''),
            Name.Builtin: ('', ''),
            Name.Builtin.Pseudo: ('', ''),
            Name.Class: ('', ''),
            Name.Constant: ('', ''),
            Name.Decorator: ('', ''),
            Name.Entity: ('', ''),
            Name.Exception: ('', ''),
            Name.Function: ('', ''),
            Name.Function.Magic: ('', ''),
            Name.Label: ('', ''),
            Name.Namespace: ('', ''),
            Name.Other: ('', ''),
            Name.Property: ('', ''),
            Name.Tag: ('', ''),
            Name.Variable: ('', ''),
            Name.Variable.Class: ('', ''),
            Name.Variable.Global: ('', ''),
            Name.Variable.Instance: ('', ''),
            Name.Variable.Magic: ('', ''),

            # Numbers - no special formatting
            Number: ('', ''),
            Number.Bin: ('', ''),
            Number.Float: ('', ''),
            Number.Hex: ('', ''),
            Number.Integer: ('', ''),
            Number.Integer.Long: ('', ''),
            Number.Oct: ('', ''),

            # Operators and punctuation - no special formatting
            Operator: ('', ''),
            Operator.Word: ('', ''),
            Punctuation: ('', ''),

            # Preprocessor - italic
            # Preprocessor: ('*', '*'),

            # Errors - strikethrough (if supported)
            Error: ('~~', '~~'),

            # Generic tokens
            Generic: ('', ''),
            Generic.Deleted: ('~~', '~~'),
            Generic.Emph: ('*', '*'),
            Generic.Error: ('~~', '~~'),
            Generic.Heading: ('**', '**'),
            Generic.Inserted: ('', ''),
            Generic.Output: ('', ''),
            Generic.Prompt: ('**', '**'),
            Generic.Strong: ('**', '**'),
            Generic.Subheading: ('**', '**'),
            Generic.Traceback: ('*', '*'),
        }

        return style_map.get(ttype, ('', ''))

    def _is_function_definition(self, tokens, start_idx):
        """
        Detect if the current position is the start of a function/method definition.
        Returns (is_function, function_name, parameters, end_idx) tuple.
        """
        if not self.highlight_functions:
            return False, None, None, start_idx

        # Look for common function definition patterns
        i = start_idx
        function_name = ""
        parameters = ""
        found_def = False
        found_name = False
        paren_count = 0

        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx

        # Look for function definition keywords
        ttype, value = tokens[i]
        if ttype in (Keyword, Keyword.Declaration) and value.lower() in ('def', 'function', 'fn', 'func', 'method', 'proc', 'procedure', 'sub', 'subroutine'):
            found_def = True
            i += 1
        elif ttype == Name and i > 0:
            # Check for patterns like "public void methodName(" or "int functionName("
            prev_tokens = []
            j = max(0, i - 5)  # Look back a few tokens
            while j < i:
                if tokens[j][0] not in (Whitespace,):
                    prev_tokens.append(tokens[j])
                j += 1

            # Look for type declarations or access modifiers before the name
            if len(prev_tokens) >= 1:
                last_token = prev_tokens[-1]
                if (last_token[0] in (Keyword.Type, Name.Builtin.Type, Keyword) or
                        last_token[1] in ('public', 'private', 'protected', 'static', 'void', 'int', 'string', 'bool', 'float', 'double')):
                    found_def = True

        if not found_def:
            return False, None, None, start_idx

        # Skip whitespace after keyword
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx

        # Get function name
        ttype, value = tokens[i]
        if ttype in (Name, Name.Function, Name.Other):
            function_name = value
            found_name = True
            i += 1

        if not found_name:
            return False, None, None, start_idx

        # Look for opening parenthesis to confirm it's a function
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found function signature, now extract parameters
                paren_count = 1
                i += 1
                param_tokens = []

                while i < len(tokens) and paren_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '(':
                            paren_count += 1
                        elif value == ')':
                            paren_count -= 1

                    # Collect parameter tokens (exclude the closing parenthesis)
                    if paren_count > 0:
                        param_tokens.append((ttype, value))

                    i += 1

                # Extract parameter string
                parameters = ''.join(token[1] for token in param_tokens).strip()
                # Clean up parameters - remove newlines and extra spaces
                parameters = ' '.join(parameters.split())

                # Continue until we find the end of the signature (colon, brace, etc.)
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if value in (':', '{', ';') or value == '\n':
                        return True, function_name, parameters, i
                    i += 1

                return True, function_name, parameters, i
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx

    def _format_function_signature(self, tokens, start_idx, end_idx, function_name):
        """
        Format a function signature with special Markdown highlighting.
        """
        signature_tokens = tokens[start_idx:end_idx]
        signature_text = ''.join(token[1] for token in signature_tokens)

        if self.function_style == 'callout':
            return f"> **📋 Function:** `{function_name}`\n> ```\n> {signature_text.strip()}\n> ```\n"
        elif self.function_style == 'heading':
            return f"### 🔧 {function_name}\n```\n{signature_text.strip()}\n```\n"
        else:  # emphasis
            return f"**🔹 {function_name}** {signature_text.strip()}\n"

    def format_unencoded(self, tokensource, outfile):
        """
        Format the token stream and write to outfile.
        """
        # Convert token source to list for multiple passes
        tokens = list(tokensource)

        # Write document header if full document requested
        if self.options.get('full', False):
            title = self.options.get('title', 'Code')
            outfile.write(f'# {title}\n\n')
            outfile.write('Generated by Pygments Markdown Formatter\n\n')

        # Pre-process to find function signatures if highlighting is enabled
        function_signatures = []
        if self.highlight_functions:
            i = 0
            while i < len(tokens):
                is_func, func_name, parameters, end_idx = self._is_function_definition(tokens, i)
                if is_func:
                    # Find the line number for this function
                    line_num = 1
                    char_count = 0
                    for j in range(i):
                        char_count += len(tokens[j][1])
                        line_num += tokens[j][1].count('\n')

                    function_signatures.append({
                        'name': func_name,
                        'parameters': parameters or '',
                        'start_idx': i,
                        'end_idx': end_idx,
                        'line_num': line_num,
                        'signature': ''.join(token[1] for token in tokens[i:end_idx])
                    })
                    i = end_idx
                else:
                    i += 1

        # Write function signatures summary if any found
        if function_signatures and self.function_style == 'callout':
            outfile.write('## 📚 Functions Found\n\n')
            for func in function_signatures:
                params_display = f"({func['parameters']})" if func['parameters'] else "()"
                outfile.write(f'- **{func["name"]}**{params_display} (line {func["line_num"]})\n')
            outfile.write('\n')

        # Start fenced code block
        fence = self.fence_char * self.fence_count
        if self.lang:
            outfile.write(f'{fence}{self.lang}\n')
        else:
            outfile.write(f'{fence}\n')

        # Process tokens line by line
        current_line = []
        line_number = self.linenostart
        token_idx = 0

        while token_idx < len(tokens):
            ttype, value = tokens[token_idx]

            # Check if this is the start of a function signature
            current_func = None
            for func in function_signatures:
                if token_idx == func['start_idx']:
                    current_func = func
                    break

            if current_func and self.function_style != 'emphasis':
                # Handle function signature with special formatting
                if self.function_style == 'callout':
                    # End current code block, add function highlight, start new block
                    if current_line:
                        self._write_line(outfile, current_line, line_number)
                        current_line = []

                    outfile.write(f'{fence}\n\n')
                    outfile.write(f'> **📋 Function:** `{current_func["name"]}`\n')
                    outfile.write(f'> Line {line_number}\n\n')
                    outfile.write(f'{fence}{self.lang}\n')

                elif self.function_style == 'heading':
                    # End current code block, add heading, start new block
                    if current_line:
                        self._write_line(outfile, current_line, line_number)
                        current_line = []

                    outfile.write(f'{fence}\n\n')
                    outfile.write(f'### 🔧 {current_func["name"]}\n\n')
                    outfile.write(f'{fence}{self.lang}\n')

                # Skip to end of function signature
                token_idx = current_func['end_idx']
                continue

            # Handle line breaks
            if '\n' in value:
                parts = value.split('\n')

                # Process the part before newline
                if parts[0]:
                    if self.inline_styles:
                        prefix, suffix = self._get_markdown_style(ttype)
                        if prefix or suffix:
                            current_line.append(f'{prefix}{parts[0]}{suffix}')
                        else:
                            current_line.append(parts[0])
                    else:
                        current_line.append(parts[0])

                # Output the completed line with special function marking
                self._write_line(outfile, current_line, line_number, tokens, token_idx)
                line_number += 1
                current_line = []

                # Handle multiple newlines
                for i in range(1, len(parts) - 1):
                    if parts[i]:
                        if self.inline_styles:
                            prefix, suffix = self._get_markdown_style(ttype)
                            if prefix or suffix:
                                current_line.append(f'{prefix}{parts[i]}{suffix}')
                            else:
                                current_line.append(parts[i])
                        else:
                            current_line.append(parts[i])
                    self._write_line(outfile, current_line, line_number, tokens, token_idx)
                    line_number += 1
                    current_line = []

                # Handle the part after the last newline
                if len(parts) > 1 and parts[-1]:
                    if self.inline_styles:
                        prefix, suffix = self._get_markdown_style(ttype)
                        if prefix or suffix:
                            current_line.append(f'{prefix}{parts[-1]}{suffix}')
                        else:
                            current_line.append(parts[-1])
                    else:
                        current_line.append(parts[-1])
            else:
                # No newline, just add to current line
                if value:  # Skip empty values
                    if self.inline_styles:
                        prefix, suffix = self._get_markdown_style(ttype)
                        if prefix or suffix:
                            current_line.append(f'{prefix}{value}{suffix}')
                        else:
                            current_line.append(value)
                    else:
                        current_line.append(value)

            token_idx += 1

        # Output any remaining content
        if current_line:
            self._write_line(outfile, current_line, line_number, tokens, len(tokens) - 1)

        # End fenced code block
        outfile.write(f'{fence}\n')

        # Add highlighted lines information as comments if specified
        if self.hl_lines:
            outfile.write('\n<!-- Highlighted lines: ')
            outfile.write(', '.join(map(str, sorted(self.hl_lines))))
            outfile.write(' -->\n')

        # Add function summary at the end if emphasis style
        if function_signatures and self.function_style == 'emphasis':
            outfile.write('\n## 🔧 Functions\n\n')
            for func in function_signatures:
                params_display = f"({func['parameters']})" if func['parameters'] else "()"
                outfile.write(f'**{func["name"]}**{params_display} - Line {func["line_num"]}\n')
            outfile.write('\n')

    def _write_line(self, outfile, line_parts, line_number, tokens=None, token_idx=None):
        """
        Write a single line to the output file.
        """
        line_content = ''.join(line_parts)

        # Check if this line contains a function definition for emphasis style
        is_function_line = False
        function_name = ""

        if (self.highlight_functions and self.function_style == 'emphasis' and
            tokens and token_idx is not None):
            # Check if current line contains a function definition
            line_tokens = []
            temp_line_num = line_number
            i = max(0, token_idx - 10)  # Look back a bit

            while i <= min(len(tokens) - 1, token_idx + 10):  # Look ahead a bit
                if i < len(tokens):
                    ttype, value = tokens[i]
                    if '\n' in value:
                        if temp_line_num == line_number:
                            line_tokens.append((ttype, value.split('\n')[0]))
                        temp_line_num += value.count('\n')
                        if temp_line_num > line_number:
                            break
                    elif temp_line_num == line_number:
                        line_tokens.append((ttype, value))
                i += 1

            # Check if this line has function keywords
            line_text = ''.join(token[1] for token in line_tokens).strip()
            if any(keyword in line_text for keyword in ['def ', 'function ', 'fn ', 'func ', 'method ', 'proc ', 'procedure ', 'sub ']):
                is_function_line = True
                # Extract function name
                for ttype, value in line_tokens:
                    if ttype in (Name.Function, Name) and value.isidentifier():
                        function_name = value
                        break

        # Add line numbers if requested
        if self.linenos:
            line_prefix = f'{line_number:4d} | '
            outfile.write(line_prefix)

        # Add special marking for function lines in emphasis mode
        if is_function_line and self.function_style == 'emphasis':
            outfile.write(f'{line_content}  # 🔧 FUNCTION: {function_name}\n')
        # Add highlight comment if this line should be highlighted
        elif line_number in self.hl_lines:
            outfile.write(f'{line_content}  # <<< HIGHLIGHTED\n')
        else:
            outfile.write(f'{line_content}\n')

    def get_style_defs(self, arg=None):
        """
        Return style definitions as Markdown comments.
        Since Markdown doesn't have CSS, this returns documentation about
        the inline formatting used.
        """
        if not self.inline_styles:
            return "<!-- No inline styles used -->"

        style_doc = """<!-- Markdown Formatter Style Guide:
- **Bold**: Keywords, headings, important elements
- *Italic*: Comments, preprocessor directives
- ~~Strikethrough~~: Errors, deleted content
- Regular text: Most code elements (strings, names, numbers, operators)
-->"""
        return style_doc


# Register the formatter (this would typically be done in _mapping.py)
__all__ = ['MarkdownFormatter']


# Example usage and testing
if __name__ == '__main__':
    import sys
    import os
    from pygments import highlight
    from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
    from pygments.util import ClassNotFound

    def main():
        """
        Main function to process a file and output Markdown formatted code.
        Usage: python markdown_formatter.py <filename> [options]
        """
        # if len(sys.argv) < 2:
        #     print("Usage: python markdown_formatter.py <filename> [--style=emphasis|callout|heading] [--linenos] [--full]")
        #     print("Example: python markdown_formatter.py example.py --style=callout --linenos")
        #     return
        #
        # filename = sys.argv[1]
        # filename = "/Users/csimoes/Projects/Python/conductor/app/processor/base_processor.py"
        filename = "/Users/csimoes/IdeaProjects/Amazon/AmazonScraper/adtrimmer-core/src/main/java/org/simoes/app/AutoBidder8.java"

        # Check if file exists
        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            return

        # Parse command line options
        function_style = 'emphasis'
        show_linenos = False
        full_document = False

        for arg in sys.argv[2:]:
            if arg.startswith('--style='):
                function_style = arg.split('=', 1)[1]
                if function_style not in ('emphasis', 'callout', 'heading'):
                    print(f"Warning: Unknown style '{function_style}', using 'emphasis'")
                    function_style = 'emphasis'
            elif arg == '--linenos':
                show_linenos = True
            elif arg == '--full':
                full_document = True

        try:
            # Read the file
            with open(filename, 'r', encoding='utf-8') as f:
                code = f.read()

            # Get appropriate lexer for the file
            try:
                lexer = get_lexer_for_filename(filename)
            except ClassNotFound:
                # Fallback to text lexer if file type not recognized
                print(f"Warning: Could not determine lexer for '{filename}', using text")
                lexer = get_lexer_by_name('text')

            # Create formatter with options
            formatter_options = {
                'highlight_functions': True,
                'function_style': function_style,
                'linenos': show_linenos,
                'full': full_document
            }

            # Auto-detect language from lexer
            if hasattr(lexer, 'aliases') and lexer.aliases:
                formatter_options['lang'] = lexer.aliases[0]

            # Set title for full documents
            if full_document:
                formatter_options['title'] = f'Code Analysis: {os.path.basename(filename)}'

            formatter = MarkdownFormatter(**formatter_options)

            # Generate the highlighted code
            result = highlight(code, lexer, formatter)

            # Output the result
            print(result)

        except Exception as e:
            print(f"Error processing file: {e}")
            return

    main()