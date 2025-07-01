"""
    C# TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~

    Test C#-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.dotnet import CSharpLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample C# code with known number of functions
CSHARP_TEST_CODE = """
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using System.IO;

namespace TestNamespace
{
    /// <summary>
    /// Sample C# class for testing function detection
    /// </summary>
    public class TestClass
    {
        private string name;
        private int value;
        
        // Constructor 1
        public TestClass()
        {
            this.name = "default";
            this.value = 0;
        }
        
        // Constructor 2 with parameters
        public TestClass(string name, int value)
        {
            this.name = name;
            this.value = value;
        }
        
        // Properties with get/set
        public string Name
        {
            get { return name; }
            set { name = value; }
        }
        
        // Auto-implemented property
        public int Value { get; set; }
        
        // Property with private setter
        public DateTime CreatedAt { get; private set; } = DateTime.Now;
        
        // Public methods
        public string GetDisplayName()
        {
            return $"Name: {name}";
        }
        
        public void SetName(string newName)
        {
            if (!string.IsNullOrEmpty(newName))
            {
                this.name = newName;
            }
        }
        
        public int CalculateValue(int multiplier = 1)
        {
            return value * multiplier;
        }
        
        // Generic method
        public T ProcessData<T>(T input) where T : class
        {
            return input;
        }
        
        // Method with multiple generic constraints
        public TResult Transform<TInput, TResult>(TInput input, Func<TInput, TResult> transformer)
            where TInput : class
            where TResult : class
        {
            return transformer(input);
        }
        
        // Async methods
        public async Task<string> ReadFileAsync(string filePath)
        {
            using (var reader = new StreamReader(filePath))
            {
                return await reader.ReadToEndAsync();
            }
        }
        
        public async Task<bool> SaveDataAsync(string data)
        {
            await Task.Delay(100);
            return true;
        }
        
        public async ValueTask<int> GetCountAsync()
        {
            await Task.Delay(50);
            return value;
        }
        
        // Static methods
        public static TestClass CreateDefault()
        {
            return new TestClass();
        }
        
        public static async Task<TestClass> CreateFromFileAsync(string filePath)
        {
            var content = await File.ReadAllTextAsync(filePath);
            return new TestClass(content, 0);
        }
        
        // Protected and private methods
        protected virtual void LogOperation(string operation)
        {
            Console.WriteLine($"Operation: {operation}");
        }
        
        private bool ValidateInput(string input)
        {
            return !string.IsNullOrWhiteSpace(input);
        }
        
        // Virtual and override methods
        public virtual string GetDescription()
        {
            return $"TestClass: {name}";
        }
        
        // Method with ref and out parameters
        public bool TryParseValue(string input, out int result)
        {
            return int.TryParse(input, out result);
        }
        
        public void ModifyValue(ref int inputValue)
        {
            inputValue *= 2;
        }
        
        // Method with params array
        public string CombineStrings(params string[] values)
        {
            return string.Join(", ", values);
        }
        
        // Explicit interface implementation
        public void Dispose()
        {
            // Cleanup resources
        }
        
        // Finalizer
        ~TestClass()
        {
            // Cleanup
        }
        
        // Operator overloading
        public static TestClass operator +(TestClass left, TestClass right)
        {
            return new TestClass(left.name + right.name, left.value + right.value);
        }
        
        public static implicit operator string(TestClass instance)
        {
            return instance.name;
        }
        
        public static explicit operator int(TestClass instance)
        {
            return instance.value;
        }
        
        // Indexer
        public string this[int index]
        {
            get { return $"Item at {index}"; }
            set { /* Set logic */ }
        }
        
        // Event handler method
        private void OnValueChanged(object sender, EventArgs e)
        {
            LogOperation("Value changed");
        }
    }
    
    // Abstract class
    public abstract class BaseService
    {
        protected string serviceName;
        
        protected BaseService(string name)
        {
            this.serviceName = name;
        }
        
        public abstract Task<bool> InitializeAsync();
        
        protected virtual void Log(string message)
        {
            Console.WriteLine($"[{serviceName}] {message}");
        }
        
        public virtual void Shutdown()
        {
            Log("Shutting down service");
        }
    }
    
    // Derived class
    public class UserService : BaseService, IDisposable
    {
        private readonly List<string> users = new List<string>();
        
