"""
    C TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~

    Test C-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.c_cpp import CLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample C code with known number of functions
C_TEST_CODE = """
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

// Global variable
static int global_counter = 0;

// Forward declarations
int add_numbers(int a, int b);
void print_message(const char* message);

// Simple function
int main(void) {
    printf("Hello, World!\\n");
    return 0;
}

// Function with parameters
int add_numbers(int a, int b) {
    return a + b;
}

// Function with void return
void print_message(const char* message) {
    if (message != NULL) {
        printf("%s\\n", message);
    }
}

// Function with pointer parameters
char* string_copy(const char* source) {
    if (source == NULL) return NULL;
    
    size_t len = strlen(source);
    char* dest = malloc(len + 1);
    if (dest != NULL) {
        strcpy(dest, source);
    }
    return dest;
}

// Function with array parameter
int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

// Function with struct parameter
typedef struct {
    int x;
    int y;
} Point;

Point create_point(int x, int y) {
    Point p;
    p.x = x;
    p.y = y;
    return p;
}

double distance_between_points(Point p1, Point p2) {
    int dx = p1.x - p2.x;
    int dy = p1.y - p2.y;
    return sqrt(dx*dx + dy*dy);
}

// Function with function pointer parameter
int apply_operation(int a, int b, int (*operation)(int, int)) {
    return operation(a, b);
}

// Recursive function
int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Static function (file scope)
static int internal_helper(int value) {
    return value * 2;
}

static void initialize_system(void) {
    global_counter = 0;
    printf("System initialized\\n");
}

// Function with multiple return statements
int find_max(int a, int b, int c) {
    if (a >= b && a >= c) return a;
    if (b >= c) return b;
    return c;
}

// Function with complex parameter list
int process_data(const char* input, char* output, size_t output_size, bool* success) {
    if (input == NULL || output == NULL || success == NULL) {
        if (success) *success = false;
        return -1;
    }
    
    size_t input_len = strlen(input);
    if (input_len >= output_size) {
        *success = false;
        return -1;
    }
    
    strcpy(output, input);
    *success = true;
    return (int)input_len;
}

// Function with variadic arguments
void log_message(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
}

// Functions with different storage classes
extern int external_function(void);
inline int inline_function(int x) {
    return x * x;
}

// Function with const parameters
int string_length(const char* str) {
    if (str == NULL) return 0;
    return (int)strlen(str);
}

// Function with volatile parameter
void handle_interrupt(volatile int* flag) {
    *flag = 1;
}

// Function returning function pointer
int (*get_operation(char op))(int, int) {
    switch (op) {
        case '+': return add_numbers;
        case '*': return multiply_numbers;
        default: return NULL;
    }
}

int multiply_numbers(int a, int b) {
    return a * b;
}

// Nested function declarations (GNU C extension, if supported)
#ifdef __GNUC__
int outer_function(int x) {
    int inner_function(int y) {
        return x + y;
    }
    return inner_function(10);
}
#endif

// Function with register keyword
int fast_calculation(register int value) {
    return value * value + value;
}

// Function with restrict keyword (C99)
void copy_array(int* restrict dest, const int* restrict src, size_t count) {
    for (size_t i = 0; i < count; i++) {
        dest[i] = src[i];
    }
}

// Function with complex return type
struct Point* allocate_point(int x, int y) {
    struct Point* p = malloc(sizeof(struct Point));
    if (p != NULL) {
        p->x = x;
        p->y = y;
    }
    return p;
}

// Function with enum parameter
typedef enum {
    STATUS_OK,
    STATUS_ERROR,
    STATUS_PENDING
} Status;

const char* status_to_string(Status status) {
    switch (status) {
        case STATUS_OK: return "OK";
        case STATUS_ERROR: return "Error";
        case STATUS_PENDING: return "Pending";
        default: return "Unknown";
    }
}

