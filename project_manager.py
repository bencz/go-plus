"""
Go-Extended project manager
Supports multiple files and dependency resolution
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from lexer import Lexer
from parser import Parser
from transpiler import Transpiler
from ast_nodes import Program, ImportDecl, ASTNode, TryStmt, ThrowStmt, CallExpr, Identifier

@dataclass
class ProjectFile:
    """Represents a project file"""
    path: Path
    package: str
    imports: List[str]
    program: Optional[Program] = None
    transpiled: bool = False

@dataclass 
class ProjectConfig:
    """Project configuration"""
    name: str
    version: str = "1.0.0"
    main_package: str = "main"
    source_dir: str = "src"
    output_dir: str = "build"
    go_mod_name: str = ""

class ProjectManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config: Optional[ProjectConfig] = None
        self.files: Dict[str, ProjectFile] = {}  # path -> ProjectFile
        self.packages: Dict[str, List[ProjectFile]] = {}  # package -> files
        self.dependency_graph: Dict[str, Set[str]] = {}  # file -> dependencies
        
    def load_config(self) -> ProjectConfig:
        """Load project configuration"""
        config_file = self.project_root / "goe2go.json"
        
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.config = ProjectConfig(**data)
        else:
            # Default configuration
            self.config = ProjectConfig(
                name=self.project_root.name,
                go_mod_name=f"github.com/user/{self.project_root.name}"
            )
            self.save_config()
        
        return self.config
    
    def save_config(self) -> None:
        """Save project configuration"""
        if not self.config:
            return
            
        config_file = self.project_root / "goe2go.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config.__dict__, f, indent=2)
    
    def discover_files(self) -> None:
        """Discover all .gox files in the project"""
        source_dir = self.project_root / self.config.source_dir
        
        if not source_dir.exists():
            source_dir = self.project_root
        
        # Find all .gox files
        for gox_file in source_dir.rglob("*.gox"):
            self._analyze_file(gox_file)
    
    def _analyze_file(self, file_path: Path) -> None:
        """Analyze a file and extract basic information"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Tokenize and parse just to extract package and imports
            lexer = Lexer(content)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            program = parser.parse()
            
            # Extract local imports (non-stdlib)
            local_imports = []
            for imp in program.imports:
                import_path = imp.path.strip('"')
                # If it doesn't start with a common stdlib path, assume it's local
                if not self._is_stdlib_import(import_path):
                    local_imports.append(import_path)
            
            # Create file entry
            rel_path = file_path.relative_to(self.project_root)
            project_file = ProjectFile(
                path=file_path,
                package=program.package,
                imports=local_imports,
                program=program
            )
            
            self.files[str(rel_path)] = project_file
            
            # Group by package
            if program.package not in self.packages:
                self.packages[program.package] = []
            self.packages[program.package].append(project_file)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _is_stdlib_import(self, import_path: str) -> bool:
        """Check if it's a Go stdlib import"""
        stdlib_packages = {
            'fmt', 'os', 'io', 'net', 'http', 'json', 'time', 'strings',
            'strconv', 'math', 'sort', 'sync', 'context', 'errors',
            'bufio', 'bytes', 'crypto', 'encoding', 'flag', 'log',
            'path', 'regexp', 'runtime', 'testing', 'unicode'
        }
        
        # Check if it's a stdlib package or subpackage
        root_package = import_path.split('/')[0]
        return root_package in stdlib_packages or '.' not in import_path
    
    def build_dependency_graph(self) -> None:
        """Build dependency graph between files"""
        self.dependency_graph = {}
        
        for file_path, project_file in self.files.items():
            deps = set()
            
            for import_path in project_file.imports:
                # Find files that provide this import
                for other_path, other_file in self.files.items():
                    if other_file.package == import_path:
                        deps.add(other_path)
            
            self.dependency_graph[file_path] = deps
    
    def get_transpilation_order(self) -> List[str]:
        """Return transpilation order based on dependencies"""
        # Topological sort algorithm
        visited = set()
        temp_visited = set()
        order = []
        
        def visit(file_path: str):
            if file_path in temp_visited:
                raise ValueError(f"Circular dependency detected involving {file_path}")
            
            if file_path in visited:
                return
            
            temp_visited.add(file_path)
            
            # Visit dependencies first
            for dep in self.dependency_graph.get(file_path, set()):
                visit(dep)
            
            temp_visited.remove(file_path)
            visited.add(file_path)
            order.append(file_path)
        
        # Visit all files
        for file_path in self.files.keys():
            if file_path not in visited:
                visit(file_path)
        
        return order
    
    def transpile_project(self) -> None:
        """Transpile the entire project"""
        if not self.config:
            self.load_config()
        
        print(f"Transpiling project: {self.config.name}")
        
        # Discover files
        self.discover_files()
        print(f"Found {len(self.files)} .gox files")
        
        # Build dependency graph
        self.build_dependency_graph()
        
        # Get transpilation order
        try:
            order = self.get_transpilation_order()
        except ValueError as e:
            print(f"Error: {e}")
            return
        
        # Create output directory
        output_dir = self.project_root / self.config.output_dir
        output_dir.mkdir(exist_ok=True)
        
        # Analyze global exception usage
        global_exceptions = self._analyze_global_exceptions()
        
        # Generate exceptions file if needed
        if global_exceptions:
            self._generate_exceptions_file(output_dir)
        
        # Transpile files in the correct order
        project_transpiler = ProjectTranspiler(self, global_exceptions)
        
        for file_path in order:
            project_file = self.files[file_path]
            print(f"Transpiling {file_path} (package {project_file.package})")
            
            # Determine output path
            rel_path = Path(file_path)
            output_path = output_dir / rel_path.with_suffix('.go')
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Transpile with project context
            go_code = project_transpiler.transpile_file(project_file, file_path)
            
            # Save
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(go_code)
            
            project_file.transpiled = True
            print(f"Generated: {file_path} -> {output_path}")
        
        # Generate go.mod if needed
        self._generate_go_mod(output_dir)
        
        print(f"Project successfully transpiled to {output_dir}")
    
    def _generate_go_mod(self, output_dir: Path) -> None:
        """Generate go.mod file"""
        go_mod_path = output_dir / "go.mod"
        
        if not go_mod_path.exists():
            with open(go_mod_path, 'w', encoding='utf-8') as f:
                f.write(f"module {self.config.go_mod_name}\n\n")
                f.write("go 1.19\n")
            print(f"Generated {go_mod_path}")
    
    def show_project_info(self) -> None:
        """Show project information"""
        if not self.config:
            self.load_config()
        
        self.discover_files()
        self.build_dependency_graph()
        
        print(f"Project Information: {self.config.name}")
        print("=" * 50)
        print(f"Version: {self.config.version}")
        print(f"Main package: {self.config.main_package}")
        print(f"Source directory: {self.config.source_dir}")
        print(f"Output directory: {self.config.output_dir}")
        print(f"Go module: {self.config.go_mod_name}")
        print()
        
        print("Files:")
        for file_path, project_file in self.files.items():
            print(f"  {file_path} (package {project_file.package})")
            if project_file.imports:
                print(f"    Imports: {', '.join(project_file.imports)}")
        print()
        
        print("Packages:")
        for package, files in self.packages.items():
            print(f"  {package}: {len(files)} file(s)")
        print()
        
        print("Dependencies:")
        for file_path, deps in self.dependency_graph.items():
            if deps:
                print(f"  {file_path} -> {', '.join(deps)}")
    
    def init_project(self, name: str, go_mod: str = "") -> None:
        """Initializes a new project"""
        if not go_mod:
            go_mod = f"github.com/user/{name}"
        
        self.config = ProjectConfig(
            name=name,
            go_mod_name=go_mod
        )
        
        # Create directory structure
        (self.project_root / self.config.source_dir).mkdir(exist_ok=True)
        (self.project_root / self.config.output_dir).mkdir(exist_ok=True)
        
        # Save configuration
        self.save_config()
        
        # Create basic example
        example_file = self.project_root / self.config.source_dir / "main.gox"
        if not example_file.exists():
            with open(example_file, 'w', encoding='utf-8') as f:
                f.write(f'''package main

import "fmt"

class HelloWorld {{
    message string = "Hello, Go-Extended!"
    
    func SayHello() {{
        fmt.Println(this.message)
    }}
}}

func main() {{
    hello := new HelloWorld()
    hello.SayHello()
}}
''')
        
        print(f"Project '{name}' initialized in {self.project_root}")
        print(f"Example file created: {example_file}")
        print(f"Configuration saved in: goe2go.json")
    
    def _analyze_global_exceptions(self) -> bool:
        """Analyze if any file uses exceptions"""
        for project_file in self.files.values():
            if self._file_uses_exceptions(project_file.program):
                return True
        return False
    
    def _file_uses_exceptions(self, node) -> bool:
        """Check if a file uses exceptions"""
        if isinstance(node, (TryStmt, ThrowStmt)):
            return True
        elif isinstance(node, CallExpr) and isinstance(node.function, Identifier):
            if node.function.name == 'NewException':
                return True
        
        # Recurse through all attributes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, '__class__') and issubclass(item.__class__, ASTNode):
                        if self._file_uses_exceptions(item):
                            return True
            elif hasattr(attr, '__class__') and issubclass(attr.__class__, ASTNode):
                if self._file_uses_exceptions(attr):
                    return True
        
        return False
    
    def _generate_exceptions_file(self, output_dir: Path) -> None:
        """Generate common exceptions file"""
        exceptions_dir = output_dir / "exceptions"
        exceptions_dir.mkdir(exist_ok=True)
        
        exceptions_file = exceptions_dir / "exceptions.go"
        
        with open(exceptions_file, 'w', encoding='utf-8') as f:
            f.write('''package exceptions

import (
    "fmt"
    "errors"
)

// Exception types
type Exception interface {
    Error() string
    Type() string
}

type BaseException struct {
    message string
    exType string
}

func (e *BaseException) Error() string {
    return e.message
}

func (e *BaseException) Type() string {
    return e.exType
}

func NewException(exType, message string) Exception {
    return &BaseException{message: message, exType: exType}
}
''')
        
        print(f"Generated exceptions file: {exceptions_file}")


