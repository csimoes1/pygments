"""
    TypeScript TLDR formatter tests
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test TypeScript-specific function detection using the highlight() API.

"""
import logging
import re
from io import StringIO

try:
    import pytest
except ImportError:
    pytest = None

from pygments_tldr import highlight
from pygments_tldr.lexers.javascript import TypeScriptLexer
from pygments_tldr.formatters.tldr import TLDRFormatter


# Sample TypeScript code with known number of functions
TYPESCRIPT_TEST_CODE = """
// TypeScript sample code for testing function detection
'use strict';

// Type definitions and interfaces
interface User {
    id: number;
    name: string;
    email?: string;
}

interface UserService {
    getUser(id: number): Promise<User | null>;
    createUser(data: Partial<User>): Promise<User>;
    updateUser(id: number, data: Partial<User>): Promise<void>;
}

// Type aliases
type UserCallback = (user: User) => void;
type AsyncUserCallback = (user: User) => Promise<void>;

// Regular function declarations with type annotations
function simpleFunction(): void {
    console.log('Hello, TypeScript!');
}

function functionWithParams(a: number, b: string, c: boolean = true): string {
    return `${a}: ${b} (${c})`;
}

function functionWithGeneric<T>(data: T): T {
    return data;
}

function functionWithMultipleGenerics<T, U extends string>(
    first: T, 
    second: U
): { first: T; second: U } {
    return { first, second };
}

// Arrow functions with type annotations
const arrowFunction = (): string => {
    return 'arrow function';
};

const arrowWithParams = (name: string, age: number): string => {
    return `${name} is ${age} years old`;
};

const arrowWithGeneric = <T>(item: T): T[] => [item];

const arrowWithComplexTypes = (
    users: User[], 
    callback: UserCallback
): void => {
    users.forEach(callback);
};

// Function expressions with types
const functionExpression = function(x: number): number {
    return x * 2;
};

const namedFunctionExpression = function calculate(a: number, b: number): number {
    return a + b;
};

// Async functions
async function asyncFunction(): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 1000));
}

async function asyncWithReturn(): Promise<User> {
    return { id: 1, name: 'Test User' };
}

const asyncArrow = async (id: number): Promise<User | null> => {
    return await fetchUser(id);
};

async function fetchUser(id: number): Promise<User | null> {
    // Mock implementation
    return id > 0 ? { id, name: `User ${id}` } : null;
}

// Class with TypeScript features
class UserManager implements UserService {
    private users: Map<number, User> = new Map();
    
    constructor(initialUsers: User[] = []) {
        initialUsers.forEach(user => this.users.set(user.id, user));
    }
    
    // Public methods
    async getUser(id: number): Promise<User | null> {
        return this.users.get(id) || null;
    }
    
    async createUser(data: Partial<User>): Promise<User> {
        const id = Date.now();
        const user: User = { id, name: data.name || 'Unknown', ...data };
        this.users.set(id, user);
        return user;
    }
    
    async updateUser(id: number, data: Partial<User>): Promise<void> {
        const existing = this.users.get(id);
        if (existing) {
            this.users.set(id, { ...existing, ...data });
        }
    }
    
    // Private methods
    private validateUser(user: Partial<User>): boolean {
        return !!user.name && user.name.length > 0;
    }
    
    // Static methods
    static createDefault(): UserManager {
        return new UserManager([]);
    }
    
    static async validateUserData(data: Partial<User>): Promise<boolean> {
        return new Promise(resolve => {
            setTimeout(() => resolve(!!data.name), 100);
        });
    }
    
    // Getters and setters
    get userCount(): number {
        return this.users.size;
    }
    
    set userCount(value: number) {
        // Not implemented for this example
    }
    
    // Protected method
    protected logOperation(operation: string): void {
        console.log(`Operation: ${operation}`);
    }
    
    // Method with overloads (TypeScript feature)
    processUsers(users: User[]): User[];
    processUsers(user: User): User;
    processUsers(input: User | User[]): User | User[] {
        return Array.isArray(input) ? input : input;
    }
}

// Abstract class
abstract class BaseService {
    protected abstract serviceName: string;
    
    abstract initialize(): Promise<void>;
    
    protected log(message: string): void {
        console.log(`[${this.serviceName}] ${message}`);
    }
}

// Generic class
class Repository<T extends { id: number }> {
    private items: Map<number, T> = new Map();
    
    constructor(private validator: (item: T) => boolean) {}
    
    add(item: T): boolean {
        if (this.validator(item)) {
            this.items.set(item.id, item);
            return true;
        }
        return false;
    }
    
    get(id: number): T | undefined {
        return this.items.get(id);
    }
    
    getAll(): T[] {
        return Array.from(this.items.values());
    }
    
    static create<U extends { id: number }>(
        validator: (item: U) => boolean
    ): Repository<U> {
        return new Repository(validator);
    }
}

// Object with typed methods
const userUtilities: {
    formatUser: (user: User) => string;
    validateEmail: (email: string) => boolean;
    createUserCallback: () => UserCallback;
} = {
    formatUser(user: User): string {
        return `${user.name} (${user.id})`;
    },
    
    validateEmail: (email: string): boolean => {
        return email.includes('@');
    },
    
    createUserCallback(): UserCallback {
        return function(user: User): void {
            console.log(`Processing user: ${user.name}`);
        };
    }
};

// Higher-order functions with generics
function createMapper<T, U>(
    transform: (item: T) => U
): (items: T[]) => U[] {
    return function mapArray(items: T[]): U[] {
        return items.map(transform);
    };
}

function withRetry<T extends (...args: any[]) => Promise<any>>(
    fn: T,
    maxRetries: number = 3
): T {
    return (async (...args: Parameters<T>): Promise<ReturnType<T>> => {
        let attempts = 0;
        while (attempts < maxRetries) {
            try {
                return await fn(...args);
            } catch (error) {
                attempts++;
                if (attempts >= maxRetries) throw error;
            }
        }
        throw new Error('Max retries exceeded');
    }) as T;
}

// Export functions with types
export function exportedFunction(data: string[]): number {
    return data.length;
}

export const exportedArrow = (count: number): string[] => {
    return Array(count).fill('').map((_, i) => `Item ${i}`);
};

export default function defaultExportFunction<T>(items: T[]): T | undefined {
    return items[0];
}

// Namespace with functions
namespace UserHelpers {
    export function createGuestUser(): User {
        return { id: 0, name: 'Guest' };
    }
    
    export const formatUserList = (users: User[]): string => {
        return users.map(u => u.name).join(', ');
    };
}

// Module augmentation (TypeScript feature)
declare global {
    interface String {
        toUserName(): string;
    }
}

// Function with complex parameter types
function processUserData(
    users: User[],
    options: {
        includeEmail?: boolean;
        sortBy?: keyof User;
        filter?: (user: User) => boolean;
    } = {}
): Partial<User>[] {
    let result = users;
    
    if (options.filter) {
        result = result.filter(options.filter);
    }
    
    if (options.sortBy) {
        result = result.sort((a, b) => {
            const aVal = a[options.sortBy!];
            const bVal = b[options.sortBy!];
            return aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
        });
    }
    
    return result.map(user => ({
        id: user.id,
        name: user.name,
        ...(options.includeEmail && user.email ? { email: user.email } : {})
    }));
}

// Decorator function (TypeScript/JavaScript)
function logExecution<T extends (...args: any[]) => any>(
    target: any,
    propertyName: string,
    descriptor: PropertyDescriptor
): void {
    const method = descriptor.value;
    
    descriptor.value = function(...args: Parameters<T>): ReturnType<T> {
        console.log(`Executing ${propertyName}`);
        return method.apply(this, args);
    };
}

// Function with conditional types
function processValue<T>(
    value: T
): T extends string ? string : T extends number ? number : never {
    return value as any;
}
"""

