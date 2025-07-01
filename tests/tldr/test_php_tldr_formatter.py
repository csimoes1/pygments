"""
    PHP TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Test PHP-specific function detection using the highlight() API.

    :copyright: Copyright 2006-2025 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.php import PhpLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample PHP code with known number of functions
PHP_TEST_CODE = """
<?php
/**
 * PHP sample code for testing function detection
 */

// Global variables
$globalVar = "initialized";
$counter = 0;

// Constants
define('MAX_SIZE', 100);
const MIN_SIZE = 1;

// Simple functions
function main() {
    echo "Hello, PHP!\\n";
    $result = addNumbers(5, 3);
    echo "Result: " . $result . "\\n";
}

function addNumbers($a, $b) {
    return $a + $b;
}

function greet($name) {
    echo "Hello, " . $name . "!\\n";
}

// Function with default parameters
function greetWithDefault($name, $greeting = "Hello") {
    echo $greeting . ", " . $name . "!\\n";
}

// Function with type hints
function addIntegers(int $a, int $b): int {
    return $a + $b;
}

function divideNumbers(float $a, float $b): float {
    if ($b == 0) {
        throw new InvalidArgumentException("Division by zero");
    }
    return $a / $b;
}

// Function with nullable types
function processString(?string $input): ?string {
    if ($input === null) {
        return null;
    }
    return strtoupper($input);
}

// Function with union types (PHP 8.0+)
function processValue(int|float $value): string {
    return "Processed: " . $value;
}

// Variadic functions
function sum(...$numbers) {
    $total = 0;
    foreach ($numbers as $num) {
        $total += $num;
    }
    return $total;
}

function printf($format, ...$args) {
    return sprintf($format, ...$args);
}

// Array functions
function processArray(array $items): array {
    return array_map(function($item) {
        return "processed_" . $item;
    }, $items);
}

function filterArray(array $items, callable $callback): array {
    return array_filter($items, $callback);
}

// Reference parameters
function swapValues(&$a, &$b) {
    $temp = $a;
    $a = $b;
    $b = $temp;
}

function incrementValue(&$value) {
    $value++;
}

// Class definitions and methods
class Person {
    private $name;
    private $age;
    
    // Constructor
    public function __construct($name, $age) {
        $this->name = $name;
        $this->age = $age;
    }
    
    // Destructor
    public function __destruct() {
        // Cleanup
    }
    
    // Magic methods
    public function __toString() {
        return $this->name . " (" . $this->age . " years old)";
    }
    
    public function __get($property) {
        if (property_exists($this, $property)) {
            return $this->$property;
        }
        return null;
    }
    
    public function __set($property, $value) {
        if (property_exists($this, $property)) {
            $this->$property = $value;
        }
    }
    
    public function __call($method, $args) {
        throw new BadMethodCallException("Method $method not found");
    }
    
    // Getter methods
    public function getName(): string {
        return $this->name;
    }
    
    public function getAge(): int {
        return $this->age;
    }
    
    // Setter methods
    public function setName(string $name): void {
        $this->name = $name;
    }
    
    public function setAge(int $age): void {
        if ($age < 0) {
            throw new InvalidArgumentException("Age cannot be negative");
        }
        $this->age = $age;
    }
    
    // Instance methods
    public function isAdult(): bool {
        return $this->age >= 18;
    }
    
    public function getInfo(): array {
        return [
            'name' => $this->name,
            'age' => $this->age,
            'is_adult' => $this->isAdult()
        ];
    }
    
    // Static methods
    public static function createDefault(): self {
        return new self("Unknown", 0);
    }
    
    public static function fromArray(array $data): self {
        return new self($data['name'] ?? 'Unknown', $data['age'] ?? 0);
    }
    
    // Protected method
    protected function validateAge($age): bool {
        return is_int($age) && $age >= 0;
    }
    
    // Private method
    private function formatName($name): string {
        return ucfirst(strtolower(trim($name)));
    }
}

// Abstract class
abstract class Animal {
    protected $name;
    protected $species;
    
    public function __construct($name, $species) {
        $this->name = $name;
        $this->species = $species;
    }
    
    // Abstract method
    abstract public function makeSound(): string;
    
