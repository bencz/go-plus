"""
Parser for Go-Extended
Converts tokens into an AST (Abstract Syntax Tree)
"""

from typing import List, Optional, Union
from tokens import Token, TokenType
from ast_nodes import *

class ParseError(Exception):
    """Parser error"""
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = [t for t in tokens if t.type not in [TokenType.COMMENT, TokenType.NEWLINE]]
        self.pos = 0
        self.current_token = self.tokens[0] if self.tokens else None
    
    def advance(self) -> None:
        """Advances to the next token"""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None
    
    def peek(self, offset: int = 1) -> Optional[Token]:
        """Peeks at the next token without advancing"""
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
    
    def match(self, *token_types: TokenType) -> bool:
        """Checks if the current token is one of the specified types"""
        if not self.current_token:
            return False
        return self.current_token.type in token_types
    
    def consume(self, token_type: TokenType, message: str = None) -> Token:
        """Consumes a token of the specified type or raises an error"""
        if not self.current_token or self.current_token.type != token_type:
            msg = message or f"Expected {token_type.name}, found {self.current_token.type.name if self.current_token else 'EOF'}"
            raise ParseError(msg)
        
        token = self.current_token
        self.advance()
        return token
    
    def parse(self) -> Program:
        """Main parse method - returns the program"""
        # package declaration
        self.consume(TokenType.PACKAGE, "Expected 'package'")
        package_name = self.consume(TokenType.IDENTIFIER, "Expected package name").value
        
        # imports
        imports = []
        while self.match(TokenType.IMPORT):
            imports.append(self.parse_import())
        
        # declarations
        declarations = []
        while self.current_token and not self.match(TokenType.EOF):
            declarations.append(self.parse_declaration())
        
        return Program(package_name, imports, declarations)
    
    def parse_import(self) -> ImportDecl:
        """Parses an import declaration"""
        self.consume(TokenType.IMPORT)
        
        alias = None
        if self.match(TokenType.IDENTIFIER) and self.peek() and self.peek().type == TokenType.STRING:
            alias = self.current_token.value
            self.advance()
        
        path = self.consume(TokenType.STRING, "Expected import path").value
        return ImportDecl(path, alias)
    
    def parse_declaration(self) -> Declaration:
        """Parses a declaration"""
        if self.match(TokenType.FUNC):
            return self.parse_func_decl()
        elif self.match(TokenType.VAR):
            return self.parse_var_decl()
        elif self.match(TokenType.CONST):
            return self.parse_const_decl()
        elif self.match(TokenType.TYPE):
            return self.parse_type_decl()
        elif self.match(TokenType.STRUCT):
            return self.parse_struct_decl()
        elif self.match(TokenType.INTERFACE):
            return self.parse_interface_decl()
        elif self.match(TokenType.CLASS):
            return self.parse_class_decl()
        else:
            raise ParseError(f"Unrecognized declaration: {self.current_token.value if self.current_token else 'EOF'}")
    
    def parse_func_decl(self) -> FuncDecl:
        """Parses a function declaration"""
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER, "Expected function name").value
        
        self.consume(TokenType.LPAREN)
        params = self.parse_parameter_list()
        self.consume(TokenType.RPAREN)
        
        return_type = None
        if not self.match(TokenType.LBRACE):
            return_type = self.consume(TokenType.IDENTIFIER, "Expected return type").value
        
        body = self.parse_block_stmt()
        return FuncDecl(name, params, return_type, body)
    
    def parse_var_decl(self) -> VarDecl:
        """Parses a variable declaration"""
        self.consume(TokenType.VAR)
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        type_name = None
        if not self.match(TokenType.ASSIGN):
            type_name = self.consume(TokenType.IDENTIFIER, "Expected variable type").value
        
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
        
        return VarDecl(name, type_name, value)
    
    def parse_const_decl(self) -> ConstDecl:
        """Parses a constant declaration"""
        self.consume(TokenType.CONST)
        name = self.consume(TokenType.IDENTIFIER, "Expected constant name").value
        
        type_name = None
        if not self.match(TokenType.ASSIGN):
            type_name = self.consume(TokenType.IDENTIFIER, "Expected constant type").value
        
        self.consume(TokenType.ASSIGN)
        value = self.parse_expression()
        
        return ConstDecl(name, type_name, value)
    
    def parse_type_decl(self) -> TypeDecl:
        """Parses a type declaration"""
        self.consume(TokenType.TYPE)
        name = self.consume(TokenType.IDENTIFIER, "Expected type name").value
        type_def = self.consume(TokenType.IDENTIFIER, "Expected type definition").value
        
        return TypeDecl(name, type_def)
    
    def parse_struct_decl(self) -> StructDecl:
        """Parses a struct declaration"""
        self.consume(TokenType.STRUCT)
        name = self.consume(TokenType.IDENTIFIER, "Expected struct name").value
        
        self.consume(TokenType.LBRACE)
        fields = []
        
        while not self.match(TokenType.RBRACE) and self.current_token:
            field_name = self.consume(TokenType.IDENTIFIER, "Expected field name").value
            field_type = self.consume(TokenType.IDENTIFIER, "Expected field type").value
            fields.append(StructField(field_name, field_type))
        
        self.consume(TokenType.RBRACE)
        return StructDecl(name, fields)
    
    def parse_interface_decl(self) -> InterfaceDecl:
        """Parses an interface declaration"""
        self.consume(TokenType.INTERFACE)
        name = self.consume(TokenType.IDENTIFIER, "Expected interface name").value
        
        self.consume(TokenType.LBRACE)
        methods = []
        
        while not self.match(TokenType.RBRACE) and self.current_token:
            method_name = self.consume(TokenType.IDENTIFIER, "Expected method name").value
            
            self.consume(TokenType.LPAREN)
            params = self.parse_parameter_list()
            self.consume(TokenType.RPAREN)
            
            return_type = None
            if not self.match(TokenType.RBRACE) and self.match(TokenType.IDENTIFIER):
                return_type = self.current_token.value
                self.advance()
            
            methods.append(MethodSignature(method_name, params, return_type))
        
        self.consume(TokenType.RBRACE)
        return InterfaceDecl(name, methods)
    
    def parse_class_decl(self) -> ClassDecl:
        """Parses a class declaration (extension)"""
        self.consume(TokenType.CLASS)
        name = self.consume(TokenType.IDENTIFIER, "Expected class name").value
        
        extends = None
        if self.match(TokenType.EXTENDS):
            self.advance()
            extends = self.consume(TokenType.IDENTIFIER, "Expected parent class name").value
        
        self.consume(TokenType.LBRACE)
        
        fields = []
        methods = []
        constructor = None
        
        while not self.match(TokenType.RBRACE) and self.current_token:
            if self.match(TokenType.IDENTIFIER) and self.current_token.value == name:
                # Constructor
                constructor = self.parse_constructor()
            elif self.match(TokenType.FUNC):
                # Method
                methods.append(self.parse_method_decl())
            else:
                # Field
                field_name = self.consume(TokenType.IDENTIFIER, "Expected field name").value
                field_type = self.consume(TokenType.IDENTIFIER, "Expected field type").value
                
                field_value = None
                if self.match(TokenType.ASSIGN):
                    self.advance()
                    field_value = self.parse_expression()
                
                fields.append(ClassField(field_name, field_type, field_value))
        
        self.consume(TokenType.RBRACE)
        return ClassDecl(name, extends, fields, methods, constructor)
    
    def parse_constructor(self) -> ConstructorDecl:
        """Parses a constructor"""
        self.advance()  # class name
        
        self.consume(TokenType.LPAREN)
        params = self.parse_parameter_list()
        self.consume(TokenType.RPAREN)
        
        body = self.parse_block_stmt()
        return ConstructorDecl(params, body)
    
    def parse_method_decl(self) -> MethodDecl:
        """Parses a method declaration"""
        self.consume(TokenType.FUNC)
        name = self.consume(TokenType.IDENTIFIER, "Expected method name").value
        
        self.consume(TokenType.LPAREN)
        params = self.parse_parameter_list()
        self.consume(TokenType.RPAREN)
        
        return_type = None
        if not self.match(TokenType.LBRACE):
            return_type = self.consume(TokenType.IDENTIFIER, "Expected return type").value
        
        body = self.parse_block_stmt()
        return MethodDecl(name, params, return_type, body)
    
    def parse_parameter_list(self) -> List[Parameter]:
        """Parses a parameter list"""
        params = []
        
        while not self.match(TokenType.RPAREN) and self.current_token:
            param_name = self.consume(TokenType.IDENTIFIER, "Expected parameter name").value
            param_type = self.consume(TokenType.IDENTIFIER, "Expected parameter type").value
            params.append(Parameter(param_name, param_type))
            
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        return params
    
    def parse_block_stmt(self) -> BlockStmt:
        """Parses a block of statements"""
        self.consume(TokenType.LBRACE)
        statements = []
        
        while not self.match(TokenType.RBRACE) and self.current_token:
            statements.append(self.parse_statement())
        
        self.consume(TokenType.RBRACE)
        return BlockStmt(statements)
    
    def parse_statement(self) -> Statement:
        """Parses a statement"""
        if self.match(TokenType.VAR):
            return self.parse_var_stmt()
        elif self.match(TokenType.IF):
            return self.parse_if_stmt()
        elif self.match(TokenType.FOR):
            return self.parse_for_stmt()
        elif self.match(TokenType.SWITCH):
            return self.parse_switch_stmt()
        elif self.match(TokenType.RETURN):
            return self.parse_return_stmt()
        elif self.match(TokenType.BREAK):
            self.advance()
            return BreakStmt()
        elif self.match(TokenType.CONTINUE):
            self.advance()
            return ContinueStmt()
        elif self.match(TokenType.GO):
            return self.parse_go_stmt()
        elif self.match(TokenType.DEFER):
            return self.parse_defer_stmt()
        elif self.match(TokenType.TRY):
            return self.parse_try_stmt()
        elif self.match(TokenType.THROW):
            return self.parse_throw_stmt()
        elif self.match(TokenType.LBRACE):
            return self.parse_block_stmt()
        else:
            # Expression statement or assignment
            expr = self.parse_expression()
            
            if self.match(TokenType.ASSIGN, TokenType.SHORT_ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN,
                         TokenType.MULT_ASSIGN, TokenType.DIV_ASSIGN, TokenType.MOD_ASSIGN):
                op = self.current_token.value
                self.advance()
                value = self.parse_expression()
                return AssignStmt(expr, value, op)
            else:
                return ExpressionStmt(expr)
    
    def parse_var_stmt(self) -> VarStmt:
        """Parses a variable statement"""
        self.consume(TokenType.VAR)
        name = self.consume(TokenType.IDENTIFIER, "Expected variable name").value
        
        type_name = None
        if not self.match(TokenType.ASSIGN):
            type_name = self.consume(TokenType.IDENTIFIER, "Expected variable type").value
        
        value = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            value = self.parse_expression()
        
        return VarStmt(name, type_name, value)
    
    def parse_if_stmt(self) -> IfStmt:
        """Parses an if statement"""
        self.consume(TokenType.IF)
        condition = self.parse_expression()
        then_stmt = self.parse_statement()
        
        else_stmt = None
        if self.match(TokenType.ELSE):
            self.advance()
            else_stmt = self.parse_statement()
        
        return IfStmt(condition, then_stmt, else_stmt)
    
    def parse_for_stmt(self) -> Union[ForStmt, RangeStmt]:
        """Parses a for statement"""
        self.consume(TokenType.FOR)
        
        # Check if it's a for range
        if self.match(TokenType.IDENTIFIER):
            # Could be for range or normal for
            checkpoint = self.pos
            
            try:
                # Try to parse as range
                key = self.current_token.value
                self.advance()
                
                value = None
                if self.match(TokenType.COMMA):
                    self.advance()
                    value = self.consume(TokenType.IDENTIFIER).value
                
                self.consume(TokenType.COLON)
                self.consume(TokenType.ASSIGN)
                self.consume(TokenType.RANGE)
                
                iterable = self.parse_expression()
                body = self.parse_statement()
                
                return RangeStmt(key, value, iterable, body)
            
            except ParseError:
                # Go back to checkpoint and try normal for
                self.pos = checkpoint
                self.current_token = self.tokens[self.pos]
        
        # Normal for
        init = None
        if not self.match(TokenType.SEMICOLON):
            init = self.parse_statement()
        self.consume(TokenType.SEMICOLON)
        
        condition = None
        if not self.match(TokenType.SEMICOLON):
            condition = self.parse_expression()
        self.consume(TokenType.SEMICOLON)
        
        update = None
        if not self.match(TokenType.LBRACE):
            update = self.parse_statement()
        
        body = self.parse_statement()
        return ForStmt(init, condition, update, body)
    
    def parse_switch_stmt(self) -> SwitchStmt:
        """Parses a switch statement"""
        self.consume(TokenType.SWITCH)
        
        expression = None
        if not self.match(TokenType.LBRACE):
            expression = self.parse_expression()
        
        self.consume(TokenType.LBRACE)
        
        cases = []
        default_case = None
        
        while not self.match(TokenType.RBRACE) and self.current_token:
            if self.match(TokenType.CASE):
                self.advance()
                values = [self.parse_expression()]
                
                while self.match(TokenType.COMMA):
                    self.advance()
                    values.append(self.parse_expression())
                
                self.consume(TokenType.COLON)
                
                body = []
                while not self.match(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE) and self.current_token:
                    body.append(self.parse_statement())
                
                cases.append(CaseStmt(values, body))
            
            elif self.match(TokenType.DEFAULT):
                self.advance()
                self.consume(TokenType.COLON)
                
                body = []
                while not self.match(TokenType.CASE, TokenType.DEFAULT, TokenType.RBRACE) and self.current_token:
                    body.append(self.parse_statement())
                
                default_case = DefaultStmt(body)
        
        self.consume(TokenType.RBRACE)
        return SwitchStmt(expression, cases, default_case)
    
    def parse_return_stmt(self) -> ReturnStmt:
        """Parses a return statement"""
        self.consume(TokenType.RETURN)
        
        value = None
        if not self.match(TokenType.RBRACE, TokenType.SEMICOLON) and self.current_token:
            value = self.parse_expression()
        
        return ReturnStmt(value)
    
    def parse_go_stmt(self) -> GoStmt:
        """Parses a go statement"""
        self.consume(TokenType.GO)
        call = self.parse_expression()
        
        if not isinstance(call, CallExpr):
            raise ParseError("Go statement must be followed by a function call")
        
        return GoStmt(call)
    
    def parse_defer_stmt(self) -> DeferStmt:
        """Parses a defer statement"""
        self.consume(TokenType.DEFER)
        call = self.parse_expression()
        
        if not isinstance(call, CallExpr):
            raise ParseError("Defer statement must be followed by a function call")
        
        return DeferStmt(call)
    
    def parse_try_stmt(self) -> TryStmt:
        """Parses a try statement (extension)"""
        self.consume(TokenType.TRY)
        body = self.parse_block_stmt()
        
        catch_blocks = []
        while self.match(TokenType.CATCH):
            catch_blocks.append(self.parse_catch_stmt())
        
        finally_block = None
        if self.match(TokenType.FINALLY):
            finally_block = self.parse_finally_stmt()
        
        return TryStmt(body, catch_blocks, finally_block)
    
    def parse_catch_stmt(self) -> CatchStmt:
        """Parses a catch statement (extension)"""
        self.consume(TokenType.CATCH)
        
        exception_type = None
        exception_var = None
        
        if self.match(TokenType.LPAREN):
            self.advance()
            
            if self.match(TokenType.IDENTIFIER):
                exception_var = self.current_token.value
                self.advance()
                
                if self.match(TokenType.IDENTIFIER):
                    exception_type = exception_var
                    exception_var = self.current_token.value
                    self.advance()
            
            self.consume(TokenType.RPAREN)
        
        body = self.parse_block_stmt()
        return CatchStmt(exception_type, exception_var, body)
    
    def parse_finally_stmt(self) -> FinallyStmt:
        """Parses a finally statement (extension)"""
        self.consume(TokenType.FINALLY)
        body = self.parse_block_stmt()
        return FinallyStmt(body)
    
    def parse_throw_stmt(self) -> ThrowStmt:
        """Parses a throw statement (extension)"""
        self.consume(TokenType.THROW)
        expression = self.parse_expression()
        return ThrowStmt(expression)
    
    def parse_expression(self) -> Expression:
        """Parses an expression (lowest precedence)"""
        return self.parse_logical_or()
    
    def parse_logical_or(self) -> Expression:
        """Parses logical OR"""
        expr = self.parse_logical_and()
        
        while self.match(TokenType.OR):
            op = self.current_token.value
            self.advance()
            right = self.parse_logical_and()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_logical_and(self) -> Expression:
        """Parses logical AND"""
        expr = self.parse_equality()
        
        while self.match(TokenType.AND):
            op = self.current_token.value
            self.advance()
            right = self.parse_equality()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_equality(self) -> Expression:
        """Parses equality"""
        expr = self.parse_comparison()
        
        while self.match(TokenType.EQ, TokenType.NE):
            op = self.current_token.value
            self.advance()
            right = self.parse_comparison()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_comparison(self) -> Expression:
        """Parses comparison"""
        expr = self.parse_addition()
        
        while self.match(TokenType.LT, TokenType.LE, TokenType.GT, TokenType.GE):
            op = self.current_token.value
            self.advance()
            right = self.parse_addition()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_addition(self) -> Expression:
        """Parses addition/subtraction"""
        expr = self.parse_multiplication()
        
        while self.match(TokenType.PLUS, TokenType.MINUS):
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplication()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_multiplication(self) -> Expression:
        """Parses multiplication/division/modulo"""
        expr = self.parse_unary()
        
        while self.match(TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op = self.current_token.value
            self.advance()
            right = self.parse_unary()
            expr = BinaryExpr(expr, op, right)
        
        return expr
    
    def parse_unary(self) -> Expression:
        """Parses unary expression"""
        if self.match(TokenType.NOT, TokenType.MINUS, TokenType.PLUS):
            op = self.current_token.value
            self.advance()
            expr = self.parse_unary()
            return UnaryExpr(op, expr)
        
        return self.parse_postfix()
    
    def parse_postfix(self) -> Expression:
        """Parses postfix expression (calls, indexes, selectors)"""
        expr = self.parse_primary()
        
        while True:
            if self.match(TokenType.LPAREN):
                # Function call
                self.advance()
                args = []
                
                while not self.match(TokenType.RPAREN) and self.current_token:
                    args.append(self.parse_expression())
                    
                    if self.match(TokenType.COMMA):
                        self.advance()
                    else:
                        break
                
                self.consume(TokenType.RPAREN)
                expr = CallExpr(expr, args)
            
            elif self.match(TokenType.LBRACKET):
                # Index access
                self.advance()
                index = self.parse_expression()
                self.consume(TokenType.RBRACKET)
                expr = IndexExpr(expr, index)
            
            elif self.match(TokenType.DOT):
                # Selector
                self.advance()
                field = self.consume(TokenType.IDENTIFIER, "Expected field name").value
                expr = SelectorExpr(expr, field)
            
            else:
                break
        
        return expr
    
    def parse_primary(self) -> Expression:
        """Parse primary expression"""
        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            return Identifier(name)
        
        elif self.match(TokenType.NUMBER):
            value = self.current_token.value
            self.advance()
            
            if '.' in value:
                return Literal(float(value), 'float')
            else:
                return Literal(int(value), 'int')
        
        elif self.match(TokenType.STRING):
            value = self.current_token.value
            self.advance()
            return Literal(value, 'string')
        
        elif self.match(TokenType.BOOLEAN):
            value = self.current_token.value == 'true'
            self.advance()
            return Literal(value, 'bool')
        
        elif self.match(TokenType.NEW):
            return self.parse_new_expr()
        
        elif self.match(TokenType.THIS):
            self.advance()
            return ThisExpr()
        
        elif self.match(TokenType.SUPER):
            self.advance()
            return SuperExpr()
        
        elif self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN)
            return expr
        
        else:
            raise ParseError(f"Unrecognized expression: {self.current_token.value if self.current_token else 'EOF'}")
    
    def parse_new_expr(self) -> NewExpr:
        """Parse new expression (extension)"""
        self.consume(TokenType.NEW)
        class_name = self.consume(TokenType.IDENTIFIER, "Expected class name").value
        
        self.consume(TokenType.LPAREN)
        args = []
        
        while not self.match(TokenType.RPAREN) and self.current_token:
            args.append(self.parse_expression())
            
            if self.match(TokenType.COMMA):
                self.advance()
            else:
                break
        
        self.consume(TokenType.RPAREN)
        return NewExpr(class_name, args)
