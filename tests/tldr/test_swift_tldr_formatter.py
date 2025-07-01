"""
    Swift TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Swift-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.objective import SwiftLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Swift code with known number of functions
SWIFT_TEST_CODE = """
// Swift sample code for testing function detection
import Foundation
import UIKit

// Protocol definition
protocol UserServiceProtocol {
    func getUser(id: Int) -> User?
    func createUser(name: String, email: String) -> User
    var userCount: Int { get }
}

// Struct with methods
struct User {
    let id: Int
    let name: String
    var email: String?
    
    // Initializer
    init(id: Int, name: String, email: String? = nil) {
        self.id = id
        self.name = name
        self.email = email
    }
    
    // Instance method
    func displayInfo() -> String {
        let emailInfo = email ?? "No email"
        return "User: \\(name), Email: \\(emailInfo)"
    }
    
    // Mutating method
    mutating func updateEmail(_ newEmail: String) {
        self.email = newEmail
    }
    
    // Static method
    static func createDefault() -> User {
        return User(id: 0, name: "Default User")
    }
    
    // Computed property
    var displayName: String {
        get {
            return "User: \\(name)"
        }
    }
    
    // Read-write computed property
    var summary: String {
        get {
            return "\\(name) (ID: \\(id))"
        }
        set {
            // Setter logic could parse the new value
        }
    }
}

// Class with inheritance
class UserService: NSObject, UserServiceProtocol {
    private var users: [User] = []
    
    // Override initializer
    override init() {
        super.init()
        self.users = []
    }
    
    // Convenience initializer
    convenience init(initialUsers: [User]) {
        self.init()
        self.users = initialUsers
    }
    
    // Protocol conformance methods
    func getUser(id: Int) -> User? {
        return users.first { $0.id == id }
    }
    
    func createUser(name: String, email: String) -> User {
        let newId = (users.map { $0.id }.max() ?? 0) + 1
        let user = User(id: newId, name: name, email: email)
        users.append(user)
        return user
    }
    
    // Computed property implementation
    var userCount: Int {
        return users.count
    }
    
    // Private method
    private func validateUser(_ user: User) -> Bool {
        return !user.name.isEmpty
    }
    
    // Class method
    class func sharedService() -> UserService {
        return UserService()
    }
    
    // Method with throws
    func saveUsers() throws {
        // Save logic that might throw
        guard !users.isEmpty else {
            throw UserServiceError.noUsers
        }
    }
    
    // Method with async
    @available(iOS 13.0, *)
    func fetchUsersAsync() async throws -> [User] {
        // Async fetch logic
        return users
    }
    
    // Method with completion handler
    func fetchUsers(completion: @escaping ([User]) -> Void) {
        DispatchQueue.main.async {
            completion(self.users)
        }
    }
    
    // Subscript
    subscript(index: Int) -> User? {
        get {
            guard index >= 0 && index < users.count else { return nil }
            return users[index]
        }
        set {
            guard let newUser = newValue,
                  index >= 0 && index < users.count else { return }
            users[index] = newUser
        }
    }
}

// Generic function
func processItems<T>(items: [T], processor: (T) -> String) -> [String] {
    return items.map(processor)
}

// Function with multiple generic constraints
func compareAndProcess<T: Comparable, U: CustomStringConvertible>(
    first: T, 
    second: T, 
    converter: U
) -> String where U.StringType == String {
    let comparison = first < second ? "less" : "greater"
    return "\\(converter): \\(comparison)"
}

// Global function with closure parameter
func performOperation(on value: Int, operation: (Int) -> Int) -> Int {
    return operation(value)
}

// Function with inout parameter
func increment(_ value: inout Int) {
    value += 1
}

// Function with variadic parameters
func sum(_ numbers: Int...) -> Int {
    return numbers.reduce(0, +)
}

// Extension with methods
extension String {
    func isValidEmail() -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\\\.[A-Za-z]{2,}"
        return NSPredicate(format: "SELF MATCHES %@", emailRegex).evaluate(with: self)
    }
    
    var reversed: String {
        return String(self.reversed())
    }
}

// Enum with methods
enum UserRole {
    case admin
    case user
    case guest
    
    func permissions() -> [String] {
        switch self {
        case .admin:
            return ["read", "write", "delete"]
        case .user:
            return ["read", "write"]
        case .guest:
            return ["read"]
        }
    }
    
    static func defaultRole() -> UserRole {
        return .guest
    }
}

// Operator overloading
func +(left: User, right: User) -> [User] {
    return [left, right]
}

// Error enum
enum UserServiceError: Error {
    case noUsers
    case invalidUser
    