    // Concrete method
    public function getName(): string {
        return $this->name;
    }
    
    public function getSpecies(): string {
        return $this->species;
    }
    
    public function getInfo(): string {
        return $this->name . " is a " . $this->species;
    }
}

// Concrete class extending abstract class
class Dog extends Animal {
    private $breed;
    
    public function __construct($name, $breed) {
        parent::__construct($name, "Canis lupus");
        $this->breed = $breed;
    }
    
    public function makeSound(): string {
        return "Woof! Woof!";
    }
    
    public function getBreed(): string {
        return $this->breed;
    }
    
    public function fetch(): string {
        return $this->name . " is fetching the ball!";
    }
    
    // Override parent method
    public function getInfo(): string {
        return parent::getInfo() . " and is a " . $this->breed;
    }
}

// Interface definitions
interface Drawable {
    public function draw(): string;
    public function getArea(): float;
    public function getPerimeter(): float;
}

interface Colorable {
    public function setColor(string $color): void;
    public function getColor(): string;
}

// Class implementing multiple interfaces
class Rectangle implements Drawable, Colorable {
    private $width;
    private $height;
    private $color;
    
    public function __construct(float $width, float $height, string $color = 'black') {
        $this->width = $width;
        $this->height = $height;
        $this->color = $color;
    }
    
    public function draw(): string {
        return "Drawing a {$this->color} rectangle {$this->width}x{$this->height}";
    }
    
    public function getArea(): float {
        return $this->width * $this->height;
    }
    
    public function getPerimeter(): float {
        return 2 * ($this->width + $this->height);
    }
    
    public function setColor(string $color): void {
        $this->color = $color;
    }
    
    public function getColor(): string {
        return $this->color;
    }
    
    public function getWidth(): float {
        return $this->width;
    }
    
    public function getHeight(): float {
        return $this->height;
    }
    
    public function scale(float $factor): void {
        $this->width *= $factor;
        $this->height *= $factor;
    }
}

// Trait definitions
trait Loggable {
    protected $logs = [];
    
    public function log(string $message): void {
        $this->logs[] = date('Y-m-d H:i:s') . ": " . $message;
    }
    
    public function getLogs(): array {
        return $this->logs;
    }
    
    public function clearLogs(): void {
        $this->logs = [];
    }
}

trait Cacheable {
    private $cache = [];
    
    public function setCache(string $key, $value): void {
        $this->cache[$key] = $value;
    }
    
    public function getCache(string $key) {
        return $this->cache[$key] ?? null;
    }
    
    public function clearCache(): void {
        $this->cache = [];
    }
}

// Class using traits
class Service {
    use Loggable, Cacheable;
    
    private $name;
    
    public function __construct(string $name) {
        $this->name = $name;
        $this->log("Service {$name} created");
    }
    
    public function getName(): string {
        return $this->name;
    }
    
    public function processData(array $data): array {
        $cacheKey = md5(serialize($data));
        
        $result = $this->getCache($cacheKey);
        if ($result !== null) {
            $this->log("Data retrieved from cache");
            return $result;
        }
        
        // Simulate processing
        $result = array_map(function($item) {
            return strtoupper($item);
        }, $data);
        
        $this->setCache($cacheKey, $result);
        $this->log("Data processed and cached");
        
        return $result;
    }
}

// Anonymous functions and closures
function createAdder($x) {
    return function($y) use ($x) {
        return $x + $y;
    };
}

function processWithCallback(array $items, callable $callback): array {
    return array_map($callback, $items);
}

function demonstrateClosures(): array {
    $multiplier = 3;
    
    $numbers = [1, 2, 3, 4, 5];
    
    // Anonymous function
    $doubled = array_map(function($n) {
        return $n * 2;
    }, $numbers);
    
    // Closure with use
    $tripled = array_map(function($n) use ($multiplier) {
        return $n * $multiplier;
    }, $numbers);
    
    // Arrow function (PHP 7.4+)
    $squared = array_map(fn($n) => $n * $n, $numbers);
    
    return [
        'doubled' => $doubled,
        'tripled' => $tripled,
        'squared' => $squared
    ];
}

