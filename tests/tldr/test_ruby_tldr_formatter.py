"""
    Ruby TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Ruby-specific function detection using the highlight() API.

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
from pygments_tldr.lexers.ruby import RubyLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Ruby code with known number of functions
RUBY_TEST_CODE = """
#!/usr/bin/env ruby

# Ruby sample code for testing function detection

# Global variables
$global_var = "initialized"
@@class_var = 0

# Constants
MAX_SIZE = 100
MIN_SIZE = 1

# Simple methods
def main
  puts "Hello, Ruby!"
  result = add_numbers(5, 3)
  puts "Result: #{result}"
end

def add_numbers(a, b)
  a + b
end

def greet(name)
  puts "Hello, #{name}!"
end

# Method with default parameters
def greet_with_default(name, greeting = "Hello")
  puts "#{greeting}, #{name}!"
end

# Method with keyword arguments
def create_user(name:, age:, email: nil)
  {
    name: name,
    age: age,
    email: email
  }
end

# Method with splat operators
def sum(*numbers)
  numbers.reduce(0, :+)
end

def process_options(**options)
  options.each do |key, value|
    puts "#{key}: #{value}"
  end
end

# Method with block
def each_item(items, &block)
  items.each(&block)
end

def with_timing
  start_time = Time.now
  result = yield
  end_time = Time.now
  puts "Execution time: #{end_time - start_time} seconds"
  result
end

# Method with question mark (predicate)
def empty?(collection)
  collection.nil? || collection.empty?
end

def positive?(number)
  number > 0
end

# Method with exclamation mark (mutating)
def upcase!(string)
  string.upcase!
end

def sort_array!(array)
  array.sort!
end

# Class definitions and methods
class Person
  attr_reader :name, :age
  attr_writer :email
  attr_accessor :phone
  
  # Class variables and methods
  @@population = 0
  
  def self.population
    @@population
  end
  
  def self.create_anonymous
    new("Anonymous", 0)
  end
  
  # Constructor
  def initialize(name, age, email = nil)
    @name = name
    @age = age
    @email = email
    @phone = nil
    @@population += 1
  end
  
  # Instance methods
  def to_s
    "#{@name} (#{@age} years old)"
  end
  
  def inspect
    "#<Person:#{object_id} @name=#{@name.inspect} @age=#{@age}>"
  end
  
  def greet
    "Hello, I'm #{@name}"
  end
  
  def birthday!
    @age += 1
    puts "Happy birthday! Now #{@age} years old."
  end
  
  def adult?
    @age >= 18
  end
  
  def email
    @email || "No email provided"
  end
  
  def update_info(name: nil, age: nil, email: nil)
    @name = name if name
    @age = age if age
    @email = email if email
    self
  end
  
  # Private methods
  private
  
  def validate_age(age)
    age.is_a?(Integer) && age >= 0
  end
  
  def format_email(email)
    email&.strip&.downcase
  end
  
  # Protected methods
  protected
  
  def same_age?(other_person)
    @age == other_person.age
  end
end

# Module definitions
module Greetings
  def hello
    "Hello from module!"
  end
  
  def goodbye
    "Goodbye from module!"
  end
  
  def self.default_greeting
    "Default greeting"
  end
  
  module_function :hello, :goodbye
end

module Enumerable
  def average
    return 0 if empty?
    sum.to_f / size
  end
  
  def median
    sorted = sort
    length = sorted.length
    if length.odd?
      sorted[length / 2]
    else
      (sorted[length / 2 - 1] + sorted[length / 2]) / 2.0
    end
  end
end

# Class with modules
class Student < Person
  include Greetings
  extend Greetings
  
  def initialize(name, age, student_id)
    super(name, age)
    @student_id = student_id
  end
  
  def study(subject)
    puts "#{@name} is studying #{subject}"
  end
  
  def to_s
    "Student: #{super} (ID: #{@student_id})"
  end
  
  # Override parent method
  def greet
    "Hi, I'm #{@name}, a student!"
  end
  
  # Class method
  def self.create_with_id(name, age, id)
    new(name, age, id)
  end
end

# Singleton methods
class Calculator
  def self.add(a, b)
    a + b
  end
  
  def self.subtract(a, b)
    a - b
  end
  
  def self.multiply(a, b)
    a * b
  end
  
  def self.divide(a, b)
    raise "Division by zero" if b == 0
    a.to_f / b
  end