    var description: String {
        switch self {
        case .noUsers:
            return "No users available"
        case .invalidUser:
            return "Invalid user data"
        }
    }
}

// Property wrapper
@propertyWrapper
struct Capitalized {
    private var value: String = ""
    
    var wrappedValue: String {
        get { value }
        set { value = newValue.capitalized }
    }
    
    init(wrappedValue: String) {
        self.value = wrappedValue.capitalized
    }
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Protocol methods
    "getUser", "createUser", "userCount",
    # Struct methods
    "init",  # User initializer
    "displayInfo", "updateEmail", "createDefault", "displayName", "summary",
    # Class methods  
    "init",  # UserService init (might be detected multiple times)
    "getUser", "createUser", "userCount",  # Protocol implementations
    "validateUser", "sharedService", "saveUsers", "fetchUsersAsync", "fetchUsers",
    "subscript",  # Subscript method
    # Global functions
    "processItems", "compareAndProcess", "performOperation", "increment", "sum",
    # Extension methods
    "isValidEmail", "reversed",
    # Enum methods
    "permissions", "defaultRole",
    # Operator overloading
    "+",  # Might not be detected as regular function
    # Property wrapper
    "wrappedValue",  # Computed property
    # Error enum
    "description"
]

# Total expected count (allowing for some variations in detection)
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestSwiftTLDRFormatter:
    """Test class for Swift-specific function detection in TLDR formatter."""
    
    def test_swift_function_detection_via_highlight_api(self):
        """Test Swift function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        
        # Use the highlight() function from __init__.py
        result = highlight(SWIFT_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Swift functions")
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
    
    def test_swift_simple_function_detection(self):
        """Test detection of simple Swift functions"""
        simple_code = """
func simpleFunction() {
    print("Hello Swift")
}

func addNumbers(a: Int, b: Int) -> Int {
    return a + b
}