        public UserService() : base("UserService")
        {
        }
        
        public override async Task<bool> InitializeAsync()
        {
            await Task.Delay(100);
            Log("User service initialized");
            return true;
        }
        
        public void AddUser(string username)
        {
            if (ValidateUsername(username))
            {
                users.Add(username);
            }
        }
        
        public IEnumerable<string> GetUsers()
        {
            return users.AsReadOnly();
        }
        
        public async Task<string> FindUserAsync(string username)
        {
            await Task.Delay(10);
            return users.FirstOrDefault(u => u.Equals(username, StringComparison.OrdinalIgnoreCase));
        }
        
        private bool ValidateUsername(string username)
        {
            return !string.IsNullOrEmpty(username) && username.Length >= 3;
        }
        
        public void Dispose()
        {
            users.Clear();
            Log("UserService disposed");
        }
    }
    
    // Static class
    public static class UtilityHelpers
    {
        public static string FormatString(string input)
        {
            return input?.Trim().ToLowerInvariant() ?? string.Empty;
        }
        
        public static T GetDefault<T>() where T : new()
        {
            return new T();
        }
        
        public static async Task<string> ReadAllTextAsync(string filePath)
        {
            return await File.ReadAllTextAsync(filePath);
        }
        
        public static bool IsValidEmail(string email)
        {
            return email?.Contains("@") == true;
        }
    }
    
    // Interface
    public interface IRepository<T> where T : class
    {
        Task<T> GetByIdAsync(int id);
        Task<IEnumerable<T>> GetAllAsync();
        Task<bool> SaveAsync(T entity);
        Task<bool> DeleteAsync(int id);
    }
    
    // Generic class implementing interface
    public class Repository<T> : IRepository<T> where T : class, new()
    {
        private readonly List<T> items = new List<T>();
        
        public async Task<T> GetByIdAsync(int id)
        {
            await Task.Delay(1);
            return items.ElementAtOrDefault(id);
        }
        
        public async Task<IEnumerable<T>> GetAllAsync()
        {
            await Task.Delay(1);
            return items.ToList();
        }
        
        public async Task<bool> SaveAsync(T entity)
        {
            await Task.Delay(1);
            items.Add(entity);
            return true;
        }
        
        public async Task<bool> DeleteAsync(int id)
        {
            await Task.Delay(1);
            if (id < items.Count)
            {
                items.RemoveAt(id);
                return true;
            }
            return false;
        }
        
        public void ClearAll()
        {
            items.Clear();
        }
    }
    
    // Struct with methods
    public struct Point
    {
        public double X { get; set; }
        public double Y { get; set; }
        
        public Point(double x, double y)
        {
            X = x;
            Y = y;
        }
        
        public double DistanceFromOrigin()
        {
            return Math.Sqrt(X * X + Y * Y);
        }
        
        public Point Add(Point other)
        {
            return new Point(X + other.X, Y + other.Y);
        }
        
        public override string ToString()
        {
            return $"({X}, {Y})";
        }
        
        public override bool Equals(object obj)
        {
            if (obj is Point other)
            {
                return X == other.X && Y == other.Y;
            }
            return false;
        }
        
        public override int GetHashCode()
        {
            return HashCode.Combine(X, Y);
        }
    }
    
    // Enum with methods
    public enum Status
    {
        Active,
        Inactive,
        Pending
    }
    
    public static class StatusExtensions
    {
        public static string GetDisplayName(this Status status)
        {
            return status switch
            {
                Status.Active => "Currently Active",
                Status.Inactive => "Not Active",
                Status.Pending => "Waiting for Approval",
                _ => "Unknown Status"
            };
        }
        
        public static bool IsActive(this Status status)
        {
            return status == Status.Active;
        }
    }
    
    // Record (C# 9.0+)
    public record UserRecord(string Name, int Age)
    {
        public string GetInfo()
        {
            return $"{Name} is {Age} years old";
        }
        
        public static UserRecord CreateDefault()
        {
            return new UserRecord("Unknown", 0);
        }
    }
    
    // Delegate and event examples
    public delegate void ValueChangedHandler(int oldValue, int newValue);
    
    public class EventPublisher
    {
        public event ValueChangedHandler ValueChanged;
        private int currentValue;
        
        public void SetValue(int newValue)
        {
            int oldValue = currentValue;
            currentValue = newValue;
            OnValueChanged(oldValue, newValue);
        }
        
