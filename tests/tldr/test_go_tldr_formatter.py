"""
    Go TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~

    Test Go-specific function detection using the highlight() API.

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
from pygments_tldr.lexers.go import GoLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample Go code with known number of functions
GO_TEST_CODE = """
// Go sample code for testing function detection
package main

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"strconv"
	"sync"
	"time"
)

// Global variables
var (
	globalCounter int
	globalMutex   sync.RWMutex
)

// Constants
const (
	MaxRetries = 3
	Timeout    = 30 * time.Second
)

// Simple functions
func main() {
	fmt.Println("Hello, Go!")
	result := addNumbers(5, 3)
	fmt.Printf("Result: %d\\n", result)
}

func addNumbers(a, b int) int {
	return a + b
}

func greet(name string) {
	fmt.Printf("Hello, %s!\\n", name)
}

// Function with multiple return values
func divide(a, b float64) (float64, error) {
	if b == 0 {
		return 0, errors.New("division by zero")
	}
	return a / b, nil
}

func swap(a, b string) (string, string) {
	return b, a
}

// Function with named return values
func calculate(x, y int) (sum, product int) {
	sum = x + y
	product = x * y
	return // naked return
}

// Variadic functions
func sum(numbers ...int) int {
	total := 0
	for _, num := range numbers {
		total += num
	}
	return total
}

func printf(format string, args ...interface{}) {
	fmt.Printf(format, args...)
}

// Function with slice and map parameters
func processSlice(items []string) []string {
	result := make([]string, len(items))
	for i, item := range items {
		result[i] = fmt.Sprintf("processed_%s", item)
	}
	return result
}

func processMap(data map[string]int) map[string]int {
	result := make(map[string]int)
	for key, value := range data {
		result[key] = value * 2
	}
	return result
}

// Struct definitions and methods
type Person struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

func NewPerson(name string, age int) *Person {
	return &Person{
		Name: name,
		Age:  age,
	}
}

func (p *Person) String() string {
	return fmt.Sprintf("%s (%d years old)", p.Name, p.Age)
}

func (p *Person) GetAge() int {
	return p.Age
}

func (p *Person) SetAge(age int) {
	p.Age = age
}

func (p *Person) IsAdult() bool {
	return p.Age >= 18
}

func (p Person) Copy() Person {
	return Person{
		Name: p.Name,
		Age:  p.Age,
	}
}

// Interface and implementations
type Shape interface {
	Area() float64
	Perimeter() float64
	String() string
}

type Rectangle struct {
	Width  float64
	Height float64
}

func NewRectangle(width, height float64) *Rectangle {
	return &Rectangle{Width: width, Height: height}
}

func (r *Rectangle) Area() float64 {
	return r.Width * r.Height
}

func (r *Rectangle) Perimeter() float64 {
	return 2 * (r.Width + r.Height)
}

func (r *Rectangle) String() string {
	return fmt.Sprintf("Rectangle(%.2f x %.2f)", r.Width, r.Height)
}

func (r *Rectangle) Scale(factor float64) {
	r.Width *= factor
	r.Height *= factor
}

type Circle struct {
	Radius float64
}

func NewCircle(radius float64) *Circle {
	return &Circle{Radius: radius}
}

func (c *Circle) Area() float64 {
	return 3.14159 * c.Radius * c.Radius
}

func (c *Circle) Perimeter() float64 {
	return 2 * 3.14159 * c.Radius
}

func (c *Circle) String() string {
	return fmt.Sprintf("Circle(radius: %.2f)", c.Radius)
}

// Generic functions (Go 1.18+)
func Max[T comparable](a, b T) T {
	if a > b {
		return a
	}
	return b
}

func SliceContains[T comparable](slice []T, item T) bool {
	for _, v := range slice {
		if v == item {
			return true
		}
	}
	return false
}

func MapKeys[K comparable, V any](m map[K]V) []K {
	keys := make([]K, 0, len(m))
	for k := range m {
		keys = append(keys, k)
	}
	return keys
}

// Generic struct and methods
type Stack[T any] struct {
	items []T
}

func NewStack[T any]() *Stack[T] {
	return &Stack[T]{items: make([]T, 0)}
}

