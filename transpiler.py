"""
Go-Extended to Go transpiler
Converts Go-Extended AST to standard Go code
"""

from typing import List, Dict, Set, Optional
from ast_nodes import *

class TranspilerError(Exception):
    """Transpiler error"""
    pass

class Transpiler:
    def __init__(self, project_mode=False):
        self.output = []
        self.indent_level = 0
        self.classes: Dict[str, ClassDecl] = {}
        self.exception_types: Set[str] = set()
        self.current_class = None
        self.current_receiver = 'this'
        self.project_mode = project_mode  # If True, does not generate exception types
        
    def transpile(self, program: Program) -> str:
        """Transpiles the program to Go"""
        self.output = []
        self.indent_level = 0
        
        # First pass: collect class information
        self._collect_classes(program)
        
        # Second pass: generate code
        self._emit_program(program)
        
        return '\n'.join(self.output)
    
    def _collect_classes(self, program: Program) -> None:
        """Collects information about classes and exceptions"""
        for decl in program.declarations:
            if isinstance(decl, ClassDecl):
                self.classes[decl.name] = decl
        
        # Detect exception usage
        self._detect_exceptions(program)
    
    def _detect_exceptions(self, node) -> None:
        """Recursively detects exception usage"""
        if isinstance(node, (TryStmt, ThrowStmt)):
            self.exception_types.add('Exception')
        elif isinstance(node, CallExpr) and isinstance(node.function, Identifier):
            if node.function.name == 'NewException':
                self.exception_types.add('Exception')
        
        # Recurse into all attributes that are lists or nodes
        for attr_name in dir(node):
            if attr_name.startswith('_'):
                continue
            attr = getattr(node, attr_name)
            if isinstance(attr, list):
                for item in attr:
                    if hasattr(item, '__class__') and issubclass(item.__class__, ASTNode):
                        self._detect_exceptions(item)
            elif hasattr(attr, '__class__') and issubclass(attr.__class__, ASTNode):
                self._detect_exceptions(attr)
    
    def _emit(self, text: str) -> None:
        """Emits text with indentation"""
        if text.strip():
            self.output.append('    ' * self.indent_level + text)
        else:
            self.output.append('')
    
    def _emit_line(self, text: str = '') -> None:
        """Emits a line"""
        self._emit(text)
    
    def _indent(self) -> None:
        """Increase indentation"""
        self.indent_level += 1
    
    def _dedent(self) -> None:
        """Decrease indentation"""
        self.indent_level = max(0, self.indent_level - 1)
    
    def _emit_program(self, program: Program) -> None:
        """Emits the program"""
        # Package
        self._emit_line(f'package {program.package}')
        self._emit_line()
        
        # Imports (combines user imports with required imports)
        all_imports = set()
        
        # User imports
        for imp in program.imports:
            if imp.path.startswith('"') and imp.path.endswith('"'):
                all_imports.add(imp.path)
            else:
                all_imports.add(f'"{imp.path}"')
        
        # Required imports for exceptions
        if self.exception_types:
            all_imports.add('"fmt"')
            all_imports.add('"errors"')
        
        if all_imports:
            self._emit_line('import (')
            self._indent()
            for imp_path in sorted(all_imports):
                self._emit_line(imp_path)
            self._dedent()
            self._emit_line(')')
            self._emit_line()
        
        # Generate types for exceptions (only if not in project mode)
        if self.exception_types and not self.project_mode:
            self._emit_exception_types()
            self._emit_line()
        
        # Declarations
        for decl in program.declarations:
            self._emit_declaration(decl)
            self._emit_line()
    
    def _emit_import(self, imp: ImportDecl) -> None:
        """Emits import"""
        if imp.alias:
            self._emit_line(f'import {imp.alias} "{imp.path}"')
        else:
            self._emit_line(f'import "{imp.path}"')
    
    def _emit_exception_types(self) -> None:
        """Emits types for exceptions"""
        self._emit_line('// Exception types')
        self._emit_line('type Exception interface {')
        self._indent()
        self._emit_line('Error() string')
        self._emit_line('Type() string')
        self._dedent()
        self._emit_line('}')
        self._emit_line()
        
        self._emit_line('type BaseException struct {')
        self._indent()
        self._emit_line('message string')
        self._emit_line('exType string')
        self._dedent()
        self._emit_line('}')
        self._emit_line()
        
        self._emit_line('func (e *BaseException) Error() string {')
        self._indent()
        self._emit_line('return e.message')
        self._dedent()
        self._emit_line('}')
        self._emit_line()
        
        self._emit_line('func (e *BaseException) Type() string {')
        self._indent()
        self._emit_line('return e.exType')
        self._dedent()
        self._emit_line('}')
        self._emit_line()
        
        self._emit_line('func NewException(exType, message string) Exception {')
        self._indent()
        self._emit_line('return &BaseException{message: message, exType: exType}')
        self._dedent()
        self._emit_line('}')
    
    def _emit_declaration(self, decl: Declaration) -> None:
        """Emits declaration"""
        if isinstance(decl, FuncDecl):
            self._emit_func_decl(decl)
        elif isinstance(decl, VarDecl):
            self._emit_var_decl(decl)
        elif isinstance(decl, ConstDecl):
            self._emit_const_decl(decl)
        elif isinstance(decl, TypeDecl):
            self._emit_type_decl(decl)
        elif isinstance(decl, StructDecl):
            self._emit_struct_decl(decl)
        elif isinstance(decl, InterfaceDecl):
            self._emit_interface_decl(decl)
        elif isinstance(decl, ClassDecl):
            self._emit_class_decl(decl)
        else:
            raise TranspilerError(f"Unsupported declaration: {type(decl)}")
    
    def _emit_func_decl(self, decl: FuncDecl) -> None:
        """Emits function declaration"""
        params = ', '.join(f'{p.name} {p.type}' for p in decl.params)
        
        if decl.return_type:
            self._emit_line(f'func {decl.name}({params}) {decl.return_type} {{')
        else:
            self._emit_line(f'func {decl.name}({params}) {{')
        
        self._indent()
        self._emit_block_stmt(decl.body)
        self._dedent()
        self._emit_line('}')
    
    def _emit_var_decl(self, decl: VarDecl) -> None:
        """Emits variable declaration"""
        if decl.type and decl.value:
            value = self._expr_to_string(decl.value)
            self._emit_line(f'var {decl.name} {decl.type} = {value}')
        elif decl.type:
            self._emit_line(f'var {decl.name} {decl.type}')
        elif decl.value:
            value = self._expr_to_string(decl.value)
            self._emit_line(f'var {decl.name} = {value}')
        else:
            raise TranspilerError("Variable must have type or value")
    
    def _emit_const_decl(self, decl: ConstDecl) -> None:
        """Emits constant declaration"""
        value = self._expr_to_string(decl.value)
        if decl.type:
            self._emit_line(f'const {decl.name} {decl.type} = {value}')
        else:
            self._emit_line(f'const {decl.name} = {value}')
    
    def _emit_type_decl(self, decl: TypeDecl) -> None:
        """Emits type declaration"""
        self._emit_line(f'type {decl.name} {decl.type}')
    
    def _emit_struct_decl(self, decl: StructDecl) -> None:
        """Emits struct declaration"""
        self._emit_line(f'type {decl.name} struct {{')
        self._indent()
        for field in decl.fields:
            self._emit_line(f'{field.name} {field.type}')
        self._dedent()
        self._emit_line('}')
    
    def _emit_interface_decl(self, decl: InterfaceDecl) -> None:
        """Emits interface declaration"""
        self._emit_line(f'type {decl.name} interface {{')
        self._indent()
        for method in decl.methods:
            params = ', '.join(f'{p.name} {p.type}' for p in method.params)
            if method.return_type:
                self._emit_line(f'{method.name}({params}) {method.return_type}')
            else:
                self._emit_line(f'{method.name}({params})')
        self._dedent()
        self._emit_line('}')
    
    def _emit_class_decl(self, decl: ClassDecl) -> None:
        """Emits class declaration (converted to struct + methods)"""
        self.current_class = decl.name
        
        # Struct for the class
        self._emit_line(f'type {decl.name} struct {{')
        self._indent()
        
        # Inheritance (embedding)
        if decl.extends:
            self._emit_line(f'{decl.extends}')
        
        # Fields
        for field in decl.fields:
            if field.value:
                # Fields with initial values will be initialized in the constructor
                self._emit_line(f'{field.name} {field.type}')
            else:
                self._emit_line(f'{field.name} {field.type}')
        
        self._dedent()
        self._emit_line('}')
        self._emit_line()
        
        # Constructor
        if decl.constructor:
            self._emit_constructor(decl.name, decl.constructor, decl.fields)
            self._emit_line()
        else:
            # Default constructor
            self._emit_default_constructor(decl.name, decl.fields)
            self._emit_line()
        
        # Methods
        for method in decl.methods:
            self._emit_method(decl.name, method)
            self._emit_line()
        
        self.current_class = None
    
    def _emit_constructor(self, class_name: str, constructor: ConstructorDecl, fields: List[ClassField]) -> None:
        """Emits constructor"""
        params = ', '.join(f'{p.name} {p.type}' for p in constructor.params)
        self._emit_line(f'func New{class_name}({params}) *{class_name} {{')
        self._indent()
        
        self._emit_line(f'obj := &{class_name}{{}}')
        
        # Inicializa campos com valores padrão
        for field in fields:
            if field.value:
                value = self._expr_to_string(field.value)
                self._emit_line(f'obj.{field.name} = {value}')
        
        # Constructor body (replaces 'this' with 'obj')
        old_class = self.current_class
        old_receiver = getattr(self, 'current_receiver', 'this')
        self.current_class = class_name
        self.current_receiver = 'obj'
        
        for stmt in constructor.body.statements:
            self._emit_statement(stmt)
        
        self.current_class = old_class
        self.current_receiver = old_receiver
        
        self._emit_line('return obj')
        self._dedent()
        self._emit_line('}')
    
    def _emit_default_constructor(self, class_name: str, fields: List[ClassField]) -> None:
        """Emits default constructor"""
        self._emit_line(f'func New{class_name}() *{class_name} {{')
        self._indent()
        
        self._emit_line(f'obj := &{class_name}{{}}')
        
        # Inicializa campos com valores padrão
        for field in fields:
            if field.value:
                value = self._expr_to_string(field.value)
                self._emit_line(f'obj.{field.name} = {value}')
        
        self._emit_line('return obj')
        self._dedent()
        self._emit_line('}')
    
    def _emit_method(self, class_name: str, method: MethodDecl) -> None:
        """Emits method"""
        params = ', '.join(f'{p.name} {p.type}' for p in method.params)
        
        if method.return_type:
            self._emit_line(f'func (this *{class_name}) {method.name}({params}) {method.return_type} {{')
        else:
            self._emit_line(f'func (this *{class_name}) {method.name}({params}) {{')
        
        self._indent()
        self._emit_block_stmt(method.body)
        self._dedent()
        self._emit_line('}')
    
    def _emit_block_stmt(self, block: BlockStmt) -> None:
        """Emits block of statements"""
        for stmt in block.statements:
            self._emit_statement(stmt)
    
    def _emit_statement(self, stmt: Statement) -> None:
        """Emits statement"""
        if isinstance(stmt, BlockStmt):
            self._emit_line('{')
            self._indent()
            self._emit_block_stmt(stmt)
            self._dedent()
            self._emit_line('}')
        
        elif isinstance(stmt, ExpressionStmt):
            # Special handling for parent class constructor calls
            if isinstance(stmt.expression, CallExpr) and isinstance(stmt.expression.function, SelectorExpr):
                if isinstance(stmt.expression.function.object, SuperExpr):
                    # super.ClassName(args) -> parent struct initialization
                    parent_class = stmt.expression.function.field
                    args = ', '.join(self._expr_to_string(arg) for arg in stmt.expression.args)
                    receiver = getattr(self, 'current_receiver', 'this')
                    self._emit_line(f'{receiver}.{parent_class} = *New{parent_class}({args})')
                    return
            
            expr = self._expr_to_string(stmt.expression)
            self._emit_line(expr)
        
        elif isinstance(stmt, VarStmt):
            if stmt.type and stmt.value:
                value = self._expr_to_string(stmt.value)
                self._emit_line(f'var {stmt.name} {stmt.type} = {value}')
            elif stmt.type:
                self._emit_line(f'var {stmt.name} {stmt.type}')
            elif stmt.value:
                value = self._expr_to_string(stmt.value)
                self._emit_line(f'{stmt.name} := {value}')
            else:
                raise TranspilerError("Variável deve ter tipo ou valor")
        
        elif isinstance(stmt, AssignStmt):
            target = self._expr_to_string(stmt.target)
            value = self._expr_to_string(stmt.value)
            self._emit_line(f'{target} {stmt.operator} {value}')
        
        elif isinstance(stmt, IfStmt):
            condition = self._expr_to_string(stmt.condition)
            self._emit_line(f'if {condition} {{')
            self._indent()
            self._emit_statement(stmt.then_stmt)
            self._dedent()
            
            if stmt.else_stmt:
                self._emit_line('} else {')
                self._indent()
                self._emit_statement(stmt.else_stmt)
                self._dedent()
            
            self._emit_line('}')
        
        elif isinstance(stmt, ForStmt):
            parts = []
            if stmt.init:
                # For init, we need to capture as string
                init_str = self._stmt_to_string(stmt.init)
                parts.append(init_str)
            else:
                parts.append('')
            
            if stmt.condition:
                parts.append(self._expr_to_string(stmt.condition))
            else:
                parts.append('')
            
            if stmt.update:
                update_str = self._stmt_to_string(stmt.update)
                parts.append(update_str)
            else:
                parts.append('')
            
            self._emit_line(f'for {"; ".join(parts)} {{')
            self._indent()
            self._emit_statement(stmt.body)
            self._dedent()
            self._emit_line('}')
        
        elif isinstance(stmt, RangeStmt):
            if stmt.key and stmt.value:
                iterable = self._expr_to_string(stmt.iterable)
                self._emit_line(f'for {stmt.key}, {stmt.value} := range {iterable} {{')
            elif stmt.key:
                iterable = self._expr_to_string(stmt.iterable)
                self._emit_line(f'for {stmt.key} := range {iterable} {{')
            else:
                iterable = self._expr_to_string(stmt.iterable)
                self._emit_line(f'for range {iterable} {{')
            
            self._indent()
            self._emit_statement(stmt.body)
            self._dedent()
            self._emit_line('}')
        
        elif isinstance(stmt, SwitchStmt):
            if stmt.expression:
                expr = self._expr_to_string(stmt.expression)
                self._emit_line(f'switch {expr} {{')
            else:
                self._emit_line('switch {')
            
            self._indent()
            
            for case in stmt.cases:
                values = ', '.join(self._expr_to_string(v) for v in case.values)
                self._emit_line(f'case {values}:')
                self._indent()
                for case_stmt in case.body:
                    self._emit_statement(case_stmt)
                self._dedent()
            
            if stmt.default_case:
                self._emit_line('default:')
                self._indent()
                for default_stmt in stmt.default_case.body:
                    self._emit_statement(default_stmt)
                self._dedent()
            
            self._dedent()
            self._emit_line('}')
        
        elif isinstance(stmt, ReturnStmt):
            if stmt.value:
                value = self._expr_to_string(stmt.value)
                self._emit_line(f'return {value}')
            else:
                self._emit_line('return')
        
        elif isinstance(stmt, BreakStmt):
            self._emit_line('break')
        
        elif isinstance(stmt, ContinueStmt):
            self._emit_line('continue')
        
        elif isinstance(stmt, GoStmt):
            call = self._expr_to_string(stmt.call)
            self._emit_line(f'go {call}')
        
        elif isinstance(stmt, DeferStmt):
            call = self._expr_to_string(stmt.call)
            self._emit_line(f'defer {call}')
        
        elif isinstance(stmt, TryStmt):
            self._emit_try_stmt(stmt)
        
        elif isinstance(stmt, ThrowStmt):
            expr = self._expr_to_string(stmt.expression)
            self._emit_line(f'panic({expr})')
        
        else:
            raise TranspilerError(f"Unsupported statement: {type(stmt)}")
    
    def _emit_try_stmt(self, stmt: TryStmt) -> None:
        """Emits try statement (converted to defer/recover)"""
        self.exception_types.add('Exception')
        
        # Função anônima com defer/recover
        self._emit_line('func() {')
        self._indent()
        
        # defer com recover
        if stmt.catch_blocks:
            self._emit_line('defer func() {')
            self._indent()
            self._emit_line('if r := recover(); r != nil {')
            self._indent()
            
            # Converte recover para Exception
            self._emit_line('var ex Exception')
            self._emit_line('if e, ok := r.(Exception); ok {')
            self._indent()
            self._emit_line('ex = e')
            self._dedent()
            self._emit_line('} else {')
            self._indent()
            self._emit_line('ex = NewException("RuntimeError", fmt.Sprintf("%v", r))')
            self._dedent()
            self._emit_line('}')
            self._emit_line()
            
            # Catch blocks
            for i, catch in enumerate(stmt.catch_blocks):
                if i > 0:
                    self._emit_line('} else ')
                
                if catch.exception_type:
                    self._emit_line(f'if ex.Type() == "{catch.exception_type}" {{')
                else:
                    self._emit_line('if true {')
                
                self._indent()
                
                if catch.exception_var:
                    self._emit_line(f'{catch.exception_var} := ex')
                
                self._emit_block_stmt(catch.body)
                self._dedent()
            
            self._emit_line('}')
            self._dedent()
            self._emit_line('}')
            self._dedent()
            self._emit_line('}()')
        
        # Finally block
        if stmt.finally_block:
            self._emit_line('defer func() {')
            self._indent()
            self._emit_block_stmt(stmt.finally_block.body)
            self._dedent()
            self._emit_line('}()')
        
        # Try body
        self._emit_block_stmt(stmt.body)
        
        self._dedent()
        self._emit_line('}()')
    
    def _stmt_to_string(self, stmt: Statement) -> str:
        """Converts statement to string"""
        if isinstance(stmt, VarStmt):
            if stmt.type and stmt.value:
                value = self._expr_to_string(stmt.value)
                return f'var {stmt.name} {stmt.type} = {value}'
            elif stmt.value:
                value = self._expr_to_string(stmt.value)
                return f'{stmt.name} := {value}'
            else:
                return f'var {stmt.name} {stmt.type}'
        
        elif isinstance(stmt, AssignStmt):
            target = self._expr_to_string(stmt.target)
            value = self._expr_to_string(stmt.value)
            return f'{target} {stmt.operator} {value}'
        
        elif isinstance(stmt, ExpressionStmt):
            return self._expr_to_string(stmt.expression)
        
        else:
            raise TranspilerError(f"Statement cannot be converted to string: {type(stmt)}")
    
    def _expr_to_string(self, expr: Expression) -> str:
        """Converts expression to string"""
        if isinstance(expr, BinaryExpr):
            left = self._expr_to_string(expr.left)
            right = self._expr_to_string(expr.right)
            return f'({left} {expr.operator} {right})'
        
        elif isinstance(expr, UnaryExpr):
            operand = self._expr_to_string(expr.operand)
            return f'{expr.operator}{operand}'
        
        elif isinstance(expr, CallExpr):
            func = self._expr_to_string(expr.function)
            args = ', '.join(self._expr_to_string(arg) for arg in expr.args)
            return f'{func}({args})'
        
        elif isinstance(expr, IndexExpr):
            obj = self._expr_to_string(expr.object)
            index = self._expr_to_string(expr.index)
            return f'{obj}[{index}]'
        
        elif isinstance(expr, SelectorExpr):
            obj = self._expr_to_string(expr.object)
            return f'{obj}.{expr.field}'
        
        elif isinstance(expr, Identifier):
            return expr.name
        
        elif isinstance(expr, Literal):
            if expr.type == 'string':
                # Escape special characters
                escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
                return f'"{escaped}"'
            elif expr.type == 'bool':
                return 'true' if expr.value else 'false'
            else:
                return str(expr.value)
        
        elif isinstance(expr, NewExpr):
            args = ', '.join(self._expr_to_string(arg) for arg in expr.args)
            return f'New{expr.class_name}({args})'
        
        elif isinstance(expr, ThisExpr):
            return getattr(self, 'current_receiver', 'this')
        
        elif isinstance(expr, SuperExpr):
            # Super is not used directly in Go; embedding handles inheritance
            return getattr(self, 'current_receiver', 'this')
        
        else:
            raise TranspilerError(f"Unsupported expression: {type(expr)}")