// Function with union parameter
typedef union {
    int i;
    float f;
    char c[4];
} Value;

void print_value(Value val, char type) {
    switch (type) {
        case 'i': printf("Integer: %d\\n", val.i); break;
        case 'f': printf("Float: %f\\n", val.f); break;
        case 'c': printf("Chars: %.4s\\n", val.c); break;
    }
}

// Function with bit field struct
typedef struct {
    unsigned int flag1 : 1;
    unsigned int flag2 : 1;
    unsigned int value : 6;
} Flags;

void set_flags(Flags* flags, bool f1, bool f2, int val) {
    if (flags) {
        flags->flag1 = f1 ? 1 : 0;
        flags->flag2 = f2 ? 1 : 0;
        flags->value = val & 0x3F;
    }
}

// Function with array of pointers parameter
void process_strings(char* strings[], int count) {
    for (int i = 0; i < count; i++) {
        if (strings[i] != NULL) {
            printf("String %d: %s\\n", i, strings[i]);
        }
    }
}

// Function with function pointer array
typedef int (*MathOperation)(int, int);

int calculate_all(int a, int b, MathOperation ops[], int op_count) {
    int result = 0;
    for (int i = 0; i < op_count; i++) {
        if (ops[i] != NULL) {
            result += ops[i](a, b);
        }
    }
    return result;
}

// Error handling function
int divide_safe(int a, int b, int* result) {
    if (b == 0) {
        return -1; // Division by zero error
    }
    if (result == NULL) {
        return -2; // Null pointer error
    }
    *result = a / b;
    return 0; // Success
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic functions
    "main", "add_numbers", "print_message", "string_copy", "sum_array",
    # Struct-related functions  
    "create_point", "distance_between_points", "allocate_point",
    # Function pointer and callback functions
    "apply_operation", "get_operation", "multiply_numbers",
    # Recursive functions
    "factorial", "fibonacci",
    # Static functions
    "internal_helper", "initialize_system",
    # Utility functions
    "find_max", "process_data", "log_message",
    # Functions with different storage classes
    "external_function", "inline_function", "string_length", "handle_interrupt",
    # Advanced parameter functions
    "fast_calculation", "copy_array", 
    # Enum and union functions
    "status_to_string", "print_value", "set_flags",
    # Array and pointer functions
    "process_strings", "calculate_all", "divide_safe",
    # Conditional compilation functions
    "outer_function", "inner_function"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestCTLDRFormatter:
    """Test class for C-specific function detection in TLDR formatter."""
    
    def test_c_function_detection_via_highlight_api(self):
        """Test C function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        
        # Use the highlight() function from __init__.py
        result = highlight(C_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} C functions")
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
    
    def test_c_simple_function_detection(self):
        """Test detection of simple C functions"""
        simple_code = """
#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void print_hello(void) {
    printf("Hello, World!\\n");
}

double calculate_area(double radius) {
    return 3.14159 * radius * radius;
}