end

# Metaprogramming methods
class DynamicClass
  def self.define_getter(name)
    define_method(name) do
      instance_variable_get("@#{name}")
    end
  end
  
  def self.define_setter(name)
    define_method("#{name}=") do |value|
      instance_variable_set("@#{name}", value)
    end
  end
  
  def method_missing(method_name, *args, &block)
    if method_name.to_s.start_with?('get_')
      attr_name = method_name.to_s[4..-1]
      instance_variable_get("@#{attr_name}")
    elsif method_name.to_s.end_with?('=')
      attr_name = method_name.to_s[0..-2]
      instance_variable_set("@#{attr_name}", args.first)
    else
      super
    end
  end
  
  def respond_to_missing?(method_name, include_private = false)
    method_name.to_s.start_with?('get_') || 
    method_name.to_s.end_with?('=') || 
    super
  end
end

# Proc and Lambda
def create_multiplier(factor)
  lambda { |x| x * factor }
end

def create_proc(message)
  Proc.new { |name| puts "#{message}, #{name}!" }
end

def with_proc(&block)
  block.call("World") if block_given?
end

# Iterator methods
def fibonacci(limit)
  a, b = 0, 1
  while a < limit
    yield a
    a, b = b, a + b
  end
end

def each_pair(array)
  (0...array.length).step(2) do |i|
    yield array[i], array[i + 1] if array[i + 1]
  end
end

def retry_operation(max_attempts = 3)
  attempts = 0
  begin
    attempts += 1
    yield
  rescue StandardError => e
    if attempts < max_attempts
      puts "Attempt #{attempts} failed: #{e.message}. Retrying..."
      retry
    else
      puts "All attempts failed."
      raise
    end
  end
end

# Exception handling
class CustomError < StandardError
  attr_reader :error_code
  
  def initialize(message, error_code = nil)
    super(message)
    @error_code = error_code
  end
  
  def to_s
    if @error_code
      "#{super} (Code: #{@error_code})"
    else
      super
    end
  end
end

def validate_input(input)
  raise ArgumentError, "Input cannot be nil" if input.nil?
  raise CustomError.new("Input cannot be empty", 1001) if input.empty?
  true
end

def process_safely(input)
  validate_input(input)
  input.upcase
rescue CustomError => e
  puts "Custom error: #{e.message}"
  nil
rescue StandardError => e
  puts "Standard error: #{e.message}"
  nil
end

# File operations
def read_file(filename)
  File.open(filename, 'r') do |file|
    file.read
  end
rescue IOError => e
  puts "Error reading file: #{e.message}"
  nil
end

def write_file(filename, content)
  File.open(filename, 'w') do |file|
    file.write(content)
  end
  true
rescue IOError => e
  puts "Error writing file: #{e.message}"
  false
end

def process_csv(filename)
  require 'csv'
  data = []
  CSV.foreach(filename, headers: true) do |row|
    data << row.to_h
  end
  data
rescue StandardError => e
  puts "Error processing CSV: #{e.message}"
  []
end

# Thread operations
def run_in_thread(&block)
  Thread.new(&block)
end

def parallel_map(array, &block)
  threads = array.map do |item|
    Thread.new { block.call(item) }
  end
  threads.map(&:value)
end

# Regular expressions
def extract_emails(text)
  email_regex = /\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b/
  text.scan(email_regex)
end

