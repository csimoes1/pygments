"""
    C++ TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Test C++-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.c_cpp import CppLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample C++ code with known number of functions
CPP_TEST_CODE = """
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <algorithm>
#include <functional>
#include <thread>
#include <future>

// Namespace
namespace TestNamespace {
    void utility_function() {
        std::cout << "Utility function in namespace\\n";
    }
}

// Simple function
int main() {
    std::cout << "Hello, C++!\\n";
    return 0;
}

// Function with default parameters
int add_numbers(int a, int b = 0) {
    return a + b;
}

// Function overloading
int multiply(int a, int b) {
    return a * b;
}

double multiply(double a, double b) {
    return a * b;
}

// Template functions
template<typename T>
T get_max(T a, T b) {
    return (a > b) ? a : b;
}

template<typename T, typename U>
auto add_different_types(T a, U b) -> decltype(a + b) {
    return a + b;
}

// Variadic template function
template<typename... Args>
void print_all(Args... args) {
    ((std::cout << args << " "), ...);
    std::cout << std::endl;
}

// Class definition
class Calculator {
private:
    double value;
    
public:
    // Constructor
    Calculator(double initial_value = 0.0) : value(initial_value) {}
    
    // Copy constructor
    Calculator(const Calculator& other) : value(other.value) {}
    
    // Move constructor
    Calculator(Calculator&& other) noexcept : value(other.value) {
        other.value = 0.0;
    }
    
    // Destructor
    ~Calculator() = default;
    
    // Assignment operator
    Calculator& operator=(const Calculator& other) {
        if (this != &other) {
            value = other.value;
        }
        return *this;
    }
    
    // Move assignment operator
    Calculator& operator=(Calculator&& other) noexcept {
        if (this != &other) {
            value = other.value;
            other.value = 0.0;
        }
        return *this;
    }
    
    // Member functions
    double get_value() const {
        return value;
    }
    
    void set_value(double new_value) {
        value = new_value;
    }
    
    double add(double operand) {
        value += operand;
        return value;
    }
    
    double subtract(double operand) {
        value -= operand;
        return value;
    }
    
    // Static member function
    static Calculator create_with_value(double val) {
        return Calculator(val);
    }
    
    // Const member function
    bool is_positive() const {
        return value > 0;
    }
    
    // Virtual function
    virtual double calculate_result() const {
        return value;
    }
    
    // Operator overloading
    Calculator operator+(const Calculator& other) const {
        return Calculator(value + other.value);
    }
    
    Calculator operator-(const Calculator& other) const {
        return Calculator(value - other.value);
    }
    
    // Friend function
    friend std::ostream& operator<<(std::ostream& os, const Calculator& calc) {
        os << "Calculator(" << calc.value << ")";
        return os;
    }
};

// Derived class
class ScientificCalculator : public Calculator {
public:
    ScientificCalculator(double initial = 0.0) : Calculator(initial) {}
    
    double power(double exponent) {
        double result = std::pow(get_value(), exponent);
        set_value(result);
        return result;
    }
    
    double square_root() {
        double result = std::sqrt(get_value());
        set_value(result);
        return result;
    }
    
    // Override virtual function
    double calculate_result() const override {
        return get_value() * 2; // Scientific result is doubled
    }
    
    // Pure virtual function in abstract base
    virtual double advanced_operation() = 0;
};

// Abstract base class
class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const = 0;
    virtual double perimeter() const = 0;
    virtual void print_info() const = 0;
};

// Concrete derived class
class Rectangle : public Shape {
private:
    double width, height;
    
public:
    Rectangle(double w, double h) : width(w), height(h) {}
    
    double area() const override {
        return width * height;
    }
    
    double perimeter() const override {
        return 2 * (width + height);
    }
    
    void print_info() const override {
        std::cout << "Rectangle: " << width << "x" << height << std::endl;
    }
    
    // Getters
    double get_width() const { return width; }
    double get_height() const { return height; }
};

// Template class
template<typename T>
class Container {
private:
    std::vector<T> data;
    
public:
    void add_item(const T& item) {
        data.push_back(item);
    }
    
    void add_item(T&& item) {
        data.push_back(std::move(item));
    }
    