int main(void) {
    return 0;
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["add", "print_hello", "calculate_area", "main"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_c_pointer_function_detection(self):
        """Test detection of C functions with pointers"""
        pointer_code = """
#include <stdlib.h>
#include <string.h>

char* create_string(const char* source) {
    if (!source) return NULL;
    char* dest = malloc(strlen(source) + 1);
    strcpy(dest, source);
    return dest;
}

void swap_integers(int* a, int* b) {
    int temp = *a;
    *a = *b;
    *b = temp;
}

int* allocate_array(size_t count) {
    return malloc(count * sizeof(int));
}

void free_array(int* array) {
    free(array);
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(pointer_code, lexer, formatter)
        
        assert result is not None
        
        # Check for pointer function detection
        pointer_functions = ["create_string", "swap_integers", "allocate_array", "free_array"]
        detected_pointers = [name for name in pointer_functions if name in result]
        
        assert len(detected_pointers) > 0, f"No pointer functions detected: {result}"
        print(f"Detected pointer functions: {detected_pointers}")
    
    def test_c_struct_function_detection(self):
        """Test detection of C functions with structs"""
        struct_code = """
typedef struct {
    int x;
    int y;
} Point;

typedef struct {
    char name[50];
    int age;
} Person;

Point create_point(int x, int y) {
    Point p = {x, y};
    return p;
}

void move_point(Point* p, int dx, int dy) {
    p->x += dx;
    p->y += dy;
}

Person* create_person(const char* name, int age) {
    Person* p = malloc(sizeof(Person));
    if (p) {
        strncpy(p->name, name, sizeof(p->name) - 1);
        p->name[sizeof(p->name) - 1] = '\\0';
        p->age = age;
    }
    return p;
}

int compare_ages(const Person* p1, const Person* p2) {
    return p1->age - p2->age;
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(struct_code, lexer, formatter)
        
        assert result is not None
        
        # Check for struct function detection
        struct_functions = ["create_point", "move_point", "create_person", "compare_ages"]
        detected_struct = [name for name in struct_functions if name in result]
        
        assert len(detected_struct) > 0, f"No struct functions detected: {result}"
        print(f"Detected struct functions: {detected_struct}")
    
    def test_c_array_function_detection(self):
        """Test detection of C functions with arrays"""
        array_code = """
#include <stdio.h>

int sum_array(int arr[], int size) {
    int sum = 0;
    for (int i = 0; i < size; i++) {
        sum += arr[i];
    }
    return sum;
}

void print_array(int* arr, size_t count) {
    for (size_t i = 0; i < count; i++) {
        printf("%d ", arr[i]);
    }
    printf("\\n");
}

void fill_array(int arr[], int size, int value) {
    for (int i = 0; i < size; i++) {
        arr[i] = value;
    }
}

int find_element(const int arr[], int size, int target) {
    for (int i = 0; i < size; i++) {
        if (arr[i] == target) {
            return i;
        }
    }
    return -1;
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(array_code, lexer, formatter)
        
        assert result is not None
        
        # Check for array function detection
        array_functions = ["sum_array", "print_array", "fill_array", "find_element"]
        detected_arrays = [name for name in array_functions if name in result]
        
        assert len(detected_arrays) > 0, f"No array functions detected: {result}"
        print(f"Detected array functions: {detected_arrays}")
    
    def test_c_static_function_detection(self):
        """Test detection of C static functions"""
        static_code = """
#include <stdio.h>

static int internal_counter = 0;

static void initialize(void) {
    internal_counter = 0;
}

static int increment_counter(void) {
    return ++internal_counter;
}

static bool validate_input(int value) {
    return value >= 0 && value <= 100;
}

int get_counter_value(void) {
    return internal_counter;
}

void reset_system(void) {
    initialize();
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(static_code, lexer, formatter)
        
        assert result is not None
        
        # Check for static function detection
        static_functions = ["initialize", "increment_counter", "validate_input", "get_counter_value", "reset_system"]
        detected_static = [name for name in static_functions if name in result]
        
        assert len(detected_static) > 0, f"No static functions detected: {result}"
        print(f"Detected static functions: {detected_static}")
    
    def test_c_function_pointer_detection(self):
        """Test detection of C function pointer functions"""
        function_pointer_code = """
#include <stdio.h>

typedef int (*BinaryOperation)(int, int);

int add(int a, int b) {
    return a + b;
}

int multiply(int a, int b) {
    return a * b;
}

int apply_operation(int x, int y, BinaryOperation op) {
    return op(x, y);
}

BinaryOperation get_operation(char symbol) {
    switch (symbol) {
        case '+': return add;
        case '*': return multiply;
        default: return NULL;
    }
}

void process_with_callback(int* data, size_t count, void (*callback)(int)) {
    for (size_t i = 0; i < count; i++) {
        callback(data[i]);
    }
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(function_pointer_code, lexer, formatter)
        
        assert result is not None
        
        # Check for function pointer detection
        fp_functions = ["add", "multiply", "apply_operation", "get_operation", "process_with_callback"]
        detected_fp = [name for name in fp_functions if name in result]
        
        assert len(detected_fp) > 0, f"No function pointer functions detected: {result}"
        print(f"Detected function pointer functions: {detected_fp}")
    
    def test_c_recursive_function_detection(self):
        """Test detection of C recursive functions"""
        recursive_code = """
#include <stdio.h>

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int gcd(int a, int b) {
    if (b == 0) return a;
    return gcd(b, a % b);
}

void print_countdown(int n) {
    if (n <= 0) {
        printf("Done!\\n");
        return;
    }
    printf("%d\\n", n);
    print_countdown(n - 1);
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(recursive_code, lexer, formatter)
        
        assert result is not None
        
        # Check for recursive function detection
        recursive_functions = ["factorial", "fibonacci", "gcd", "print_countdown"]
        detected_recursive = [name for name in recursive_functions if name in result]
        
        assert len(detected_recursive) > 0, f"No recursive functions detected: {result}"
        print(f"Detected recursive functions: {detected_recursive}")
    
    def test_c_language_detection(self):
        """Test that C language is properly detected"""
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        
        # Verify language detection
        detected_lang = formatter._detect_language()
        assert detected_lang in ['c_family', 'c'], f"C language not properly detected, got: {detected_lang}"
    
    def test_c_variadic_function_detection(self):
        """Test detection of C variadic functions"""
        variadic_code = """
#include <stdio.h>
#include <stdarg.h>

void print_integers(int count, ...) {
    va_list args;
    va_start(args, count);
    
    for (int i = 0; i < count; i++) {
        int value = va_arg(args, int);
        printf("%d ", value);
    }
    
    va_end(args);
    printf("\\n");
}

int sum_all(int count, ...) {
    va_list args;
    va_start(args, count);
    
    int sum = 0;
    for (int i = 0; i < count; i++) {
        sum += va_arg(args, int);
    }
    
    va_end(args);
    return sum;
}

void log_message(const char* format, ...) {
    va_list args;
    va_start(args, format);
    vprintf(format, args);
    va_end(args);
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(variadic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for variadic function detection
        variadic_functions = ["print_integers", "sum_all", "log_message"]
        detected_variadic = [name for name in variadic_functions if name in result]
        
        assert len(detected_variadic) > 0, f"No variadic functions detected: {result}"
        print(f"Detected variadic functions: {detected_variadic}")
    
    def test_c_inline_function_detection(self):
        """Test detection of C inline functions"""
        inline_code = """
#include <stdio.h>

inline int square(int x) {
    return x * x;
}

inline double max_double(double a, double b) {
    return (a > b) ? a : b;
}

static inline bool is_even(int n) {
    return (n % 2) == 0;
}

extern inline void debug_print(const char* msg) {
    #ifdef DEBUG
    printf("DEBUG: %s\\n", msg);
    #endif
}
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(inline_code, lexer, formatter)
        
        assert result is not None
        
        # Check for inline function detection
        inline_functions = ["square", "max_double", "is_even", "debug_print"]
        detected_inline = [name for name in inline_functions if name in result]
        
        assert len(detected_inline) > 0, f"No inline functions detected: {result}"
        print(f"Detected inline functions: {detected_inline}")
    
    def test_empty_c_file(self):
        """Test handling of empty C file"""
        empty_code = """
// Just comments and includes
#include <stdio.h>
#include <stdlib.h>

// Global variables
int global_var = 0;

// Macro definitions
#define MAX_SIZE 100

// No functions defined
"""
        
        lexer = CLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='c')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestCTLDRFormatter()
    test.test_c_function_detection_via_highlight_api()
    print("C TLDR formatter test completed successfully!")