// Generator functions
function fibonacci($limit) {
    $a = 0;
    $b = 1;
    
    yield $a;
    yield $b;
    
    while ($a + $b < $limit) {
        $c = $a + $b;
        yield $c;
        $a = $b;
        $b = $c;
    }
}

function numberGenerator($start, $end) {
    for ($i = $start; $i <= $end; $i++) {
        yield $i;
    }
}

function readLines($filename) {
    $file = fopen($filename, 'r');
    try {
        while (!feof($file)) {
            yield fgets($file);
        }
    } finally {
        fclose($file);
    }
}

// Exception handling
class CustomException extends Exception {
    private $errorCode;
    
    public function __construct($message, $errorCode = 0, Exception $previous = null) {
        parent::__construct($message, 0, $previous);
        $this->errorCode = $errorCode;
    }
    
    public function getErrorCode(): int {
        return $this->errorCode;
    }
    
    public function __toString(): string {
        return "CustomException [{$this->errorCode}]: {$this->getMessage()}";
    }
}

function validateData($data) {
    if (empty($data)) {
        throw new InvalidArgumentException("Data cannot be empty");
    }
    
    if (!is_array($data)) {
        throw new CustomException("Data must be an array", 1001);
    }
    
    return true;
}

function processDataSafely($data) {
    try {
        validateData($data);
        return array_map('strtoupper', $data);
    } catch (CustomException $e) {
        error_log("Custom error: " . $e->getMessage());
        return [];
    } catch (Exception $e) {
        error_log("General error: " . $e->getMessage());
        return [];
    }
}

// Namespace functions
namespace Utils\\String {
    function formatText($text) {
        return ucwords(strtolower(trim($text)));
    }
    
    function slugify($text) {
        return strtolower(preg_replace('/[^a-zA-Z0-9]+/', '-', $text));
    }
}

namespace Utils\\Array {
    function flattenArray(array $array): array {
        $result = [];
        array_walk_recursive($array, function($value) use (&$result) {
            $result[] = $value;
        });
        return $result;
    }
    
    function groupBy(array $array, $key): array {
        return array_reduce($array, function($result, $item) use ($key) {
            $result[$item[$key]][] = $item;
            return $result;
        }, []);
    }
}

// Magic methods class
class MagicContainer {
    private $data = [];
    
    public function __get($key) {
        return $this->data[$key] ?? null;
    }
    
    public function __set($key, $value) {
        $this->data[$key] = $value;
    }
    
    public function __isset($key) {
        return isset($this->data[$key]);
    }
    
    public function __unset($key) {
        unset($this->data[$key]);
    }
    
    public function __call($method, $args) {
        if (strpos($method, 'get') === 0) {
            $key = strtolower(substr($method, 3));
            return $this->data[$key] ?? null;
        }
        
        if (strpos($method, 'set') === 0) {
            $key = strtolower(substr($method, 3));
            $this->data[$key] = $args[0] ?? null;
            return $this;
        }
        
        throw new BadMethodCallException("Method $method not found");
    }
    
    public static function __callStatic($method, $args) {
        return new static();
    }
    
    public function __invoke($key = null) {
        if ($key === null) {
            return $this->data;
        }
        return $this->data[$key] ?? null;
    }
    
    public function __clone() {
        $this->data = array_map(function($item) {
            return is_object($item) ? clone $item : $item;
        }, $this->data);
    }
    
    public function __serialize(): array {
        return $this->data;
    }
    
    public function __unserialize(array $data): void {
        $this->data = $data;
    }
}

// Static methods and late static binding
class BaseModel {
    protected static $tableName = 'base';
    
    public static function getTableName(): string {
        return static::$tableName;
    }
    
    public static function create(array $data): static {
        $instance = new static();
        foreach ($data as $key => $value) {
            $instance->$key = $value;
        }
        return $instance;
    }
    
    public static function findById($id): ?static {
        // Simulate database lookup
        return static::create(['id' => $id]);
    }
    
    public function save(): bool {
        // Simulate save operation
        return true;
    }
    
    public function delete(): bool {
        // Simulate delete operation
        return true;
    }
}

class User extends BaseModel {
    protected static $tableName = 'users';
    