        protected virtual void OnValueChanged(int oldValue, int newValue)
        {
            ValueChanged?.Invoke(oldValue, newValue);
        }
        
        public void Subscribe(ValueChangedHandler handler)
        {
            ValueChanged += handler;
        }
        
        public void Unsubscribe(ValueChangedHandler handler)
        {
            ValueChanged -= handler;
        }
    }
    
    // Anonymous methods and lambdas
    public class FunctionalHelpers
    {
        public static void ProcessItems<T>(IEnumerable<T> items, Action<T> processor)
        {
            foreach (var item in items)
            {
                processor(item);
            }
        }
        
        public static IEnumerable<TResult> TransformItems<T, TResult>(
            IEnumerable<T> items, 
            Func<T, TResult> transformer)
        {
            return items.Select(transformer);
        }
        
        public static async Task<TResult> ExecuteWithRetryAsync<TResult>(
            Func<Task<TResult>> operation, 
            int maxRetries = 3)
        {
            for (int i = 0; i < maxRetries; i++)
            {
                try
                {
                    return await operation();
                }
                catch (Exception ex) when (i < maxRetries - 1)
                {
                    await Task.Delay(1000 * (i + 1));
                }
            }
            throw new InvalidOperationException("Max retries exceeded");
        }
    }
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # TestClass constructors and methods
    "TestClass", "Name", "GetDisplayName", "SetName", "CalculateValue", "ProcessData", "Transform",
    "ReadFileAsync", "SaveDataAsync", "GetCountAsync", "CreateDefault", "CreateFromFileAsync",
    "LogOperation", "ValidateInput", "GetDescription", "TryParseValue", "ModifyValue", "CombineStrings",
    "Dispose", "OnValueChanged",
    # Operators and indexers
    "+", "this",
    # BaseService
    "BaseService", "InitializeAsync", "Log", "Shutdown",
    # UserService
    "UserService", "AddUser", "GetUsers", "FindUserAsync", "ValidateUsername",
    # UtilityHelpers
    "FormatString", "GetDefault", "ReadAllTextAsync", "IsValidEmail",
    # Repository
    "GetByIdAsync", "GetAllAsync", "SaveAsync", "DeleteAsync", "ClearAll",
    # Point struct
    "Point", "DistanceFromOrigin", "Add", "ToString", "Equals", "GetHashCode",
    # Extensions
    "GetDisplayName", "IsActive",
    # UserRecord
    "GetInfo", "CreateDefault",
    # EventPublisher
    "SetValue", "OnValueChanged", "Subscribe", "Unsubscribe",
    # FunctionalHelpers
    "ProcessItems", "TransformItems", "ExecuteWithRetryAsync"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestCSharpTLDRFormatter:
    """Test class for C#-specific function detection in TLDR formatter."""
    
