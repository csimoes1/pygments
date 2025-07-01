"""
    Rust TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Rust-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.rust import RustLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Rust code with known number of functions
RUST_TEST_CODE = """
// Rust sample code for testing function detection
use std::collections::HashMap;
use std::fmt::Display;
use std::error::Error;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

// Simple functions
fn main() {
    println!("Hello, Rust!");
}

fn add_numbers(a: i32, b: i32) -> i32 {
    a + b
}

fn greet(name: &str) {
    println!("Hello, {}!", name);
}

// Function with multiple return types
fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        Err("Division by zero".to_string())
    } else {
        Ok(a / b)
    }
}

// Function with Option return type
fn find_item(items: &[i32], target: i32) -> Option<usize> {
    for (index, &item) in items.iter().enumerate() {
        if item == target {
            return Some(index);
        }
    }
    None
}

// Function with borrowing and lifetimes
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    
    &s[..]
}

// Generic functions
fn get_largest<T: PartialOrd + Copy>(list: &[T]) -> T {
    let mut largest = list[0];
    
    for &item in list {
        if item > largest {
            largest = item;
        }
    }
    
    largest
}

fn swap<T>(a: &mut T, b: &mut T) {
    std::mem::swap(a, b);
}

// Function with multiple generic parameters
fn compare_and_display<T, U>(a: T, b: U) -> String
where
    T: Display + PartialOrd,
    U: Display,
{
    format!("Comparing {} with {}", a, b)
}

// Struct definition with methods
#[derive(Debug, Clone)]
struct Rectangle {
    width: f64,
    height: f64,
}

impl Rectangle {
    // Associated function (constructor)
    fn new(width: f64, height: f64) -> Self {
        Rectangle { width, height }
    }
    
    // Method with &self
    fn area(&self) -> f64 {
        self.width * self.height
    }
    
    // Method with &mut self
    fn double_size(&mut self) {
        self.width *= 2.0;
        self.height *= 2.0;
    }
    
    // Method with self (takes ownership)
    fn into_square(self) -> Rectangle {
        let size = (self.width + self.height) / 2.0;
        Rectangle::new(size, size)
    }
    
    // Method with multiple parameters
    fn can_contain(&self, other: &Rectangle) -> bool {
        self.width >= other.width && self.height >= other.height
    }
    
    // Static method
    fn square(size: f64) -> Rectangle {
        Rectangle::new(size, size)
    }
}

// Trait definition
trait Drawable {
    fn draw(&self);
    fn area(&self) -> f64;
    
    // Default implementation
    fn describe(&self) {
        println!("This shape has an area of {}", self.area());
    }
}

// Implement trait for Rectangle
impl Drawable for Rectangle {
    fn draw(&self) {
        println!("Drawing rectangle {}x{}", self.width, self.height);
    }
    
    fn area(&self) -> f64 {
        self.width * self.height
    }
}

// Generic trait implementation
trait Container<T> {
    fn get(&self, index: usize) -> Option<&T>;
    fn push(&mut self, item: T);
    fn len(&self) -> usize;
    
    fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

// Enum with methods
#[derive(Debug, PartialEq)]
enum Direction {
    North,
    South,
    East,
    West,
}

impl Direction {
    fn opposite(&self) -> Direction {
        match self {
            Direction::North => Direction::South,
            Direction::South => Direction::North,
            Direction::East => Direction::West,
            Direction::West => Direction::East,
        }
    }
    
    fn is_horizontal(&self) -> bool {
        matches!(self, Direction::East | Direction::West)
    }
    
