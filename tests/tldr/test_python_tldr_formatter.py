"""
    Python TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Python-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

import pytest

from pygments_tldr import highlight
from pygments_tldr.lexers.python import PythonLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Python code with known number of functions
PYTHON_TEST_CODE = """
#!/usr/bin/env python3
'''
Sample Python module for testing function detection
'''
import os
import sys
from typing import List, Dict, Optional, Union
from abc import ABC, abstractmethod


class TestClass:
    \"\"\"Sample class for testing method detection\"\"\"
    
    def __init__(self, name: str = "default"):
        \"\"\"Constructor method\"\"\"
        self.name = name
        self._value = 0
    
    def get_name(self) -> str:
        \"\"\"Getter method with type hint\"\"\"
        return self.name
    
    def set_name(self, name: str) -> None:
        \"\"\"Setter method with type hints\"\"\"
        self.name = name
    
    @property
    def value(self) -> int:
        \"\"\"Property getter\"\"\"
        return self._value
    
    @value.setter
    def value(self, val: int) -> None:
        \"\"\"Property setter\"\"\"
        self._value = val
    
    @staticmethod
    def static_method(x: int, y: int) -> int:
        \"\"\"Static method with type hints\"\"\"
        return x + y
    
    @classmethod
    def class_method(cls, name: str):
        \"\"\"Class method\"\"\"
        return cls(name)
    
    def _private_method(self, data: List[str]) -> Dict[str, int]:
        \"\"\"Private method with complex type hints\"\"\"
        return {item: len(item) for item in data}
    
    async def async_method(self, delay: float = 1.0) -> str:
        \"\"\"Async method\"\"\"
        import asyncio
        await asyncio.sleep(delay)
        return "completed"
    
    def method_with_defaults(self, x: int = 10, y: str = "default") -> tuple:
        \"\"\"Method with default parameters\"\"\"
        return (x, y)


def standalone_function(param1: str, param2: Optional[int] = None) -> bool:
    \"\"\"Standalone function with type hints\"\"\"
    return param1 is not None and param2 is not None


async def async_function(data: List[Dict[str, Union[str, int]]]) -> None:
    \"\"\"Async standalone function\"\"\"
    for item in data:
        print(item)


def simple_function():
    \"\"\"Simple function without type hints\"\"\"
    pass


def function_with_args(*args, **kwargs):
    \"\"\"Function with variable arguments\"\"\"
    return args, kwargs


def decorated_function():
    \"\"\"Function that might be decorated\"\"\"
    return "decorated"


@abstractmethod
def abstract_function(self) -> str:
    \"\"\"Abstract method\"\"\"
    pass


def nested_function_container():
    \"\"\"Function containing nested function\"\"\"
    def nested_function(x):
        \"\"\"Nested function\"\"\"
        return x * 2
    
    return nested_function(5)


# Lambda functions (should not be detected as regular functions)
lambda_func = lambda x: x + 1
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    "__init__",
    "get_name",
    "set_name", 
    "value",  # property getter
    "value",  # property setter (might be detected separately)
    "static_method",
    "class_method",
    "_private_method",
    "async_method",
    "method_with_defaults",
    "standalone_function",
    "async_function",
    "simple_function",
    "function_with_args",
    "decorated_function",
    "abstract_function",
    "nested_function_container",
    "nested_function"  # nested functions might or might not be detected
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestPythonTLDRFormatter:
    """Test class for Python-specific function detection in TLDR formatter."""
    
    def test_python_function_detection_via_highlight_api(self):
        """Test Python function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        
        # Use the highlight() function from __init__.py
        result = highlight(PYTHON_TEST_CODE, lexer, formatter)
        
        # Basic assertions
        assert result is not None
        assert isinstance(result, str)
        
        # Count detected functions by looking for function names in output
        detected_functions = []
        lines = result.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                # Look for function names in the output
                for expected_func in EXPECTED_FUNCTIONS:
                    if expected_func in line and expected_func not in detected_functions:
                        detected_functions.append(expected_func)
        
        # Log the results for debugging
        logging.debug(f"TLDR Formatter output:\n{result}")
        logging.debug(f"Detected functions: {detected_functions}")
        logging.debug(f"Expected functions: {EXPECTED_FUNCTIONS}")
        
        # Verify we detected functions
        assert len(detected_functions) > 0, f"No functions detected in output: {result}"
        
        # Verify we detected most expected functions (allowing some variance in detection logic)
        detection_ratio = len(detected_functions) / EXPECTED_FUNCTION_COUNT
        assert detection_ratio >= 0.4, f"Detection ratio too low: {detection_ratio:.2f} ({len(detected_functions)}/{EXPECTED_FUNCTION_COUNT})"
        
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Python functions")
    
    def test_python_simple_function_detection(self):
        """Test detection of simple Python functions"""
        simple_code = """
def hello_world():
    print("Hello, World!")