    public $id;
    public $name;
    public $email;
    
    public function getFullInfo(): string {
        return "User: {$this->name} ({$this->email})";
    }
    
    public static function findByEmail(string $email): ?static {
        // Simulate email lookup
        return static::create(['email' => $email, 'name' => 'John Doe']);
    }
}

// File handling functions
function readFileContents($filename): string {
    if (!file_exists($filename)) {
        throw new RuntimeException("File not found: $filename");
    }
    
    $contents = file_get_contents($filename);
    if ($contents === false) {
        throw new RuntimeException("Failed to read file: $filename");
    }
    
    return $contents;
}

function writeFileContents($filename, $data): bool {
    $result = file_put_contents($filename, $data);
    return $result !== false;
}

function processCSV($filename): array {
    $data = [];
    $handle = fopen($filename, 'r');
    
    if ($handle === false) {
        throw new RuntimeException("Cannot open file: $filename");
    }
    
    try {
        while (($row = fgetcsv($handle)) !== false) {
            $data[] = $row;
        }
    } finally {
        fclose($handle);
    }
    
    return $data;
}

// Database-like functions
function connectDatabase($host, $user, $password, $database) {
    // Simulate database connection
    return new stdClass();
}

function executeQuery($connection, $query, $params = []) {
    // Simulate query execution
    return [];
}

function prepareStatement($connection, $query) {
    // Simulate prepared statement
    return new stdClass();
}

// Utility functions
function sanitizeInput($input): string {
    return htmlspecialchars(strip_tags(trim($input)), ENT_QUOTES, 'UTF-8');
}