    fn turn_right(&self) -> Direction {
        match self {
            Direction::North => Direction::East,
            Direction::East => Direction::South,
            Direction::South => Direction::West,
            Direction::West => Direction::North,
        }
    }
}

// Async functions
async fn fetch_data(url: &str) -> Result<String, Box<dyn Error>> {
    // Simulated async operation
    tokio::time::sleep(Duration::from_millis(100)).await;
    Ok(format!("Data from {}", url))
}

async fn process_data(data: String) -> String {
    // Simulated processing
    tokio::time::sleep(Duration::from_millis(50)).await;
    data.to_uppercase()
}

async fn fetch_and_process(url: &str) -> Result<String, Box<dyn Error>> {
    let data = fetch_data(url).await?;
    let processed = process_data(data).await;
    Ok(processed)
}

// Closure functions
fn create_adder(x: i32) -> impl Fn(i32) -> i32 {
    move |y| x + y
}

fn apply_operation<F>(x: i32, y: i32, op: F) -> i32
where
    F: Fn(i32, i32) -> i32,
{
    op(x, y)
}

fn filter_and_map<T, U, F, P>(items: Vec<T>, predicate: P, mapper: F) -> Vec<U>
where
    F: Fn(T) -> U,
    P: Fn(&T) -> bool,
{
    items
        .into_iter()
        .filter(predicate)
        .map(mapper)
        .collect()
}

// Error handling functions
#[derive(Debug)]
struct CustomError {
    message: String,
}

impl CustomError {
    fn new(message: &str) -> Self {
        CustomError {
            message: message.to_string(),
        }
    }
}

impl Display for CustomError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        write!(f, "Custom error: {}", self.message)
    }
}

impl Error for CustomError {}

fn might_fail(input: i32) -> Result<i32, CustomError> {
    if input < 0 {
        Err(CustomError::new("Negative input not allowed"))
    } else {
        Ok(input * 2)
    }
}

fn handle_error() -> Result<(), Box<dyn Error>> {
    let result = might_fail(-5)?;
    println!("Result: {}", result);
    Ok(())
}

// Iterator functions
fn sum_even_squares(numbers: &[i32]) -> i32 {
    numbers
        .iter()
        .filter(|&&x| x % 2 == 0)
        .map(|&x| x * x)
        .sum()
}

fn collect_names(people: Vec<(String, i32)>) -> Vec<String> {
    people
        .into_iter()
        .filter(|(_, age)| *age >= 18)
        .map(|(name, _)| name)
        .collect()
}

// Pattern matching functions
fn describe_point(point: (i32, i32)) -> String {
    match point {
        (0, 0) => "Origin".to_string(),
        (x, 0) => format!("On x-axis at {}", x),
        (0, y) => format!("On y-axis at {}", y),
        (x, y) => format!("Point at ({}, {})", x, y),
    }
}

fn process_option(opt: Option<i32>) -> i32 {
    match opt {
        Some(value) => value * 2,
        None => 0,
    }
}

// Macro functions
macro_rules! vec_of_strings {
    ($($x:expr),*) => {
        vec![$(String::from($x)),*]
    };
}

fn use_macro() -> Vec<String> {
    vec_of_strings!["hello", "world", "rust"]
}

// Unsafe functions
unsafe fn dangerous_function() {
    // Unsafe operations would go here
    let raw_ptr = 0x123456 as *const i32;
    println!("Raw pointer: {:p}", raw_ptr);
}

fn safe_wrapper() {
    unsafe {
        dangerous_function();
    }
}

// Thread and concurrency functions
fn spawn_thread() -> thread::JoinHandle<i32> {
    thread::spawn(|| {
        let mut sum = 0;
        for i in 1..=10 {
            sum += i;
        }
        sum
    })
}

