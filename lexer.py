"""
Lexer for Go-Extended
Converts source code into tokens
"""

import re
from typing import List, Optional
from tokens import Token, TokenType, KEYWORDS, TWO_CHAR_OPERATORS, ONE_CHAR_OPERATORS

class LexerError(Exception):
    """Lexer error"""
    pass

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def current_char(self) -> Optional[str]:
        """Returns the current character or None if end of file"""
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset: int = 1) -> Optional[str]:
        """Peeks at the next character without advancing"""
        peek_pos = self.pos + offset
        if peek_pos >= len(self.source):
            return None
        return self.source[peek_pos]
    
    def advance(self) -> None:
        """Advances to the next character"""
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self) -> None:
        """Skips whitespace (except newlines)"""
        while self.current_char() and self.current_char() in ' \t\r':
            self.advance()
    
    def read_string(self, quote_char: str) -> str:
        """Reads a string literal"""
        value = ''
        self.advance()  # Skip the opening quote
        
        while self.current_char() and self.current_char() != quote_char:
            if self.current_char() == '\\':
                self.advance()
                if self.current_char():
                    # Basic escape sequences
                    escape_chars = {
                        'n': '\n',
                        't': '\t',
                        'r': '\r',
                        '\\': '\\',
                        '"': '"',
                        "'": "'",
                    }
                    value += escape_chars.get(self.current_char(), self.current_char())
                    self.advance()
            else:
                value += self.current_char()
                self.advance()
        
        if not self.current_char():
            raise LexerError(f"Unclosed string at line {self.line}")
        
        self.advance()  # Skip the closing quote
        return value
    
    def read_number(self) -> str:
        """Reads a number (int or float)"""
        value = ''
        has_dot = False
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            if self.current_char() == '.':
                if has_dot:
                    break  # Second dot, stop reading
                has_dot = True
            value += self.current_char()
            self.advance()
        
        return value
    
    def read_identifier(self) -> str:
        """Reads an identifier or keyword"""
        value = ''
        
        while (self.current_char() and 
               (self.current_char().isalnum() or self.current_char() == '_')):
            value += self.current_char()
            self.advance()
        
        return value
    
    def read_comment(self) -> str:
        """Reads a comment"""
        value = ''
        
        if self.current_char() == '/' and self.peek_char() == '/':
            # Line comment
            while self.current_char() and self.current_char() != '\n':
                value += self.current_char()
                self.advance()
        elif self.current_char() == '/' and self.peek_char() == '*':
            # Block comment
            self.advance()  # /
            self.advance()  # *
            value = '/*'
            
            while self.current_char():
                if self.current_char() == '*' and self.peek_char() == '/':
                    value += '*/'
                    self.advance()  # *
                    self.advance()  # /
                    break
                value += self.current_char()
                self.advance()
            else:
                raise LexerError(f"Unclosed block comment at line {self.line}")
        
        return value
    
    def tokenize(self) -> List[Token]:
        """Tokenizes the source code"""
        self.tokens = []
        
        while self.current_char():
            start_line = self.line
            start_column = self.column
            
            # Skip whitespace
            if self.current_char() in ' \t\r':
                self.skip_whitespace()
                continue
            
            # Newline
            if self.current_char() == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\\n', start_line, start_column))
                self.advance()
                continue
            
            # Comments
            if self.current_char() == '/' and self.peek_char() in ['/', '*']:
                comment = self.read_comment()
                self.tokens.append(Token(TokenType.COMMENT, comment, start_line, start_column))
                continue
            
            # Strings
            if self.current_char() in ['"', "'"]:
                quote_char = self.current_char()
                string_value = self.read_string(quote_char)
                self.tokens.append(Token(TokenType.STRING, string_value, start_line, start_column))
                continue
            
            # Numbers
            if self.current_char().isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, start_line, start_column))
                continue
            
            # Identifiers and keywords
            if self.current_char().isalpha() or self.current_char() == '_':
                identifier = self.read_identifier()
                token_type = KEYWORDS.get(identifier, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, identifier, start_line, start_column))
                continue
            
            # Two-character operators
            two_char = self.current_char() + (self.peek_char() or '')
            if two_char in TWO_CHAR_OPERATORS:
                self.tokens.append(Token(TWO_CHAR_OPERATORS[two_char], two_char, start_line, start_column))
                self.advance()
                self.advance()
                continue
            
            # One-character operators
            if self.current_char() in ONE_CHAR_OPERATORS:
                char = self.current_char()
                self.tokens.append(Token(ONE_CHAR_OPERATORS[char], char, start_line, start_column))
                self.advance()
                continue
            
            # Unrecognized character
            raise LexerError(f"Unrecognized character '{self.current_char()}' at line {self.line}, column {self.column}")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