func (s *Stack[T]) Push(item T) {
	s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
	if len(s.items) == 0 {
		var zero T
		return zero, false
	}
	index := len(s.items) - 1
	item := s.items[index]
	s.items = s.items[:index]
	return item, true
}

func (s *Stack[T]) IsEmpty() bool {
	return len(s.items) == 0
}

func (s *Stack[T]) Size() int {
	return len(s.items)
}

// Error handling functions
type CustomError struct {
	Message string
	Code    int
}

func (e *CustomError) Error() string {
	return fmt.Sprintf("Error %d: %s", e.Code, e.Message)
}

func NewCustomError(message string, code int) *CustomError {
	return &CustomError{Message: message, Code: code}
}

func validateInput(input string) error {
	if input == "" {
		return NewCustomError("input cannot be empty", 400)
	}
	return nil
}

func processWithError(input string) (string, error) {
	if err := validateInput(input); err != nil {
		return "", err
	}
	return fmt.Sprintf("processed: %s", input), nil
}

// Goroutine and channel functions
func worker(id int, jobs <-chan int, results chan<- int) {
	for job := range jobs {
		fmt.Printf("Worker %d processing job %d\\n", id, job)
		time.Sleep(time.Millisecond * 100)
		results <- job * 2
	}
}

func startWorkers(numWorkers int) {
	jobs := make(chan int, 10)
	results := make(chan int, 10)

	// Start workers
	for w := 1; w <= numWorkers; w++ {
		go worker(w, jobs, results)
	}

	// Send jobs
	for j := 1; j <= 5; j++ {
		jobs <- j
	}
	close(jobs)

	// Collect results
	for r := 1; r <= 5; r++ {
		<-results
	}
}

func pingPong(ball chan string) {
	for {
		select {
		case msg := <-ball:
			fmt.Println("Received:", msg)
			time.Sleep(time.Millisecond * 100)
			ball <- "pong"
		case <-time.After(time.Second):
			fmt.Println("Timeout")
			return
		}
	}
}

// HTTP handler functions
func homeHandler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "Welcome to the home page!")
}

func apiHandler(w http.ResponseWriter, r *http.Request) {
	data := map[string]interface{}{
		"message": "Hello from API",
		"time":    time.Now(),
	}
	
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(data)
}