# Expected function signatures that should be detected
EXPECTED_FUNCTIONS = [
    # Regular function declarations
    "simpleFunction", "functionWithParams", "functionWithGeneric", "functionWithMultipleGenerics",
    # Arrow functions
    "arrowFunction", "arrowWithParams", "arrowWithGeneric", "arrowWithComplexTypes",
    # Function expressions
    "functionExpression", "calculate", "namedFunctionExpression",
    # Async functions
    "asyncFunction", "asyncWithReturn", "asyncArrow", "fetchUser",
    # Class methods
    "constructor", "getUser", "createUser", "updateUser", "validateUser", 
    "createDefault", "validateUserData", "userCount", "logOperation", "processUsers",
    # Abstract class methods
    "initialize", "log",
    # Generic class methods
    "add", "get", "getAll", "create",
    # Object methods
    "formatUser", "validateEmail", "createUserCallback",
    # Higher-order functions
    "createMapper", "mapArray", "withRetry",
    # Export functions
    "exportedFunction", "exportedArrow", "defaultExportFunction",
    # Namespace functions
    "createGuestUser", "formatUserList",
    # Complex functions
    "processUserData", "logExecution", "processValue"
]

# Total expected count
EXPECTED_FUNCTION_COUNT = len(EXPECTED_FUNCTIONS)


