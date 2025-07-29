# Go-Plus Transpiler

**ATTENTION: THIS IS AN EXPERIMENTAL PROJECT!**

A complete transpiler that extends Go with object-oriented features like classes, inheritance, and exception handling, then converts the extended syntax back to idiomatic standard Go code.

## Key Features:
- Classes with inheritance and constructors
- Exception handling (try/catch/finally/throw)
- Multi-file project support with automatic dependency resolution
- Centralized exception management
- Complete CLI with project scaffolding
- Generates clean, readable Go code

Perfect for developers who want OOP features in Go while maintaining compatibility with the standard Go ecosystem.

**Supports both single files and complete multi-file projects with packages.**

## Features

### Supported Extensions

#### Classes
- Class definitions with fields and methods
- Custom constructors
- Simple inheritance with `extends`
- `this` reference for the current object
- `super` reference for the parent class
- Instantiation with `new ClassName(args)`

#### Exceptions
- `try/catch/finally` blocks
- `throw` command to throw exceptions
- Multiple `catch` blocks with specific types
- Exception system based on interfaces

### Go-Plus Syntax

#### Classes
```go
class Person {
    name string
    age int
    
    // Constructor
    Person(n string, a int) {
        this.name = n
        this.age = a
    }
    
    getName() string {
        return this.name
    }
    
    setAge(a int) {
        if a < 0 {
            throw new Exception("InvalidAge", "Age cannot be negative")
        }
        this.age = a
    }
}

class Student extends Person {
    studentId string
    
    Student(n string, a int, id string) {
        super(n, a)
        this.studentId = id
    }
    
    study() {
        fmt.Printf("%s is studying\n", this.name)
    }
}
```

#### Exceptions
```go
func main() {
    try {
        person := new Person("John", -5)
    } catch (Exception e) {
        fmt.Printf("Error: %s\n", e.Error())
    } finally {
        fmt.Println("Cleanup")
    }
}
```

## How to Use

### Installation
```bash
# Clone or download the transpiler files
cd goe2go
```

### Main CLI - goe2go.py

The transpiler offers two operation modes:

#### 1. Complete Projects (Recommended)

```bash
# Initialize new project
python3 goe2go.py init my_project --module github.com/user/my_project

# Build project
python3 goe2go.py build

# Build and run
python3 goe2go.py run

# Show project information
python3 goe2go.py info
```

#### 2. Single Files

```bash
# Transpile a single file
python3 goe2go.py transpile examples/example1.gox -o output.go

# Verbose mode
python3 goe2go.py transpile examples/example1.gox -o output.go -v
```

### Project Structure

A Go-Plus project has the following structure:

```
my_project/
├── goe2go.json          # Project configuration
├── src/                 # Go-Plus source code
│   ├── main/
│   │   └── main.gox
│   ├── models/
│   │   ├── person.gox
│   │   └── student.gox
│   └── utils/
│       └── validator.gox
└── build/               # Generated Go code
    ├── go.mod
    ├── exceptions/
    │   └── exceptions.go
    └── src/
        ├── main/
        ├── models/
        └── utils/
```

### Project Configuration (goe2go.json)

```json
{
  "name": "my_project",
  "version": "1.0.0",
  "main_package": "main",
  "source_dir": "src",
  "output_dir": "build",
  "go_mod_name": "github.com/user/my_project"
}
```

### Testing
```bash
# Run tests
python3 test_transpiler.py

# Complete demonstration
python3 demo.py
```

## Architecture

### Components

1. **Lexer** (`lexer.py`)
   - Converts source code to tokens
   - Supports all Go keywords + extensions
   - Handles comments, strings and numbers

2. **Parser** (`parser.py`) 
   - Converts tokens to AST (Abstract Syntax Tree)
   - Implements grammar for Go + classes + exceptions
   - Syntax analysis with error recovery

3. **AST Nodes** (`ast_nodes.py`)
   - Syntax tree node definitions
   - Structures for classes, methods, exceptions
   - Well-defined type hierarchy

4. **Transpiler** (`transpiler.py`)
   - Converts AST to standard Go code
   - Classes → structs + methods with receivers
   - Exceptions → defer/recover + interfaces
   - Constructors → `NewClassName` functions

5. **Project Manager** (`project_manager.py`)
   - Manages multi-file projects
   - Resolves dependencies between packages
   - Topological sorting for transpilation
   - Generates centralized exceptions file

6. **CLI** (`goe2go.py`)
   - Main command line interface
   - Support for projects and single files
   - Commands: init, build, run, info, transpile

### Main Conversions

#### Classes to Structs
```go
// Go-Plus
class Person {
    name string
    age int
    
    Person(n string, a int) {
        this.name = n
        this.age = a
    }
    
    greet() {
        fmt.Printf("Hello, I'm %s\n", this.name)
    }
}

// Standard Go
type Person struct {
    name string
    age int
}

func NewPerson(n string, a int) *Person {
    obj := &Person{}
    obj.name = n
    obj.age = a
    return obj
}

func (this *Person) greet() {
    fmt.Printf("Hello, I'm %s\n", this.name)
}
```

#### Inheritance to Embedding
```go
// Go-Plus
class Student extends Person {
    studentId string
    
    Student(n string, a int, id string) {
        super(n, a)
        this.studentId = id
    }
}

// Standard Go
type Student struct {
    Person
    studentId string
}

func NewStudent(n string, a int, id string) *Student {
    obj := &Student{}
    obj.Person = *NewPerson(n, a)
    obj.studentId = id
    return obj
}
```