class ProjectTranspiler:
    """Specialized transpiler for projects"""
    
    def __init__(self, project_manager: ProjectManager, has_exceptions: bool):
        self.project_manager = project_manager
        self.has_exceptions = has_exceptions
    
    def transpile_file(self, project_file: ProjectFile, file_path: str) -> str:
        """Transpile a file in the context of the project"""
        from transpiler import Transpiler
        
        # Create custom transpiler in project mode
        transpiler = Transpiler(project_mode=True)
        
        # Transpile the program
        program = project_file.program
        
        # Modify imports if necessary
        if self.has_exceptions and self._program_uses_exceptions(program):
            # Add import for exceptions if using exceptions
            from ast_nodes import ImportDecl
            go_mod_name = self.project_manager.config.go_mod_name
            exceptions_import = ImportDecl(f"{go_mod_name}/exceptions")
            program.imports.append(exceptions_import)
        
        # Transpile
        go_code = transpiler.transpile(program)
        
        # Remove duplicate exception definitions if present
        if self.has_exceptions:
            go_code = self._remove_exception_definitions(go_code)
        
        return go_code
    
    def _program_uses_exceptions(self, program) -> bool:
        """Check if the program uses exceptions"""
        return self.project_manager._file_uses_exceptions(program)
    
    def _remove_exception_definitions(self, go_code: str) -> str:
        """Remove duplicate exception definitions"""
        lines = go_code.split('\n')
        filtered_lines = []
        skip_block = False
        in_import_block = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detect start of exception block
            if '// Exception types' in line:
                skip_block = True
                # Skip until finding a blank line after the block
                while i < len(lines) and not (lines[i].strip() == '' and i + 1 < len(lines) and 
                                             (lines[i + 1].startswith('type ') or lines[i + 1].startswith('func ') or 
                                              lines[i + 1].strip() == '')):
                    i += 1
                skip_block = False
                i += 1
                continue
            
            # Detect import block
            if line.strip() == 'import (':
                in_import_block = True
                # Collect all imports
                import_lines = [line]
                i += 1
                while i < len(lines) and lines[i].strip() != ')':
                    import_line = lines[i]
                    # Remove fmt and errors imports if only for exceptions
                    if import_line.strip() not in ['"fmt"', '"errors"']:
                        import_lines.append(import_line)
                    i += 1
                
                # Add closing parenthesis
                if i < len(lines):
                    import_lines.append(lines[i])  # )
                
                # Only add block if it contains more than fmt/errors
                if len(import_lines) > 2:  # More than import( and )
                    filtered_lines.extend(import_lines)
                
                in_import_block = False
                i += 1
                continue
            
            if not skip_block:
                filtered_lines.append(line)
            
            i += 1
        
        return '\n'.join(filtered_lines)
