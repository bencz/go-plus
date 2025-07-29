#!/usr/bin/env python3
"""
Go-Extended to Go Transpiler
Transpiles Go code with classes and exceptions to standard Go
"""

import sys
import argparse
from pathlib import Path
from lexer import Lexer
from parser import Parser
from transpiler import Transpiler

def main():
    parser = argparse.ArgumentParser(description='Go-Extended to Go Transpiler')
    parser.add_argument('input', help='Input Go-Extended file')
    parser.add_argument('-o', '--output', help='Output Go file (default: <input>.go)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode')
    
    args = parser.parse_args()
    
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"Error: File '{input_file}' not found")
        sys.exit(1)
    
    output_file = Path(args.output) if args.output else input_file.with_suffix('.go')
    
    try:
        # Read source code
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        if args.verbose:
            print(f"Reading file: {input_file}")
        
        # Tokenize
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        if args.verbose:
            print(f"Generated tokens: {len(tokens)}")
        
        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        
        if args.verbose:
            print("AST generated successfully")
        
        # Transpile
        transpiler = Transpiler()
        go_code = transpiler.transpile(ast)
        
        # Write output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(go_code)
        
        print(f"Transpilation completed: {input_file} -> {output_file}")
        
    except Exception as e:
        print(f"Error during transpilation: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
