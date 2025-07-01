"""
Pygments TLDR Formatter

A formatter for Pygments that outputs TLDR-formatted code with syntax highlighting
using fenced code blocks and optional inline styling.
"""
import logging

from pygments_tldr.formatter import Formatter
from pygments_tldr.token import (
    Token, Whitespace, Error, Other, Keyword, Name, Literal, String,
    Number, Punctuation, Operator, Comment, Generic, Text
)
from pygments_tldr.util import get_bool_opt, get_int_opt, get_list_opt


class TLDRFormatter(Formatter):
    """
    Format tokens as TLDR code blocks with optional syntax highlighting.

    This formatter outputs code in TLDR format using fenced
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
        Generate a complete TLDR document with title and metadata.
        (default: False)

    `title` : string
        Title for the document when `full` is True. (default: '')

    `inline_styles` : bool
        Use inline TLDR formatting for syntax highlighting instead of
        just the fenced code block. (default: False)

    `fence_char` : string
        Character to use for fencing. Either '`' or '~'. (default: '`')

    `fence_count` : integer
        Number of fence characters to use. Must be at least 3. (default: 3)

    `highlight_functions` : bool
        Add special highlighting for function/method signatures

    """

    name = 'TLDR'
    aliases = ['tldr', 'TLDR']
    filenames = ['*.*']

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

    def _detect_language(self):
        """
        Detect the programming language based on lexer information.
        Returns a language category for function detection.
        """
        if hasattr(self, 'lexer') and self.lexer:
            if hasattr(self.lexer, 'aliases') and self.lexer.aliases:
                lang_name = self.lexer.aliases[0].lower()
            elif hasattr(self.lexer, 'name'):
                lang_name = self.lexer.name.lower()
            else:
                lang_name = self.lang.lower() if self.lang else 'unknown'
        else:
            lang_name = self.lang.lower() if self.lang else 'unknown'
        
        # Map language names to categories
        if lang_name in ('python', 'py'):
            return 'python'
        elif lang_name in ('javascript', 'js', 'jsx'):
            return 'javascript'
        elif lang_name in ('typescript', 'ts', 'tsx'):
            return 'typescript'
        elif lang_name in ('java'):
            return 'java'
        elif lang_name in ('c#', 'csharp'):
            return 'csharp'
        elif lang_name in ('c++', 'cpp', 'c'):
            return 'c_family'
        elif lang_name in ('rust', 'rs'):
            return 'rust'
        elif lang_name in ('go', 'golang'):
            return 'go'
        elif lang_name in ('php'):
            return 'php'
        elif lang_name in ('ruby', 'rb'):
            return 'ruby'
        elif lang_name in ('swift'):
            return 'swift'
        else:
            return 'generic'

    def _is_function_definition(self, tokens, start_idx):
        """
        Detect if the current position is the start of a function/method definition.
        Returns (is_function, function_name, parameters, end_idx, access_modifier, return_type) tuple.
        """
        if not self.highlight_functions:
            return False, None, None, start_idx, None, None

        # Detect language first
        language = self._detect_language()
        
        # Apply language-specific detection logic
        if language == 'python':
            return self._detect_python_function(tokens, start_idx)
        elif language == 'javascript':
            return self._detect_javascript_function(tokens, start_idx)
        elif language == 'typescript':
            return self._detect_typescript_function(tokens, start_idx)
        elif language == 'java':
            return self._detect_java_function(tokens, start_idx)
        elif language == 'csharp':
            return self._detect_csharp_function(tokens, start_idx)
        elif language == 'c_family':
            return self._detect_c_family_function(tokens, start_idx)
        elif language == 'rust':
            return self._detect_rust_function(tokens, start_idx)
        elif language == 'go':
            return self._detect_go_function(tokens, start_idx)
        elif language == 'php':
            return self._detect_php_function(tokens, start_idx)
        elif language == 'ruby':
            return self._detect_ruby_function(tokens, start_idx)
        elif language == 'swift':
            return self._detect_swift_function(tokens, start_idx)
        else:
            return self._detect_generic_function(tokens, start_idx)

    def _detect_python_function(self, tokens, start_idx):
        """
        Method 1: Detect Python function definitions using Name.Function tokens.
        """
        i = start_idx
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        # Look for Name.Function token (Python)
        if ttype == Name.Function or ttype == Name.Function.Magic:
            function_name = value
            logging.debug(f"Found Python function definition: {function_name}")
            i += 1
            
            return self._extract_function_parameters(tokens, i, function_name, start_idx)
        
        return False, None, None, start_idx, None, None

    def _detect_javascript_function(self, tokens, start_idx):
        """
        Method 2: Detect JavaScript/TypeScript function definitions.
        Handles: function declarations, arrow functions, export functions.
        """
        i = start_idx
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        # Method 2a: Traditional function declarations
        if ttype == Keyword.Declaration and value == 'function':
            return self._extract_js_function_declaration(tokens, i)
        
        # Method 2b: Export function patterns
        elif ttype == Keyword and value == 'export':
            return self._extract_js_export_function(tokens, i)
        
        # Method 2c: Arrow functions (const/let/var)
        elif ttype in (Keyword.Declaration, Keyword) and value in ('const', 'let', 'var'):
            return self._extract_js_arrow_function(tokens, i)
        
        # Method 2d: Class methods and object methods (Name.Other followed by parentheses)
        elif ttype in (Name.Other, Name.Function) and i + 1 < len(tokens):
            # Look ahead to see if this is followed by parentheses (indicating a method)
            next_idx = i + 1
            while next_idx < len(tokens) and tokens[next_idx][0] in (Whitespace,):
                next_idx += 1
            if next_idx < len(tokens) and tokens[next_idx][1] == '(':
                function_name = value
                logging.debug(f"Found JavaScript method: {function_name}")
                return self._extract_js_method_parameters(tokens, next_idx, function_name, i)
        
        return False, None, None, start_idx, None, None

    def _detect_typescript_function(self, tokens, start_idx):
        """
        Method 3: Detect TypeScript function definitions.
        Handles: function declarations, arrow functions, class methods, interfaces, generics, type annotations.
        """
        i = start_idx
        access_modifiers = []
        return_types = []
        is_interface_method = False
        is_abstract = False
        
        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        # Look backwards for TypeScript-specific modifiers and keywords
        # TypeScript: [export] [access_modifier] [static] [async] [abstract] function/method
        # Interfaces: methodName(params): returnType;
        # Classes: [access] [static] [async] methodName(params): returnType
        
        # Collect TypeScript-specific modifiers by looking back
        lookback_start = max(0, start_idx - 25)
        for j in range(lookback_start, i):
            if j < len(tokens):
                ttype, value = tokens[j]
                if ttype == Keyword and value in ('public', 'private', 'protected', 'static', 'readonly', 'abstract', 'async', 'export', 'default'):
                    access_modifiers.append(value)
                    if value == 'abstract':
                        is_abstract = True
                elif ttype == Keyword and value in ('interface', 'declare'):
                    is_interface_method = True
        
        # Look for TypeScript function/method patterns
        ttype, value = tokens[i]
        function_name = ""
        
        # Method 3a: Traditional TypeScript function declarations
        if ttype == Keyword.Declaration and value == 'function':
            return self._extract_typescript_function_declaration(tokens, i, access_modifiers, is_abstract)
        
        # Method 3b: TypeScript export function patterns
        elif ttype == Keyword and value == 'export':
            return self._extract_typescript_export_function(tokens, i)
        
        # Method 3c: TypeScript arrow functions (const/let/var with type annotations)
        elif ttype in (Keyword.Declaration, Keyword) and value in ('const', 'let', 'var'):
            return self._extract_typescript_arrow_function(tokens, i)
        
        # Method 3d: TypeScript class method or interface method signatures
        elif ttype in (Name.Function, Name.Other, Name) and i + 1 < len(tokens):
            # Look ahead to see if this looks like a TypeScript method signature
            temp_i = i + 1
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1
            
            if temp_i < len(tokens):
                next_token = tokens[temp_i][1]
                
                # TypeScript method signature patterns
                if next_token in ('(', '<'):  # Method call or generic method
                    function_name = value
                    logging.debug(f"Found TypeScript method/function: {function_name}")
                    i += 1
                    return self._extract_typescript_method_parameters(tokens, i, function_name, start_idx, access_modifiers, is_interface_method, is_abstract)
        
        return False, None, None, start_idx, None, None

    def _detect_java_function(self, tokens, start_idx):
        """
        Method 4: Detect Java method definitions.
        Handles: public/private/protected methods, static methods, constructors.
        """
        i = start_idx
        access_modifiers = []
        return_types = []
        is_constructor = False
        
        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        # Look backwards and forwards for Java method patterns
        # Java methods typically have: [access_modifier] [static] [return_type] methodName(params)
        # Constructors have: [access_modifier] ClassName(params)
        
        # Collect access modifiers and return types by looking back
        lookback_start = max(0, start_idx - 15)
        for j in range(lookback_start, i):
            if j < len(tokens):
                ttype, value = tokens[j]
                if ttype == Keyword and value in ('public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized', 'native', 'strictfp'):
                    access_modifiers.append(value)
                elif ttype in (Keyword.Type, Name.Builtin.Type) and value in ('void', 'int', 'boolean', 'char', 'byte', 'short', 'long', 'float', 'double'):
                    return_types.append(value)
                elif ttype == Name and value[0].isupper():  # Likely a class type
                    return_types.append(value)
        
        # Look for method name
        ttype, value = tokens[i]
        function_name = ""
        
        # Check if this is a method name (Name token followed by parentheses)
        if ttype in (Name.Function, Name.Other, Name):
            # Look ahead to confirm this is followed by parentheses
            temp_i = i + 1
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1
            
            if temp_i < len(tokens) and tokens[temp_i][1] == '(':
                function_name = value
                logging.debug(f"Found Java method definition: {function_name}")
                
                # Check if this might be a constructor (method name matches class name pattern)
                if value[0].isupper() and not return_types:
                    is_constructor = True
                    logging.debug(f"Detected Java constructor: {function_name}")
                
                i += 1
                return self._extract_java_method_parameters(tokens, i, function_name, start_idx, access_modifiers, return_types, is_constructor)
        
        return False, None, None, start_idx, None, None

    def _detect_csharp_function(self, tokens, start_idx):
        """
        Method 5: Detect C# method definitions.
        Handles: access modifiers, properties, async methods, generic methods, operators.
        """
        i = start_idx
        access_modifiers = []
        return_types = []
        is_constructor = False
        is_property = False
        is_async = False
        
        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        # Look backwards and forwards for C# method patterns
        # C# methods: [access_modifier] [static] [async] [return_type] MethodName(params)
        # Properties: [access_modifier] [static] Type PropertyName { get; set; }
        # Constructors: [access_modifier] ClassName(params)
        
        # Collect access modifiers and return types by looking back
        lookback_start = max(0, start_idx - 20)
        for j in range(lookback_start, i):
            if j < len(tokens):
                ttype, value = tokens[j]
                if ttype == Keyword and value in ('public', 'private', 'protected', 'internal', 'static', 'virtual', 'override', 'abstract', 'sealed', 'extern', 'readonly', 'const'):
                    access_modifiers.append(value)
                elif ttype == Keyword and value == 'async':
                    is_async = True
                    access_modifiers.append(value)
                elif ttype in (Keyword.Type, Name.Builtin.Type) and value in ('void', 'int', 'string', 'bool', 'float', 'double', 'decimal', 'char', 'byte', 'short', 'long', 'object', 'dynamic'):
                    return_types.append(value)
                elif ttype == Name and value[0].isupper():  # Likely a class/interface type
                    return_types.append(value)
        
        # Look for method/property name
        ttype, value = tokens[i]
        function_name = ""
        
        # Check if this is a method name (Name token followed by parentheses or property)
        if ttype in (Name.Function, Name.Other, Name, Name.Property):
            # Look ahead to determine if this is a method, property, or constructor
            temp_i = i + 1
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1
            
            if temp_i < len(tokens):
                next_token = tokens[temp_i][1]
                
                if next_token == '(':
                    # This is a method or constructor
                    function_name = value
                    logging.debug(f"Found C# method definition: {function_name}")
                    
                    # Check if this might be a constructor
                    if value[0].isupper() and not return_types:
                        is_constructor = True
                        logging.debug(f"Detected C# constructor: {function_name}")
                    
                    i += 1
                    return self._extract_csharp_method_parameters(tokens, i, function_name, start_idx, access_modifiers, return_types, is_constructor, is_async)
                    
                elif next_token == '{':
                    # This might be a property
                    function_name = value
                    is_property = True
                    logging.debug(f"Found C# property definition: {function_name}")
                    
                    i += 1
                    return self._extract_csharp_property_definition(tokens, i, function_name, start_idx, access_modifiers, return_types)
        
        return False, None, None, start_idx, None, None

    def _detect_c_family_function(self, tokens, start_idx):
        """
        Method 6: Detect C/C++ function definitions.
        """
        return self._detect_generic_function(tokens, start_idx)

    def _detect_rust_function(self, tokens, start_idx):
        """
        Method 7: Detect Rust function definitions (fn keyword).
        """
        i = start_idx
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        if ttype == Keyword and value == 'fn':
            i += 1
            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                i += 1
            
            if i < len(tokens):
                next_ttype, next_value = tokens[i]
                if next_ttype in (Name.Other, Name, Name.Function):
                    function_name = next_value
                    logging.debug(f"Found Rust function definition: {function_name}")
                    i += 1
                    return self._extract_function_parameters(tokens, i, function_name, start_idx)
        
        return False, None, None, start_idx, None, None

    def _detect_go_function(self, tokens, start_idx):
        """
        Method 8: Detect Go function definitions (func keyword).
        Handles both regular functions and receiver methods.
        """
        i = start_idx
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        if ttype in (Keyword, Keyword.Declaration) and value == 'func':
            i += 1
            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                i += 1
            
            if i < len(tokens):
                next_ttype, next_value = tokens[i]
                
                # Check for receiver method: func (receiver Type) methodName
                if next_ttype == Punctuation and next_value == '(':
                    # Skip receiver parameters by finding the closing ')'
                    paren_count = 1
                    i += 1
                    while i < len(tokens) and paren_count > 0:
                        if tokens[i][1] == '(':
                            paren_count += 1
                        elif tokens[i][1] == ')':
                            paren_count -= 1
                        i += 1
                    
                    # Now look for the method name
                    while i < len(tokens) and tokens[i][0] in (Whitespace,):
                        i += 1
                    
                    if i < len(tokens):
                        method_ttype, method_value = tokens[i]
                        if method_ttype in (Name.Other, Name, Name.Function):
                            function_name = method_value
                            logging.debug(f"Found Go receiver method: {function_name}")
                            i += 1
                            return self._extract_function_parameters(tokens, i, function_name, start_idx)
                
                # Regular function: func functionName
                elif next_ttype in (Name.Other, Name, Name.Function):
                    function_name = next_value
                    logging.debug(f"Found Go function definition: {function_name}")
                    i += 1
                    return self._extract_function_parameters(tokens, i, function_name, start_idx)
        
        return False, None, None, start_idx, None, None

    def _detect_php_function(self, tokens, start_idx):
        """
        Method 9: Detect PHP function definitions.
        """
        i = start_idx
        while i < len(tokens) and (tokens[i][0] in (Whitespace,) or (tokens[i][0] == Text and tokens[i][1].strip() == '')):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        if ttype == Keyword and value == 'function':
            i += 1
            while i < len(tokens) and (tokens[i][0] in (Whitespace,) or (tokens[i][0] == Text and tokens[i][1].strip() == '')):
                i += 1
            
            if i < len(tokens):
                next_ttype, next_value = tokens[i]
                if next_ttype in (Name.Other, Name, Name.Function, Name.Function.Magic):
                    function_name = next_value
                    logging.debug(f"Found PHP function definition: {function_name}")
                    i += 1
                    return self._extract_function_parameters(tokens, i, function_name, start_idx)
        
        return False, None, None, start_idx, None, None

    def _detect_ruby_function(self, tokens, start_idx):
        """
        Method 10: Detect Ruby function definitions (def keyword).
        Handles both instance methods and class methods (def self.method_name).
        """
        i = start_idx
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        ttype, value = tokens[i]
        
        if ttype == Keyword and value == 'def':
            i += 1
            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                i += 1
            
            if i < len(tokens):
                next_ttype, next_value = tokens[i]
                
                # Check for class method: def self.method_name
                if next_ttype == Name.Class and next_value == 'self':
                    i += 1
                    # Skip the dot operator
                    while i < len(tokens) and tokens[i][0] in (Whitespace, Operator):
                        if tokens[i][1] == '.':
                            i += 1
                            break
                        i += 1
                    
                    # Skip any whitespace after the dot
                    while i < len(tokens) and tokens[i][0] in (Whitespace,):
                        i += 1
                    
                    # Now get the actual method name
                    if i < len(tokens):
                        method_ttype, method_value = tokens[i]
                        if method_ttype in (Name.Other, Name, Name.Function):
                            function_name = method_value
                            logging.debug(f"Found Ruby class method: {function_name}")
                            i += 1
                            return self._extract_ruby_function_parameters(tokens, i, function_name, start_idx)
                
                # Regular instance method: def method_name
                elif next_ttype in (Name.Other, Name, Name.Function):
                    function_name = next_value
                    logging.debug(f"Found Ruby instance method: {function_name}")
                    i += 1
                    return self._extract_ruby_function_parameters(tokens, i, function_name, start_idx)
        
        return False, None, None, start_idx, None, None

    def _detect_swift_function(self, tokens, start_idx):
        """
        Method 11: Detect Swift function definitions.
        Handles: func keyword, init methods, computed properties, closures.
        """
        i = start_idx
        access_modifiers = []
        return_types = []
        is_initializer = False
        is_computed_property = False
        
        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        # Look backwards for Swift access modifiers and attributes
        # Swift functions: [access_level] [mutating] [class/static] func name(params) -> ReturnType
        # Swift init: [access_level] [convenience] init(params)
        # Swift computed properties: [access_level] var name: Type { get set }
        
        # Collect access modifiers and attributes by looking back
        lookback_start = max(0, start_idx - 20)
        for j in range(lookback_start, i):
            if j < len(tokens):
                ttype, value = tokens[j]
                if ttype == Keyword and value in ('public', 'private', 'internal', 'fileprivate', 'open', 'static', 'class', 'final', 'override', 'mutating', 'nonmutating', 'convenience', 'required', 'lazy', 'weak', 'unowned'):
                    access_modifiers.append(value)
                elif ttype == Name and value.startswith('@'):  # Swift attributes like @objc, @available
                    access_modifiers.append(value)
        
        # Look for function/init/property keywords
        ttype, value = tokens[i]
        function_name = ""
        
        # Method 11a: Traditional Swift functions
        if ttype == Keyword.Declaration and value == 'func':
            return self._extract_swift_function_declaration(tokens, i, access_modifiers)
        # Handle case where 'func' is tokenized as Name.Class (after 'class' keyword)
        elif ttype == Name.Class and value == 'func':
            return self._extract_swift_function_declaration(tokens, i, access_modifiers)
        
        # Method 11b: Swift initializers
        elif ttype == Keyword.Declaration and value == 'init':
            is_initializer = True
            function_name = 'init'
            logging.debug(f"Found Swift initializer: {function_name}")
            i += 1
            return self._extract_swift_initializer_parameters(tokens, i, function_name, start_idx, access_modifiers)
        
        # Method 11c: Swift computed properties and subscripts
        elif ttype == Keyword.Declaration and value in ('var', 'let'):
            return self._extract_swift_property_or_subscript(tokens, i, access_modifiers, value)
        
        # Method 11d: Swift subscripts
        elif ttype == Keyword.Declaration and value == 'subscript':
            function_name = 'subscript'
            logging.debug(f"Found Swift subscript: {function_name}")
            i += 1
            return self._extract_swift_subscript_parameters(tokens, i, function_name, start_idx, access_modifiers)
        
        return False, None, None, start_idx, None, None

    def _detect_generic_function(self, tokens, start_idx):
        """
        Generic function detection fallback for unrecognized languages.
        Uses original complex logic for broad compatibility.
        """
        i = start_idx
        function_name = ""
        parameters = ""
        access_modifier = ""
        return_type = ""

        # Skip whitespace at the beginning
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1

        if i >= len(tokens):
            return False, None, None, start_idx, None, None

        # Look backwards for access modifiers and return types
        access_modifiers = []
        return_types = []

        # Look back up to 10 tokens for modifiers/types
        lookback_start = max(0, start_idx - 10)
        for j in range(lookback_start, i):
            if j < len(tokens):
                ttype, value = tokens[j]
                if ttype == Keyword and value.lower() in ('public', 'private', 'protected', 'static', 'final', 'abstract', 'virtual', 'override', 'async', 'extern'):
                    access_modifiers.append(value)
                elif ttype in (Keyword.Type, Name.Builtin.Type, Keyword) and value.lower() in ('void', 'int', 'string', 'bool', 'float', 'double', 'long', 'short', 'char', 'byte'):
                    return_types.append(value)
                elif ttype == Name and value in ('String', 'Integer', 'Boolean', 'List', 'Dict', 'Array'):
                    return_types.append(value)

        # Look for function definition patterns
        ttype, value = tokens[i]
        
        # Try to find function name through various patterns
        if ttype == Name.Function or ttype == Name.Function.Magic:
            function_name = value
            i += 1
        elif ttype in (Name.Other, Name) and i + 1 < len(tokens):
            # Check if next significant token suggests this is a function
            temp_i = i + 1
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1
            if temp_i < len(tokens) and tokens[temp_i][1] == '(':
                function_name = value
                i += 1

        if not function_name:
            return False, None, None, start_idx, None, None

        # Combine modifiers and return types
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = ' '.join(return_types) if return_types else None

        return self._extract_function_parameters(tokens, i, function_name, start_idx, access_modifier, return_type)

    def _extract_js_function_declaration(self, tokens, i):
        """
        Extract JavaScript function declaration: function name(...) { } or function* name(...) { }
        """
        # Skip 'function' keyword
        i += 1
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1
        
        # Handle generator functions (function*)
        is_generator = False
        if i < len(tokens) and tokens[i][0] == Operator and tokens[i][1] == '*':
            is_generator = True
            i += 1
            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                i += 1
        
        if i < len(tokens):
            next_ttype, next_value = tokens[i]
            if next_ttype in (Name.Other, Name):
                function_name = next_value
                if is_generator:
                    logging.debug(f"Found JS generator function definition: {function_name}")
                else:
                    logging.debug(f"Found JS function definition: {function_name}")
                i += 1
                return self._extract_function_parameters(tokens, i, function_name, i)
        
        return False, None, None, i, None, None

    def _extract_js_export_function(self, tokens, i):
        """
        Extract export function pattern: export function name(...) { }
        """
        # Look ahead for 'function' keyword
        temp_i = i + 1
        while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
            temp_i += 1
        
        if temp_i < len(tokens) and tokens[temp_i][0] == Keyword.Declaration and tokens[temp_i][1] == 'function':
            # Found export function, look for the function name
            temp_i += 1
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1
            
            if temp_i < len(tokens) and tokens[temp_i][0] in (Name.Other, Name):
                function_name = tokens[temp_i][1]
                logging.debug(f"Found export function definition: {function_name}")
                temp_i += 1
                return self._extract_function_parameters(tokens, temp_i, function_name, i)
        
        return False, None, None, i, None, None

    def _extract_js_arrow_function(self, tokens, i):
        """
        Extract arrow function pattern: const name = (...) => { }
        """
        # Look ahead for arrow function pattern: const name = (...) => {...}
        temp_i = i + 1
        potential_name = ""
        
        # Skip whitespace and get the name
        while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
            temp_i += 1
        if temp_i < len(tokens) and tokens[temp_i][0] in (Name.Other, Name):
            potential_name = tokens[temp_i][1]
            temp_i += 1
        
        # Look for = ... => pattern
        found_arrow = False
        paren_depth = 0
        while temp_i < len(tokens) and temp_i < i + 20:  # Limit search range
            temp_ttype, temp_value = tokens[temp_i]
            if temp_value == '=' and paren_depth == 0:
                # Found assignment, look for arrow function
                temp_i += 1
                while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                    temp_i += 1
                
                # Check for different arrow function patterns
                arrow_start = temp_i
                while temp_i < len(tokens) and temp_i < arrow_start + 10:
                    temp_ttype, temp_value = tokens[temp_i]
                    if temp_value == '=>':
                        found_arrow = True
                        break
                    elif temp_value == '(':
                        paren_depth += 1
                    elif temp_value == ')':
                        paren_depth -= 1
                    temp_i += 1
                break
            elif temp_value == '(':
                paren_depth += 1
            elif temp_value == ')':
                paren_depth -= 1
            temp_i += 1
        
        if found_arrow and potential_name:
            function_name = potential_name
            logging.debug(f"Found arrow function definition: {function_name}")
            return self._extract_arrow_function_parameters(tokens, i, function_name)
        
        return False, None, None, i, None, None

    def _extract_arrow_function_parameters(self, tokens, start_i, function_name):
        """
        Extract parameters from arrow function.
        """
        # This is an arrow function, extract parameters differently
        temp_i = start_i + 1  # Skip past const/let/var
        while temp_i < len(tokens):
            temp_ttype, temp_value = tokens[temp_i]
            if temp_value == '=':
                temp_i += 1
                while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                    temp_i += 1
                
                # Look for parameter pattern: () or (param1, param2) or param
                if temp_i < len(tokens) and tokens[temp_i][1] == '(':
                    # Extract parameters from parentheses
                    paren_count = 1
                    temp_i += 1
                    param_tokens = []
                    
                    while temp_i < len(tokens) and paren_count > 0:
                        temp_ttype, temp_value = tokens[temp_i]
                        if temp_value == '(':
                            paren_count += 1
                        elif temp_value == ')':
                            paren_count -= 1
                        
                        if paren_count > 0:
                            param_tokens.append((temp_ttype, temp_value))
                        temp_i += 1
                    
                    parameters = ''.join(token[1] for token in param_tokens).strip()
                    parameters = ' '.join(parameters.split())
                    
                    # Look for the arrow
                    while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                        temp_i += 1
                    if temp_i < len(tokens) and tokens[temp_i][1] == '=>':
                        return True, function_name, parameters, temp_i, None, None
                else:
                    # Single parameter without parentheses
                    param_start = temp_i
                    while temp_i < len(tokens) and tokens[temp_i][1] != '=>':
                        temp_i += 1
                    if temp_i < len(tokens):
                        param_tokens = tokens[param_start:temp_i]
                        parameters = ''.join(token[1] for token in param_tokens).strip()
                        parameters = ' '.join(parameters.split())
                        return True, function_name, parameters, temp_i, None, None
                break
            temp_i += 1
        
        return False, None, None, start_i, None, None

    def _extract_js_method_parameters(self, tokens, paren_idx, function_name, start_idx):
        """
        Extract parameters from JavaScript class methods and object methods.
        Handles: method() {}, async method() {}, static method() {}, get/set methods.
        """
        # Extract parameters from parentheses
        i = paren_idx
        if i < len(tokens) and tokens[i][1] == '(':
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
                
                if paren_count > 0:
                    param_tokens.append((ttype, value))
                i += 1
            
            # Build parameter string
            parameters = ''.join(token[1] for token in param_tokens).strip()
            parameters = ' '.join(parameters.split())  # Normalize whitespace
            
            # Look for access modifiers before the method name
            access_modifier = None
            for j in range(max(0, start_idx - 5), start_idx):
                if j < len(tokens):
                    ttype, value = tokens[j]
                    if ttype == Keyword and value in ('static', 'async', 'get', 'set'):
                        access_modifier = value if access_modifier is None else f"{access_modifier} {value}"
            
            logging.debug(f"Found JavaScript method: {function_name}({parameters})")
            return True, function_name, f"({parameters})", i, access_modifier, None
        
        return False, None, None, start_idx, None, None

    def _extract_java_method_parameters(self, tokens, i, function_name, start_idx, access_modifiers, return_types, is_constructor):
        """
        Extract parameters from Java method definitions.
        Handles generics, annotations, and Java-specific syntax.
        """
        # Combine modifiers and return types
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = ' '.join(return_types) if return_types else None
        
        # For constructors, the return type is implicitly the class name
        if is_constructor:
            return_type = function_name  # Constructor returns instance of the class
        
        # Skip over any generic type parameters (e.g., <T, U>)
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '<':
                # Skip over generic type parameters
                angle_count = 1
                i += 1
                while i < len(tokens) and angle_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '<':
                            angle_count += 1
                        elif value == '>':
                            angle_count -= 1
                    i += 1
                break
            elif ttype == Punctuation and value == '(':
                break
            elif ttype not in (Whitespace,):
                # Skip over other tokens until we find ( or <
                i += 1
                if i >= len(tokens):
                    break
            else:
                i += 1

        # Now look for the opening parenthesis
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found method signature, now extract parameters
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

                # Look for throws clause (throws Exception1, Exception2)
                throws_clause = []
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Keyword and value == 'throws':
                        # Found throws clause, collect exception types
                        i += 1
                        while i < len(tokens):
                            ttype, value = tokens[i]
                            if value in ('{', ';') or value == '\n':
                                break
                            if ttype in (Name, Name.Exception) and value not in (',', ' '):
                                throws_clause.append(value)
                            i += 1
                        break
                    elif value in ('{', ';') or value == '\n':
                        break
                    i += 1

                # Add throws clause to access modifier if present
                if throws_clause:
                    throws_str = 'throws ' + ', '.join(throws_clause)
                    if access_modifier:
                        access_modifier += ' ' + throws_str
                    else:
                        access_modifier = throws_str

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_csharp_method_parameters(self, tokens, i, function_name, start_idx, access_modifiers, return_types, is_constructor, is_async):
        """
        Extract parameters from C# method definitions.
        Handles generics, nullable types, default parameters, ref/out parameters.
        """
        # Combine modifiers and return types
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = ' '.join(return_types) if return_types else None
        
        # For constructors, the return type is implicitly the class name
        if is_constructor:
            return_type = function_name
        
        # Skip over any generic type parameters (e.g., <T, U>)
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '<':
                # Skip over generic type parameters
                angle_count = 1
                i += 1
                while i < len(tokens) and angle_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '<':
                            angle_count += 1
                        elif value == '>':
                            angle_count -= 1
                    i += 1
                break
            elif ttype == Punctuation and value == '(':
                break
            elif ttype not in (Whitespace,):
                # Skip over other tokens until we find ( or <
                i += 1
                if i >= len(tokens):
                    break
            else:
                i += 1

        # Now look for the opening parenthesis
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found method signature, now extract parameters
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

                # Look for where clause (generic constraints)
                where_clause = []
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Keyword and value == 'where':
                        # Found where clause for generic constraints
                        constraint_start = i
                        i += 1
                        while i < len(tokens):
                            ttype, value = tokens[i]
                            if value in ('{', ';') or value == '\n':
                                break
                            i += 1
                        
                        # Extract the where clause
                        where_tokens = tokens[constraint_start:i]
                        where_str = ''.join(token[1] for token in where_tokens).strip()
                        where_clause.append(where_str)
                        break
                    elif value in ('{', ';') or value == '\n':
                        break
                    i += 1

                # Add where clause to access modifier if present
                if where_clause:
                    where_str = ' '.join(where_clause)
                    if access_modifier:
                        access_modifier += ' ' + where_str
                    else:
                        access_modifier = where_str

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_csharp_property_definition(self, tokens, i, property_name, start_idx, access_modifiers, return_types):
        """
        Extract C# property definitions like: public string Name { get; set; }
        """
        # Combine modifiers and return types
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = ' '.join(return_types) if return_types else None
        
        # Look for property accessors within braces
        brace_count = 0
        accessor_tokens = []
        
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '{':
                brace_count += 1
                if brace_count == 1:
                    # Start collecting accessor tokens
                    i += 1
                    continue
            elif ttype == Punctuation and value == '}':
                brace_count -= 1
                if brace_count == 0:
                    # End of property definition
                    break
            
            if brace_count > 0:
                accessor_tokens.append((ttype, value))
            
            i += 1
        
        # Extract accessor information (get, set, init, etc.)
        accessors = ''.join(token[1] for token in accessor_tokens).strip()
        accessors = ' '.join(accessors.split())
        
        # Properties don't have traditional parameters, but we can show the accessors
        parameters = f"{{ {accessors} }}" if accessors else "{ }"
        
        return True, property_name, parameters, i, access_modifier, return_type

    def _extract_typescript_function_declaration(self, tokens, i, access_modifiers, is_abstract):
        """
        Extract TypeScript function declaration: [export] function name<T>(params): ReturnType
        """
        # Skip 'function' keyword
        i += 1
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1
        
        if i < len(tokens):
            next_ttype, next_value = tokens[i]
            if next_ttype in (Name.Function, Name.Other, Name):
                function_name = next_value
                logging.debug(f"Found TypeScript function declaration: {function_name}")
                i += 1
                return self._extract_typescript_method_parameters(tokens, i, function_name, i, access_modifiers, False, is_abstract)
        
        return False, None, None, i, None, None

    def _extract_typescript_export_function(self, tokens, i):
        """
        Extract TypeScript export function patterns: export [default] function name() / export const name = ()
        """
        # Look ahead for function patterns after 'export'
        temp_i = i + 1
        while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
            temp_i += 1
        
        if temp_i < len(tokens):
            next_ttype, next_value = tokens[temp_i]
            
            # export default function
            if next_ttype == Keyword and next_value == 'default':
                temp_i += 1
                while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                    temp_i += 1
                if temp_i < len(tokens) and tokens[temp_i][0] == Keyword.Declaration and tokens[temp_i][1] == 'function':
                    return self._extract_typescript_function_declaration(tokens, temp_i, ['export', 'default'], False)
            
            # export function
            elif next_ttype == Keyword.Declaration and next_value == 'function':
                return self._extract_typescript_function_declaration(tokens, temp_i, ['export'], False)
            
            # export const/let arrow function
            elif next_ttype in (Keyword.Declaration, Keyword) and next_value in ('const', 'let', 'var'):
                return self._extract_typescript_arrow_function(tokens, temp_i, ['export'])
        
        return False, None, None, i, None, None

    def _extract_typescript_arrow_function(self, tokens, i, extra_modifiers=[]):
        """
        Extract TypeScript arrow function: const name = (params): ReturnType => { }
        """
        # Look ahead for arrow function pattern with TypeScript type annotations
        temp_i = i + 1
        potential_name = ""
        
        # Skip whitespace and get the name
        while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
            temp_i += 1
        if temp_i < len(tokens) and tokens[temp_i][0] in (Name.Other, Name):
            potential_name = tokens[temp_i][1]
            temp_i += 1
        
        # Look for TypeScript type annotation and arrow pattern
        found_arrow = False
        type_annotation = ""
        paren_depth = 0
        
        while temp_i < len(tokens) and temp_i < i + 30:  # Extended search for TypeScript
            temp_ttype, temp_value = tokens[temp_i]
            
            if temp_value == '=' and paren_depth == 0:
                # Found assignment, look for arrow function with type annotations
                temp_i += 1
                while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                    temp_i += 1
                
                # Look for arrow function patterns (including type annotations)
                arrow_start = temp_i
                while temp_i < len(tokens) and temp_i < arrow_start + 20:
                    temp_ttype, temp_value = tokens[temp_i]
                    if temp_value == '=>':
                        found_arrow = True
                        break
                    elif temp_value == '(':
                        paren_depth += 1
                    elif temp_value == ')':
                        paren_depth -= 1
                        # After closing paren, look for TypeScript return type annotation
                        if paren_depth == 0:
                            type_start = temp_i + 1
                            while type_start < len(tokens) and tokens[type_start][0] in (Whitespace,):
                                type_start += 1
                            if type_start < len(tokens) and tokens[type_start][1] == ':':
                                # Collect return type annotation
                                type_start += 1
                                while type_start < len(tokens) and tokens[type_start][1] != '=>':
                                    if tokens[type_start][0] not in (Whitespace,):
                                        type_annotation += tokens[type_start][1]
                                    type_start += 1
                    temp_i += 1
                break
            elif temp_value == '(':
                paren_depth += 1
            elif temp_value == ')':
                paren_depth -= 1
            temp_i += 1
        
        if found_arrow and potential_name:
            function_name = potential_name
            logging.debug(f"Found TypeScript arrow function: {function_name}")
            access_modifier = ' '.join(extra_modifiers) if extra_modifiers else None
            return_type = type_annotation.strip() if type_annotation else None
            return self._extract_typescript_arrow_function_parameters(tokens, i, function_name, access_modifier, return_type)
        
        return False, None, None, i, None, None

    def _extract_typescript_method_parameters(self, tokens, i, function_name, start_idx, access_modifiers, is_interface_method, is_abstract):
        """
        Extract parameters from TypeScript method definitions with type annotations.
        Handles: generics, return types, optional parameters, rest parameters.
        """
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = None
        
        # Skip over TypeScript generic type parameters (e.g., <T, U extends Base>)
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '<':
                # Skip over generic type parameters with constraints
                angle_count = 1
                i += 1
                while i < len(tokens) and angle_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '<':
                            angle_count += 1
                        elif value == '>':
                            angle_count -= 1
                    i += 1
                break
            elif ttype == Punctuation and value == '(':
                break
            elif ttype not in (Whitespace,):
                i += 1
                if i >= len(tokens):
                    break
            else:
                i += 1

        # Extract parameters with TypeScript type annotations
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found method signature, extract parameters
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

                # Extract parameter string with TypeScript types
                parameters = ''.join(token[1] for token in param_tokens).strip()
                parameters = ' '.join(parameters.split())

                # Look for TypeScript return type annotation (: ReturnType)
                return_type_tokens = []
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Punctuation and value == ':':
                        # Found return type annotation
                        i += 1
                        while i < len(tokens) and tokens[i][0] in (Whitespace,):
                            i += 1
                        
                        # Collect return type tokens until {, ;, or =>
                        while i < len(tokens):
                            ttype, value = tokens[i]
                            if value in ('{', ';', '=>') or value == '\n':
                                break
                            return_type_tokens.append((ttype, value))
                            i += 1
                        
                        if return_type_tokens:
                            return_type = ''.join(token[1] for token in return_type_tokens).strip()
                            return_type = ' '.join(return_type.split())
                        break
                    elif value in ('{', ';', '=>') or value == '\n':
                        break
                    i += 1

                # Add TypeScript-specific information to access modifier
                ts_info = []
                if is_interface_method:
                    ts_info.append('interface')
                if is_abstract:
                    ts_info.append('abstract')
                
                if ts_info:
                    if access_modifier:
                        access_modifier = ' '.join(ts_info) + ' ' + access_modifier
                    else:
                        access_modifier = ' '.join(ts_info)

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_typescript_arrow_function_parameters(self, tokens, start_i, function_name, access_modifier, return_type):
        """
        Extract parameters from TypeScript arrow function with type annotations.
        """
        # Similar to JavaScript but with TypeScript type handling
        temp_i = start_i + 1  # Skip past const/let/var
        while temp_i < len(tokens):
            temp_ttype, temp_value = tokens[temp_i]
            if temp_value == '=':
                temp_i += 1
                while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                    temp_i += 1
                
                # Look for parameter pattern with TypeScript types
                if temp_i < len(tokens) and tokens[temp_i][1] == '(':
                    # Extract parameters from parentheses with types
                    paren_count = 1
                    temp_i += 1
                    param_tokens = []
                    
                    while temp_i < len(tokens) and paren_count > 0:
                        temp_ttype, temp_value = tokens[temp_i]
                        if temp_value == '(':
                            paren_count += 1
                        elif temp_value == ')':
                            paren_count -= 1
                        
                        if paren_count > 0:
                            param_tokens.append((temp_ttype, temp_value))
                        temp_i += 1
                    
                    parameters = ''.join(token[1] for token in param_tokens).strip()
                    parameters = ' '.join(parameters.split())
                    
                    # Look for the arrow and return type
                    while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                        temp_i += 1
                        
                    # TypeScript arrow functions might have return type before =>
                    if temp_i < len(tokens) and tokens[temp_i][1] == ':':
                        # Extract return type
                        temp_i += 1
                        return_type_tokens = []
                        while temp_i < len(tokens) and tokens[temp_i][1] != '=>':
                            if tokens[temp_i][0] not in (Whitespace,):
                                return_type_tokens.append(tokens[temp_i])
                            temp_i += 1
                        if return_type_tokens:
                            return_type = ''.join(token[1] for token in return_type_tokens).strip()
                    
                    if temp_i < len(tokens) and tokens[temp_i][1] == '=>':
                        return True, function_name, parameters, temp_i, access_modifier, return_type
                else:
                    # Single parameter without parentheses (less common in TypeScript)
                    param_start = temp_i
                    while temp_i < len(tokens) and tokens[temp_i][1] != '=>':
                        temp_i += 1
                    if temp_i < len(tokens):
                        param_tokens = tokens[param_start:temp_i]
                        parameters = ''.join(token[1] for token in param_tokens).strip()
                        parameters = ' '.join(parameters.split())
                        return True, function_name, parameters, temp_i, access_modifier, return_type
                break
            temp_i += 1
        
        return False, None, None, start_i, None, None

    def _extract_swift_function_declaration(self, tokens, i, access_modifiers):
        """
        Extract Swift function declaration: func name(params) -> ReturnType
        """
        # Skip 'func' keyword
        i += 1
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1
        
        if i < len(tokens):
            next_ttype, next_value = tokens[i]
            if next_ttype in (Name.Function, Name.Other, Name):
                function_name = next_value
                logging.debug(f"Found Swift function definition: {function_name}")
                i += 1
                return self._extract_swift_function_parameters(tokens, i, function_name, i, access_modifiers)
        
        return False, None, None, i, None, None

    def _extract_swift_function_parameters(self, tokens, i, function_name, start_idx, access_modifiers):
        """
        Extract parameters from Swift function definitions.
        Handles: parameter labels, default values, variadic parameters, inout parameters, return types.
        """
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = None
        
        # Skip over any generic type parameters (e.g., <T>)
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '<':
                # Skip over generic type parameters
                angle_count = 1
                i += 1
                while i < len(tokens) and angle_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '<':
                            angle_count += 1
                        elif value == '>':
                            angle_count -= 1
                    i += 1
                break
            elif ttype == Punctuation and value == '(':
                break
            elif ttype not in (Whitespace,):
                # Skip over other tokens until we find ( or <
                i += 1
                if i >= len(tokens):
                    break
            else:
                i += 1

        # Extract parameters
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
                parameters = ' '.join(parameters.split())

                # Look for Swift return type annotation (-> ReturnType)
                return_type_tokens = []
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Punctuation and value == '-':
                        # Check if this is followed by >
                        if i + 1 < len(tokens) and tokens[i + 1][1] == '>':
                            # Found -> return type annotation
                            i += 2  # Skip ->
                            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                                i += 1
                            
                            # Collect return type tokens until { or where
                            while i < len(tokens):
                                ttype, value = tokens[i]
                                if value in ('{', 'where') or value == '\n':
                                    break
                                return_type_tokens.append((ttype, value))
                                i += 1
                            
                            if return_type_tokens:
                                return_type = ''.join(token[1] for token in return_type_tokens).strip()
                                return_type = ' '.join(return_type.split())
                            break
                    elif value in ('{', 'where') or value == '\n':
                        break
                    i += 1

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_swift_initializer_parameters(self, tokens, i, function_name, start_idx, access_modifiers):
        """
        Extract Swift initializer parameters: init(params)
        """
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        
        # Initializers don't have explicit return types (they return Self)
        return_type = "Self"
        
        # Look for opening parenthesis
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found initializer signature, extract parameters
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

                    if paren_count > 0:
                        param_tokens.append((ttype, value))

                    i += 1

                # Extract parameter string
                parameters = ''.join(token[1] for token in param_tokens).strip()
                parameters = ' '.join(parameters.split())

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_swift_property_or_subscript(self, tokens, i, access_modifiers, keyword):
        """
        Extract Swift computed properties: var name: Type { get set }
        """
        # Skip var/let keyword
        i += 1
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1
        
        if i < len(tokens):
            ttype, value = tokens[i]
            if ttype in (Name.Other, Name, Name.Property, Name.Variable):
                property_name = value
                i += 1
                
                # Look for type annotation and computed property braces
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Punctuation and value == '{':
                        # Found computed property
                        logging.debug(f"Found Swift computed property: {property_name}")
                        
                        # Extract the property accessors
                        brace_count = 1
                        i += 1
                        accessor_tokens = []
                        
                        while i < len(tokens) and brace_count > 0:
                            ttype, value = tokens[i]
                            if ttype == Punctuation:
                                if value == '{':
                                    brace_count += 1
                                elif value == '}':
                                    brace_count -= 1
                            
                            if brace_count > 0:
                                accessor_tokens.append((ttype, value))
                            i += 1
                        
                        # Extract accessor information
                        accessors = ''.join(token[1] for token in accessor_tokens).strip()
                        accessors = ' '.join(accessors.split())
                        
                        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
                        parameters = f"{{ {accessors} }}" if accessors else "{ }"
                        
                        return True, property_name, parameters, i, access_modifier, None
                    i += 1
        
        return False, None, None, i, None, None

    def _extract_swift_subscript_parameters(self, tokens, i, function_name, start_idx, access_modifiers):
        """
        Extract Swift subscript parameters: subscript(index: Int) -> Element
        """
        access_modifier = ' '.join(access_modifiers) if access_modifiers else None
        return_type = None
        
        # Look for opening parenthesis
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '(':
                # Found subscript signature, extract parameters
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

                    if paren_count > 0:
                        param_tokens.append((ttype, value))

                    i += 1

                # Extract parameter string
                parameters = ''.join(token[1] for token in param_tokens).strip()
                parameters = ' '.join(parameters.split())

                # Look for return type (-> ReturnType)
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Punctuation and value == '-':
                        if i + 1 < len(tokens) and tokens[i + 1][1] == '>':
                            i += 2
                            while i < len(tokens) and tokens[i][0] in (Whitespace,):
                                i += 1
                            
                            return_type_tokens = []
                            while i < len(tokens):
                                ttype, value = tokens[i]
                                if value in ('{', 'where') or value == '\n':
                                    break
                                return_type_tokens.append((ttype, value))
                                i += 1
                            
                            if return_type_tokens:
                                return_type = ''.join(token[1] for token in return_type_tokens).strip()
                                return_type = ' '.join(return_type.split())
                            break
                    elif value in ('{', 'where') or value == '\n':
                        break
                    i += 1

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_function_parameters(self, tokens, i, function_name, start_idx, access_modifier=None, return_type=None):
        """
        Common parameter extraction logic for traditional function definitions.
        """
        # Look forward for return type annotations (like Python type hints: -> int)
        temp_i = i
        while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
            temp_i += 1

        # Check for opening paren first
        if temp_i < len(tokens) and tokens[temp_i][1] == '(':
            # Skip to after the closing paren to look for return type
            paren_depth = 1
            temp_i += 1
            while temp_i < len(tokens) and paren_depth > 0:
                if tokens[temp_i][1] == '(':
                    paren_depth += 1
                elif tokens[temp_i][1] == ')':
                    paren_depth -= 1
                temp_i += 1

            # Now look for return type annotation (-> Type)
            while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                temp_i += 1

            if temp_i < len(tokens) - 1:
                if tokens[temp_i][1] == '-' and temp_i + 1 < len(tokens) and tokens[temp_i + 1][1] == '>':
                    # Found -> annotation, get the return type
                    temp_i += 2
                    while temp_i < len(tokens) and tokens[temp_i][0] in (Whitespace,):
                        temp_i += 1
                    if temp_i < len(tokens) and tokens[temp_i][0] in (Name, Name.Builtin, Keyword.Type):
                        if not return_type:  # Don't override if already found
                            return_type = tokens[temp_i][1]

        # Look for opening parenthesis to extract parameters
        # First, skip over any generic type parameters (e.g., <T>)
        while i < len(tokens):
            ttype, value = tokens[i]
            if ttype == Punctuation and value == '<':
                # Skip over generic type parameters
                angle_count = 1
                i += 1
                while i < len(tokens) and angle_count > 0:
                    ttype, value = tokens[i]
                    if ttype == Punctuation:
                        if value == '<':
                            angle_count += 1
                        elif value == '>':
                            angle_count -= 1
                    i += 1
                break
            elif ttype == Punctuation and value == '(':
                break
            elif ttype not in (Whitespace,):
                # Skip over other tokens until we find ( or <
                i += 1
                if i >= len(tokens):
                    break
            else:
                i += 1

        # Now look for the opening parenthesis
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

                # Look for TypeScript return type annotation (: Type)
                return_type_tokens = []
                while i < len(tokens):
                    ttype, value = tokens[i]
                    if ttype == Punctuation and value == ':':
                        # Found return type annotation, collect tokens until { or ;
                        i += 1
                        while i < len(tokens):
                            ttype, value = tokens[i]
                            if value in ('{', ';') or value == '\n':
                                break
                            return_type_tokens.append((ttype, value))
                            i += 1
                        
                        if return_type_tokens:
                            return_type = ''.join(token[1] for token in return_type_tokens).strip()
                            return_type = ' '.join(return_type.split())
                        
                        return True, function_name, parameters, i, access_modifier, return_type
                    elif value in ('{', ';') or value == '\n':
                        return True, function_name, parameters, i, access_modifier, return_type
                    i += 1

                return True, function_name, parameters, i, access_modifier, return_type
            elif ttype not in (Whitespace,):
                break
            i += 1

        return False, None, None, start_idx, None, None

    def _extract_ruby_function_parameters(self, tokens, i, function_name, start_idx, access_modifier=None, return_type=None):
        """
        Ruby-specific parameter extraction that handles optional parentheses.
        Ruby allows: def method_name, def method_name(), def method_name(params)
        """
        # Skip any whitespace after the function name
        while i < len(tokens) and tokens[i][0] in (Whitespace,):
            i += 1
        
        # Check if there are parentheses
        if i < len(tokens) and tokens[i][1] == '(':
            # Has parentheses - extract parameters normally
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
            
            return True, function_name, parameters, i, access_modifier, return_type
        else:
            # No parentheses - Ruby method without parameters or with implicit parameters
            # Look ahead to see if there are parameters without parentheses
            param_tokens = []
            
            # Ruby can have parameters without parentheses like: def greet name, age
            # Continue collecting tokens until we hit a newline or Ruby method body indicators
            while i < len(tokens):
                ttype, value = tokens[i]
                
                # Stop at newlines - this indicates end of method signature line
                if '\n' in value:
                    break
                
                # Stop at semicolons
                if value == ';':
                    break
                
                # Stop at comments
                if ttype in (Comment, Comment.Single, Comment.Multiline):
                    break
                
                # Stop at Ruby keywords that indicate method body or control structures
                if ttype == Keyword and value in ('end', 'do', 'if', 'unless', 'while', 'until', 'case', 'when', 'else', 'elsif', 'rescue', 'ensure', 'class', 'module', 'def'):
                    break
                
                # For Ruby, also stop at common statement patterns that indicate method body
                if ttype in (Name, Name.Builtin) and value in ('puts', 'print', 'p', 'return', 'raise', 'require', 'include', 'extend'):
                    break
                
                # Collect parameter tokens
                param_tokens.append((ttype, value))
                i += 1
            
            # Extract parameter string
            parameters = ''.join(token[1] for token in param_tokens).strip()
            # Clean up parameters - remove newlines and extra spaces
            parameters = ' '.join(parameters.split())
            
            # If we found parameters, format them appropriately
            if parameters:
                return True, function_name, parameters, i, access_modifier, return_type
            else:
                # No parameters
                return True, function_name, "", i, access_modifier, return_type

    def _format_function_signature(self, tokens, start_idx, end_idx, function_name):
        """
        Format a function signature with special Markdown highlighting.
        """
        signature_tokens = tokens[start_idx:end_idx]
        signature_text = ''.join(token[1] for token in signature_tokens)

        return f"**🔹 {function_name}** {signature_text.strip()}\n"

    def format_unencoded(self, tokensource, outfile):
        """
        Format the token stream and write to outfile.
        """
        # Convert token source to list for multiple passes
        tokens = list(tokensource)

        # Write document header if full document requested
        if self.options.get('full'):
            title = self.options.get('title', 'Code')
            outfile.write(f'# {title}\n\n')
            outfile.write('Generated by Pygments Markdown Formatter\n\n')

        # Pre-process to find function signatures if highlighting is enabled
        function_signatures = []
        if self.highlight_functions:
            i = 0
            while i < len(tokens):
                is_func, func_name, parameters, end_idx, access_modifier, return_type = self._is_function_definition(tokens, i)
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
                        'access_modifier': access_modifier,
                        'return_type': return_type,
                        'start_idx': i,
                        'end_idx': end_idx,
                        'line_num': line_num,
                        'signature': ''.join(token[1] for token in tokens[i:end_idx])
                    })
                    i = end_idx
                else:
                    i += 1

        # Write function signatures summary if any found
        if function_signatures:
            # outfile.write('## 📚 Functions Found\n\n')
            for func in function_signatures:
                # Build the display string with access modifier and return type
                signature_parts = []

                if func['access_modifier']:
                    signature_parts.append(f"{func['access_modifier']}")

                # TODO: we don't currently get all return types so ignore for now
                # if func['return_type']:
                #     signature_parts.append(f"{func['return_type']}")

                # signature_parts.append(f"**{func['name']}**")
                signature_parts.append(f"{func['name']}")

                params_display = f"({func['parameters']})" if func['parameters'] else "()"
                signature_parts.append(params_display)

                signature_display = ' '.join(signature_parts)

                # do we show line numbers?
                if self.linenos:
                    outfile.write(f'- {signature_display} (line {func["line_num"]})\n')
                else:
                    outfile.write(f'{signature_display}\n')

            outfile.write('\n')

        # This entire IF block is to output the entire document in fenced code blocks
        # we will not use this for just getting signatures
        if self.options.get('full'):
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
        else:
            logging.debug('SKIPPED OUTPUTTING FILE CONTENTS - FULL DOCUMENT MODE IS OFF')

        # Add highlighted lines information as comments if specified
        if self.hl_lines:
            outfile.write('\n<!-- Highlighted lines: ')
            outfile.write(', '.join(map(str, sorted(self.hl_lines))))
            outfile.write(' -->\n')

    def _write_line(self, outfile, line_parts, line_number, tokens=None, token_idx=None):
        """
        Write a single line to the output file.
        """
        line_content = ''.join(line_parts)

        # Check if this line contains a function definition for emphasis style
        is_function_line = False
        function_name = ""

        if (self.highlight_functions and tokens and token_idx is not None):
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
__all__ = ['TLDRFormatter']