function validateEmail($email): bool {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

function generateHash($data, $salt = ''): string {
    return hash('sha256', $data . $salt);
}

function formatCurrency($amount, $currency = 'USD'): string {
    return $currency . ' ' . number_format($amount, 2);
}

function calculateAge($birthdate): int {
    $birth = new DateTime($birthdate);
    $today = new DateTime();
    return $today->diff($birth)->y;
}

// Testing functions (PHPUnit style)
function testAddNumbers() {
    $result = addNumbers(2, 3);
    assert($result === 5, "addNumbers(2, 3) should return 5");
}

function testPersonClass() {
    $person = new Person("John", 30);
    assert($person->getName() === "John", "getName should return John");
    assert($person->getAge() === 30, "getAge should return 30");
    assert($person->isAdult() === true, "isAdult should return true");
}

function testRectangleClass() {
    $rect = new Rectangle(5.0, 3.0);
    assert($rect->getArea() === 15.0, "Area should be 15.0");
    assert($rect->getPerimeter() === 16.0, "Perimeter should be 16.0");
}

// Run the main function
if (php_sapi_name() === 'cli') {
    main();
}

?>
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic functions
    "main", "addNumbers", "greet", "greetWithDefault", "addIntegers", "divideNumbers",
    "processString", "processValue", "sum", "printf", "processArray", "filterArray",
    "swapValues", "incrementValue",
    # Person class methods
    "__construct", "__destruct", "__toString", "__get", "__set", "__call",
    "getName", "getAge", "setName", "setAge", "isAdult", "getInfo",
    "createDefault", "fromArray", "validateAge", "formatName",
    # Animal abstract class
    "makeSound", "getSpecies",
    # Dog class methods
    "getBreed", "fetch",
    # Rectangle class methods
    "draw", "getArea", "getPerimeter", "setColor", "getColor",
    "getWidth", "getHeight", "scale",
    # Trait methods
    "log", "getLogs", "clearLogs", "setCache", "getCache", "clearCache",
    # Service class methods
    "processData",
    # Closure functions
    "createAdder", "processWithCallback", "demonstrateClosures",
    # Generator functions
    "fibonacci", "numberGenerator", "readLines",
    # Exception handling
    "getErrorCode", "validateData", "processDataSafely",
    # Namespace functions
    "formatText", "slugify", "flattenArray", "groupBy",
    # Magic methods
    "__isset", "__unset", "__invoke", "__clone", "__serialize", "__unserialize",
    "__callStatic",
    # Model methods
    "getTableName", "create", "findById", "save", "delete", "getFullInfo", "findByEmail",
    # File functions
    "readFileContents", "writeFileContents", "processCSV",
    # Database functions
    "connectDatabase", "executeQuery", "prepareStatement",
    # Utility functions
    "sanitizeInput", "validateEmail", "generateHash", "formatCurrency", "calculateAge",
    # Test functions
    "testAddNumbers", "testPersonClass", "testRectangleClass"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestPHPTLDRFormatter:
    """Test class for PHP-specific function detection in TLDR formatter."""
    
    def test_php_function_detection_via_highlight_api(self):
        """Test PHP function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        
        # Use the highlight() function from __init__.py
        result = highlight(PHP_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} PHP functions")
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
    
    def test_php_simple_function_detection(self):
        """Test detection of simple PHP functions"""
        simple_code = """
<?php
function hello() {
    echo "Hello, World!";
}

function add($a, $b) {
    return $a + $b;
}

function greet($name) {
    echo "Hello, " . $name;
}

function divide($a, $b) {
    if ($b == 0) {
        throw new Exception("Division by zero");
    }
    return $a / $b;
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["hello", "add", "greet", "divide"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_php_class_methods_detection(self):
        """Test detection of PHP class methods"""
        class_code = """
<?php
class TestClass {
    private $value;
    
    public function __construct($value) {
        $this->value = $value;
    }
    
    public function getValue() {
        return $this->value;
    }
    
    public function setValue($value) {
        $this->value = $value;
    }
    
    public static function createDefault() {
        return new self(0);
    }
    
    protected function validateValue($value) {
        return is_numeric($value);
    }
    
    private function formatValue($value) {
        return number_format($value, 2);
    }
    
    public function __toString() {
        return "TestClass: " . $this->value;
    }
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(class_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["__construct", "getValue", "setValue", "createDefault", "validateValue", "formatValue", "__toString"]
        detected_class = [name for name in class_methods if name in result]
        
        assert len(detected_class) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class}")
    
    def test_php_interface_methods_detection(self):
        """Test detection of PHP interface methods"""
        interface_code = """
<?php
interface Drawable {
    public function draw();
    public function getArea();
    public function getPerimeter();
}

class Circle implements Drawable {
    private $radius;
    
    public function __construct($radius) {
        $this->radius = $radius;
    }
    
    public function draw() {
        return "Drawing circle with radius " . $this->radius;
    }
    
    public function getArea() {
        return pi() * $this->radius * $this->radius;
    }
    
    public function getPerimeter() {
        return 2 * pi() * $this->radius;
    }
    
    public function getRadius() {
        return $this->radius;
    }
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(interface_code, lexer, formatter)
        
        assert result is not None
        
        # Check for interface method detection
        interface_methods = ["draw", "getArea", "getPerimeter", "getRadius"]
        detected_interface = [name for name in interface_methods if name in result]
        
        assert len(detected_interface) > 0, f"No interface methods detected: {result}"
        print(f"Detected interface methods: {detected_interface}")
    
    def test_php_magic_methods_detection(self):
        """Test detection of PHP magic methods"""
        magic_code = """
<?php
class MagicClass {
    private $data = [];
    
    public function __construct($data = []) {
        $this->data = $data;
    }
    
    public function __get($key) {
        return $this->data[$key] ?? null;
    }
    
    public function __set($key, $value) {
        $this->data[$key] = $value;
    }
    
    public function __isset($key) {
        return isset($this->data[$key]);
    }
    
    public function __unset($key) {
        unset($this->data[$key]);
    }
    
    public function __call($method, $args) {
        throw new BadMethodCallException("Method $method not found");
    }
    
    public static function __callStatic($method, $args) {
        return new static();
    }
    
    public function __toString() {
        return json_encode($this->data);
    }
    
    public function __invoke($key = null) {
        return $key ? $this->data[$key] : $this->data;
    }
    
    public function __clone() {
        $this->data = array_map(function($item) {
            return is_object($item) ? clone $item : $item;
        }, $this->data);
    }
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(magic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for magic method detection
        magic_methods = ["__construct", "__get", "__set", "__isset", "__unset", "__call", "__callStatic", "__toString", "__invoke", "__clone"]
        detected_magic = [name for name in magic_methods if name in result]
        
        assert len(detected_magic) > 0, f"No magic methods detected: {result}"
        print(f"Detected magic methods: {detected_magic}")
    
    def test_php_trait_methods_detection(self):
        """Test detection of PHP trait methods"""
        trait_code = """
<?php
trait Loggable {
    protected $logs = [];
    
    public function log($message) {
        $this->logs[] = date('Y-m-d H:i:s') . ': ' . $message;
    }
    
    public function getLogs() {
        return $this->logs;
    }
    
    public function clearLogs() {
        $this->logs = [];
    }
}

trait Cacheable {
    private $cache = [];
    
    public function setCache($key, $value) {
        $this->cache[$key] = $value;
    }
    
    public function getCache($key) {
        return $this->cache[$key] ?? null;
    }
    
    public function hasCache($key) {
        return isset($this->cache[$key]);
    }
}

class Service {
    use Loggable, Cacheable;
    
    public function processData($data) {
        $this->log('Processing data');
        
        $cacheKey = md5(serialize($data));
        if ($this->hasCache($cacheKey)) {
            return $this->getCache($cacheKey);
        }
        
        $result = array_map('strtoupper', $data);
        $this->setCache($cacheKey, $result);
        
        return $result;
    }
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(trait_code, lexer, formatter)
        
        assert result is not None
        
        # Check for trait method detection
        trait_methods = ["log", "getLogs", "clearLogs", "setCache", "getCache", "hasCache", "processData"]
        detected_traits = [name for name in trait_methods if name in result]
        
        assert len(detected_traits) > 0, f"No trait methods detected: {result}"
        print(f"Detected trait methods: {detected_traits}")
    
    def test_php_anonymous_function_detection(self):
        """Test detection of PHP anonymous functions and closures"""
        closure_code = """
<?php
function createMultiplier($factor) {
    return function($number) use ($factor) {
        return $number * $factor;
    };
}

function processArray($array, $callback) {
    return array_map($callback, $array);
}

function demonstrateClosures() {
    $numbers = [1, 2, 3, 4, 5];
    
    // Anonymous function
    $doubled = array_map(function($n) {
        return $n * 2;
    }, $numbers);
    
    // Closure with use
    $multiplier = 3;
    $tripled = array_map(function($n) use ($multiplier) {
        return $n * $multiplier;
    }, $numbers);
    
    // Arrow function (PHP 7.4+)
    $squared = array_map(fn($n) => $n * $n, $numbers);
    
    return compact('doubled', 'tripled', 'squared');
}

$adder = function($a, $b) {
    return $a + $b;
};

$calculator = function($operation) {
    return function($a, $b) use ($operation) {
        switch ($operation) {
            case 'add': return $a + $b;
            case 'multiply': return $a * $b;
            default: return 0;
        }
    };
};
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(closure_code, lexer, formatter)
        
        assert result is not None
        
        # Check for closure function detection
        closure_functions = ["createMultiplier", "processArray", "demonstrateClosures"]
        detected_closures = [name for name in closure_functions if name in result]
        
        assert len(detected_closures) > 0, f"No closure functions detected: {result}"
        print(f"Detected closure functions: {detected_closures}")
    
    def test_php_generator_function_detection(self):
        """Test detection of PHP generator functions"""
        generator_code = """
<?php
function simpleGenerator() {
    yield 1;
    yield 2;
    yield 3;
}

function fibonacci($limit) {
    $a = 0;
    $b = 1;
    
    yield $a;
    yield $b;
    
    while ($a + $b < $limit) {
        $c = $a + $b;
        yield $c;
        $a = $b;
        $b = $c;
    }
}

function numberRange($start, $end) {
    for ($i = $start; $i <= $end; $i++) {
        yield $i;
    }
}

function readFileLines($filename) {
    $handle = fopen($filename, 'r');
    if ($handle) {
        try {
            while (($line = fgets($handle)) !== false) {
                yield rtrim($line);
            }
        } finally {
            fclose($handle);
        }
    }
}

function keyValueGenerator() {
    yield 'name' => 'John';
    yield 'age' => 30;
    yield 'city' => 'New York';
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(generator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generator function detection
        generator_functions = ["simpleGenerator", "fibonacci", "numberRange", "readFileLines", "keyValueGenerator"]
        detected_generators = [name for name in generator_functions if name in result]
        
        assert len(detected_generators) > 0, f"No generator functions detected: {result}"
        print(f"Detected generator functions: {detected_generators}")
    
    def test_php_namespace_function_detection(self):
        """Test detection of PHP namespace functions"""
        namespace_code = """
<?php
namespace App\\Utils;

function formatString($string) {
    return ucwords(strtolower(trim($string)));
}

function validateEmail($email) {
    return filter_var($email, FILTER_VALIDATE_EMAIL) !== false;
}

namespace App\\Database;

function connect($host, $user, $password, $database) {
    return new \\PDO("mysql:host=$host;dbname=$database", $user, $password);
}

function executeQuery($connection, $query, $params = []) {
    $stmt = $connection->prepare($query);
    $stmt->execute($params);
    return $stmt->fetchAll();
}

namespace App\\Http;

class Request {
    public function getParameter($name) {
        return $_GET[$name] ?? $_POST[$name] ?? null;
    }
    
    public function isPost() {
        return $_SERVER['REQUEST_METHOD'] === 'POST';
    }
    
    public function getHeaders() {
        return getallheaders();
    }
}

function handleRequest(Request $request) {
    if ($request->isPost()) {
        return processPostRequest($request);
    }
    return processGetRequest($request);
}

function processPostRequest($request) {
    return ['status' => 'POST processed'];
}

function processGetRequest($request) {
    return ['status' => 'GET processed'];
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(namespace_code, lexer, formatter)
        
        assert result is not None
        
        # Check for namespace function detection
        namespace_functions = ["formatString", "validateEmail", "connect", "executeQuery", "getParameter", "isPost", "getHeaders", "handleRequest", "processPostRequest", "processGetRequest"]
        detected_namespace = [name for name in namespace_functions if name in result]
        
        assert len(detected_namespace) > 0, f"No namespace functions detected: {result}"
        print(f"Detected namespace functions: {detected_namespace}")
    
    def test_php_language_detection(self):
        """Test that PHP language is properly detected"""
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        
        # Verify language detection
        detected_lang = formatter._detect_language()
        assert detected_lang == 'php', f"PHP language not properly detected, got: {detected_lang}"
    
    def test_php_type_hint_function_detection(self):
        """Test detection of PHP functions with type hints"""
        type_hint_code = """
<?php
function addNumbers(int $a, int $b): int {
    return $a + $b;
}

function processString(?string $input): ?string {
    return $input ? strtoupper($input) : null;
}

function handleValue(int|float $value): string {
    return "Value: " . $value;
}

function processArray(array $items, callable $callback): array {
    return array_map($callback, $items);
}

class TypedClass {
    public function setData(array $data): self {
        $this->data = $data;
        return $this;
    }
    
    public function getData(): array {
        return $this->data ?? [];
    }
    
    public function findItem(string $key): mixed {
        return $this->data[$key] ?? null;
    }
    
    public function hasItem(string $key): bool {
        return isset($this->data[$key]);
    }
}

function createUser(string $name, int $age, ?string $email = null): object {
    return (object) compact('name', 'age', 'email');
}
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(type_hint_code, lexer, formatter)
        
        assert result is not None
        
        # Check for type hint function detection
        type_hint_functions = ["addNumbers", "processString", "handleValue", "processArray", "setData", "getData", "findItem", "hasItem", "createUser"]
        detected_type_hints = [name for name in type_hint_functions if name in result]
        
        assert len(detected_type_hints) > 0, f"No type hint functions detected: {result}"
        print(f"Detected type hint functions: {detected_type_hints}")
    
    def test_empty_php_file(self):
        """Test handling of empty PHP file"""
        empty_code = """
<?php
// Just comments and variables
$globalVar = "test";
define('CONSTANT', 123);

// No functions defined
?>
"""
        
        lexer = PhpLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='php')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestPHPTLDRFormatter()
    test.test_php_function_detection_via_highlight_api()
    print("PHP TLDR formatter test completed successfully!")