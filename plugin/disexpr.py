import decimal
import math
import contextlib

from parsy import string, regex, seq, generate, eof

WS = regex(r'\s*')
PLUS = string('+') << WS
MINUS = string('-') << WS
STAR = string('*') << WS
SLASH = string('/') << WS
LBRACKET = string('(') << WS
RBRACKET = string(')') << WS
LSQUARE = string('[') << WS
RSQUARE = string(']') << WS
COMMA = string(',') << WS
IDENTIFIER = regex(r'[A-Za-z_][A-Za-z0-9_]*') << WS

Int = regex(r'-?[0-9]+').map(int) << WS
Decimal = regex(r'-?[0-9]+\.[0-9]*').map(decimal.Decimal) << WS
String = string('"') >> regex(r'[^"]*') << string('"') << WS
Identifier = IDENTIFIER.map(lambda ident: ('ident', (ident,)))
NumericRelativeSingleRef = string('@') >> Int.map(lambda single: ('rel', [single]))
DirectionalRelativeSingleRef =  \
    string("before").map(lambda single: ('rel', [-1])) \
    | string("after").map(lambda single: ('rel', [1])) \
    | string("this").map(lambda single: ('rel', [0]))
RelativeSingleRef = NumericRelativeSingleRef | DirectionalRelativeSingleRef
AbsoluteSingleRef = Int.map(lambda single: ('abs', [single]))
ColOrRowRef = seq(RelativeSingleRef | AbsoluteSingleRef, seq(string('..') >> (RelativeSingleRef | AbsoluteSingleRef)).optional()) \
    .combine(lambda r1, r2: ('range', [r1] + r2) if r2 else r1)
ExplicitRef = seq(ColOrRowRef, WS >> ColOrRowRef).combine(lambda row, col: ('cell', [row, col]))
DirRef = (string('l') >> WS >> Int).map(lambda single: ('cell', [('rel', [0]), ('rel', [-single])])) \
        | (string('r') >> WS >> Int).map(lambda single: ('cell', [('rel', [0]), ('rel', [single])])) \
        | (string('u') >> WS >> Int).map(lambda single: ('cell', [('rel', [-single]), ('rel', [0])])) \
        | (string('d') >> WS >> Int).map(lambda single: ('cell', [('rel', [single]), ('rel', [0])]))
CellRef = (LSQUARE >> (ExplicitRef | DirRef) << RSQUARE)

def combine_expr(*args):
    return args
    if rhs is None:
        return lhs
    else:
        oper, subexpr = rhs
        return (oper, lhs, subexpr)

# Pretty much all the @generate-based combinators are to break circular dependencies
# -- which is why Python is less well-suited to this type of parsing than Haskell.
@generate
def ExprBracketed():
    yield LBRACKET
    expr = yield Expr
    yield RBRACKET
    return expr

@generate
def ExprList():  # using generate to break circular dependency between Expr and ExprList
    exprs = []
    while True:
        expr = yield Expr.optional()
        if not expr:
            break
        exprs.append(expr)

        comma = yield COMMA.optional()
        if not comma:
            break

    return exprs

def _expr_generator(sub_expr, oper):
    @generate
    def parse_expr():
        result = yield sub_expr << WS
        oper_val = yield oper.optional()
        while oper_val:
            rhs = yield sub_expr << WS
            result = (oper_val, [result, rhs])
            oper_val = yield oper.optional()

        return result
    return parse_expr

ExprBasic = Decimal | Int | String | CellRef | Identifier
ExprFunction = seq(IDENTIFIER,  LBRACKET >> ExprList << RBRACKET).combine(lambda name, args: (name, args))
ExprOptBracket = ExprBracketed | ExprFunction | ExprBasic
ExprMulDiv = _expr_generator(ExprOptBracket, STAR | SLASH)
Expr = _expr_generator(ExprMulDiv, PLUS | MINUS)

class EmptyCell:
    def eh(self, other):
        return other

    __add__ = __radd__ = eh

    def dis_eval(self, _context):
        return self

TheEmptyCell = EmptyCell()

Cell = (WS >> Expr.optional() << eof).map(lambda expr: expr if expr is not None else TheEmptyCell)

def dis_eval(expr, context=None):
    if context is None:
        context = DEFAULT_CONTEXT.copy()

    if isinstance(expr, (int, decimal.Decimal, str)):
        return expr
    elif isinstance(expr, tuple):
        oper = context[expr[0]]
        return oper(context, *expr[1])
    elif isinstance(expr, list):
        return [dis_eval(elem, context) for elem in expr]
    elif hasattr(expr, 'dis_eval'):
        return expr.dis_eval(context)
    else:
        return "A suffusion of yellow (%s)" % (type(expr),)

class Scopes:
    def __init__(self, *scopes):
        self.scopes = list(scopes)

    def push(self, updates):
        self.scopes.append(updates)

    def pop(self):
        self.scopes.pop()

    def __getitem__(self, key):
        for scope in reversed(self.scopes):
            try:
                return scope[key]
            except KeyError:
                pass

        raise KeyError(key)

    def __contains__(self, key):
        for scope in reversed(self.scopes):
            if key in scope:
                return True

        return False

    def __setitem__(self, key, value):
        self.scopes[-1][key] = value

    def __delitem__(self, key):
        del self.scopes[-1][key]

    def copy(self):
        return self.__class__(*[scope.copy() for scope in self.scopes])

    @contextlib.contextmanager
    def newscope(self, **scope_vals):
        self.push(scope_vals)
        yield
        self.pop()

    def dumps(self):
        return repr(self.scopes)

def flatlist(l):
    for elem in l:
        if isinstance(elem, list):
            for subelem in flatlist(elem):
                yield subelem
        else:
            yield elem

def unlist(elem):
    if isinstance(elem, list):
        assert len(elem) == 1
        return elem[0]
    return elem

DEFAULT_CONTEXT = Scopes({
    'pi': math.pi,
    'sin': lambda context, val: math.sin(dis_eval(val, context)),
    'cos': lambda context, val: math.cos(dis_eval(val, context)),
    'tan': lambda context, val: math.tan(dis_eval(val, context)),
    'sqrt': lambda context, val: math.sqrt(dis_eval(val, context)),
    '+': lambda context, lhs, rhs: unlist(dis_eval(lhs, context)) + unlist(dis_eval(rhs, context)),
    '-': lambda context, lhs, rhs: unlist(dis_eval(lhs, context)) - unlist(dis_eval(rhs, context)),
    '*': lambda context, lhs, rhs: unlist(dis_eval(lhs, context)) * unlist(dis_eval(rhs, context)),
    '/': lambda context, lhs, rhs: unlist(dis_eval(lhs, context)) / unlist(dis_eval(rhs, context)),
    'ident': lambda context, ident: context[ident],
})

def test(expr_string):
    expr = Cell.parse(expr_string)
    print(expr)

    # Create a context supporting the most basic table action for testing.
    context = DEFAULT_CONTEXT.copy()
    context.push({
        "cell": lambda context, row, col: 42,
    })

    print(dis_eval(expr, context))

if __name__ == '__main__':
    import sys
    test(sys.argv[1])