#### Exceptions to Defer/Recover
```go
// Go-Plus
try {
    riskyOperation()
} catch (Exception e) {
    fmt.Println("Error:", e.Error())
} finally {
    cleanup()
}

// Standard Go (with centralized exceptions file)
func() {
    defer func() {
        if r := recover(); r != nil {
            var ex exceptions.Exception
            if e, ok := r.(exceptions.Exception); ok {
                ex = e
            } else {
                ex = exceptions.NewException("RuntimeError", fmt.Sprintf("%v", r))
            }
            
            if true {
                e := ex
                fmt.Println("Error:", e.Error())
            }
        }
    }()
    
    defer func() {
        cleanup()
    }()
    
    riskyOperation()
}()
```

#### Centralized Exception System

In projects, exceptions are centralized in a dedicated package:

```go
// exceptions/exceptions.go
package exceptions

type Exception interface {
    Error() string
    Type() string
}

type BaseException struct {
    message string
    exType string
}

func NewException(exType, message string) Exception {
    return &BaseException{message: message, exType: exType}
}
```

Each file that uses exceptions automatically imports:
```go
import "github.com/user/project/exceptions"
```

## Examples

### Example 1: Complete Project

Let's create an example project with multiple packages:

```bash
# Create project
python3 goe2go.py init example --module github.com/user/example
cd example
```

#### Compiling the Provided Example Project

To build the included example project, run:

```bash
python3 goe2go.py build -d example_project -v
```

#### src/models/person.gox
```go
package models

import "fmt"

class Person {
    name string
    age int
    
    Person(n string, a int) {
        this.name = "Unknown"
        this.age = 0
        
        if a < 0 {
            throw new Exception("InvalidAge", "Age cannot be negative")
        }
        
        this.name = n
        this.age = a
    }
    
    getName() string {
        return this.name
    }
    
    setAge(a int) {
        if a < 0 {
            throw new Exception("InvalidAge", "Age cannot be negative")
        }
        this.age = a
    }
    
    greet() {
        fmt.Printf("Hello, I'm %s and I'm %d years old\n", this.name, this.age)
    }
}
```

#### src/models/student.gox
```go
package models

import "fmt"

class Student extends Person {
    studentId string
    grade float64
    
    Student(n string, a int, id string) {
        super(n, a)
        this.studentId = id
        this.grade = 0.0
    }
    
    setGrade(g float64) {
        if g < 0.0 || g > 10.0 {
            throw new Exception("InvalidGrade", "Grade must be between 0 and 10")
        }
        this.grade = g
    }
    
    study() {
        fmt.Printf("%s (ID: %s) is studying\n", this.name, this.studentId)
    }
}
```

#### src/main/main.gox
```go
package main

import (
    "fmt"
    "github.com/user/example/src/models"
)

func main() {
    try {
        person := new models.Person("John", 25)
        person.greet()
        
        student := new models.Student("Mary", 20, "S123")
        student.setGrade(8.5)
        student.study()
        
    } catch (Exception e) {
        fmt.Printf("Error: %s\n", e.Error())
    }
}
```

#### Build and Run
```bash
# Build project
python3 goe2go.py build

# Run
python3 goe2go.py run
```

### Example 2: Single File

See `examples/example1.gox` for a single file example:
- Classes with inheritance
- Constructors
- Methods
- Exception handling

```bash
# Transpile single file
python3 goe2go.py transpile examples/example1.gox -o output.go
```

## Current Limitations

1. **Classes**
   - No access modifiers (private, protected)
   - No static methods/fields
   - Multiple inheritance not supported
   - No interfaces as field types

2. **Exceptions**
   - Simplified string-based system
   - No detailed stack traces
   - Finally always executes (even with panic)

3. **General**
   - No generics support
   - Limited type analysis
   - Basic error messages

## Recent Improvements

### System Features
- Complete multi-file project support
- Automatic dependency resolution between packages
- Topological sorting for correct transpilation
- Centralized exceptions file (avoids duplication)
- Complete CLI with `init`, `build`, `run`, `info` commands

### Exception Management
- Centralized system in dedicated `exceptions` package
- Avoids code duplication between files
- Automatic imports for files using exceptions
- Go modules compatibility

### CLI Improvements
- Project vs single file mode
- Custom directory support
- Verbose mode for debugging
- Automatic `go.mod` generation

## Project Files

```
goe2go/
├── goe2go.py              # Main CLI
├── main.py                # Single file CLI (legacy)
├── tokens.py              # Token definitions
├── lexer.py               # Lexical analyzer
├── ast_nodes.py           # AST nodes
├── parser.py              # Syntax analyzer
├── transpiler.py          # Go code generator
├── project_manager.py     # Project manager
├── test_transpiler.py     # Automated tests
├── README.md              # Documentation
├── requirements.txt       # Python dependencies
├── examples/              # Single file examples
│   ├── example1.gox
│   ├── example2.gox
│   └── advanced_example.gox
└── example_project/       # Example project
    ├── goe2go.json
    ├── src/
    │   ├── main/
    │   ├── models/
    │   └── utils/
    └── build/             # Generated Go code
        ├── go.mod
        ├── exceptions/
        └── src/
```

## Contributing

1. Fork the project
2. Create a branch for your feature
3. Add tests for new functionality
4. Run `python3 test_transpiler.py` to verify
5. Commit your changes
6. Open a Pull Request

## License

This project is open source. Feel free to use, modify and distribute.