def add_numbers(a, b):
    return a + b

class SimpleClass:
    def method(self):
        pass
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["hello_world", "add_numbers", "method"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_python_type_hints_detection(self):
        """Test detection of Python functions with type hints"""
        type_hints_code = """
from typing import List, Dict, Optional

def process_data(items: List[str]) -> Dict[str, int]:
    return {item: len(item) for item in items}

def optional_param(value: Optional[int] = None) -> bool:
    return value is not None

async def async_with_types(data: List[Dict[str, str]]) -> None:
    pass
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(type_hints_code, lexer, formatter)
        
        assert result is not None
        
        # Check for type-hinted function detection
        type_hint_functions = ["process_data", "optional_param", "async_with_types"]
        detected_type_hints = [name for name in type_hint_functions if name in result]
        
        assert len(detected_type_hints) > 0, f"No type-hinted functions detected: {result}"
        print(f"Detected type-hinted functions: {detected_type_hints}")
    
    def test_python_class_methods_detection(self):
        """Test detection of Python class methods"""
        class_methods_code = """
class TestMethods:
    def __init__(self, value):
        self.value = value
    
    @staticmethod
    def static_method():
        return "static"
    
    @classmethod
    def class_method(cls):
        return cls(0)
    
    @property
    def prop(self):
        return self.value
    
    def regular_method(self):
        return self.value
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(class_methods_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["__init__", "static_method", "class_method", "prop", "regular_method"]
        detected_class_methods = [name for name in class_methods if name in result]
        
        assert len(detected_class_methods) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class_methods}")
    
    def test_python_async_function_detection(self):
        """Test detection of Python async functions"""
        async_code = """
import asyncio

async def simple_async():
    await asyncio.sleep(1)

async def async_with_params(delay: float, message: str) -> str:
    await asyncio.sleep(delay)
    return message

class AsyncClass:
    async def async_method(self):
        return "async method"
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async function detection
        async_functions = ["simple_async", "async_with_params", "async_method"]
        detected_async = [name for name in async_functions if name in result]
        
        assert len(detected_async) > 0, f"No async functions detected: {result}"
        print(f"Detected async functions: {detected_async}")
    
    def test_python_language_detection(self):
        """Test that Python language is properly detected"""
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        
        # Verify language detection
        assert formatter._detect_language() == 'python', "Python language not properly detected"
    
    def test_python_decorator_functions(self):
        """Test detection of decorated Python functions"""
        decorator_code = """
def my_decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def decorated_function():
    return "decorated"

@staticmethod
def static_decorated():
    return "static decorated"

@property
def property_method(self):
    return self._value
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(decorator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for decorator and decorated function detection
        decorator_functions = ["my_decorator", "wrapper", "decorated_function", "static_decorated", "property_method"]
        detected_decorators = [name for name in decorator_functions if name in result]
        
        assert len(detected_decorators) > 0, f"No decorated functions detected: {result}"
        print(f"Detected decorated functions: {detected_decorators}")
    
    def test_python_nested_functions(self):
        """Test detection of nested Python functions"""
        nested_code = """
def outer_function(x):
    def inner_function(y):
        return x + y
    
    def another_inner(z):
        def deeply_nested():
            return z * 2
        return deeply_nested()
    
    return inner_function, another_inner
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(nested_code, lexer, formatter)
        
        assert result is not None
        
        # Check for nested function detection
        nested_functions = ["outer_function", "inner_function", "another_inner", "deeply_nested"]
        detected_nested = [name for name in nested_functions if name in result]
        
        # At least the outer function should be detected
        assert len(detected_nested) > 0, f"No nested functions detected: {result}"
        print(f"Detected nested functions: {detected_nested}")
    
    def test_empty_python_file(self):
        """Test handling of empty Python file"""
        empty_code = """
# Just comments and imports
import os
import sys

# No functions defined
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)
    
    def test_python_magic_methods(self):
        """Test detection of Python magic methods"""
        magic_methods_code = """
class MagicClass:
    def __init__(self, value):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"MagicClass({self.value})"
    
    def __len__(self):
        return len(str(self.value))
    
    def __getitem__(self, key):
        return str(self.value)[key]
    
    def __setitem__(self, key, value):
        pass
"""
        
        lexer = PythonLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='python')
        result = highlight(magic_methods_code, lexer, formatter)
        
        assert result is not None
        
        # Check for magic method detection
        magic_methods = ["__init__", "__str__", "__repr__", "__len__", "__getitem__", "__setitem__"]
        detected_magic = [name for name in magic_methods if name in result]
        
        assert len(detected_magic) > 0, f"No magic methods detected: {result}"
        print(f"Detected magic methods: {detected_magic}")


if __name__ == "__main__":
    # Run a quick test
    test = TestPythonTLDRFormatter()
    test.test_python_function_detection_via_highlight_api()
    print("Python TLDR formatter test completed successfully!")