fn shared_data_example() {
    let data = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    
    for _ in 0..3 {
        let data = Arc::clone(&data);
        let handle = thread::spawn(move || {
            let mut num = data.lock().unwrap();
            *num += 1;
        });
        handles.push(handle);
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

// Module functions
mod math_utils {
    pub fn factorial(n: u64) -> u64 {
        match n {
            0 | 1 => 1,
            _ => n * factorial(n - 1),
        }
    }
    
    pub fn fibonacci(n: u32) -> u64 {
        match n {
            0 => 0,
            1 => 1,
            _ => fibonacci(n - 1) + fibonacci(n - 2),
        }
    }
    
    pub fn gcd(mut a: u64, mut b: u64) -> u64 {
        while b != 0 {
            let temp = b;
            b = a % b;
            a = temp;
        }
        a
    }
}

// Type alias and advanced functions
type Result<T> = std::result::Result<T, Box<dyn Error>>;

fn parse_config(input: &str) -> Result<HashMap<String, String>> {
    let mut config = HashMap::new();
    
    for line in input.lines() {
        if let Some((key, value)) = line.split_once('=') {
            config.insert(key.trim().to_string(), value.trim().to_string());
        }
    }
    
    Ok(config)
}

// Const functions
const fn const_factorial(n: u32) -> u32 {
    match n {
        0 | 1 => 1,
        _ => n * const_factorial(n - 1),
    }
}

const fn const_power(base: u32, exp: u32) -> u32 {
    let mut result = 1;
    let mut i = 0;
    while i < exp {
        result *= base;
        i += 1;
    }
    result
}

// Tests module
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_add_numbers() {
        assert_eq!(add_numbers(2, 3), 5);
    }
    
    #[test]
    fn test_rectangle_area() {
        let rect = Rectangle::new(5.0, 3.0);
        assert_eq!(rect.area(), 15.0);
    }
    
    #[test]
    fn test_direction_opposite() {
        assert_eq!(Direction::North.opposite(), Direction::South);
    }
}

// Documentation functions
/// Calculates the distance between two points
/// 
/// # Arguments
/// 
/// * `p1` - The first point as a tuple (x, y)
/// * `p2` - The second point as a tuple (x, y)
/// 
/// # Returns
/// 
/// The Euclidean distance between the points
/// 
/// # Examples
/// 
/// ```
/// let distance = calculate_distance((0.0, 0.0), (3.0, 4.0));
/// assert_eq!(distance, 5.0);
/// ```
fn calculate_distance(p1: (f64, f64), p2: (f64, f64)) -> f64 {
    let dx = p2.0 - p1.0;
    let dy = p2.1 - p1.1;
    (dx * dx + dy * dy).sqrt()
}

// Advanced lifetime functions
fn lifetime_example<'a, 'b>(x: &'a str, y: &'b str) -> &'a str
where
    'b: 'a,
{
    if x.len() > y.len() { x } else { y }
}

// Higher-order functions
fn compose<A, B, C, F, G>(f: F, g: G) -> impl Fn(A) -> C
where
    F: Fn(A) -> B,
    G: Fn(B) -> C,
{
    move |x| g(f(x))
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic functions
    "main", "add_numbers", "greet", "divide", "find_item",
    # Lifetime functions
    "longest", "first_word",
    # Generic functions
    "get_largest", "swap", "compare_and_display",
    # Rectangle methods
    "new", "area", "double_size", "into_square", "can_contain", "square",
    # Trait methods
    "draw", "describe", "get", "push", "len", "is_empty",
    # Enum methods
    "opposite", "is_horizontal", "turn_right",
    # Async functions
    "fetch_data", "process_data", "fetch_and_process",
    # Closure functions
    "create_adder", "apply_operation", "filter_and_map",
    # Error handling
    "new", "fmt", "might_fail", "handle_error",
    # Iterator functions
    "sum_even_squares", "collect_names",
    # Pattern matching
    "describe_point", "process_option",
    # Macro usage
    "use_macro",
    # Unsafe functions
    "dangerous_function", "safe_wrapper",
    # Concurrency
    "spawn_thread", "shared_data_example",
    # Module functions
    "factorial", "fibonacci", "gcd",
    # Advanced functions
    "parse_config",
    # Const functions
    "const_factorial", "const_power",
    # Test functions
    "test_add_numbers", "test_rectangle_area", "test_direction_opposite",
    # Documentation
    "calculate_distance",
    # Advanced lifetimes
    "lifetime_example",
    # Higher-order functions
    "compose"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestRustTLDRFormatter:
    """Test class for Rust-specific function detection in TLDR formatter."""
    
    def test_rust_function_detection_via_highlight_api(self):
        """Test Rust function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        
        # Use the highlight() function from __init__.py
        result = highlight(RUST_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Rust functions")
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
    
    def test_rust_simple_function_detection(self):
        """Test detection of simple Rust functions"""
        simple_code = """
fn hello_world() {
    println!("Hello, World!");
}

fn add(a: i32, b: i32) -> i32 {
    a + b
}

fn greet(name: &str) {
    println!("Hello, {}!", name);
}

fn main() {
    hello_world();
    let result = add(5, 3);
    greet("Rust");
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["hello_world", "add", "greet", "main"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_rust_struct_methods_detection(self):
        """Test detection of Rust struct methods"""
        struct_code = """
struct Point {
    x: f64,
    y: f64,
}

impl Point {
    fn new(x: f64, y: f64) -> Self {
        Point { x, y }
    }
    
    fn distance_from_origin(&self) -> f64 {
        (self.x * self.x + self.y * self.y).sqrt()
    }
    
    fn move_by(&mut self, dx: f64, dy: f64) {
        self.x += dx;
        self.y += dy;
    }
    
    fn into_tuple(self) -> (f64, f64) {
        (self.x, self.y)
    }
    
    fn zero() -> Point {
        Point::new(0.0, 0.0)
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(struct_code, lexer, formatter)
        
        assert result is not None
        
        # Check for struct method detection
        struct_methods = ["new", "distance_from_origin", "move_by", "into_tuple", "zero"]
        detected_struct = [name for name in struct_methods if name in result]
        
        assert len(detected_struct) > 0, f"No struct methods detected: {result}"
        print(f"Detected struct methods: {detected_struct}")
    
    def test_rust_trait_detection(self):
        """Test detection of Rust trait methods"""
        trait_code = """
trait Drawable {
    fn draw(&self);
    fn area(&self) -> f64;
    
    fn describe(&self) {
        println!("Area: {}", self.area());
    }
}

trait Resizable {
    fn resize(&mut self, factor: f64);
    fn get_size(&self) -> (f64, f64);
}

struct Circle {
    radius: f64,
}

impl Drawable for Circle {
    fn draw(&self) {
        println!("Drawing circle with radius {}", self.radius);
    }
    
    fn area(&self) -> f64 {
        std::f64::consts::PI * self.radius * self.radius
    }
}

impl Resizable for Circle {
    fn resize(&mut self, factor: f64) {
        self.radius *= factor;
    }
    
    fn get_size(&self) -> (f64, f64) {
        (self.radius * 2.0, self.radius * 2.0)
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(trait_code, lexer, formatter)
        
        assert result is not None
        
        # Check for trait method detection
        trait_methods = ["draw", "area", "describe", "resize", "get_size"]
        detected_traits = [name for name in trait_methods if name in result]
        
        assert len(detected_traits) > 0, f"No trait methods detected: {result}"
        print(f"Detected trait methods: {detected_traits}")
    
    def test_rust_generic_function_detection(self):
        """Test detection of Rust generic functions"""
        generic_code = """
fn identity<T>(value: T) -> T {
    value
}

fn swap<T>(a: &mut T, b: &mut T) {
    std::mem::swap(a, b);
}

fn max<T: PartialOrd>(a: T, b: T) -> T {
    if a > b { a } else { b }
}

fn process_container<T, F>(items: Vec<T>, processor: F) -> Vec<T>
where
    F: Fn(T) -> T,
{
    items.into_iter().map(processor).collect()
}

struct Container<T> {
    items: Vec<T>,
}

impl<T> Container<T> {
    fn new() -> Self {
        Container { items: Vec::new() }
    }
    
    fn add(&mut self, item: T) {
        self.items.push(item);
    }
    
    fn get(&self, index: usize) -> Option<&T> {
        self.items.get(index)
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(generic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generic function detection
        generic_functions = ["identity", "swap", "max", "process_container", "new", "add", "get"]
        detected_generic = [name for name in generic_functions if name in result]
        
        assert len(detected_generic) > 0, f"No generic functions detected: {result}"
        print(f"Detected generic functions: {detected_generic}")
    
    def test_rust_async_function_detection(self):
        """Test detection of Rust async functions"""
        async_code = """
use std::time::Duration;

async fn simple_async() {
    tokio::time::sleep(Duration::from_millis(100)).await;
}

async fn fetch_data(url: &str) -> Result<String, Box<dyn std::error::Error>> {
    // Simulated fetch
    tokio::time::sleep(Duration::from_millis(200)).await;
    Ok(format!("Data from {}", url))
}

async fn process_async<T>(data: T) -> T
where
    T: Send + 'static,
{
    tokio::task::spawn_blocking(move || {
        // Simulated processing
        std::thread::sleep(Duration::from_millis(50));
        data
    }).await.unwrap()
}

struct AsyncProcessor;

impl AsyncProcessor {
    async fn process(&self, input: String) -> String {
        tokio::time::sleep(Duration::from_millis(10)).await;
        input.to_uppercase()
    }
    
    async fn batch_process(&self, inputs: Vec<String>) -> Vec<String> {
        let mut results = Vec::new();
        for input in inputs {
            results.push(self.process(input).await);
        }
        results
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async function detection
        async_functions = ["simple_async", "fetch_data", "process_async", "process", "batch_process"]
        detected_async = [name for name in async_functions if name in result]
        
        assert len(detected_async) > 0, f"No async functions detected: {result}"
        print(f"Detected async functions: {detected_async}")
    
    def test_rust_enum_methods_detection(self):
        """Test detection of Rust enum methods"""
        enum_code = """
#[derive(Debug, PartialEq)]
enum Color {
    Red,
    Green,
    Blue,
    RGB(u8, u8, u8),
    HSV { h: u16, s: u8, v: u8 },
}

impl Color {
    fn is_primary(&self) -> bool {
        matches!(self, Color::Red | Color::Green | Color::Blue)
    }
    
    fn to_rgb(&self) -> (u8, u8, u8) {
        match self {
            Color::Red => (255, 0, 0),
            Color::Green => (0, 255, 0),
            Color::Blue => (0, 0, 255),
            Color::RGB(r, g, b) => (*r, *g, *b),
            Color::HSV { h, s, v } => {
                // Simplified HSV to RGB conversion
                (*v, *s, (*h / 360 * 255) as u8)
            }
        }
    }
    
    fn red() -> Self {
        Color::Red
    }
    
    fn custom_rgb(r: u8, g: u8, b: u8) -> Self {
        Color::RGB(r, g, b)
    }
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}

impl<T, E> Result<T, E> {
    fn is_ok(&self) -> bool {
        matches!(self, Result::Ok(_))
    }
    
    fn unwrap(self) -> T
    where
        E: std::fmt::Debug,
    {
        match self {
            Result::Ok(value) => value,
            Result::Err(err) => panic!("Unwrap error: {:?}", err),
        }
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(enum_code, lexer, formatter)
        
        assert result is not None
        
        # Check for enum method detection
        enum_methods = ["is_primary", "to_rgb", "red", "custom_rgb", "is_ok", "unwrap"]
        detected_enum = [name for name in enum_methods if name in result]
        
        assert len(detected_enum) > 0, f"No enum methods detected: {result}"
        print(f"Detected enum methods: {detected_enum}")
    
    def test_rust_closure_function_detection(self):
        """Test detection of Rust closure and higher-order functions"""
        closure_code = """
fn create_multiplier(factor: i32) -> impl Fn(i32) -> i32 {
    move |x| x * factor
}

fn apply_twice<F>(f: F, x: i32) -> i32
where
    F: Fn(i32) -> i32,
{
    f(f(x))
}

fn filter_map_collect<T, U, F, P>(
    items: Vec<T>,
    predicate: P,
    mapper: F,
) -> Vec<U>
where
    F: Fn(&T) -> U,
    P: Fn(&T) -> bool,
{
    items
        .iter()
        .filter(predicate)
        .map(mapper)
        .collect()
}

fn demonstrate_closures() {
    let add_one = |x| x + 1;
    let multiply_by_two = |x: i32| -> i32 { x * 2 };
    
    let numbers = vec![1, 2, 3, 4, 5];
    let doubled: Vec<i32> = numbers.iter().map(|&x| x * 2).collect();
}

fn compose<A, B, C, F, G>(f: F, g: G) -> impl Fn(A) -> C
where
    F: Fn(A) -> B,
    G: Fn(B) -> C,
{
    move |x| g(f(x))
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(closure_code, lexer, formatter)
        
        assert result is not None
        
        # Check for closure function detection
        closure_functions = ["create_multiplier", "apply_twice", "filter_map_collect", "demonstrate_closures", "compose"]
        detected_closures = [name for name in closure_functions if name in result]
        
        assert len(detected_closures) > 0, f"No closure functions detected: {result}"
        print(f"Detected closure functions: {detected_closures}")
    
    def test_rust_error_handling_detection(self):
        """Test detection of Rust error handling functions"""
        error_code = """
use std::fmt;
use std::error::Error;

#[derive(Debug)]
struct CustomError {
    message: String,
}

impl CustomError {
    fn new(message: &str) -> Self {
        CustomError {
            message: message.to_string(),
        }
    }
}

impl fmt::Display for CustomError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "Custom error: {}", self.message)
    }
}

impl Error for CustomError {}

fn might_fail(input: i32) -> Result<i32, CustomError> {
    if input < 0 {
        Err(CustomError::new("Negative input"))
    } else {
        Ok(input * 2)
    }
}

fn chain_operations(input: i32) -> Result<i32, Box<dyn Error>> {
    let step1 = might_fail(input)?;
    let step2 = might_fail(step1)?;
    Ok(step2 + 10)
}

fn handle_multiple_errors(inputs: Vec<i32>) -> Result<Vec<i32>, Box<dyn Error>> {
    let mut results = Vec::new();
    for input in inputs {
        results.push(might_fail(input)?);
    }
    Ok(results)
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(error_code, lexer, formatter)
        
        assert result is not None
        
        # Check for error handling function detection
        error_functions = ["new", "fmt", "might_fail", "chain_operations", "handle_multiple_errors"]
        detected_error = [name for name in error_functions if name in result]
        
        assert len(detected_error) > 0, f"No error handling functions detected: {result}"
        print(f"Detected error handling functions: {detected_error}")
    
    def test_rust_lifetime_function_detection(self):
        """Test detection of Rust functions with lifetimes"""
        lifetime_code = """
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }
    &s[..]
}

struct ImportantExcerpt<'a> {
    part: &'a str,
}

impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 {
        3
    }
    
    fn announce_and_return_part(&self, announcement: &str) -> &str {
        println!("Attention please: {}", announcement);
        self.part
    }
    
    fn return_part_or_default<'b>(&self, default: &'b str) -> &'a str
    where
        'a: 'b,
    {
        if self.part.is_empty() {
            self.part
        } else {
            self.part
        }
    }
}

fn parse_and_return<'a>(input: &'a str, delimiter: char) -> Option<&'a str> {
    input.split(delimiter).next()
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(lifetime_code, lexer, formatter)
        
        assert result is not None
        
        # Check for lifetime function detection
        lifetime_functions = ["longest", "first_word", "level", "announce_and_return_part", "return_part_or_default", "parse_and_return"]
        detected_lifetime = [name for name in lifetime_functions if name in result]
        
        assert len(detected_lifetime) > 0, f"No lifetime functions detected: {result}"
        print(f"Detected lifetime functions: {detected_lifetime}")
    
    def test_rust_language_detection(self):
        """Test that Rust language is properly detected"""
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        
        # Verify language detection
        assert formatter._detect_language() == 'rust', "Rust language not properly detected"
    
    def test_rust_macro_and_test_detection(self):
        """Test detection of Rust macros and test functions"""
        macro_test_code = """
macro_rules! say_hello {
    () => {
        println!("Hello!");
    };
    ($name:expr) => {
        println!("Hello, {}!", $name);
    };
}

macro_rules! create_function {
    ($func_name:ident) => {
        fn $func_name() {
            println!("You called {:?}()", stringify!($func_name));
        }
    };
}

create_function!(foo);
create_function!(bar);

fn use_macros() {
    say_hello!();
    say_hello!("World");
    foo();
    bar();
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_macro_usage() {
        use_macros();
    }
    
    #[test]
    fn test_addition() {
        assert_eq!(2 + 2, 4);
    }
    
    #[test]
    #[should_panic]
    fn test_panic() {
        panic!("This test should panic");
    }
    
    #[test]
    #[ignore]
    fn expensive_test() {
        // This test is ignored by default
    }
}

#[bench]
fn bench_addition(b: &mut test::Bencher) {
    b.iter(|| {
        let n = test::black_box(1000);
        (0..n).fold(0, |a, b| a ^ b)
    });
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(macro_test_code, lexer, formatter)
        
        assert result is not None
        
        # Check for macro and test function detection
        macro_test_functions = ["foo", "bar", "use_macros", "test_macro_usage", "test_addition", "test_panic", "expensive_test", "bench_addition"]
        detected_macro_test = [name for name in macro_test_functions if name in result]
        
        assert len(detected_macro_test) > 0, f"No macro/test functions detected: {result}"
        print(f"Detected macro/test functions: {detected_macro_test}")
    
    def test_rust_unsafe_function_detection(self):
        """Test detection of Rust unsafe functions"""
        unsafe_code = """
unsafe fn dangerous_operation() -> i32 {
    let mut num = 5;
    let r1 = &num as *const i32;
    let r2 = &mut num as *mut i32;
    
    *r2 = 10;
    *r1
}

fn safe_wrapper() -> i32 {
    unsafe {
        dangerous_operation()
    }
}

unsafe trait UnsafeTrait {
    unsafe fn unsafe_method(&self);
}

struct SafeStruct;

unsafe impl UnsafeTrait for SafeStruct {
    unsafe fn unsafe_method(&self) {
        // Unsafe implementation
    }
}

fn call_unsafe_function() {
    let result = safe_wrapper();
    println!("Result: {}", result);
    
    let safe_struct = SafeStruct;
    unsafe {
        safe_struct.unsafe_method();
    }
}
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(unsafe_code, lexer, formatter)
        
        assert result is not None
        
        # Check for unsafe function detection
        unsafe_functions = ["dangerous_operation", "safe_wrapper", "unsafe_method", "call_unsafe_function"]
        detected_unsafe = [name for name in unsafe_functions if name in result]
        
        assert len(detected_unsafe) > 0, f"No unsafe functions detected: {result}"
        print(f"Detected unsafe functions: {detected_unsafe}")
    
    def test_empty_rust_file(self):
        """Test handling of empty Rust file"""
        empty_code = """
// Just comments and use statements
use std::collections::HashMap;
use std::fmt::Debug;

// Type aliases
type Result<T> = std::result::Result<T, Box<dyn std::error::Error>>;

// Constants
const MAX_SIZE: usize = 1000;

// No functions defined
"""
        
        lexer = RustLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='rust')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestRustTLDRFormatter()
    test.test_rust_function_detection_via_highlight_api()
    print("Rust TLDR formatter test completed successfully!")