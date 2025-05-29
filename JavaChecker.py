import re

'''
From Google Gemini, this should be pretty good at guessing if a line of Java code is the start of a method declaration.
'''
def is_java_method_start(line: str) -> bool:
    """
    Guesses if a single line of Java code is the start of a method declaration.

    Args:
        line: A string representing a single line of Java code.

    Returns:
        True if the line is likely the start of a method, False otherwise.
    """
    line = line.strip()

    # 1. Ignore empty lines or comments
    if not line or line.startswith("//") or line.startswith("/*") or line.startswith("*"):
        return False

    # 2. Quick checks for keywords that are definitively NOT method starts if they begin the line
    # (excluding annotations which can precede a method)
    non_method_keywords_prefix = [
        "class ", "interface ", "enum ", # Add space to avoid matching method names
        "import ", "package "
    ]
    for kw in non_method_keywords_prefix:
        if line.startswith(kw):
            return False

    # 3. Quick checks for common statement keywords (if they appear early and are not part of a name)
    #    This helps filter out lines from within a method body.
    statement_keywords = [
        "if ", "if(", "for ", "for(", "while ", "while(", "switch ", "switch(",
        "try ", "try{", "catch ", "catch(", "finally ", "finally{",
        "return ", "throw ", "new ", "super(", "this(" # super() and this() are constructor calls
    ]
    # Check if line starts with these, indicating it's likely not a method declaration itself.
    for kw in statement_keywords:
        if line.startswith(kw):
            # Further check: make sure it's not a method name that happens to start with this.
            # e.g. "ifthenelse()" is a valid method name, but "if (condition)" is not.
            # A simple check is if the keyword is followed by typical statement syntax or is a prefix.
            if kw.endswith("(") or kw.endswith("{") or ' ' in kw: # kw itself contains typical follow-up
                return False
            # For keywords like "return ", if line is "return something;", it's not a method def.
            # The regex below is the main checker, this is just a fast path for common cases.

    # 4. Regex for a Java method signature
    # Components:
    # - Optional annotations: @Override, @Nullable, etc.
    # - Modifiers: public, static, abstract, final, etc. (zero or more)
    # - Method-specific generic type: <T>, <T extends Something> (optional)
    # - Return type: void, int, String, List<String>, String[], etc.
    # - Method name: valid Java identifier
    # - Parameters: (...) (content inside can be anything for this check)
    # - Throws clause: throws ExceptionType (optional)
    # - Ending: optionally ends with { or ;

    annotations_pattern = r"(?:@\w+(?:\([^)]*\))?\s+)*" # @Override, @Deprecated("reason")

    modifiers_pattern = r"(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)\s+)*"

    method_generics_pattern = r"(?:<\s*[\w\s,<>?&extends]+\s*>\s+)?" # e.g., <T>, <T extends Collection<?>>

    # Return type: accounts for primitives, class names, qualified names, generics, and arrays
    type_name_start_char = r"[a-zA-Z_$]" # Java identifiers can start with $, _
    type_name_chars = r"[\w$.<>\[\]]"    # Subsequent chars in type (incl. generics, arrays, qualified names)
    return_type_pattern = rf"(void|{type_name_start_char}{type_name_chars}*)" # e.g. void, int, String, com.example.MyClass, List<String>, int[]

    method_name_pattern = rf"({type_name_start_char}\w*)" # Standard Java identifier

    parameters_pattern = r"\(\s*(?:[^)]*)\s*\)" # Matches anything (or nothing) within parentheses

    throws_pattern = r"(?:\s*throws\s+[\w\s,.<>\[\]]+)?" # e.g., throws IOException, MyException

    # The regex will try to match the core signature.
    # How it ends (with '{', ';', or nothing specific) will be checked after a successful match.
    java_method_regex_str = (
            r"^\s*" +
            annotations_pattern +
            modifiers_pattern +
            method_generics_pattern +
            rf"({return_type_pattern})\s+" +   # Capture group 1: Full return type
            rf"{method_name_pattern}\s*" +     # Capture group for method name (implicit from method_name_pattern)
            parameters_pattern +
            throws_pattern +
            r"\s*(\{?|;?)\s*$" # Capture group for optional ending char '{' or ';'
    )
    java_method_regex = re.compile(java_method_regex_str)

    match = java_method_regex.match(line)

    if match:
        # To determine if 'abstract' or 'native' is present, check before the first parenthesis
        # This is a simpler way than trying to parse specific modifier groups from the regex.
        signature_before_params = line.split('(', 1)[0]

        is_abstract = "abstract " in signature_before_params
        is_native = "native " in signature_before_params

        ends_with_brace = line.rstrip().endswith('{')
        ends_with_semicolon = line.rstrip().endswith(';')

        # Constructor check: a constructor doesn't have a return type in its declaration.
        # Our regex currently requires a return type.
        # However, if ClassName is matched as return_type AND method_name, it's a constructor.
        # Example: "public MyClass(String name)" matches "MyClass" as return type and "MyClass" as name.
        # This is acceptable as constructors are a special kind of method.

        if is_abstract:
            # Abstract methods must not have an opening brace '{' on the same line.
            # They typically end with ';' or just the parameter list/throws clause.
            return not ends_with_brace

        if is_native:
            # Native methods must end with a semicolon and no body.
            return ends_with_semicolon and not ends_with_brace

        # For concrete methods or interface methods (which are non-abstract, non-native):
        # A line is a start of a method if:
        # 1. It ends with an opening brace '{'.
        # 2. It's a complete signature that doesn't end with ';' (implies '{' is on the next line).
        # 3. It's a complete signature that ends with ';' (implies an interface method declaration).

        if ends_with_brace: # e.g. public void foo() {
            return True

        if ends_with_semicolon: # e.g. public void foo(); (interface method)
            return True

        # If it doesn't end with brace and doesn't end with semicolon,
        # then it ends with ')' or a throws clause. This is a valid start for a method
        # whose body '{' is on the next line. E.g., public void foo()
        # or public void foo() throws SomeException
        if not ends_with_brace and not ends_with_semicolon:
            return True

        return False # Should be covered by conditions if match was successful

    # Rule out field declarations that might look a bit like methods but have assignment
    # e.g., "private final String name = "Default";"
    # The regex should generally not match these because of the lack of '()' after name before '=',
    # or the presence of '=' before '('.
    if '=' in line and '(' not in line.split('=')[0]: # Basic check for assignment not in parameters
        # Check if it looks like "Type var = ...;" more definitively
        if re.match(r"^\s*(?:(?:public|private|protected|static|final)\s+)*[\w.<>\[\]]+\s+[\w\[\]]+\s*=\s*.*;", line):
            return False
        if re.match(r"^\s*[\w.<>\[\]]+\s+[\w\[\]]+\s*=\s*.*;", line): # No modifiers
            return False


    return False # No regex match and other checks failed