def validate_phone(phone)
  phone_regex = /^\\(?([0-9]{3})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/
  !phone_regex.match(phone).nil?
end

# Hash and Array operations
def deep_merge(hash1, hash2)
  hash1.merge(hash2) do |key, old_val, new_val|
    if old_val.is_a?(Hash) && new_val.is_a?(Hash)
      deep_merge(old_val, new_val)
    else
      new_val
    end
  end
end

def flatten_hash(hash, parent_key = '', separator = '.')
  hash.each_with_object({}) do |(key, value), result|
    new_key = parent_key.empty? ? key.to_s : "#{parent_key}#{separator}#{key}"
    if value.is_a?(Hash)
      result.merge!(flatten_hash(value, new_key, separator))
    else
      result[new_key] = value
    end
  end
end

# String operations
def titleize(string)
  string.split.map(&:capitalize).join(' ')
end

def slugify(string)
  string.downcase.gsub(/[^a-z0-9]+/, '-').gsub(/-+/, '-').gsub(/^-|-$/, '')
end

def truncate(string, length, omission = '...')
  return string if string.length <= length
  string[0, length - omission.length] + omission
end

# Date and time operations
def days_between(date1, date2)
  (date2 - date1).to_i.abs
end

def format_duration(seconds)
  hours = seconds / 3600
  minutes = (seconds % 3600) / 60
  remaining_seconds = seconds % 60
  
  if hours > 0
    "#{hours}h #{minutes}m #{remaining_seconds}s"
  elsif minutes > 0
    "#{minutes}m #{remaining_seconds}s"
  else
    "#{remaining_seconds}s"
  end
end

# Testing methods (RSpec style)
def expect_equal(actual, expected)
  if actual == expected
    puts "✓ Test passed: #{actual} == #{expected}"
  else
    puts "✗ Test failed: expected #{expected}, got #{actual}"
  end
end

def test_add_numbers
  result = add_numbers(2, 3)
  expect_equal(result, 5)
end

def test_person_creation
  person = Person.new("John", 30)
  expect_equal(person.name, "John")
  expect_equal(person.age, 30)
  expect_equal(person.adult?, true)
end

def test_calculator
  expect_equal(Calculator.add(2, 3), 5)
  expect_equal(Calculator.multiply(4, 5), 20)
end

# DSL-like methods
def configure(&block)
  config = Configuration.new
  config.instance_eval(&block) if block_given?
  config
end

class Configuration
  attr_accessor :host, :port, :timeout
  
  def initialize
    @host = 'localhost'
    @port = 3000
    @timeout = 30
  end
  
  def database(&block)
    @database_config = DatabaseConfig.new
    @database_config.instance_eval(&block) if block_given?
    @database_config
  end
end

class DatabaseConfig
  attr_accessor :adapter, :host, :username, :password
  
  def initialize
    @adapter = 'postgresql'
    @host = 'localhost'
  end
end

# Operator overloading
class Vector
  attr_reader :x, :y
  
  def initialize(x, y)
    @x, @y = x, y
  end
  
  def +(other)
    Vector.new(@x + other.x, @y + other.y)
  end
  
  def -(other)
    Vector.new(@x - other.x, @y - other.y)
  end
  
  def *(scalar)
    Vector.new(@x * scalar, @y * scalar)
  end
  
  def ==(other)
    @x == other.x && @y == other.y
  end
  
  def to_s
    "(#{@x}, #{@y})"
  end
end

# Finalizer
def setup_finalizer(object, &cleanup_block)
  ObjectSpace.define_finalizer(object, cleanup_block)
end

# Run main if this is the main file
if __FILE__ == $0
  main
end
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic methods
    "main", "add_numbers", "greet", "greet_with_default", "create_user",
    "sum", "process_options", "each_item", "with_timing",
    # Predicate and mutating methods
    "empty?", "positive?", "upcase!", "sort_array!",
    # Person class methods
    "population", "create_anonymous", "initialize", "to_s", "inspect",
    "greet", "birthday!", "adult?", "email", "update_info",
    "validate_age", "format_email", "same_age?",
    # Module methods
    "hello", "goodbye", "default_greeting", "average", "median",
    # Student class methods
    "study", "create_with_id",
    # Calculator class methods
    "add", "subtract", "multiply", "divide",
    # Metaprogramming methods
    "define_getter", "define_setter", "method_missing", "respond_to_missing?",
    # Proc and Lambda methods
    "create_multiplier", "create_proc", "with_proc",
    # Iterator methods
    "fibonacci", "each_pair", "retry_operation",
    # Exception handling
    "validate_input", "process_safely",
    # File operations
    "read_file", "write_file", "process_csv",
    # Thread operations
    "run_in_thread", "parallel_map",
    # Regular expressions
    "extract_emails", "validate_phone",
    # Hash and Array operations
    "deep_merge", "flatten_hash",
    # String operations
    "titleize", "slugify", "truncate",
    # Date and time operations
    "days_between", "format_duration",
    # Testing methods
    "expect_equal", "test_add_numbers", "test_person_creation", "test_calculator",
    # DSL methods
    "configure", "database",
    # Operator methods
    "+", "-", "*", "==",
    # Finalizer
    "setup_finalizer"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestRubyTLDRFormatter:
    """Test class for Ruby-specific function detection in TLDR formatter."""
    
    def test_ruby_function_detection_via_highlight_api(self):
        """Test Ruby function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        
        # Use the highlight() function from __init__.py
        result = highlight(RUBY_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Ruby functions")
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
    
    def test_ruby_simple_method_detection(self):
        """Test detection of simple Ruby methods"""
        simple_code = """
def hello
  puts "Hello, World!"
end

def add(a, b)
  a + b
end

def greet(name)
  puts "Hello, #{name}!"
end

def empty?(array)
  array.nil? || array.empty?
end

def upcase!(string)
  string.upcase!
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple method detection
        expected_simple = ["hello", "add", "greet", "empty?", "upcase!"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple methods detected: {result}"
        print(f"Detected simple methods: {detected_simple}")
    
    def test_ruby_class_methods_detection(self):
        """Test detection of Ruby class methods"""
        class_code = """
class TestClass
  attr_reader :name
  attr_writer :email
  attr_accessor :age
  
  def initialize(name, age)
    @name = name
    @age = age
  end
  
  def to_s
    "#{@name} (#{@age})"
  end
  
  def greet
    "Hello, I'm #{@name}"
  end
  
  def self.create_default
    new("Unknown", 0)
  end
  
  def adult?
    @age >= 18
  end
  
  private
  
  def validate_age(age)
    age.is_a?(Integer) && age >= 0
  end
  
  protected
  
  def same_age?(other)
    @age == other.age
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(class_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["initialize", "to_s", "greet", "create_default", "adult?", "validate_age", "same_age?"]
        detected_class = [name for name in class_methods if name in result]
        
        assert len(detected_class) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class}")
    
    def test_ruby_module_methods_detection(self):
        """Test detection of Ruby module methods"""
        module_code = """
module Greetings
  def hello
    "Hello from module!"
  end
  
  def goodbye
    "Goodbye!"
  end
  
  def self.default_greeting
    "Default greeting"
  end
  
  module_function :hello, :goodbye
end

module Enumerable
  def average
    return 0 if empty?
    sum.to_f / size
  end
  
  def median
    sorted = sort
    sorted[sorted.length / 2]
  end
end

class TestClass
  include Greetings
  extend Greetings
  
  def test_method
    hello
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(module_code, lexer, formatter)
        
        assert result is not None
        
        # Check for module method detection
        module_methods = ["hello", "goodbye", "default_greeting", "average", "median", "test_method"]
        detected_module = [name for name in module_methods if name in result]
        
        assert len(detected_module) > 0, f"No module methods detected: {result}"
        print(f"Detected module methods: {detected_module}")
    
    def test_ruby_block_methods_detection(self):
        """Test detection of Ruby methods with blocks"""
        block_code = """
def each_item(items, &block)
  items.each(&block)
end

def with_timing
  start_time = Time.now
  result = yield
  end_time = Time.now
  puts "Time: #{end_time - start_time}"
  result
end

def fibonacci(limit)
  a, b = 0, 1
  while a < limit
    yield a
    a, b = b, a + b
  end
end

def retry_operation(max_attempts = 3)
  attempts = 0
  begin
    attempts += 1
    yield
  rescue => e
    retry if attempts < max_attempts
    raise
  end
end

# Block usage
def process_data(data)
  data.map { |item| item.upcase }
    .select { |item| item.length > 2 }
    .each { |item| puts item }
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(block_code, lexer, formatter)
        
        assert result is not None
        
        # Check for block method detection
        block_methods = ["each_item", "with_timing", "fibonacci", "retry_operation", "process_data"]
        detected_blocks = [name for name in block_methods if name in result]
        
        assert len(detected_blocks) > 0, f"No block methods detected: {result}"
        print(f"Detected block methods: {detected_blocks}")
    
    def test_ruby_metaprogramming_detection(self):
        """Test detection of Ruby metaprogramming methods"""
        meta_code = """
class DynamicClass
  def self.define_getter(name)
    define_method(name) do
      instance_variable_get("@#{name}")
    end
  end
  
  def self.define_setter(name)
    define_method("#{name}=") do |value|
      instance_variable_set("@#{name}", value)
    end
  end
  
  def method_missing(method_name, *args, &block)
    if method_name.to_s.start_with?('get_')
      attr_name = method_name.to_s[4..-1]
      instance_variable_get("@#{attr_name}")
    else
      super
    end
  end
  
  def respond_to_missing?(method_name, include_private = false)
    method_name.to_s.start_with?('get_') || super
  end
end

# Class methods and singleton methods
obj = Object.new

def obj.singleton_method
  "I'm a singleton method"
end

class << obj
  def another_singleton
    "Another singleton method"
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(meta_code, lexer, formatter)
        
        assert result is not None
        
        # Check for metaprogramming method detection
        meta_methods = ["define_getter", "define_setter", "method_missing", "respond_to_missing?", "singleton_method", "another_singleton"]
        detected_meta = [name for name in meta_methods if name in result]
        
        assert len(detected_meta) > 0, f"No metaprogramming methods detected: {result}"
        print(f"Detected metaprogramming methods: {detected_meta}")
    
    def test_ruby_proc_lambda_detection(self):
        """Test detection of Ruby Proc and Lambda methods"""
        proc_code = """
def create_multiplier(factor)
  lambda { |x| x * factor }
end

def create_proc(message)
  Proc.new { |name| puts "#{message}, #{name}!" }
end

def with_proc(&block)
  block.call("World") if block_given?
end

# Different ways to create procs
multiply_by_two = proc { |x| x * 2 }
add_one = ->(x) { x + 1 }

def apply_proc(value, operation)
  operation.call(value)
end

def compose_functions(f, g)
  lambda { |x| f.call(g.call(x)) }
end

# Method that returns a proc
def counter(start = 0)
  count = start
  lambda { count += 1 }
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(proc_code, lexer, formatter)
        
        assert result is not None
        
        # Check for proc/lambda method detection
        proc_methods = ["create_multiplier", "create_proc", "with_proc", "apply_proc", "compose_functions", "counter"]
        detected_procs = [name for name in proc_methods if name in result]
        
        assert len(detected_procs) > 0, f"No proc/lambda methods detected: {result}"
        print(f"Detected proc/lambda methods: {detected_procs}")
    
    def test_ruby_exception_handling_detection(self):
        """Test detection of Ruby exception handling methods"""
        exception_code = """
class CustomError < StandardError
  attr_reader :error_code
  
  def initialize(message, error_code = nil)
    super(message)
    @error_code = error_code
  end
  
  def to_s
    if @error_code
      "#{super} (Code: #{@error_code})"
    else
      super
    end
  end
end

def validate_input(input)
  raise ArgumentError, "Input cannot be nil" if input.nil?
  raise CustomError.new("Input cannot be empty", 1001) if input.empty?
  true
end

def process_safely(input)
  validate_input(input)
  input.upcase
rescue CustomError => e
  puts "Custom error: #{e.message}"
  nil
rescue StandardError => e
  puts "Standard error: #{e.message}"
  nil
ensure
  puts "Processing completed"
end

def retry_with_backoff(max_attempts = 3)
  attempts = 0
  begin
    attempts += 1
    yield
  rescue => e
    if attempts < max_attempts
      sleep(2 ** attempts)
      retry
    else
      raise
    end
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(exception_code, lexer, formatter)
        
        assert result is not None
        
        # Check for exception handling method detection
        exception_methods = ["initialize", "to_s", "validate_input", "process_safely", "retry_with_backoff"]
        detected_exceptions = [name for name in exception_methods if name in result]
        
        assert len(detected_exceptions) > 0, f"No exception handling methods detected: {result}"
        print(f"Detected exception handling methods: {detected_exceptions}")
    
    def test_ruby_operator_methods_detection(self):
        """Test detection of Ruby operator methods"""
        operator_code = """
class Vector
  attr_reader :x, :y
  
  def initialize(x, y)
    @x, @y = x, y
  end
  
  def +(other)
    Vector.new(@x + other.x, @y + other.y)
  end
  
  def -(other)
    Vector.new(@x - other.x, @y - other.y)
  end
  
  def *(scalar)
    Vector.new(@x * scalar, @y * scalar)
  end
  
  def ==(other)
    @x == other.x && @y == other.y
  end
  
  def <=>(other)
    magnitude <=> other.magnitude
  end
  
  def [](index)
    case index
    when 0 then @x
    when 1 then @y
    else nil
    end
  end
  
  def []=(index, value)
    case index
    when 0 then @x = value
    when 1 then @y = value
    end
  end
  
  def to_s
    "(#{@x}, #{@y})"
  end
  
  def magnitude
    Math.sqrt(@x * @x + @y * @y)
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(operator_code, lexer, formatter)
        
        assert result is not None
        
        # Check for operator method detection
        operator_methods = ["initialize", "+", "-", "*", "==", "<=>", "[]", "[]=", "to_s", "magnitude"]
        detected_operators = [name for name in operator_methods if name in result]
        
        assert len(detected_operators) > 0, f"No operator methods detected: {result}"
        print(f"Detected operator methods: {detected_operators}")
    
    def test_ruby_language_detection(self):
        """Test that Ruby language is properly detected"""
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        
        # Verify language detection
        detected_lang = formatter._detect_language()
        assert detected_lang == 'ruby', f"Ruby language not properly detected, got: {detected_lang}"
    
    def test_ruby_keyword_argument_detection(self):
        """Test detection of Ruby methods with keyword arguments"""
        keyword_code = """
def create_user(name:, age:, email: nil, phone: nil)
  {
    name: name,
    age: age,
    email: email,
    phone: phone
  }
end

def process_options(**options)
  options.each do |key, value|
    puts "#{key}: #{value}"
  end
end

def flexible_method(required, optional = "default", *splat, keyword:, optional_keyword: nil, **kwargs)
  puts "Required: #{required}"
  puts "Optional: #{optional}"
  puts "Splat: #{splat}"
  puts "Keyword: #{keyword}"
  puts "Optional keyword: #{optional_keyword}"
  puts "Kwargs: #{kwargs}"
end

class Configuration
  def initialize(host: 'localhost', port: 3000, ssl: false)
    @host = host
    @port = port
    @ssl = ssl
  end
  
  def update(host: nil, port: nil, ssl: nil)
    @host = host if host
    @port = port if port
    @ssl = ssl unless ssl.nil?
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(keyword_code, lexer, formatter)
        
        assert result is not None
        
        # Check for keyword argument method detection
        keyword_methods = ["create_user", "process_options", "flexible_method", "initialize", "update"]
        detected_keywords = [name for name in keyword_methods if name in result]
        
        assert len(detected_keywords) > 0, f"No keyword argument methods detected: {result}"
        print(f"Detected keyword argument methods: {detected_keywords}")
    
    def test_ruby_test_methods_detection(self):
        """Test detection of Ruby test methods (RSpec/Test::Unit style)"""
        test_code = """
# Test::Unit style
class TestCalculator < Test::Unit::TestCase
  def test_addition
    assert_equal(5, Calculator.add(2, 3))
  end
  
  def test_subtraction
    assert_equal(1, Calculator.subtract(3, 2))
  end
  
  def setup
    @calculator = Calculator.new
  end
  
  def teardown
    @calculator = nil
  end
end

# RSpec style helper methods
def expect_equal(actual, expected)
  if actual == expected
    puts "✓ Test passed"
  else
    puts "✗ Test failed"
  end
end

def describe_calculator
  it_should_add_correctly
  it_should_handle_zero
end

def it_should_add_correctly
  result = Calculator.add(2, 3)
  expect_equal(result, 5)
end

def it_should_handle_zero
  result = Calculator.add(0, 5)
  expect_equal(result, 5)
end

# Benchmark methods
def benchmark_addition
  require 'benchmark'
  
  Benchmark.bm do |x|
    x.report("simple") { 1000.times { Calculator.add(2, 3) } }
    x.report("complex") { 1000.times { Calculator.add(rand(100), rand(100)) } }
  end
end
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(test_code, lexer, formatter)
        
        assert result is not None
        
        # Check for test method detection
        test_methods = ["test_addition", "test_subtraction", "setup", "teardown", "expect_equal", "describe_calculator", "it_should_add_correctly", "it_should_handle_zero", "benchmark_addition"]
        detected_tests = [name for name in test_methods if name in result]
        
        assert len(detected_tests) > 0, f"No test methods detected: {result}"
        print(f"Detected test methods: {detected_tests}")
    
    def test_empty_ruby_file(self):
        """Test handling of empty Ruby file"""
        empty_code = """
#!/usr/bin/env ruby

# Just comments and constants
MAX_SIZE = 100
$global_var = "test"
@@class_var = 0

# Require statements
require 'json'
require 'net/http'

# No methods defined
"""
        
        lexer = RubyLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='ruby')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestRubyTLDRFormatter()
    test.test_ruby_function_detection_via_highlight_api()
    print("Ruby TLDR formatter test completed successfully!")