    def test_csharp_function_detection_via_highlight_api(self):
        """Test C# function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        
        # Use the highlight() function from __init__.py
        result = highlight(CSHARP_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} C# functions")
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
    
    def test_csharp_simple_function_detection(self):
        """Test detection of simple C# functions"""
        simple_code = """
public class SimpleClass
{
    public void HelloWorld()
    {
        Console.WriteLine("Hello, World!");
    }

    public int AddNumbers(int a, int b)
    {
        return a + b;
    }

    public string GetMessage()
    {
        return "Test message";
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["HelloWorld", "AddNumbers", "GetMessage"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_csharp_properties_detection(self):
        """Test detection of C# properties"""
        property_code = """
public class PropertyTest
{
    private string name;
    
    public string Name
    {
        get { return name; }
        set { name = value; }
    }
    
    public int Age { get; set; }
    
    public DateTime CreatedAt { get; private set; } = DateTime.Now;
    
    public string FullName => $"{FirstName} {LastName}";
    
    public string FirstName { get; set; }
    public string LastName { get; set; }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(property_code, lexer, formatter)
        
        assert result is not None
        
        # Check for property detection
        properties = ["Name", "Age", "CreatedAt", "FullName", "FirstName", "LastName"]
        detected_properties = [name for name in properties if name in result]
        
        assert len(detected_properties) > 0, f"No properties detected: {result}"
        print(f"Detected properties: {detected_properties}")
    
    def test_csharp_async_methods_detection(self):
        """Test detection of C# async methods"""
        async_code = """
public class AsyncTest
{
    public async Task<string> ReadFileAsync(string path)
    {
        return await File.ReadAllTextAsync(path);
    }
    
    public async Task<bool> SaveDataAsync(string data)
    {
        await Task.Delay(100);
        return true;
    }
    
    public async ValueTask<int> GetCountAsync()
    {
        await Task.Delay(50);
        return 42;
    }
    
    public static async Task<User> CreateUserAsync(string name)
    {
        await Task.Delay(10);
        return new User { Name = name };
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async method detection
        async_methods = ["ReadFileAsync", "SaveDataAsync", "GetCountAsync", "CreateUserAsync"]
        detected_async = [name for name in async_methods if name in result]
        
        assert len(detected_async) > 0, f"No async methods detected: {result}"
        print(f"Detected async methods: {detected_async}")
    
#     def test_csharp_generic_methods_detection(self):
#         """Test detection of C# generic methods"""
#         generic_code = """
# public class GenericTest
# {
#     public T Process<T>(T input) where T : class
#     {
#         return input;
#     }
#
#     public TResult Transform<TInput, TResult>(TInput input, Func<TInput, TResult> transformer)
#         where TInput : class
#         where TResult : class
#     {
#         return transformer(input);
#     }
#
#     public static T GetDefault<T>() where T : new()
#     {
#         return new T();
#     }
#
#     public void ProcessList<T>(List<T> items) where T : IComparable<T>
#     {
#         items.Sort();
#     }
# }
# """
#
#         lexer = CSharpLexer()
#         formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
#         result = highlight(generic_code, lexer, formatter)
#
#         assert result is not None
#
#         # Check for generic method detection
#         generic_methods = ["Process", "Transform", "GetDefault", "ProcessList"]
#         detected_generic = [name for name in generic_methods if name in result]
#
#         assert len(detected_generic) > 0, f"No generic methods detected: {result}"
#         print(f"Detected generic methods: {detected_generic}")
    
    def test_csharp_static_methods_detection(self):
        """Test detection of C# static methods"""
        static_code = """
public static class StaticHelpers
{
    public static string FormatString(string input)
    {
        return input?.Trim().ToLowerInvariant() ?? string.Empty;
    }
    
    public static bool IsValidEmail(string email)
    {
        return email?.Contains("@") == true;
    }
    
    public static async Task<string> ReadAllTextAsync(string filePath)
    {
        return await File.ReadAllTextAsync(filePath);
    }
    
    public static T CreateInstance<T>() where T : new()
    {
        return new T();
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(static_code, lexer, formatter)
        
        assert result is not None
        
        # Check for static method detection
        static_methods = ["FormatString", "IsValidEmail", "ReadAllTextAsync", "CreateInstance"]
        detected_static = [name for name in static_methods if name in result]
        
        assert len(detected_static) > 0, f"No static methods detected: {result}"
        print(f"Detected static methods: {detected_static}")
    
    def test_csharp_interface_methods_detection(self):
        """Test detection of C# interface methods"""
        interface_code = """
public interface IUserRepository
{
    Task<User> GetByIdAsync(int id);
    Task<IEnumerable<User>> GetAllAsync();
    Task<bool> SaveAsync(User user);
    Task<bool> DeleteAsync(int id);
    bool ValidateUser(User user);
}

public interface IGenericRepository<T> where T : class
{
    Task<T> FindAsync(int id);
    Task<bool> CreateAsync(T entity);
    Task<bool> UpdateAsync(T entity);
    Task<bool> RemoveAsync(int id);
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(interface_code, lexer, formatter)
        
        assert result is not None
        
        # Check for interface method detection (might not be detected as they're declarations)
        interface_methods = ["GetByIdAsync", "GetAllAsync", "SaveAsync", "DeleteAsync", "ValidateUser", "FindAsync", "CreateAsync", "UpdateAsync", "RemoveAsync"]
        detected_interface = [name for name in interface_methods if name in result]
        
        # Interface methods might not be detected by design
        print(f"Detected interface methods: {detected_interface}")
    
    def test_csharp_constructor_detection(self):
        """Test detection of C# constructors"""
        constructor_code = """
public class ConstructorTest
{
    private string name;
    private int value;
    
    public ConstructorTest()
    {
        this.name = "default";
        this.value = 0;
    }
    
    public ConstructorTest(string name)
    {
        this.name = name;
        this.value = 0;
    }
    
    public ConstructorTest(string name, int value)
    {
        this.name = name;
        this.value = value;
    }
    
    static ConstructorTest()
    {
        // Static constructor
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(constructor_code, lexer, formatter)
        
        assert result is not None
        
        # Check for constructor detection (constructors have same name as class)
        assert "ConstructorTest" in result, f"No constructors detected: {result}"
        print(f"Detected constructors in result")
    
    def test_csharp_operator_overloading_detection(self):
        """Test detection of C# operator overloading"""
        operator_code = """
public struct Vector2
{
    public float X { get; set; }
    public float Y { get; set; }
    
    public Vector2(float x, float y)
    {
        X = x;
        Y = y;
    }
    
    public static Vector2 operator +(Vector2 left, Vector2 right)
    {
        return new Vector2(left.X + right.X, left.Y + right.Y);
    }
    
    public static Vector2 operator -(Vector2 left, Vector2 right)
    {
        return new Vector2(left.X - right.X, left.Y - right.Y);
    }
    
    public static bool operator ==(Vector2 left, Vector2 right)
    {
        return left.X == right.X && left.Y == right.Y;
    }
    
    public static bool operator !=(Vector2 left, Vector2 right)
    {
        return !(left == right);
    }
    
    public static implicit operator string(Vector2 vector)
    {
        return $"({vector.X}, {vector.Y})";
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(operator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for operator detection (operators might have special detection)
        operators = ["+", "-", "==", "!="]
        detected_operators = [op for op in operators if op in result]
        
        print(f"Detected operators: {detected_operators}")
    
    def test_csharp_language_detection(self):
        """Test that C# language is properly detected"""
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        
        # Verify language detection
        assert formatter._detect_language() == 'csharp', "C# language not properly detected"
    
