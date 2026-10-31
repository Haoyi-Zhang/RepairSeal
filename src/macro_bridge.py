"""Fail-closed lowering of a selected pure unsigned macro expression.

The caller supplies the authoritative definition, unsigned-32 argument types,
and side-effect-free argument premise. This is not a preprocessor, caller-type
inference, or a general C/C++ frontend. Inserted source-if traces belong to the
normalization, not to execution of the macro's containing application.
"""
from dataclasses import dataclass
import re


class Unsupported(ValueError):pass


@dataclass(frozen=True)
class Term:
    op:str
    sort:str
    args:tuple=()
    value:object=None


PREC={'==':1,'!=':1,'<':2,'<=':2,'>':2,'>=':2,'+':3,'-':3,'*':4,'/':4,'%':4}
REL={'==','!=','<','<=','>','>='}
TOKEN=re.compile(r'\s*(?:([A-Za-z_][A-Za-z_0-9]*)|([0-9]+[uU]?)|(!=|==|<=|>=|[()+*/%<>-]))')
NAME=re.compile(r'[A-Za-z][A-Za-z_0-9]*')


class Parser:
    def __init__(self,body,parameters):
        self.tokens=[];position=0
        while position<len(body):
            if not body[position:].strip():break
            match=TOKEN.match(body,position)
            if match is None:raise Unsupported('macro token')
            self.tokens.append(next(value for value in match.groups() if value is not None))
            position=match.end()
        if len(self.tokens)>512:raise Unsupported('macro token bound')
        self.position=0;self.parameters=parameters

    def atom(self,depth):
        if depth>32 or self.position>=len(self.tokens):raise Unsupported('macro expression depth or operand')
        token=self.tokens[self.position];self.position+=1
        if token=='(':
            result=self.expression(1,depth+1)
            if self.position>=len(self.tokens) or self.tokens[self.position]!=')':raise Unsupported('macro closing parenthesis')
            self.position+=1;return result
        if token in self.parameters:return Term('input','word',value=self.parameters[token])
        if re.fullmatch(r'[0-9]+[uU]?',token):
            digits=token.rstrip('uU');unsigned=digits!=token
            if len(digits)>10 or len(digits)>1 and digits.startswith('0'):raise Unsupported('nondecimal or long macro literal')
            value=int(digits)
            if value>(2**32-1 if unsigned else 2**31-1):raise Unsupported('macro literal type')
            return Term('literal','word' if unsigned else 'int',value=value)
        raise Unsupported('unknown macro operand')

    def expression(self,minimum=1,depth=0):
        left=self.atom(depth)
        while self.position<len(self.tokens):
            op=self.tokens[self.position];precedence=PREC.get(op,0)
            if precedence<minimum:break
            self.position+=1;right=self.expression(precedence+1,depth+1)
            if op in REL:sort='bool'
            else:
                # Without a word operand, C's signed intermediate semantics
                # needs an additional range proof. Do not silently replace it.
                if 'word' not in (left.sort,right.sort):raise Unsupported('signed or promoted-int arithmetic')
                sort='word'
            left=Term(op,sort,(left,right))
        return left

    def parse(self):
        term=self.expression()
        if self.position!=len(self.tokens):raise Unsupported('macro trailing tokens')
        return term


def translate(definition,input_order):
    """Return a scalar function plus its exact selected expression contract."""
    if (type(definition) is not str or len(definition)>4096 or '\n' in definition
            or any(ord(c)>127 for c in definition)
            or any(x in definition for x in ('\\','??','/*','//'))):
        raise Unsupported('macro definition surface')
    match=re.fullmatch(r'\s*#\s*define\s+([A-Za-z][A-Za-z_0-9]*)\(([^()]*)\)\s+(.+?)\s*',definition)
    if not match:raise Unsupported('function-like macro definition')
    parameters=[name.strip() for name in match[2].split(',')]
    if type(input_order) not in (list,tuple) or any(type(n) is not str for n in input_order):
        raise Unsupported('macro input schema')
    if (not 1<=len(parameters)<=8
            or len(parameters)!=len(input_order) or len(set(parameters))!=len(parameters)
            or len(set(input_order))!=len(input_order)
            or any(type(n) is not str or not NAME.fullmatch(n) for n in (*parameters,*input_order))):
        raise Unsupported('macro parameter contract')
    reserved=set('auto break case char const continue default do double else enum extern float for goto if inline int long register restrict return short signed sizeof static struct switch typedef union unsigned void volatile while'.split())
    if any(n in reserved or n.startswith('rs_generated') for n in input_order):raise Unsupported('macro input name')
    term=Parser(match[3],dict(zip(parameters,input_order))).parse()
    pending=[(term,1)]
    while pending:
        node,depth=pending.pop()
        if depth>32:raise Unsupported('macro term depth')
        pending.extend((child,depth+1) for child in node.args)
    declarations=[];statements=[]
    def word(node):
        if node.sort=='bool':
            condition=boolean(node)
            name='rs_generated'+str(len(declarations))
            if len(declarations)>=64:raise Unsupported('macro local bound')
            declarations.append('unsigned '+name+' = 0u;')
            statements.append('if ('+condition+') { '+name+' = 1u; } else { '+name+' = 0u; }')
            return name
        if node.op=='input':return node.value
        if node.op=='literal':return str(node.value)+'u'
        return '('+word(node.args[0])+' '+node.op+' '+word(node.args[1])+')'
    def boolean(node):
        return '('+word(node.args[0])+' '+node.op+' '+word(node.args[1])+')'
    expression=word(term)
    source='unsigned f('+', '.join('unsigned '+n for n in input_order)+') { '
    source+=' '.join((*declarations,*statements,'return '+expression+';'))+' }'
    if len(source)>16384:raise Unsupported('macro lowered source bound')
    return dict(macro=match[1],parameters=parameters,input_order=list(input_order),
                expression=match[3],source=source,
                premises='Pure unsigned-32 arguments supplied by the receiver; selected definition and caller applicability are not inferred',
                trace='Source-if events refer only to this deterministic normalization')
