
"""
Mini Compiler for Basic Math in Python
--------------------------------------
Features:
- Lexer (tokenizer)
- Parser (recursive descent) building an AST
- Code generator to a tiny stack-based bytecode
- Virtual Machine to execute the bytecode
- REPL supporting expressions, assignments, and print statements

Supported:
- Numbers (ints/floats), identifiers (variables)
- Operators: +, -, *, /, ^ (power), unary minus
- Parentheses for grouping
- Assignment:   x = 2 + 3*4
- Print:        print x + 1   or   print( x + 1 )

Run:
    python3 mini_compiler.py
Then type expressions. Use Ctrl+C or `exit` to quit.
"""

import math
import sys
import re
from dataclasses import dataclass
from typing import List, Union, Optional, Tuple, Dict, Any



TokenType = str

@dataclass
class Token:
    type: TokenType
    value: Any
    pos: int

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.length = len(text)

    def peek(self) -> str:
        return self.text[self.i] if self.i < self.length else ""

    def advance(self) -> str:
        ch = self.peek()
        self.i += 1
        return ch

    def skip_ws(self):
        while self.peek() and self.peek().isspace():
            self.advance()

    def number(self, start_pos: int) -> Token:
        s = self.peek()
        num = ""
        dot_seen = False
        while self.peek() and (self.peek().isdigit() or self.peek() == "."):
            if self.peek() == ".":
                if dot_seen:
                    break
                dot_seen = True
            num += self.advance()
        val = float(num) if "." in num else int(num)
        return Token("NUMBER", val, start_pos)

    def ident(self, start_pos: int) -> Token:
        ident = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            ident += self.advance()
        if ident == "print":
            return Token("PRINT", ident, start_pos)
        return Token("IDENT", ident, start_pos)

    def tokens(self) -> List[Token]:
        toks: List[Token] = []
        while self.i < self.length:
            self.skip_ws()
            start = self.i
            ch = self.peek()
            if not ch:
                break
            if ch.isdigit():
                toks.append(self.number(start))
                continue
            if ch.isalpha() or ch == "_":
                toks.append(self.ident(start))
                continue
            # single char tokens
            if ch == "+":
                toks.append(Token("PLUS", self.advance(), start)); continue
            if ch == "-":
                toks.append(Token("MINUS", self.advance(), start)); continue
            if ch == "*":
                toks.append(Token("MUL", self.advance(), start)); continue
            if ch == "/":
                toks.append(Token("DIV", self.advance(), start)); continue
            if ch == "^":
                toks.append(Token("POW", self.advance(), start)); continue
            if ch == "(":
                toks.append(Token("LPAREN", self.advance(), start)); continue
            if ch == ")":
                toks.append(Token("RPAREN", self.advance(), start)); continue
            if ch == "=":
                toks.append(Token("ASSIGN", self.advance(), start)); continue
            # Unknown character
            raise SyntaxError(f"Unexpected character '{ch}' at {start}")
        toks.append(Token("EOF", None, self.i))
        return toks



@dataclass
class Num:
    value: float

@dataclass
class Var:
    name: str

@dataclass
class BinOp:
    op: str
    left: Any
    right: Any

@dataclass
class UnaryOp:
    op: str
    expr: Any

@dataclass
class Assign:
    name: str
    expr: Any

@dataclass
class PrintStmt:
    expr: Any

Stmt = Union[Assign, PrintStmt, Any]  