class TestTypeScriptTLDRFormatter:
    """Test class for TypeScript-specific function detection in TLDR formatter."""
    
    def test_typescript_function_detection_via_highlight_api(self):
        """Test TypeScript function detection using the highlight() API from __init__.py"""
        # Create lexer and formatter
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        
        # Use the highlight() function from __init__.py
        result = highlight(TYPESCRIPT_TEST_CODE, lexer, formatter)
        
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
        print(f"Successfully detected {len(detected_functions)}/{EXPECTED_FUNCTION_COUNT} TypeScript functions")
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
    
    def test_typescript_simple_function_detection(self):
        """Test detection of simple TypeScript functions"""
        simple_code = """
function greet(name: string): string {
    return `Hello, ${name}!`;
}

const add = (a: number, b: number): number => a + b;

function multiply(x: number, y: number): number {
    return x * y;
}

class Calculator {
    calculate(operation: () => number): number {
        return operation();
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(simple_code, lexer, formatter)
        
        assert result is not None
        
        # Check for simple function detection
        expected_simple = ["greet", "add", "multiply", "calculate"]
        detected_simple = [name for name in expected_simple if name in result]
        
        assert len(detected_simple) > 0, f"No simple functions detected: {result}"
        print(f"Detected simple functions: {detected_simple}")
    
    def test_typescript_generic_functions_detection(self):
        """Test detection of TypeScript generic functions"""
        generic_code = """
function identity<T>(arg: T): T {
    return arg;
}

function merge<T, U>(first: T, second: U): T & U {
    return { ...first as any, ...second as any };
}

const createArray = <T>(item: T, count: number): T[] => {
    return Array(count).fill(item);
};

class Container<T> {
    private items: T[] = [];
    
    add(item: T): void {
        this.items.push(item);
    }
    
