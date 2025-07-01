"""
    Java TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Java-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.jvm import JavaLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Java code with known number of functions
JAVA_TEST_CODE = """
package com.example.test;

import java.util.List;
import java.util.ArrayList;
import java.io.IOException;

/**
 * Sample Java class for testing function detection
 */
public class TestClass {
    private String name;
    private int value;
    
    // Constructor 1
    public TestClass() {
        this.name = "default";
        this.value = 0;
    }
    
    // Constructor 2 with parameters
    public TestClass(String name, int value) {
        this.name = name;
        this.value = value;
    }
    
    // Getter method
    public String getName() {
        return name;
    }
    
    // Setter method
    public void setName(String name) {
        this.name = name;
    }
    
    // Public method with return type
    public int getValue() {
        return value;
    }
    
    // Method with throws clause
    public void readFile(String filename) throws IOException {
        // File reading logic here
    }
    
    // Static method
    public static void staticMethod() {
        System.out.println("Static method called");
    }
    
    // Protected method
    protected void protectedMethod() {
        // Protected logic
    }
    
    // Private method with parameters
    private boolean isValid(String input) {
        return input != null && !input.isEmpty();
    }
    
    // Method with generic parameters
    public <T> List<T> createList(T item) {
        List<T> list = new ArrayList<>();
        list.add(item);
        return list;
    }
    
    // Abstract method declaration (if this were abstract class)
    // public abstract void abstractMethod();
    
    // Final method
    public final void finalMethod() {
        // Final implementation
    }
    
    // Synchronized method
    public synchronized void synchronizedMethod() {
        // Thread-safe logic
    }
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    "TestClass",  # Constructor 1
    "TestClass",  # Constructor 2  
    "getName",
    "setName", 
    "getValue",
    "readFile",
    "staticMethod",
    "protectedMethod", 
    "isValid",
    "createList",
    "finalMethod",
    "synchronizedMethod"
]

# Total expected count (note: constructors might be counted differently)
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestJavaTLDRFormatter:
    """Test class for Java-specific function detection in TLDR formatter."""
    
    def test_java_function_detection_via_highlight_api(self):
        """Test Java function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        
        # Use the highlight() function from __init__.py
        result = highlight(JAVA_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Java functions")
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
        
        # Verify we detected most expected functions (allowing some variance in detection logic)
        detection_ratio = len(detected_functions) / EXPECTED_FUNCTION_COUNT
        assert detection_ratio >= 0.5, f"Detection ratio too low: {detection_ratio:.2f} ({len(detected_functions)}/{EXPECTED_FUNCTION_COUNT})"
    
    def test_java_constructor_detection(self):
        """Test that Java constructors are properly detected"""
        # Simple class with constructor
        constructor_code = """
        public class SimpleClass {
            public SimpleClass() {
                // Constructor
            }
            
            public SimpleClass(int value) {
                // Parameterized constructor
            }
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(constructor_code, lexer, formatter)
        
        assert result is not None
        assert "SimpleClass" in result, f"Constructor not detected in: {result}"
    
    def test_java_method_with_access_modifiers(self):
        """Test detection of methods with various access modifiers"""
        access_modifier_code = """
        public class AccessTest {
            public void publicMethod() {}
            private void privateMethod() {}
            protected void protectedMethod() {}
            static void packagePrivateMethod() {}
            public static void publicStaticMethod() {}
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(access_modifier_code, lexer, formatter)
        
        assert result is not None
        
        # Check for method names
        method_names = ["publicMethod", "privateMethod", "protectedMethod", "packagePrivateMethod", "publicStaticMethod"]
        detected_methods = [name for name in method_names if name in result]
        
        assert len(detected_methods) > 0, f"No methods with access modifiers detected: {result}"
        print(f"Detected methods with access modifiers: {detected_methods}")
    
    def test_java_generic_method_detection(self):
        """Test detection of Java generic methods"""
        generic_code = """
        public class GenericTest {
            public <T> T identity(T input) {
                return input;
            }
            
            public <T, U> void swap(List<T> list1, List<U> list2) {
                // Swap logic
            }
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(generic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generic method detection
        assert "identity" in result or "swap" in result, f"Generic methods not detected: {result}"
    
    def test_java_throws_clause_detection(self):
        """Test detection of methods with throws clauses"""
        throws_code = """
        public class ThrowsTest {
            public void methodWithThrows() throws IOException, SQLException {
                // Method with throws clause
            }
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(throws_code, lexer, formatter)
        
        assert result is not None
        assert "methodWithThrows" in result, f"Method with throws clause not detected: {result}"
    
    def test_java_language_detection(self):
        """Test that Java language is properly detected"""
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        
        # Verify language detection
        assert formatter._detect_language() == 'java', "Java language not properly detected"
    
    def test_java_vs_javascript_differentiation(self):
        """Test that Java and JavaScript are differentiated"""
        java_code = """
        public class JavaClass {
            public void javaMethod() {
                System.out.println("Java");
            }
        }
        """
        
        # Test with Java lexer
        java_lexer = JavaLexer()
        java_formatter = TLDRFormatter(highlight_functions=True, lang='java')
        java_result = highlight(java_code, java_lexer, java_formatter)
        
        # Verify Java-specific detection
        assert java_result is not None
        assert "javaMethod" in java_result, f"Java method not detected: {java_result}"
        
        # Verify language detection is Java, not JavaScript
        assert java_formatter._detect_language() == 'java'
    
    def test_empty_java_class(self):
        """Test handling of empty Java class"""
        empty_code = """
        public class EmptyClass {
            // No methods
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)
    
    def test_java_interface_methods(self):
        """Test detection of interface method declarations"""
        interface_code = """
        public interface TestInterface {
            void interfaceMethod();
            default void defaultMethod() {
                // Default implementation
            }
            static void staticInterfaceMethod() {
                // Static method in interface
            }
        }
        """
        
        lexer = JavaLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='java')
        result = highlight(interface_code, lexer, formatter)
        
        assert result is not None
        
        # Check for interface method detection
        interface_methods = ["interfaceMethod", "defaultMethod", "staticInterfaceMethod"]
        detected_methods = [name for name in interface_methods if name in result]
        
        # At least some interface methods should be detected
        assert len(detected_methods) > 0, f"No interface methods detected: {result}"
        print(f"Detected interface methods: {detected_methods}")


if __name__ == "__main__":
    # Run a quick test
    test = TestJavaTLDRFormatter()
    test.test_java_function_detection_via_highlight_api()
    print("Java TLDR formatter test completed successfully!")