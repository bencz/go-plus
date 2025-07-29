"""
AST (Abstract Syntax Tree) nodes for Go-Extended
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from dataclasses import dataclass

class ASTNode(ABC):
    """Base class for all AST nodes"""
    pass

# ============================================================================
# Program and Declarations
# ============================================================================

@dataclass
class Program(ASTNode):
    """Main program"""
    package: str
    imports: List['ImportDecl']
    declarations: List['Declaration']

@dataclass
class ImportDecl(ASTNode):
    """Import declaration"""
    path: str
    alias: Optional[str] = None

# ============================================================================
# Declarations
# ============================================================================

class Declaration(ASTNode):
    """Base class for declarations"""
    pass

@dataclass
class FuncDecl(Declaration):
    """Function declaration"""
    name: str
    params: List['Parameter']
    return_type: Optional[str]
    body: 'BlockStmt'

@dataclass
class VarDecl(Declaration):
    """Variable declaration"""
    name: str
    type: Optional[str]
    value: Optional['Expression']

@dataclass
class ConstDecl(Declaration):
    """Constant declaration"""
    name: str
    type: Optional[str]
    value: 'Expression'

@dataclass
class TypeDecl(Declaration):
    """Type declaration"""
    name: str
    type: str

@dataclass
class StructDecl(Declaration):
    """Struct declaration"""
    name: str
    fields: List['StructField']

@dataclass
class InterfaceDecl(Declaration):
    """Interface declaration"""
    name: str
    methods: List['MethodSignature']

# ============================================================================
# Extensions - Classes
# ============================================================================

@dataclass
class ClassDecl(Declaration):
    """Class declaration (extension)"""
    name: str
    extends: Optional[str]
    fields: List['ClassField']
    methods: List['MethodDecl']
    constructor: Optional['ConstructorDecl']

@dataclass
class ClassField(ASTNode):
    """Class field"""
    name: str
    type: str
    value: Optional['Expression'] = None

@dataclass
class MethodDecl(ASTNode):
    """Method declaration"""
    name: str
    params: List['Parameter']
    return_type: Optional[str]
    body: 'BlockStmt'

@dataclass
class ConstructorDecl(ASTNode):
    """Constructor declaration"""
    params: List['Parameter']
    body: 'BlockStmt'

# ============================================================================
# Parameters and Fields
# ============================================================================

@dataclass
class Parameter(ASTNode):
    """Function parameter"""
    name: str
    type: str

@dataclass
class StructField(ASTNode):
    """Struct field"""
    name: str
    type: str

@dataclass
class MethodSignature(ASTNode):
    """Method signature (interface)"""
    name: str
    params: List['Parameter']
    return_type: Optional[str]

# ============================================================================
# Statements
# ============================================================================

class Statement(ASTNode):
    """Base class for statements"""
    pass

@dataclass
class BlockStmt(Statement):
    """Block of statements"""
    statements: List[Statement]

@dataclass
class ExpressionStmt(Statement):
    """Expression statement"""
    expression: 'Expression'

@dataclass
class VarStmt(Statement):
    """Variable declaration statement"""
    name: str
    type: Optional[str]
    value: Optional['Expression']

@dataclass
class AssignStmt(Statement):
    """Assignment statement"""
    target: 'Expression'
    value: 'Expression'
    operator: str = '='

@dataclass
class IfStmt(Statement):
    """If statement"""
    condition: 'Expression'
    then_stmt: Statement
    else_stmt: Optional[Statement] = None

@dataclass
class ForStmt(Statement):
    """For statement"""
    init: Optional[Statement]
    condition: Optional['Expression']
    update: Optional[Statement]
    body: Statement

@dataclass
class RangeStmt(Statement):
    """For range statement"""
    key: Optional[str]
    value: Optional[str]
    iterable: 'Expression'
    body: Statement

@dataclass
class SwitchStmt(Statement):
    """Switch statement"""
    expression: Optional['Expression']
    cases: List['CaseStmt']
    default_case: Optional['DefaultStmt']

@dataclass
class CaseStmt(Statement):
    """Switch case"""
    values: List['Expression']
    body: List[Statement]

@dataclass
class DefaultStmt(Statement):
    """Switch default"""
    body: List[Statement]

@dataclass
class ReturnStmt(Statement):
    """Return statement"""
    value: Optional['Expression'] = None

@dataclass
class BreakStmt(Statement):
    """Break statement"""
    pass

@dataclass
class ContinueStmt(Statement):
    """Continue statement"""
    pass

@dataclass
class GoStmt(Statement):
    """Go statement (goroutine)"""
    call: 'CallExpr'

@dataclass
class DeferStmt(Statement):
    """Defer statement"""
    call: 'CallExpr'

# ============================================================================
# Extensions - Exception Handling
# ============================================================================

@dataclass
class TryStmt(Statement):
    """Try statement (extension)"""
    body: BlockStmt
    catch_blocks: List['CatchStmt']
    finally_block: Optional['FinallyStmt'] = None

@dataclass
class CatchStmt(Statement):
    """Catch statement (extension)"""
    exception_type: Optional[str]
    exception_var: Optional[str]
    body: BlockStmt

@dataclass
class FinallyStmt(Statement):
    """Finally statement (extension)"""
    body: BlockStmt

@dataclass
class ThrowStmt(Statement):
    """Throw statement (extension)"""
    expression: 'Expression'

# ============================================================================
# Expressions
# ============================================================================

class Expression(ASTNode):
    """Base class for expressions"""
    pass

@dataclass
class BinaryExpr(Expression):
    """Binary expression"""
    left: Expression
    operator: str
    right: Expression

@dataclass
class UnaryExpr(Expression):
    """Unary expression"""
    operator: str
    operand: Expression

@dataclass
class CallExpr(Expression):
    """Function call"""
    function: Expression
    args: List[Expression]

@dataclass
class IndexExpr(Expression):
    """Index access (array/slice/map)"""
    object: Expression
    index: Expression

@dataclass
class SelectorExpr(Expression):
    """Selector (obj.field)"""
    object: Expression
    field: str

@dataclass
class Identifier(Expression):
    """Identifier"""
    name: str

@dataclass
class Literal(Expression):
    """Literal (number, string, boolean)"""
    value: Any
    type: str  # 'int', 'float', 'string', 'bool'

@dataclass
class ArrayLiteral(Expression):
    """Array literal"""
    elements: List[Expression]
    type: Optional[str] = None

@dataclass
class MapLiteral(Expression):
    """Map literal"""
    pairs: List[tuple[Expression, Expression]]
    key_type: Optional[str] = None
    value_type: Optional[str] = None

@dataclass
class StructLiteral(Expression):
    """Struct literal"""
    type: str
    fields: List[tuple[str, Expression]]

# ============================================================================
# Extensions - Class Expressions
# ============================================================================

@dataclass
class NewExpr(Expression):
    """New expression (extension)"""
    class_name: str
    args: List[Expression]

@dataclass
class ThisExpr(Expression):
    """This expression (extension)"""
    pass

@dataclass
class SuperExpr(Expression):
    """Super expression (extension)"""
    pass
