"""
    JavaScript TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test JavaScript-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.javascript import JavascriptLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample JavaScript code with known number of functions
JAVASCRIPT_TEST_CODE = """
// JavaScript sample code for testing function detection
'use strict';

// Regular function declarations
function simpleFunction() {
    console.log('Hello, World!');
}

function functionWithParams(a, b, c) {
    return a + b + c;
}

function functionWithDefaults(x = 10, y = 'default') {
    return { x, y };
}

// Arrow functions
const arrowFunction = () => {
    return 'arrow function';
};

const arrowWithParams = (name, age) => {
    return `${name} is ${age} years old`;
};

const arrowSingleParam = param => param * 2;

const arrowWithDefaults = (a = 1, b = 2) => a + b;

// Function expressions
const functionExpression = function() {
    return 'function expression';
};

const namedFunctionExpression = function namedFunc() {
    return 'named function expression';
};

// Async functions
async function asyncFunction() {
    await new Promise(resolve => setTimeout(resolve, 1000));
    return 'async completed';
}

const asyncArrow = async () => {
    return await fetch('/api/data');
};

async function asyncWithParams(url, options = {}) {
    const response = await fetch(url, options);
    return response.json();
}

// Generator functions
function* generatorFunction() {
    yield 1;
    yield 2;
    yield 3;
}

function* generatorWithParams(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

// Class methods
class TestClass {
    constructor(name) {
        this.name = name;
    }
    
    // Instance methods
    getName() {
        return this.name;
    }
    
    setName(newName) {
        this.name = newName;
    }
    
    // Async method
    async fetchData() {
        return await fetch(`/api/users/${this.name}`);
    }
    
    // Static methods
    static createDefault() {
        return new TestClass('default');
    }
    
    static async validateUser(userData) {
        const isValid = await this.checkValidation(userData);
        return isValid;
    }
    
    // Private methods (modern JavaScript)
    #privateMethod() {
        return 'private';
    }
    
    // Getter and setter
    get displayName() {
        return `User: ${this.name}`;
    }
    
    set displayName(value) {
        this.name = value.replace('User: ', '');
    }
    
    // Method with complex parameters
    processData(data, callback = null, options = { async: true }) {
        if (callback) {
            return callback(data);
        }
        return data;
    }
}

// Object methods
const objectWithMethods = {
    property: 'value',
    
    method() {
        return this.property;
    },
    
    asyncMethod: async function() {
        return await this.method();
    },
    
    arrowMethod: () => {
        return 'arrow in object';
    },
    
    // Method shorthand
    shorthandMethod(param) {
        return param.toString();
    }
};

// Higher-order functions
function higherOrderFunction(callback) {
    return function(data) {
        return callback(data);
    };
}

const returnFunction = () => {
    return function innerFunction(x) {
        return x * 2;
    };
};

// IIFE (Immediately Invoked Function Expression)
(function iife() {
    console.log('IIFE executed');
})();

// Export functions (ES6 modules)
export function exportedFunction() {
    return 'exported';
}

export const exportedArrow = () => 'exported arrow';

export default function defaultExport() {
    return 'default export';
}

// Destructuring function parameters
function destructuringParams({ name, age, ...rest }) {
    return { name, age, rest };
}

// Rest parameters
function restParams(first, ...others) {
    return [first, ...others];
}

// Callback function patterns
function withCallback(data, callback) {
    setTimeout(() => callback(data), 100);
}

// Promise-based functions
function promiseFunction() {
    return new Promise((resolve, reject) => {
        setTimeout(() => resolve('resolved'), 1000);
    });
}

// Event handler function
function handleClick(event) {
    event.preventDefault();
    console.log('Button clicked');
}

