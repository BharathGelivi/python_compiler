# Mini Math Compiler in Python

A simple compiler and virtual machine implemented in Python that can handle basic math expressions, variables, and print statements.

## Features

- **Lexical Analysis (Lexer)**: Tokenizes input strings into meaningful symbols (numbers, identifiers, operators).
- **Parsing (Recursive Descent Parser)**: Builds an Abstract Syntax Tree (AST) from tokens.
- **Code Generation**: Compiles AST to a tiny stack-based bytecode.
- **Virtual Machine (VM)**: Executes the bytecode.
- **REPL Mode**: Interactive mode to type and execute expressions.

## Supported Syntax

- **Basic arithmetic**: `+`, `-`, `*`, `/`, `^` (power)
- **Parentheses**: `( ... )` for grouping
- **Unary minus**: `-5`, `-(2+3)`
- **Variables**: Assignment using `=`
- **Print statements**: `print x + 1` or `print( x + 1 )`

## Examples

```text
x = 2 + 3*4
print x + 1
print( (1+2)^3 - 4/5 )
-3 + 4 * 2
```

Special commands in REPL:
- `env`: Show current variables
- `exit`: Quit the REPL

## How to Run

1. **Download the script**:
   ```bash
   wget https://path-to-your/mini_compiler.py
   ```

2. **Run in REPL mode**:
   ```bash
   python3 mini_compiler.py
   ```

3. **Run a single expression from command line**:
   ```bash
   python3 mini_compiler.py "print (2+3)*4"
   ```

## File Structure

```
mini_compiler.py   # Main compiler + VM implementation
README.md          # This documentation
```

## Implementation Details

The compiler has 5 stages:

1. **Lexer** – Converts the input text into tokens.
2. **Parser** – Converts the token stream into an AST using recursive descent parsing.
3. **Code Generator** – Converts the AST into a list of bytecode instructions.
4. **Virtual Machine** – Executes the bytecode instructions using a stack.
5. **Driver / REPL** – Interactive loop for running commands.

## License

MIT License - Feel free to use and modify.