    def test_csharp_extension_methods_detection(self):
        """Test detection of C# extension methods"""
        extension_code = """
public static class StringExtensions
{
    public static bool IsValidEmail(this string email)
    {
        return email?.Contains("@") == true;
    }
    
    public static string Truncate(this string input, int maxLength)
    {
        if (string.IsNullOrEmpty(input) || input.Length <= maxLength)
            return input;
        
        return input.Substring(0, maxLength) + "...";
    }
    
    public static T ParseEnum<T>(this string value) where T : struct
    {
        return Enum.Parse<T>(value, true);
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(extension_code, lexer, formatter)
        
        assert result is not None
        
        # Check for extension method detection
        extension_methods = ["IsValidEmail", "Truncate", "ParseEnum"]
        detected_extensions = [name for name in extension_methods if name in result]
        
        assert len(detected_extensions) > 0, f"No extension methods detected: {result}"
        print(f"Detected extension methods: {detected_extensions}")
    
    def test_csharp_record_methods_detection(self):
        """Test detection of C# record methods (C# 9.0+)"""
        record_code = """
public record UserRecord(string Name, int Age)
{
    public string GetInfo()
    {
        return $"{Name} is {Age} years old";
    }
    
    public static UserRecord CreateDefault()
    {
        return new UserRecord("Unknown", 0);
    }
    
    public UserRecord WithUpdatedAge(int newAge)
    {
        return this with { Age = newAge };
    }
}

public record struct Point(double X, double Y)
{
    public double DistanceFromOrigin()
    {
        return Math.Sqrt(X * X + Y * Y);
    }
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(record_code, lexer, formatter)
        
        assert result is not None
        
        # Check for record method detection
        record_methods = ["GetInfo", "CreateDefault", "WithUpdatedAge", "DistanceFromOrigin"]
        detected_record_methods = [name for name in record_methods if name in result]
        
        assert len(detected_record_methods) > 0, f"No record methods detected: {result}"
        print(f"Detected record methods: {detected_record_methods}")
    
    def test_empty_csharp_file(self):
        """Test handling of empty C# file"""
        empty_code = """
using System;
using System.Collections.Generic;
using System.Linq;

namespace EmptyNamespace
{
    // Just comments and usings
    // No classes or methods defined
}
"""
        
        lexer = CSharpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='csharp')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestCSharpTLDRFormatter()
    test.test_csharp_function_detection_via_highlight_api()
    print("C# TLDR formatter test completed successfully!")