class SimpleClass {
    func method() -> String {
        return "method"
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["simpleFunction", "addNumbers", "method"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_swift_initializers_detection(self):
        """Test detection of Swift initializers"""
        init_code = """
struct Point {
    let x: Double
    let y: Double
    
    init(x: Double, y: Double) {
        self.x = x
        self.y = y
    }
    
    init() {
        self.init(x: 0, y: 0)
    }
}

class Rectangle {
    let width: Double
    let height: Double
    
    init(width: Double, height: Double) {
        self.width = width
        self.height = height
    }
    
    convenience init(square side: Double) {
        self.init(width: side, height: side)
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(init_code, lexer, formatter)
        
        assert result is not None
        
        # Check for initializer detection
        assert "init" in result, f"No initializers detected: {result}"
        print(f"Detected initializers in result")
    
#     def test_swift_computed_properties_detection(self):
#         """Test detection of Swift computed properties"""
#         property_code = """
# struct Circle {
#     let radius: Double
#
#     var area: Double {
#         return .pi * radius * radius
#     }
#
#     var diameter: Double {
#         get {
#             return radius * 2
#         }
#         set {
#             radius = newValue / 2
#         }
#     }
#
#     var description: String {
#         return "Circle with radius \\(radius)"
#     }
# }
# """
#
#         lexer = SwiftLexer()
#         formatter = TLDRFormatter(highlight_functions=True, lang='swift')
#         result = highlight(property_code, lexer, formatter)
#
#         assert result is not None
#
#         # Check for computed property detection
#         properties = ["area", "diameter", "description"]
#         detected_properties = [name for name in properties if name in result]
#
#         # At least some properties should be detected
#         assert len(detected_properties) > 0, f"No computed properties detected: {result}"
#         print(f"Detected computed properties: {detected_properties}")
    
    def test_swift_protocol_methods_detection(self):
        """Test detection of Swift protocol methods"""
        protocol_code = """
protocol Drawable {
    func draw()
    func area() -> Double
    var description: String { get }
}

protocol Movable {
    mutating func move(to point: CGPoint)
    func canMove() -> Bool
}

struct Shape: Drawable, Movable {
    func draw() {
        // Drawing implementation
    }
    
    func area() -> Double {
        return 0.0
    }
    
    var description: String {
        return "Generic shape"
    }
    
    mutating func move(to point: CGPoint) {
        // Move implementation
    }
    
    func canMove() -> Bool {
        return true
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(protocol_code, lexer, formatter)
        
        assert result is not None
        
        # Check for protocol method detection
        protocol_methods = ["draw", "area", "description", "move", "canMove"]
        detected_methods = [name for name in protocol_methods if name in result]
        
        assert len(detected_methods) > 0, f"No protocol methods detected: {result}"
        print(f"Detected protocol methods: {detected_methods}")
    
    def test_swift_generic_functions_detection(self):
        """Test detection of Swift generic functions"""
        generic_code = """
func identity<T>(value: T) -> T {
    return value
}

func swap<T>(a: inout T, b: inout T) {
    let temp = a
    a = b
    b = temp
}

func compare<T: Comparable>(a: T, b: T) -> Bool {
    return a < b
}

class Container<Element> {
    var items: [Element] = []
    
    func add(_ item: Element) {
        items.append(item)
    }
    
    func get(at index: Int) -> Element? {
        guard index < items.count else { return nil }
        return items[index]
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(generic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generic function detection
        generic_functions = ["identity", "swap", "compare", "add", "get"]
        detected_generics = [name for name in generic_functions if name in result]
        
        assert len(detected_generics) > 0, f"No generic functions detected: {result}"
        print(f"Detected generic functions: {detected_generics}")
    
    def test_swift_subscript_detection(self):
        """Test detection of Swift subscripts"""
        subscript_code = """
struct Matrix {
    let rows: Int
    let columns: Int
    private var grid: [Double]
    
    init(rows: Int, columns: Int) {
        self.rows = rows
        self.columns = columns
        self.grid = Array(repeating: 0.0, count: rows * columns)
    }
    
    subscript(row: Int, column: Int) -> Double {
        get {
            assert(indexIsValid(row: row, column: column), "Index out of range")
            return grid[(row * columns) + column]
        }
        set {
            assert(indexIsValid(row: row, column: column), "Index out of range")
            grid[(row * columns) + column] = newValue
        }
    }
    
    subscript(row: Int) -> [Double] {
        get {
            let startIndex = row * columns
            let endIndex = startIndex + columns
            return Array(grid[startIndex..<endIndex])
        }
    }
    
    private func indexIsValid(row: Int, column: Int) -> Bool {
        return row >= 0 && row < rows && column >= 0 && column < columns
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(subscript_code, lexer, formatter)
        
        assert result is not None
        
        # Check for subscript detection
        assert "subscript" in result, f"No subscripts detected: {result}"
        print(f"Detected subscripts in result")
    
    def test_swift_language_detection(self):
        """Test that Swift language is properly detected"""
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        
        # Verify language detection
        assert formatter._detect_language() == 'swift', "Swift language not properly detected"
    
    def test_swift_access_modifiers(self):
        """Test detection of Swift functions with various access modifiers"""
        access_code = """
public class PublicClass {
    public func publicMethod() -> String {
        return "public"
    }
    
    internal func internalMethod() -> String {
        return "internal"
    }
    
    private func privateMethod() -> String {
        return "private"
    }
    
    fileprivate func fileprivateMethod() -> String {
        return "fileprivate"
    }
    
    open func openMethod() -> String {
        return "open"
    }
    
    final func finalMethod() -> String {
        return "final"
    }
    
    static func staticMethod() -> String {
        return "static"
    }
    
    class func classMethod() -> String {
        return "class"
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(access_code, lexer, formatter)
        
        assert result is not None
        
        # Check for access modifier methods
        access_methods = ["publicMethod", "internalMethod", "privateMethod", "fileprivateMethod", "openMethod", "finalMethod", "staticMethod", "classMethod"]
        detected_access = [name for name in access_methods if name in result]
        
        assert len(detected_access) > 0, f"No access modifier methods detected: {result}"
        print(f"Detected access modifier methods: {detected_access}")
    
    def test_empty_swift_file(self):
        """Test handling of empty Swift file"""
        empty_code = """
// Just comments and imports
import Foundation
import UIKit

// No functions defined
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)
    
    def test_swift_async_functions(self):
        """Test detection of Swift async/await functions"""
        async_code = """
@available(iOS 13.0, *)
func fetchData() async -> Data? {
    // Async implementation
    return nil
}

@available(iOS 13.0, *)
func processData() async throws -> String {
    let data = await fetchData()
    guard let data = data else {
        throw DataError.noData
    }
    return "processed"
}

class AsyncService {
    @available(iOS 13.0, *)
    func performAsync() async {
        // Async method
    }
    
    @available(iOS 13.0, *)
    func fetchAndProcess() async throws -> [String] {
        // Complex async method
        return []
    }
}
"""
        
        lexer = SwiftLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='swift')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async function detection
        async_functions = ["fetchData", "processData", "performAsync", "fetchAndProcess"]
        detected_async = [name for name in async_functions if name in result]
        
        assert len(detected_async) > 0, f"No async functions detected: {result}"
        print(f"Detected async functions: {detected_async}")


if __name__ == "__main__":
    # Run a quick test
    test = TestSwiftTLDRFormatter()
    test.test_swift_function_detection_via_highlight_api()
    print("Swift TLDR formatter test completed successfully!")