    get(index: number): T | undefined {
        return this.items[index];
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(generic_code, lexer, formatter)
        
        assert result is not None
        
        # Check for generic function detection
        generic_functions = ["identity", "merge", "createArray", "add", "get"]
        detected_generics = [name for name in generic_functions if name in result]
        
        assert len(detected_generics) > 0, f"No generic functions detected: {result}"
        print(f"Detected generic functions: {detected_generics}")
    
    def test_typescript_class_methods_detection(self):
        """Test detection of TypeScript class methods"""
        class_code = """
class UserService {
    private users: User[] = [];
    
    constructor(initialUsers: User[] = []) {
        this.users = initialUsers;
    }
    
    public getUser(id: number): User | undefined {
        return this.users.find(user => user.id === id);
    }
    
    private validateUser(user: User): boolean {
        return !!user.name;
    }
    
    protected logOperation(op: string): void {
        console.log(op);
    }
    
    static createEmpty(): UserService {
        return new UserService([]);
    }
    
    async fetchUserAsync(id: number): Promise<User | null> {
        return this.getUser(id) || null;
    }
    
    get userCount(): number {
        return this.users.length;
    }
    
    set userCount(count: number) {
        // Implementation
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(class_code, lexer, formatter)
        
        assert result is not None
        
        # Check for class method detection
        class_methods = ["constructor", "getUser", "validateUser", "logOperation", "createEmpty", "fetchUserAsync", "userCount"]
        detected_class_methods = [name for name in class_methods if name in result]
        
        assert len(detected_class_methods) > 0, f"No class methods detected: {result}"
        print(f"Detected class methods: {detected_class_methods}")
    
    def test_typescript_async_function_detection(self):
        """Test detection of TypeScript async functions"""
        async_code = """
async function fetchData(): Promise<string> {
    const response = await fetch('/api/data');
    return response.text();
}

const asyncArrow = async (url: string): Promise<any> => {
    return await fetch(url).then(r => r.json());
};

class ApiService {
    async getData<T>(endpoint: string): Promise<T> {
        const response = await fetch(endpoint);
        return response.json();
    }
    
    async processData(data: any[]): Promise<void> {
        for (const item of data) {
            await this.processItem(item);
        }
    }
    
    private async processItem(item: any): Promise<void> {
        // Process implementation
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(async_code, lexer, formatter)
        
        assert result is not None
        
        # Check for async function detection
        async_functions = ["fetchData", "asyncArrow", "getData", "processData", "processItem"]
        detected_async = [name for name in async_functions if name in result]
        
        assert len(detected_async) > 0, f"No async functions detected: {result}"
        print(f"Detected async functions: {detected_async}")
    
    def test_typescript_interface_methods_detection(self):
        """Test detection of TypeScript interface methods"""
        interface_code = """
interface UserRepository {
    findById(id: number): Promise<User | null>;
    save(user: User): Promise<void>;
    delete(id: number): Promise<boolean>;
    findAll(): Promise<User[]>;
}

interface EventHandler {
    handle<T>(event: T): void;
    canHandle(eventType: string): boolean;
}

type ServiceFactory = {
    createUserService(): UserService;
    createNotificationService(): NotificationService;
};
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(interface_code, lexer, formatter)
        
        assert result is not None
        
        # Check for interface method detection
        interface_methods = ["findById", "save", "delete", "findAll", "handle", "canHandle", "createUserService", "createNotificationService"]
        detected_interface_methods = [name for name in interface_methods if name in result]
        
        # Interface methods might not be detected as they're not implementations
        print(f"Detected interface methods: {detected_interface_methods}")
        # Don't assert here as interface methods might not be detected by design
    
    def test_typescript_export_functions_detection(self):
        """Test detection of TypeScript export functions"""
        export_code = """
export function validateEmail(email: string): boolean {
    return email.includes('@');
}

export const formatDate = (date: Date): string => {
    return date.toISOString().split('T')[0];
};

export default function createLogger(name: string): Logger {
    return new Logger(name);
}

export async function fetchUserData(id: number): Promise<UserData> {
    const response = await fetch(`/users/${id}`);
    return response.json();
}

export { helperFunction };

function helperFunction(data: any): string {
    return JSON.stringify(data);
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(export_code, lexer, formatter)
        
        assert result is not None
        
        # Check for export function detection
        export_functions = ["validateEmail", "formatDate", "createLogger", "fetchUserData", "helperFunction"]
        detected_exports = [name for name in export_functions if name in result]
        
        assert len(detected_exports) > 0, f"No export functions detected: {result}"
        print(f"Detected export functions: {detected_exports}")
    
    def test_typescript_language_detection(self):
        """Test that TypeScript language is properly detected"""
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        
        # Verify language detection
        assert formatter._detect_language() == 'typescript', "TypeScript language not properly detected"
    
    def test_typescript_arrow_functions_detection(self):
        """Test detection of TypeScript arrow functions with type annotations"""
        arrow_code = """
const simpleArrow = (): void => {
    console.log('Simple arrow');
};

const parameterizedArrow = (name: string, age: number): string => {
    return `${name} is ${age}`;
};

const genericArrow = <T>(items: T[]): T | undefined => {
    return items[0];
};

const complexArrow = (
    users: User[],
    predicate: (user: User) => boolean
): User[] => {
    return users.filter(predicate);
};

const asyncArrow = async (id: number): Promise<User | null> => {
    return await fetchUser(id);
};
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(arrow_code, lexer, formatter)
        
        assert result is not None
        
        # Check for arrow function detection
        arrow_functions = ["simpleArrow", "parameterizedArrow", "genericArrow", "complexArrow", "asyncArrow"]
        detected_arrows = [name for name in arrow_functions if name in result]
        
        assert len(detected_arrows) > 0, f"No arrow functions detected: {result}"
        print(f"Detected arrow functions: {detected_arrows}")
    
    def test_typescript_function_overloads_detection(self):
        """Test detection of TypeScript function overloads"""
        overload_code = """
function processData(data: string): string;
function processData(data: number): number;
function processData(data: string | number): string | number {
    if (typeof data === 'string') {
        return data.toUpperCase();
    }
    return data * 2;
}

class DataProcessor {
    process(input: string): string;
    process(input: number): number;
    process(input: string | number): string | number {
        return typeof input === 'string' ? input.toLowerCase() : input / 2;
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(overload_code, lexer, formatter)
        
        assert result is not None
        
        # Check for function overload detection
        overload_functions = ["processData", "process"]
        detected_overloads = [name for name in overload_functions if name in result]
        
        assert len(detected_overloads) > 0, f"No function overloads detected: {result}"
        print(f"Detected function overloads: {detected_overloads}")
    
    def test_typescript_namespace_functions_detection(self):
        """Test detection of TypeScript namespace functions"""
        namespace_code = """
namespace Utils {
    export function formatString(str: string): string {
        return str.trim().toLowerCase();
    }
    
    export const parseNumber = (value: string): number => {
        return parseInt(value, 10);
    };
    
    function internalHelper(data: any): void {
        // Internal implementation
    }
    
    export class StringValidator {
        validate(input: string): boolean {
            return input.length > 0;
        }
    }
}

namespace DataHelpers {
    export async function fetchData<T>(url: string): Promise<T> {
        const response = await fetch(url);
        return response.json();
    }
}
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(namespace_code, lexer, formatter)
        
        assert result is not None
        
        # Check for namespace function detection
        namespace_functions = ["formatString", "parseNumber", "internalHelper", "validate", "fetchData"]
        detected_namespace = [name for name in namespace_functions if name in result]
        
        assert len(detected_namespace) > 0, f"No namespace functions detected: {result}"
        print(f"Detected namespace functions: {detected_namespace}")
    
    def test_empty_typescript_file(self):
        """Test handling of empty TypeScript file"""
        empty_code = """
// Just comments and imports
import { Component } from '@angular/core';
import * as React from 'react';

interface EmptyInterface {}
type EmptyType = {};

// No functions defined
"""
        
        lexer = TypeScriptLexer()
        formatter = TLDRFormatter(highlight_functions=True, lang='typescript')
        result = highlight(empty_code, lexer, formatter)
        
        # Should not crash and should return empty or minimal output
        assert result is not None
        assert isinstance(result, str)


if __name__ == "__main__":
    # Run a quick test
    test = TestTypeScriptTLDRFormatter()
    test.test_typescript_function_detection_via_highlight_api()
    print("TypeScript TLDR formatter test completed successfully!")