// Recursive function
function factorial(n) {
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Regular function declarations
    "simpleFunction", "functionWithParams", "functionWithDefaults",
    # Arrow functions
    "arrowFunction", "arrowWithParams", "arrowSingleParam", "arrowWithDefaults",
    # Function expressions
    "functionExpression", "namedFunctionExpression", "namedFunc",
    # Async functions
    "asyncFunction", "asyncArrow", "asyncWithParams",
    # Generator functions
    "generatorFunction", "generatorWithParams",
    # Class constructor and methods
    "constructor", "getName", "setName", "fetchData", "createDefault", "validateUser",
    "displayName",  # getter/setter might be detected
    "processData",
    # Object methods
    "method", "asyncMethod", "arrowMethod", "shorthandMethod",
    # Higher-order functions
    "higherOrderFunction", "returnFunction", "innerFunction",
    # IIFE
    "iife",
    # Export functions
    "exportedFunction", "exportedArrow", "defaultExport",
    # Parameter patterns
    "destructuringParams", "restParams",
    # Callback patterns
    "withCallback", "promiseFunction", "handleClick",
    # Recursive function
    "factorial"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestJavaScriptTLDRFormatter:
    """Test class for JavaScript-specific function detection in TLDR formatter."""
    
    def test_javascript_function_detection_via_highlight_api(self):
        """Test JavaScript function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        
        # Use the highlight() function from __init__.py
        result = highlight(JAVASCRIPT_TEST_CODE, lexer, formatter)
        
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
        
        # Find missing functions
        missing_functions = [func for func in EXPECTED_FUNCTIONS if func not in detected_functions]
        
        # Log the results for debugging
        logging.debug(f"TLDR Formatter output:\n{result}")
        logging.debug(f"Detected functions: {detected_functions}")
        logging.debug(f"Expected functions: {EXPECTED_FUNCTIONS}")
        
        # Print detailed results
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} JavaScript functions")
        print(f"Detected functions: {detected_functions}")
        print(f"Missing functions: {missing_functions}")
        
        # Print basic debugging info for missing functions
        for missing_func in missing_functions:
            if missing_func in result:
                print(f"  ** {missing_func} IS in the output but not detected by search logic")
            else:
                print(f"  ** {missing_func} is NOT in the output")
        
        # Verify we detected functions
        assert len(detected_functions) > 0, f"No functions detected in output: {result}"
        
        # Verify we detected a reasonable number of expected functions
        detection_ratio = len(detected_functions) / EXPECTED_FUNCTION_COUNT
        assert detection_ratio >= 0.3, f"Detection ratio too low: {detection_ratio:.2f} ({len(detected_functions)}/{EXPECTED_FUNCTION_COUNT})"
    
    def test_javascript_simple_function_detection(self):
        """Test detection of simple JavaScript functions"""
        simple_code = """
function hello() {
    console.log('Hello');
}

const add = (a, b) => a + b;

function multiply(x, y) {
    return x * y;
}

class Calculator {
    calculate(operation) {
        return operation();
    }
}
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["hello", "add", "multiply", "calculate"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_javascript_arrow_functions_detection(self):
        """Test detection of JavaScript arrow functions"""
        arrow_code = """
const simple = () => 'hello';
const withParams = (x, y) => x + y;
const withBlock = (data) => {
    return data.map(item => item * 2);
};
const async = async () => await fetch('/api');
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(arrow_code, lexer, formatter)
        
        assert result is not None
        
        # Check for arrow function detection
        arrow_functions = ["simple", "withParams", "withBlock", "async"]
        detected_arrows = [name for name in arrow_functions if name in result]
        
        assert len(detected_arrows) > 0, f"No arrow functions detected: {result}"
        print(f"Detected arrow functions: {detected_arrows}")
    
    def test_javascript_class_methods_detection(self):
        """Test detection of JavaScript class methods"""
        class_code = """
class TestClass {
    constructor(value) {
        this.value = value;
    }
    
    getValue() {
        return this.value;
    }
    
    static create() {
        return new TestClass(0);
    }
    
    async asyncMethod() {
        return await Promise.resolve(this.value);
    }
    
    get computed() {
        return this.value * 2;
    }
    
    set computed(val) {
        this.value = val / 2;
    }
}
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(class_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["constructor", "getValue", "create", "asyncMethod", "computed"]
        detected_class_methods = [name for name in class_methods if name in result]
        
        assert len(detected_class_methods) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class_methods}")
    
    def test_javascript_async_function_detection(self):
        """Test detection of JavaScript async functions"""
        async_code = """
async function fetchData() {
    const response = await fetch('/api/data');
    return response.json();
}

const asyncArrow = async (url) => {
    return await fetch(url);
};

class AsyncClass {
    async processData(data) {
        return await this.transform(data);
    }
}
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async function detection
        async_functions = ["fetchData", "asyncArrow", "processData"]
        detected_async = [name for name in async_functions if name in result]
        
        assert len(detected_async) > 0, f"No async functions detected: {result}"
        print(f"Detected async functions: {detected_async}")
    
    def test_javascript_generator_function_detection(self):
        """Test detection of JavaScript generator functions"""
        generator_code = """
function* simpleGenerator() {
    yield 1;
    yield 2;
}

function* generatorWithParams(start, end) {
    for (let i = start; i <= end; i++) {
        yield i;
    }
}

const generatorExpression = function* () {
    yield* [1, 2, 3];
};
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(generator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generator function detection
        generator_functions = ["simpleGenerator", "generatorWithParams", "generatorExpression"]
        detected_generators = [name for name in generator_functions if name in result]
        
        assert len(detected_generators) > 0, f"No generator functions detected: {result}"
        print(f"Detected generator functions: {detected_generators}")
    
    def test_javascript_object_methods_detection(self):
        """Test detection of JavaScript object methods"""
        object_code = """
const obj = {
    property: 'value',
    
    method() {
        return this.property;
    },
    
    arrowMethod: () => {
        return 'arrow';
    },
    
    async asyncMethod() {
        return await Promise.resolve('async');
    },
    
    // Method with function keyword
    explicitMethod: function() {
        return 'explicit';
    }
};
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(object_code, lexer, formatter)
        
        assert result is not None
        
        # Check for object method detection
        object_methods = ["method", "arrowMethod", "asyncMethod", "explicitMethod"]
        detected_object_methods = [name for name in object_methods if name in result]
        
        assert len(detected_object_methods) > 0, f"No object methods detected: {result}"
        print(f"Detected object methods: {detected_object_methods}")
    
    def test_javascript_export_functions_detection(self):
        """Test detection of JavaScript export functions"""
        export_code = """
export function namedExport() {
    return 'named export';
}

export const arrowExport = () => 'arrow export';

export default function defaultFunc() {
    return 'default';
}

export { localFunction as aliasedFunction };

function localFunction() {
    return 'local';
}
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(export_code, lexer, formatter)
        
        assert result is not None
        
        # Check for export function detection
        export_functions = ["namedExport", "arrowExport", "defaultFunc", "localFunction"]
        detected_exports = [name for name in export_functions if name in result]
        
        assert len(detected_exports) > 0, f"No export functions detected: {result}"
        print(f"Detected export functions: {detected_exports}")
    
    def test_javascript_language_detection(self):
        """Test that JavaScript language is properly detected"""
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        
        # Verify language detection
        assert formatter._detect_language() == 'javascript', "JavaScript language not properly detected"
    
    def test_javascript_function_expressions_detection(self):
        """Test detection of JavaScript function expressions"""
        expression_code = """
const func1 = function() {
    return 'anonymous';
};

const func2 = function namedExpression() {
    return 'named expression';
};

// Higher-order function
function createFunction(name) {
    return function dynamicFunction() {
        return `Hello, ${name}`;
    };
}

// Callback function
setTimeout(function timeoutCallback() {
    console.log('Timeout');
}, 1000);
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(expression_code, lexer, formatter)
        
        assert result is not None
        
        # Check for function expression detection
        expressions = ["func1", "func2", "namedExpression", "createFunction", "dynamicFunction", "timeoutCallback"]
        detected_expressions = [name for name in expressions if name in result]
        
        assert len(detected_expressions) > 0, f"No function expressions detected: {result}"
        print(f"Detected function expressions: {detected_expressions}")
    
    def test_javascript_destructuring_params_detection(self):
        """Test detection of JavaScript functions with destructuring parameters"""
        destructuring_code = """
function destructureObject({ name, age, ...rest }) {
    return { name, age, rest };
}

const destructureArray = ([first, second, ...others]) => {
    return { first, second, others };
};

function mixedParams(id, { name, settings = {} }, ...flags) {
    return { id, name, settings, flags };
}
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(destructuring_code, lexer, formatter)
        
        assert result is not None
        
        # Check for destructuring function detection
        destructuring_functions = ["destructureObject", "destructureArray", "mixedParams"]
        detected_destructuring = [name for name in destructuring_functions if name in result]
        
        assert len(detected_destructuring) > 0, f"No destructuring functions detected: {result}"
        print(f"Detected destructuring functions: {detected_destructuring}")
    
    def test_empty_javascript_file(self):
        """Test handling of empty JavaScript file"""
        empty_code = """
// Just comments and imports
import { something } from './module';
const variable = 'value';

// No functions defined
"""
        
        lexer = JavascriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='javascript')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestJavaScriptTLDRFormatter()
    test.test_javascript_function_detection_via_highlight_api()
    print("JavaScript TLDR formatter test completed successfully!")