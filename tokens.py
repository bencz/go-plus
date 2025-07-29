"""
Token definitions for Go-Extended
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, Optional

class TokenType(Enum):
    # Literal Types
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    
    # Keywords Go standard
    PACKAGE = auto()
    IMPORT = auto()
    FUNC = auto()
    VAR = auto()
    CONST = auto()
    TYPE = auto()
    STRUCT = auto()
    INTERFACE = auto()
    IF = auto()
    ELSE = auto()
    FOR = auto()
    RANGE = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    GO = auto()
    DEFER = auto()
    SELECT = auto()
    CHAN = auto()
    MAP = auto()
    
    # Extensions - Classes
    CLASS = auto()
    NEW = auto()
    THIS = auto()
    SUPER = auto()
    EXTENDS = auto()
    
    # Extensions - Exceptions
    TRY = auto()
    CATCH = auto()
    FINALLY = auto()
    THROW = auto()
    EXCEPTION = auto()
    
    # Operators
    ASSIGN = auto()          # =
    SHORT_ASSIGN = auto()    # :=
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    MULT_ASSIGN = auto()     # *=
    DIV_ASSIGN = auto()      # /=
    MOD_ASSIGN = auto()      # %=
    
    PLUS = auto()            # +
    MINUS = auto()           # -
    MULTIPLY = auto()        # *
    DIVIDE = auto()          # /
    MODULO = auto()          # %
    
    EQ = auto()              # ==
    NE = auto()              # !=
    LT = auto()              # <
    LE = auto()              # <=
    GT = auto()              # >
    GE = auto()              # >=
    
    AND = auto()             # &&
    OR = auto()              # ||
    NOT = auto()             # !
    
    BITWISE_AND = auto()     # &
    BITWISE_OR = auto()      # |
    BITWISE_XOR = auto()     # ^
    BITWISE_NOT = auto()     # ~
    LEFT_SHIFT = auto()      # <<
    RIGHT_SHIFT = auto()     # >>
    
    INCREMENT = auto()       # ++
    DECREMENT = auto()       # --
    
    # Delimiters
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    
    SEMICOLON = auto()       # ;
    COMMA = auto()           # ,
    DOT = auto()             # .
    COLON = auto()           # :
    DOUBLE_COLON = auto()    # ::
    ARROW = auto()           # ->
    
    # Specials
    NEWLINE = auto()
    EOF = auto()
    COMMENT = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __str__(self):
        return f"Token({self.type.name}, '{self.value}', {self.line}:{self.column})"
    
    def __repr__(self):
        return self.__str__()

# Keyword mapping
KEYWORDS = {
    # Standard Go
    'package': TokenType.PACKAGE,
    'import': TokenType.IMPORT,
    'func': TokenType.FUNC,
    'var': TokenType.VAR,
    'const': TokenType.CONST,
    'type': TokenType.TYPE,
    'struct': TokenType.STRUCT,
    'interface': TokenType.INTERFACE,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'for': TokenType.FOR,
    'range': TokenType.RANGE,
    'switch': TokenType.SWITCH,
    'case': TokenType.CASE,
    'default': TokenType.DEFAULT,
    'break': TokenType.BREAK,
    'continue': TokenType.CONTINUE,
    'return': TokenType.RETURN,
    'go': TokenType.GO,
    'defer': TokenType.DEFER,
    'select': TokenType.SELECT,
    'chan': TokenType.CHAN,
    'map': TokenType.MAP,
    'true': TokenType.BOOLEAN,
    'false': TokenType.BOOLEAN,
    
    # Extensions - Classes
    'class': TokenType.CLASS,
    'new': TokenType.NEW,
    'this': TokenType.THIS,
    'super': TokenType.SUPER,
    'extends': TokenType.EXTENDS,
    
    # Extensions - Exceptions
    'try': TokenType.TRY,
    'catch': TokenType.CATCH,
    'finally': TokenType.FINALLY,
    'throw': TokenType.THROW,
    'exception': TokenType.EXCEPTION,
}

# Two-character operators
TWO_CHAR_OPERATORS = {
    '==': TokenType.EQ,
    '!=': TokenType.NE,
    '<=': TokenType.LE,
    '>=': TokenType.GE,
    '&&': TokenType.AND,
    '||': TokenType.OR,
    '<<': TokenType.LEFT_SHIFT,
    '>>': TokenType.RIGHT_SHIFT,
    '++': TokenType.INCREMENT,
    '--': TokenType.DECREMENT,
    ':=': TokenType.SHORT_ASSIGN,
    '+=': TokenType.PLUS_ASSIGN,
    '-=': TokenType.MINUS_ASSIGN,
    '*=': TokenType.MULT_ASSIGN,
    '/=': TokenType.DIV_ASSIGN,
    '%=': TokenType.MOD_ASSIGN,
    '::': TokenType.DOUBLE_COLON,
    '->': TokenType.ARROW,
}

# One-character operators
ONE_CHAR_OPERATORS = {
    '=': TokenType.ASSIGN,
    '+': TokenType.PLUS,
    '-': TokenType.MINUS,
    '*': TokenType.MULTIPLY,
    '/': TokenType.DIVIDE,
    '%': TokenType.MODULO,
    '<': TokenType.LT,
    '>': TokenType.GT,
    '!': TokenType.NOT,
    '&': TokenType.BITWISE_AND,
    '|': TokenType.BITWISE_OR,
    '^': TokenType.BITWISE_XOR,
    '~': TokenType.BITWISE_NOT,
    '(': TokenType.LPAREN,
    ')': TokenType.RPAREN,
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ';': TokenType.SEMICOLON,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
    ':': TokenType.COLON,
}