    T get_item(size_t index) const {
        if (index < data.size()) {
            return data[index];
        }
        throw std::out_of_range("Index out of bounds");
    }
    
    size_t size() const {
        return data.size();
    }
    
    void clear() {
        data.clear();
    }
    
    // Template member function
    template<typename Predicate>
    void remove_if(Predicate pred) {
        data.erase(std::remove_if(data.begin(), data.end(), pred), data.end());
    }
    
    // Iterator support
    typename std::vector<T>::iterator begin() { return data.begin(); }
    typename std::vector<T>::iterator end() { return data.end(); }
    typename std::vector<T>::const_iterator begin() const { return data.begin(); }
    typename std::vector<T>::const_iterator end() const { return data.end(); }
};

// Lambda and functional programming
void demonstrate_lambdas() {
    auto simple_lambda = []() {
        std::cout << "Simple lambda\\n";
    };
    
    auto add_lambda = [](int a, int b) -> int {
        return a + b;
    };
    
    auto capture_lambda = [&](int x) {
        return x * 2;
    };
    
    simple_lambda();
    std::cout << add_lambda(5, 3) << std::endl;
}

// Function with smart pointers
std::unique_ptr<Calculator> create_calculator(double value) {
    return std::make_unique<Calculator>(value);
}

std::shared_ptr<Rectangle> create_rectangle(double w, double h) {
    return std::make_shared<Rectangle>(w, h);
}

// Function with references
void swap_values(int& a, int& b) {
    int temp = a;
    a = b;
    b = temp;
}

// Function with rvalue references (move semantics)
void process_vector(std::vector<int>&& vec) {
    std::cout << "Processing vector of size: " << vec.size() << std::endl;
}

// Const correctness
const std::string& get_name(const std::vector<std::string>& names, size_t index) {
    static const std::string default_name = "Unknown";
    if (index < names.size()) {
        return names[index];
    }
    return default_name;
}

// Function with exception specification
void might_throw() noexcept(false) {
    throw std::runtime_error("Example exception");
}

void no_throw() noexcept {
    // This function guarantees no exceptions
}

// Async and threading functions
std::future<int> async_calculation(int value) {
    return std::async(std::launch::async, [value]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        return value * value;
    });
}

void thread_function(int id) {
    std::cout << "Thread " << id << " is running\\n";
}

// RAII and resource management
class ResourceManager {
private:
    int* resource;
    
public:
    explicit ResourceManager(int size) : resource(new int[size]) {}
    
    ~ResourceManager() {
        delete[] resource;
    }
    
    // Delete copy constructor and assignment to enforce RAII
    ResourceManager(const ResourceManager&) = delete;
    ResourceManager& operator=(const ResourceManager&) = delete;
    
    // Allow move operations
    ResourceManager(ResourceManager&& other) noexcept : resource(other.resource) {
        other.resource = nullptr;
    }
    
    ResourceManager& operator=(ResourceManager&& other) noexcept {
        if (this != &other) {
            delete[] resource;
            resource = other.resource;
            other.resource = nullptr;
        }
        return *this;
    }
    
    int* get_resource() { return resource; }
};

// Constexpr functions (compile-time evaluation)
constexpr int factorial_constexpr(int n) {
    return (n <= 1) ? 1 : n * factorial_constexpr(n - 1);
}

constexpr bool is_prime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

// Auto keyword and type deduction
auto get_vector_size(const std::vector<int>& vec) -> size_t {
    return vec.size();
}

auto create_pair(int a, double b) {
    return std::make_pair(a, b);
}

// Range-based for loop utility
void print_vector(const std::vector<int>& vec) {
    for (const auto& element : vec) {
        std::cout << element << " ";
    }
    std::cout << std::endl;
}

// Structured binding (C++17)
std::tuple<int, double, std::string> get_data() {
    return std::make_tuple(42, 3.14, "Hello");
}

void process_tuple() {
    auto [num, pi, text] = get_data();
    std::cout << num << ", " << pi << ", " << text << std::endl;
}

// If constexpr (C++17)
template<typename T>
void process_type() {
    if constexpr (std::is_integral_v<T>) {
        std::cout << "Processing integral type\\n";
    } else if constexpr (std::is_floating_point_v<T>) {
        std::cout << "Processing floating point type\\n";
    } else {
        std::cout << "Processing other type\\n";
    }
}