class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def peek(self) -> Token:
        return self.tokens[self.i]

    def eat(self, kind: TokenType) -> Token:
        tok = self.peek()
        if tok.type != kind:
            raise SyntaxError(f"Expected {kind} but found {tok.type} at pos {tok.pos}")
        self.i += 1
        return tok

    def at(self, kind: TokenType) -> bool:
        return self.peek().type == kind



    def parse(self) -> Stmt:
        if self.at("PRINT"):
            self.eat("PRINT")
            # allow optional parens: print ( expr )
            if self.at("LPAREN"):
                self.eat("LPAREN")
                e = self.expr()
                self.eat("RPAREN")
            else:
                e = self.expr()
            return PrintStmt(e)
        # assignment or expression statement
        if self.at("IDENT"):
            # lookahead
            ident_tok = self.peek()
            if self.tokens[self.i + 1].type == "ASSIGN":
                self.eat("IDENT")
                self.eat("ASSIGN")
                e = self.expr()
                return Assign(ident_tok.value, e)
        return self.expr()

    def expr(self):
        node = self.term()
        while self.at("PLUS") or self.at("MINUS"):
            if self.at("PLUS"):
                self.eat("PLUS")
                node = BinOp("+", node, self.term())
            else:
                self.eat("MINUS")
                node = BinOp("-", node, self.term())
        return node

    def term(self):
        node = self.power()
        while self.at("MUL") or self.at("DIV"):
            if self.at("MUL"):
                self.eat("MUL")
                node = BinOp("*", node, self.power())
            else:
                self.eat("DIV")
                node = BinOp("/", node, self.power())
        return node

    def power(self):
        node = self.unary()
        if self.at("POW"):
            self.eat("POW")
            # right-associative
            node = BinOp("^", node, self.power())
        return node

    def unary(self):
        if self.at("PLUS"):
            self.eat("PLUS")
            return self.unary()
        if self.at("MINUS"):
            self.eat("MINUS")
            return UnaryOp("-", self.unary())
        return self.primary()

    def primary(self):
        tok = self.peek()
        if tok.type == "NUMBER":
            self.eat("NUMBER")
            return Num(tok.value)
        if tok.type == "IDENT":
            self.eat("IDENT")
            return Var(tok.value)
        if tok.type == "LPAREN":
            self.eat("LPAREN")
            e = self.expr()
            self.eat("RPAREN")
            return e
        raise SyntaxError(f"Unexpected token {tok.type} at pos {tok.pos}")



@dataclass
class Instr:
    op: str
    arg: Any = None

Bytecode = List[Instr]

class Codegen:
    def __init__(self):
        self.code: Bytecode = []

    def emit(self, op: str, arg: Any = None):
        self.code.append(Instr(op, arg))

    def gen(self, node: Stmt):
        t = type(node)
        if t is Num:
            self.emit("PUSH", node.value)
        elif t is Var:
            self.emit("LOAD", node.name)
        elif t is UnaryOp:
            self.gen(node.expr)
            if node.op == "-":
                self.emit("NEG")
            else:
                raise NotImplementedError(f"Unary {node.op}")
        elif t is BinOp:
            self.gen(node.left)
            self.gen(node.right)
            if node.op == "+":
                self.emit("ADD")
            elif node.op == "-":
                self.emit("SUB")
            elif node.op == "*":
                self.emit("MUL")
            elif node.op == "/":
                self.emit("DIV")
            elif node.op == "^":
                self.emit("POW")
            else:
                raise NotImplementedError(f"BinOp {node.op}")
        elif t is Assign:
            self.gen(node.expr)
            self.emit("STORE", node.name)
        elif t is PrintStmt:
            self.gen(node.expr)
            self.emit("PRINT")
        else:
           
            self.gen(node)
            self.emit("PRINT")

class VM:
    def __init__(self):
        self.stack: List[float] = []
        self.env: Dict[str, float] = {}

    def run(self, code: Bytecode):
        for ins in code:
            op, arg = ins.op, ins.arg
            if op == "PUSH":
                self.stack.append(arg)
            elif op == "LOAD":
                if arg not in self.env:
                    raise NameError(f"Undefined variable '{arg}'")
                self.stack.append(self.env[arg])
            elif op == "STORE":
                val = self.stack.pop()
                self.env[arg] = val
            elif op == "NEG":
                a = self.stack.pop()
                self.stack.append(-a)
            elif op == "ADD":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a + b)
            elif op == "SUB":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a - b)
            elif op == "MUL":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a * b)
            elif op == "DIV":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a / b)
            elif op == "POW":
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(a ** b)
            elif op == "PRINT":
                val = self.stack.pop()
                print(val)
            else:
                raise RuntimeError(f"Unknown instruction {op}")



BANNER = """Mini Math Compiler
Type expressions, assignments, or print statements.
Examples:
  x = 2 + 3*4
  print x + 1
  print( (1+2)^3 - 4/5 )
  -3 + 4 * 2
Type 'env' to see variables, 'exit' to quit.
"""

def compile_and_run(line: str, vm: VM):
    lexer = Lexer(line)
    tokens = lexer.tokens()
    parser = Parser(tokens)
    ast = parser.parse()
    cg = Codegen()
    cg.gen(ast)
    vm.run(cg.code)

def repl():
    vm = VM()
    print(BANNER)
    while True:
        try:
            line = input(">>> ").strip()
            if not line:
                continue
            if line.lower() in ("exit", "quit"):
                break
            if line.lower() == "env":
                print(vm.env)
                continue
            compile_and_run(line, vm)
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        
        vm = VM()
        compile_and_run(" ".join(sys.argv[1:]), vm)
    else:
        repl()