func userHandler(w http.ResponseWriter, r *http.Request) {
	switch r.Method {
	case http.MethodGet:
		getUserHandler(w, r)
	case http.MethodPost:
		createUserHandler(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
	user := Person{Name: "John Doe", Age: 30}
	json.NewEncoder(w).Encode(user)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
	var user Person
	if err := json.NewDecoder(r.Body).Decode(&user); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}
	
	// Simulate saving user
	fmt.Fprintf(w, "User created: %s", user.String())
}

// Context functions
func doWork(ctx context.Context, duration time.Duration) error {
	select {
	case <-time.After(duration):
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func workWithTimeout(duration time.Duration) error {
	ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
	defer cancel()
	
	return doWork(ctx, duration)
}

func workWithCancel() error {
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()
	
	go func() {
		time.Sleep(time.Second)
		cancel()
	}()
	
	return doWork(ctx, 5*time.Second)
}

// Closure functions
func createAdder(x int) func(int) int {
	return func(y int) int {
		return x + y
	}
}

func fibonacci() func() int {
	a, b := 0, 1
	return func() int {
		a, b = b, a+b
		return a
	}
}

func processNumbers(numbers []int, processor func(int) int) []int {
	result := make([]int, len(numbers))
	for i, num := range numbers {
		result[i] = processor(num)
	}
	return result
}

// Method on built-in types
type Age int

func (a Age) String() string {
	return fmt.Sprintf("%d years old", int(a))
}

func (a Age) IsAdult() bool {
	return a >= 18
}

func (a *Age) IncrementYear() {
	*a++
}

type StringSlice []string

func (ss StringSlice) Join(separator string) string {
	result := ""
	for i, s := range ss {
		if i > 0 {
			result += separator
		}
		result += s
	}
	return result
}

func (ss StringSlice) Contains(item string) bool {
	for _, s := range ss {
		if s == item {
			return true
		}
	}
	return false
}

// Embedded structs and methods
type Animal struct {
	Name string
	Age  int
}

func (a *Animal) Speak() string {
	return fmt.Sprintf("%s makes a sound", a.Name)
}

func (a *Animal) GetInfo() string {
	return fmt.Sprintf("%s is %d years old", a.Name, a.Age)
}

type Dog struct {
	Animal
	Breed string
}

func NewDog(name, breed string, age int) *Dog {
	return &Dog{
		Animal: Animal{Name: name, Age: age},
		Breed:  breed,
	}
}

func (d *Dog) Speak() string {
	return fmt.Sprintf("%s barks", d.Name)
}

func (d *Dog) Fetch() string {
	return fmt.Sprintf("%s fetches the ball", d.Name)
}

// Package-level functions
func init() {
	log.Println("Package initialized")
}

func helper() string {
	return "helper function"
}

// Deferred functions
func demonstrateDefer() {
	defer fmt.Println("This will be printed last")
	defer func() {
		fmt.Println("Anonymous deferred function")
	}()
	
	fmt.Println("This will be printed first")
}

func fileOperations(filename string) error {
	file, err := openFile(filename)
	if err != nil {
		return err
	}
	defer file.Close()
	
	return processFile(file)
}

func openFile(filename string) (io.ReadCloser, error) {
	// Simulated file opening
	return io.NopCloser(nil), nil
}

func processFile(file io.ReadCloser) error {
	// Simulated file processing
	return nil
}

// Panic and recover functions
func riskyOperation() {
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("Recovered from panic: %v\\n", r)
		}
	}()
	
	panic("Something went wrong!")
}

func safeWrapper() {
	defer func() {
		if r := recover(); r != nil {
			log.Printf("Caught panic: %v", r)
		}
	}()
	
	riskyOperation()
}

// Benchmark and test functions (testing package style)
func BenchmarkAddNumbers(b *testing.B) {
	for i := 0; i < b.N; i++ {
		addNumbers(5, 3)
	}
}

func TestAddNumbers(t *testing.T) {
	result := addNumbers(2, 3)
	if result != 5 {
		t.Errorf("Expected 5, got %d", result)
	}
}

func TestDivide(t *testing.T) {
	result, err := divide(10, 2)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}
	if result != 5.0 {
		t.Errorf("Expected 5.0, got %f", result)
	}
}

// Type conversion functions
func convertTypes(s string) (int, float64, bool, error) {
	intVal, err := strconv.Atoi(s)
	if err != nil {
		return 0, 0, false, err
	}
	
	floatVal, err := strconv.ParseFloat(s, 64)
	if err != nil {
		return 0, 0, false, err
	}
	
	boolVal, err := strconv.ParseBool(s)
	if err != nil {
		return 0, 0, false, err
	}
	
	return intVal, floatVal, boolVal, nil
}

