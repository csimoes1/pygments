#!/usr/bin/env python3
"""
Simple file test script for TLDR formatter function extraction.

This script takes a filename as input and uses the TLDRFormatter to extract
and display all the functions it finds in the file.

Usage:
    python simple_file_test.py <filename>
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the Python path so we can import pygments_tldr
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from pygments_tldr import highlight
    from pygments_tldr.lexers import get_lexer_for_filename
    from pygments_tldr.formatters.tldr import TLDRFormatter
except ImportError as e:
    print(f"Error importing pygments_tldr: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def extract_functions_from_file(filename):
    """Extract functions from a file using TLDRFormatter."""
    
    # Check if file exists
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' does not exist")
        return None
    
    # Read the file content
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        print(f"Error reading file '{filename}': {e}")
        return None
    
    # Get appropriate lexer for the file
    try:
        lexer = get_lexer_for_filename(filename)
        print(f"Using lexer: {lexer.__class__.__name__}")
    except Exception as e:
        print(f"Error getting lexer for file '{filename}': {e}")
        return None
    
    # Determine language for TLDR formatter
    lexer_name = lexer.__class__.__name__.lower()
    if 'typescript' in lexer_name:
        lang = 'typescript'
    elif 'javascript' in lexer_name:
        lang = 'javascript'
    elif 'python' in lexer_name:
        lang = 'python'
    elif 'java' in lexer_name:
        lang = 'java'
    elif 'csharp' in lexer_name:
        lang = 'csharp'
    elif 'cpp' in lexer_name or 'c++' in lexer_name:
        lang = 'cpp'
    elif 'c' in lexer_name:
        lang = 'c'
    elif 'go' in lexer_name:
        lang = 'go'
    elif 'rust' in lexer_name:
        lang = 'rust'
    elif 'ruby' in lexer_name:
        lang = 'ruby'
    elif 'php' in lexer_name:
        lang = 'php'
    elif 'swift' in lexer_name:
        lang = 'swift'
    else:
        lang = 'generic'
    
    print(f"Using language: {lang}")
    
    # Create TLDR formatter
    formatter = TLDRFormatter(highlight_functions=True, lang=lang)
    
    # Extract functions using highlight
    try:
        result = highlight(code, lexer, formatter)
        return result
    except Exception as e:
        print(f"Error highlighting code: {e}")
        return None


def main():
    """Main function to process command line arguments and extract functions."""
    
    if len(sys.argv) != 2:
        print("Usage: python simple_file_test.py <filename>")
        print("Example: python simple_file_test.py helper.ts")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    print(f"Extracting functions from: {filename}")
    print("=" * 50)
    
    result = extract_functions_from_file(filename)
    
    if result is not None:
        print("\nExtracted functions:")
        print("-" * 30)
        if result.strip():
            print(result)
        else:
            print("No functions found or empty result")
    else:
        print("Failed to extract functions")


if __name__ == "__main__":
    main()