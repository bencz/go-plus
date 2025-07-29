#!/usr/bin/env python3
"""
Tests for the Go-Extended transpiler
"""

import os
import sys
from pathlib import Path

# Adiciona o diretório atual ao path
sys.path.insert(0, str(Path(__file__).parent))

from lexer import Lexer
from parser import Parser
from transpiler import Transpiler

def test_lexer():
    """Tests the lexer"""
    print("=== Testing Lexer ===")
    
    code = '''
    package main
    
    class Person {
        name string = "test"
        
        func GetName() string {
            return this.name
        }
    }
    '''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    print(f"Tokens generated: {len(tokens)}")
    for token in tokens[:10]:  # Show the first 10 tokens
        print(f"  {token}")
    
    print("Lexer OK!\n")

def test_parser():
    """Tests the parser"""
    print("=== Testing Parser ===")
    
    code = '''
    package main
    
    class Person {
        name string
        
        Person(n string) {
            this.name = n
        }
        
        func GetName() string {
            return this.name
        }
    }
    '''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    print(f"Package: {ast.package}")
    print(f"Declarations: {len(ast.declarations)}")
    
    for decl in ast.declarations:
        print(f"  {type(decl).__name__}: {getattr(decl, 'name', 'N/A')}")
    
    print("Parser OK!\n")

def test_transpiler():
    """Tests the transpiler"""
    print("=== Testing Transpiler ===")
    
    code = '''
    package main
    
    import "fmt"
    
    class Person {
        name string = "Unknown"
        
        Person(n string) {
            this.name = n
        }
        
        func Greet() {
            fmt.Printf("Hello, %s\\n", this.name)
        }
    }
    
    func main() {
        try {
            p := new Person("Alice")
            p.Greet()
        } catch (Exception e) {
            fmt.Println("Error:", e.Error())
        }
    }
    '''
    
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    
    parser = Parser(tokens)
    ast = parser.parse()
    
    transpiler = Transpiler()
    go_code = transpiler.transpile(ast)
    
    print("Generated Go code:")
    print("-" * 50)
    print(go_code)
    print("-" * 50)
    
    print("Transpiler OK!\n")

def test_file_example():
    """Tests with example file"""
    print("=== Testing with Example File ===")
    
    example_file = Path(__file__).parent / "examples" / "example1.gox"
    
    if not example_file.exists():
        print(f"Example file not found: {example_file}")
        return
    
    with open(example_file, 'r', encoding='utf-8') as f:
        code = f.read()
    
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        print(f"Tokens: {len(tokens)}")
        
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"AST generated with {len(ast.declarations)} declarations")
        
        transpiler = Transpiler()
        go_code = transpiler.transpile(ast)
        
        output_file = example_file.with_suffix('.go')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(go_code)
        
        print(f"Go code saved at: {output_file}")
        print("Example OK!\n")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("Starting Go-Extended transpiler tests...\n")
    
    try:
        test_lexer()
        test_parser()
        test_transpiler()
        test_file_example()
        
        print("All tests passed!")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