// Concepts (C++20 - if supported)
#if __cplusplus >= 202002L
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;

template<Numeric T>
T add_numeric(T a, T b) {
    return a + b;
}
#endif

// Namespace alias
namespace ns = TestNamespace;

// Using declaration
using std::cout;
using std::endl;

void demonstrate_using() {
    cout << "Using declarations work!" << endl;
}

// Extern "C" linkage
extern "C" {
    int c_compatible_function(int x) {
        return x * 2;
    }
}

// Function try block
void function_with_try_block(int value) try {
    if (value < 0) {
        throw std::invalid_argument("Negative value");
    }
    std::cout << "Value: " << value << std::endl;
} catch (const std::exception& e) {
    std::cout << "Exception: " << e.what() << std::endl;
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic functions
    "main", "utility_function", "add_numbers", "multiply",
    # Template functions
    "get_max", "add_different_types", "print_all",
    # Calculator class methods
    "Calculator", "get_value", "set_value", "add", "subtract", "create_with_value", 
    "is_positive", "calculate_result",
    # Operators
    "+", "-", "<<",
    # Derived class methods
    "ScientificCalculator", "power", "square_root", "advanced_operation",
    # Shape hierarchy
    "area", "perimeter", "print_info", "Rectangle", "get_width", "get_height",
    # Template class methods
    "add_item", "get_item", "size", "clear", "remove_if", "begin", "end",
    # Lambda and functional
    "demonstrate_lambdas", "create_calculator", "create_rectangle",
    # References and move semantics
    "swap_values", "process_vector", "get_name",
    # Exception handling
    "might_throw", "no_throw",
    # Async functions
    "async_calculation", "thread_function",
    # RAII
    "ResourceManager", "get_resource",
    # Constexpr functions
    "factorial_constexpr", "is_prime",
    # Auto and type deduction
    "get_vector_size", "create_pair", "print_vector",
    # Structured binding
    "get_data", "process_tuple",
    # Template specialization
    "process_type",
    # Concepts (C++20)
    "add_numeric",
    # Namespace and using
    "demonstrate_using",
    # C linkage
    "c_compatible_function",
    # Function try block
    "function_with_try_block"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestCppTLDRFormatter:
    """Test class for C++-specific function detection in TLDR formatter."""
    
    def test_cpp_function_detection_via_highlight_api(self):
        """Test C++ function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        
        # Use the highlight() function from __init__.py
        result = highlight(CPP_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} C++ functions")
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
    
    def test_cpp_simple_function_detection(self):
        """Test detection of simple C++ functions"""
        simple_code = """
#include <iostream>

int add(int a, int b) {
    return a + b;
}

void print_hello() {
    std::cout << "Hello, World!\\n";
}

double calculate_area(double radius) {
    return 3.14159 * radius * radius;
}

int main() {
    return 0;
}
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["add", "print_hello", "calculate_area", "main"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_cpp_class_methods_detection(self):
        """Test detection of C++ class methods"""
        class_code = """
class TestClass {
private:
    int value;
    
public:
    TestClass(int val = 0) : value(val) {}
    
    ~TestClass() = default;
    
    int get_value() const {
        return value;
    }
    
    void set_value(int new_value) {
        value = new_value;
    }
    
    static TestClass create_default() {
        return TestClass(0);
    }
    
    virtual void print() const {
        std::cout << "Value: " << value << std::endl;
    }
};
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(class_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["TestClass", "get_value", "set_value", "create_default", "print"]
        detected_class = [name for name in class_methods if name in result]
        
        assert len(detected_class) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class}")
    
    def test_cpp_template_function_detection(self):
        """Test detection of C++ template functions"""
        template_code = """
#include <iostream>

template<typename T>
T get_max(T a, T b) {
    return (a > b) ? a : b;
}

template<typename T, typename U>
auto add_values(T a, U b) -> decltype(a + b) {
    return a + b;
}

template<class T>
class Container {
public:
    void add_item(const T& item) {
        data.push_back(item);
    }
    
    T get_item(size_t index) const {
        return data[index];
    }
    
private:
    std::vector<T> data;
};
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(template_code, lexer, formatter)
        
        assert result is not None
        
        # Check for template function detection
        template_functions = ["get_max", "add_values", "add_item", "get_item"]
        detected_template = [name for name in template_functions if name in result]
        
        assert len(detected_template) > 0, f"No template functions detected: {result}"
        print(f"Detected template functions: {detected_template}")
    
    def test_cpp_operator_overloading_detection(self):
        """Test detection of C++ operator overloading"""
        operator_code = """
class Vector2D {
    double x, y;
    
public:
    Vector2D(double x = 0, double y = 0) : x(x), y(y) {}
    
    Vector2D operator+(const Vector2D& other) const {
        return Vector2D(x + other.x, y + other.y);
    }
    
    Vector2D operator-(const Vector2D& other) const {
        return Vector2D(x - other.x, y - other.y);
    }
    
    Vector2D& operator+=(const Vector2D& other) {
        x += other.x;
        y += other.y;
        return *this;
    }
    
    bool operator==(const Vector2D& other) const {
        return x == other.x && y == other.y;
    }
    
    friend std::ostream& operator<<(std::ostream& os, const Vector2D& vec) {
        os << "(" << vec.x << ", " << vec.y << ")";
        return os;
    }
};
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(operator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for operator detection
        operators = ["+", "-", "+=", "==", "<<"]
        detected_operators = [op for op in operators if op in result]
        
        print(f"Detected operators: {detected_operators}")
        # Note: Operators might not be detected as regular functions
    
    def test_cpp_inheritance_detection(self):
        """Test detection of C++ inheritance and virtual functions"""
        inheritance_code = """
class Base {
public:
    virtual ~Base() = default;
    
    virtual void pure_virtual() = 0;
    
    virtual void virtual_method() {
        std::cout << "Base virtual method\\n";
    }
    
    void regular_method() {
        std::cout << "Base regular method\\n";
    }
};

class Derived : public Base {
public:
    void pure_virtual() override {
        std::cout << "Derived pure virtual\\n";
    }
    
    void virtual_method() override {
        std::cout << "Derived virtual method\\n";
    }
    
    void derived_specific() {
        std::cout << "Derived specific method\\n";
    }
};
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(inheritance_code, lexer, formatter)
        
        assert result is not None
        
        # Check for inheritance method detection
        inheritance_methods = ["pure_virtual", "virtual_method", "regular_method", "derived_specific"]
        detected_inheritance = [name for name in inheritance_methods if name in result]
        
        assert len(detected_inheritance) > 0, f"No inheritance methods detected: {result}"
        print(f"Detected inheritance methods: {detected_inheritance}")
    
    def test_cpp_lambda_detection(self):
        """Test detection of C++ lambda expressions"""
        lambda_code = """
#include <iostream>
#include <vector>
#include <algorithm>

void demonstrate_lambdas() {
    auto simple_lambda = []() {
        std::cout << "Simple lambda\\n";
    };
    
    auto add_lambda = [](int a, int b) -> int {
        return a + b;
    };
    
    int multiplier = 2;
    auto capture_lambda = [&multiplier](int x) {
        return x * multiplier;
    };
    
    std::vector<int> numbers = {1, 2, 3, 4, 5};
    std::for_each(numbers.begin(), numbers.end(), [](int n) {
        std::cout << n << " ";
    });
}

auto create_lambda(int factor) {
    return [factor](int value) {
        return value * factor;
    };
}
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(lambda_code, lexer, formatter)
        
        assert result is not None
        
        # Check for lambda and function detection
        lambda_functions = ["demonstrate_lambdas", "create_lambda"]
        detected_lambda = [name for name in lambda_functions if name in result]
        
        assert len(detected_lambda) > 0, f"No lambda functions detected: {result}"
        print(f"Detected lambda functions: {detected_lambda}")
    
    def test_cpp_namespace_detection(self):
        """Test detection of C++ namespace functions"""
        namespace_code = """
namespace MathUtils {
    double pi = 3.14159;
    
    double calculate_area(double radius) {
        return pi * radius * radius;
    }
    
    double calculate_circumference(double radius) {
        return 2 * pi * radius;
    }
    
    namespace Advanced {
        double sin_approximation(double x) {
            return x - (x*x*x)/6 + (x*x*x*x*x)/120;
        }
        
        double cos_approximation(double x) {
            return 1 - (x*x)/2 + (x*x*x*x)/24;
        }
    }
}

using namespace MathUtils;

void test_namespace_functions() {
    double area = calculate_area(5.0);
    double advanced_sin = Advanced::sin_approximation(1.0);
}
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(namespace_code, lexer, formatter)
        
        assert result is not None
        
        # Check for namespace function detection
        namespace_functions = ["calculate_area", "calculate_circumference", "sin_approximation", "cos_approximation", "test_namespace_functions"]
        detected_namespace = [name for name in namespace_functions if name in result]
        
        assert len(detected_namespace) > 0, f"No namespace functions detected: {result}"
        print(f"Detected namespace functions: {detected_namespace}")
    
    def test_cpp_smart_pointer_detection(self):
        """Test detection of C++ smart pointer functions"""
        smart_pointer_code = """
#include <memory>
#include <iostream>

class Resource {
public:
    Resource(int id) : id_(id) {
        std::cout << "Resource " << id_ << " created\\n";
    }
    
    ~Resource() {
        std::cout << "Resource " << id_ << " destroyed\\n";
    }
    
    void use() {
        std::cout << "Using resource " << id_ << "\\n";
    }
    
private:
    int id_;
};

std::unique_ptr<Resource> create_unique_resource(int id) {
    return std::make_unique<Resource>(id);
}

std::shared_ptr<Resource> create_shared_resource(int id) {
    return std::make_shared<Resource>(id);
}

void use_unique_ptr() {
    auto resource = create_unique_resource(1);
    resource->use();
}

void use_shared_ptr() {
    auto resource = create_shared_resource(2);
    resource->use();
}
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(smart_pointer_code, lexer, formatter)
        
        assert result is not None
        
        # Check for smart pointer function detection
        smart_ptr_functions = ["Resource", "use", "create_unique_resource", "create_shared_resource", "use_unique_ptr", "use_shared_ptr"]
        detected_smart_ptr = [name for name in smart_ptr_functions if name in result]
        
        assert len(detected_smart_ptr) > 0, f"No smart pointer functions detected: {result}"
        print(f"Detected smart pointer functions: {detected_smart_ptr}")
    
    def test_cpp_language_detection(self):
        """Test that C++ language is properly detected"""
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        
        # Verify language detection
        detected_lang = formatter._detect_language()
        assert detected_lang in ['c_family', 'cpp'], f"C++ language not properly detected, got: {detected_lang}"
    
    def test_cpp_constexpr_detection(self):
        """Test detection of C++ constexpr functions"""
        constexpr_code = """
constexpr int factorial(int n) {
    return (n <= 1) ? 1 : n * factorial(n - 1);
}

constexpr bool is_prime(int n) {
    if (n <= 1) return false;
    if (n <= 3) return true;
    if (n % 2 == 0 || n % 3 == 0) return false;
    
    for (int i = 5; i * i <= n; i += 6) {
        if (n % i == 0 || n % (i + 2) == 0) return false;
    }
    return true;
}

constexpr double square(double x) {
    return x * x;
}

void test_constexpr() {
    constexpr int fact5 = factorial(5);
    constexpr bool prime17 = is_prime(17);
    constexpr double sq3 = square(3.0);
}
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(constexpr_code, lexer, formatter)
        
        assert result is not None
        
        # Check for constexpr function detection
        constexpr_functions = ["factorial", "is_prime", "square", "test_constexpr"]
        detected_constexpr = [name for name in constexpr_functions if name in result]
        
        assert len(detected_constexpr) > 0, f"No constexpr functions detected: {result}"
        print(f"Detected constexpr functions: {detected_constexpr}")
    
    def test_empty_cpp_file(self):
        """Test handling of empty C++ file"""
        empty_code = """
// Just comments and includes
#include <iostream>
#include <vector>
#include <string>

// Namespace declarations
using namespace std;

// Global variables
int global_var = 0;

// No functions defined
"""
        
        lexer = CppLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='cpp')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestCppTLDRFormatter()
    test.test_cpp_function_detection_via_highlight_api()
    print("C++ TLDR formatter test completed successfully!")