func typeAssertions(i interface{}) string {
	switch v := i.(type) {
	case string:
		return fmt.Sprintf("String: %s", v)
	case int:
		return fmt.Sprintf("Integer: %d", v)
	case float64:
		return fmt.Sprintf("Float: %f", v)
	default:
		return fmt.Sprintf("Unknown type: %T", v)
	}
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Basic functions
    "main", "addNumbers", "greet", "divide", "swap", "calculate", "sum", "printf",
    # Slice and map functions
    "processSlice", "processMap",
    # Person struct methods
    "NewPerson", "String", "GetAge", "SetAge", "IsAdult", "Copy",
    # Shape interface implementations
    "NewRectangle", "Area", "Perimeter", "Scale",
    "NewCircle",
    # Generic functions
    "Max", "SliceContains", "MapKeys",
    # Stack generic methods
    "NewStack", "Push", "Pop", "IsEmpty", "Size",
    # Error handling
    "Error", "NewCustomError", "validateInput", "processWithError",
    # Goroutine and channel functions
    "worker", "startWorkers", "pingPong",
    # HTTP handlers
    "homeHandler", "apiHandler", "userHandler", "getUserHandler", "createUserHandler",
    # Context functions
    "doWork", "workWithTimeout", "workWithCancel",
    # Closure functions
    "createAdder", "fibonacci", "processNumbers",
    # Method on built-in types
    "IncrementYear", "Join", "Contains",
    # Embedded structs
    "Speak", "GetInfo", "NewDog", "Fetch",
    # Package functions
    "init", "helper",
    # Deferred functions
    "demonstrateDefer", "fileOperations", "openFile", "processFile",
    # Panic and recover
    "riskyOperation", "safeWrapper",
    # Test functions
    "BenchmarkAddNumbers", "TestAddNumbers", "TestDivide",
    # Type functions
    "convertTypes", "typeAssertions"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestGoTLDRFormatter:
    """Test class for Go-specific function detection in TLDR formatter."""
    
    def test_go_function_detection_via_highlight_api(self):
        """Test Go function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        
        # Use the highlight() function from __init__.py
        result = highlight(GO_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} Go functions")
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
    
    def test_go_simple_function_detection(self):
        """Test detection of simple Go functions"""
        simple_code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}

func add(a, b int) int {
    return a + b
}

func greet(name string) {
    fmt.Printf("Hello, %s!\\n", name)
}

func divide(a, b float64) (float64, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero")
    }
    return a / b, nil
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["main", "add", "greet", "divide"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_go_struct_methods_detection(self):
        """Test detection of Go struct methods"""
        struct_code = """
package main

import "fmt"

type Person struct {
    Name string
    Age  int
}

func NewPerson(name string, age int) *Person {
    return &Person{Name: name, Age: age}
}

func (p *Person) String() string {
    return fmt.Sprintf("%s (%d)", p.Name, p.Age)
}

func (p *Person) GetAge() int {
    return p.Age
}

func (p *Person) SetAge(age int) {
    p.Age = age
}

func (p Person) Copy() Person {
    return Person{Name: p.Name, Age: p.Age}
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(struct_code, lexer, formatter)
        
        assert result is not None
        
        # Check for struct method detection
        struct_methods = ["NewPerson", "String", "GetAge", "SetAge", "Copy"]
        detected_struct = [name for name in struct_methods if name in result]
        
        assert len(detected_struct) > 0, f"No struct methods detected: {result}"
        print(f"Detected struct methods: {detected_struct}")
    
    def test_go_interface_methods_detection(self):
        """Test detection of Go interface implementations"""
        interface_code = """
package main

import "fmt"

type Shape interface {
    Area() float64
    Perimeter() float64
}

type Rectangle struct {
    Width, Height float64
}

func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}

type Circle struct {
    Radius float64
}

func (c Circle) Area() float64 {
    return 3.14159 * c.Radius * c.Radius
}

func (c Circle) Perimeter() float64 {
    return 2 * 3.14159 * c.Radius
}

func printShapeInfo(s Shape) {
    fmt.Printf("Area: %.2f, Perimeter: %.2f\\n", s.Area(), s.Perimeter())
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(interface_code, lexer, formatter)
        
        assert result is not None
        
        # Check for interface method detection
        interface_methods = ["Area", "Perimeter", "printShapeInfo"]
        detected_interface = [name for name in interface_methods if name in result]
        
        assert len(detected_interface) > 0, f"No interface methods detected: {result}"
        print(f"Detected interface methods: {detected_interface}")
    
    def test_go_generic_function_detection(self):
        """Test detection of Go generic functions (Go 1.18+)"""
        generic_code = """
package main

import "fmt"

func Max[T comparable](a, b T) T {
    if a > b {
        return a
    }
    return b
}

func SliceContains[T comparable](slice []T, item T) bool {
    for _, v := range slice {
        if v == item {
            return true
        }
    }
    return false
}

type Stack[T any] struct {
    items []T
}

func NewStack[T any]() *Stack[T] {
    return &Stack[T]{}
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(generic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generic function detection
        generic_functions = ["Max", "SliceContains", "NewStack", "Push", "Pop"]
        detected_generic = [name for name in generic_functions if name in result]
        
        assert len(detected_generic) > 0, f"No generic functions detected: {result}"
        print(f"Detected generic functions: {detected_generic}")
    
    def test_go_goroutine_function_detection(self):
        """Test detection of Go goroutine and channel functions"""
        goroutine_code = """
package main

import (
    "fmt"
    "time"
)

func worker(id int, jobs <-chan int, results chan<- int) {
    for j := range jobs {
        fmt.Printf("worker %d started job %d\\n", id, j)
        time.Sleep(time.Second)
        results <- j * 2
    }
}

func startWorkers() {
    jobs := make(chan int, 100)
    results := make(chan int, 100)

    for w := 1; w <= 3; w++ {
        go worker(w, jobs, results)
    }

    for j := 1; j <= 5; j++ {
        jobs <- j
    }
    close(jobs)

    for a := 1; a <= 5; a++ {
        <-results
    }
}

func ping(pings chan<- string, msg string) {
    pings <- msg
}

func pong(pings <-chan string, pongs chan<- string) {
    msg := <-pings
    pongs <- msg
}

func channelDemo() {
    pings := make(chan string, 1)
    pongs := make(chan string, 1)
    ping(pings, "passed message")
    pong(pings, pongs)
    fmt.Println(<-pongs)
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(goroutine_code, lexer, formatter)
        
        assert result is not None
        
        # Check for goroutine function detection
        goroutine_functions = ["worker", "startWorkers", "ping", "pong", "channelDemo"]
        detected_goroutine = [name for name in goroutine_functions if name in result]
        
        assert len(detected_goroutine) > 0, f"No goroutine functions detected: {result}"
        print(f"Detected goroutine functions: {detected_goroutine}")
    
    def test_go_http_handler_detection(self):
        """Test detection of Go HTTP handler functions"""
        http_code = """
package main

import (
    "encoding/json"
    "fmt"
    "net/http"
)

func homeHandler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Welcome to the home page!")
}

func apiHandler(w http.ResponseWriter, r *http.Request) {
    data := map[string]string{"message": "Hello API"}
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(data)
}

func userHandler(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        getUserHandler(w, r)
    case "POST":
        createUserHandler(w, r)
    default:
        http.Error(w, "Method not allowed", 405)
    }
}

func getUserHandler(w http.ResponseWriter, r *http.Request) {
    user := map[string]interface{}{"name": "John", "age": 30}
    json.NewEncoder(w).Encode(user)
}

func createUserHandler(w http.ResponseWriter, r *http.Request) {
    var user map[string]interface{}
    json.NewDecoder(r.Body).Decode(&user)
    fmt.Fprintf(w, "User created: %v", user)
}

func setupRoutes() {
    http.HandleFunc("/", homeHandler)
    http.HandleFunc("/api", apiHandler)
    http.HandleFunc("/users", userHandler)
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(http_code, lexer, formatter)
        
        assert result is not None
        
        # Check for HTTP handler detection
        http_functions = ["homeHandler", "apiHandler", "userHandler", "getUserHandler", "createUserHandler", "setupRoutes"]
        detected_http = [name for name in http_functions if name in result]
        
        assert len(detected_http) > 0, f"No HTTP handler functions detected: {result}"
        print(f"Detected HTTP handler functions: {detected_http}")
    
    def test_go_error_handling_detection(self):
        """Test detection of Go error handling functions"""
        error_code = """
package main

import (
    "errors"
    "fmt"
)

type CustomError struct {
    Message string
    Code    int
}

func (e *CustomError) Error() string {
    return fmt.Sprintf("Error %d: %s", e.Code, e.Message)
}

func NewCustomError(message string, code int) *CustomError {
    return &CustomError{Message: message, Code: code}
}

func validateInput(input string) error {
    if input == "" {
        return errors.New("input cannot be empty")
    }
    return nil
}

func processData(input string) (string, error) {
    if err := validateInput(input); err != nil {
        return "", err
    }
    return fmt.Sprintf("processed: %s", input), nil
}

func handleErrors() {
    result, err := processData("")
    if err != nil {
        fmt.Printf("Error: %v\\n", err)
        return
    }
    fmt.Println("Result:", result)
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(error_code, lexer, formatter)
        
        assert result is not None
        
        # Check for error handling function detection
        error_functions = ["Error", "NewCustomError", "validateInput", "processData", "handleErrors"]
        detected_error = [name for name in error_functions if name in result]
        
        assert len(detected_error) > 0, f"No error handling functions detected: {result}"
        print(f"Detected error handling functions: {detected_error}")
    
    def test_go_closure_function_detection(self):
        """Test detection of Go closure and anonymous functions"""
        closure_code = """
package main

import "fmt"

func createAdder(x int) func(int) int {
    return func(y int) int {
        return x + y
    }
}

func fibonacci() func() int {
    a, b := 0, 1
    return func() int {
        a, b = b, a+b
        return a
    }
}

func processNumbers(numbers []int, processor func(int) int) []int {
    result := make([]int, len(numbers))
    for i, num := range numbers {
        result[i] = processor(num)
    }
    return result
}

func demonstrateClosures() {
    add5 := createAdder(5)
    fmt.Println(add5(3)) // Output: 8

    fib := fibonacci()
    for i := 0; i < 10; i++ {
        fmt.Println(fib())
    }

    numbers := []int{1, 2, 3, 4, 5}
    doubled := processNumbers(numbers, func(x int) int {
        return x * 2
    })
    fmt.Println(doubled)
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(closure_code, lexer, formatter)
        
        assert result is not None
        
        # Check for closure function detection
        closure_functions = ["createAdder", "fibonacci", "processNumbers", "demonstrateClosures"]
        detected_closures = [name for name in closure_functions if name in result]
        
        assert len(detected_closures) > 0, f"No closure functions detected: {result}"
        print(f"Detected closure functions: {detected_closures}")
    
    def test_go_language_detection(self):
        """Test that Go language is properly detected"""
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        
        # Verify language detection
        detected_lang = formatter._detect_language()
        assert detected_lang == 'go', f"Go language not properly detected, got: {detected_lang}"
    
    def test_go_package_functions_detection(self):
        """Test detection of Go package-level functions"""
        package_code = """
package utils

import (
    "fmt"
    "strings"
)

var globalVar = "initialized"

func init() {
    fmt.Println("Package initialized")
}

func PublicFunction() string {
    return "This is a public function"
}

func privateFunction() string {
    return "This is a private function"
}

func StringUtility(s string) string {
    return strings.ToUpper(s)
}

func HelperFunction(a, b int) int {
    return privateFunction() + a + b
}

const (
    MaxSize = 100
    MinSize = 1
)

type PublicStruct struct {
    Field string
}

func (ps *PublicStruct) Method() string {
    return ps.Field
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(package_code, lexer, formatter)
        
        assert result is not None
        
        # Check for package function detection
        package_functions = ["init", "PublicFunction", "privateFunction", "StringUtility", "HelperFunction", "Method"]
        detected_package = [name for name in package_functions if name in result]
        
        assert len(detected_package) > 0, f"No package functions detected: {result}"
        print(f"Detected package functions: {detected_package}")
    
    def test_go_test_function_detection(self):
        """Test detection of Go test and benchmark functions"""
        test_code = """
package main

import (
    "testing"
    "time"
)

func TestAddition(t *testing.T) {
    result := 2 + 3
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}

func TestSubtraction(t *testing.T) {
    result := 5 - 3
    if result != 2 {
        t.Errorf("Expected 2, got %d", result)
    }
}

func BenchmarkAddition(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = 2 + 3
    }
}

func BenchmarkStringConcatenation(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = "hello" + "world"
    }
}

func ExampleAdd() {
    result := 2 + 3
    fmt.Println(result)
    // Output: 5
}

func TestHelper(t *testing.T) {
    helper := func(a, b int) int {
        return a + b
    }
    
    result := helper(2, 3)
    if result != 5 {
        t.Errorf("Expected 5, got %d", result)
    }
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(test_code, lexer, formatter)
        
        assert result is not None
        
        # Check for test function detection
        test_functions = ["TestAddition", "TestSubtraction", "BenchmarkAddition", "BenchmarkStringConcatenation", "ExampleAdd", "TestHelper"]
        detected_tests = [name for name in test_functions if name in result]
        
        assert len(detected_tests) > 0, f"No test functions detected: {result}"
        print(f"Detected test functions: {detected_tests}")
    
    def test_empty_go_file(self):
        """Test handling of empty Go file"""
        empty_code = """
package main

import (
    "fmt"
    "time"
)

// Just comments and imports
// No functions defined

var globalVar = "initialized"

const MaxSize = 100

type EmptyStruct struct {
    Field string
}
"""
        
        lexer = GoLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='go')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestGoTLDRFormatter()
    test.test_go_function_detection_via_highlight_api()
    print("Go TLDR formatter test completed successfully!")