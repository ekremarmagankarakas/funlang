# FunLang - A Simple Programming Language

FunLang is a lightweight, interpreted programming language designed for learning compiler/interpreter concepts. 

## Features

- **Dynamic and Static Typing**: Variables support both dynamic typing and optional type declarations
- **First-class Functions**: Functions are values that can be passed around with strict return type checking
- **Control Flow**: If/elif/else statements, for and while loops with break/continue support
- **Data Structures**: Numbers (integers and floats), strings, and lists with comprehensive operations
- **Type Casting**: Convert between different data types
- **Built-in Functions**: Several utility functions included
- **LLVM Compilation**: Compile FunLang code to LLVM IR and native executables

## Language Syntax

### Variables

```
var name = value;
```

Variables can be reassigned after declaration:

```
var x = 5;
x = 10;  // Reassignment
```

### Data Types

#### Numbers
```
var integer = 42;
var float_num = 3.14;
```

#### Strings
```
var greeting = "Hello, world!";
```

#### Lists
```
var numbers = [1, 2, 3, 4, 5];
var mixed = [1, "two", 3.0];
```

#### Functions
```
fun add(a, b) {
    return a + b;
};

// Functions with type annotations and return types
fun int multiply(int a, int b) {
    return a * b;
};

var result = add(5, 3);
```

#### Type Annotations
```
var int num = 42;
var float pi = 3.14;
var string hello = "hello world!";
var list numbers = [1, 2, 3, 4, 5];

// Strict type checking ensures type safety
var int strict_num = 42;  // Must be an integer
```

### Control Flow

#### If Statements
```
if condition {
  // code
} elif another_condition {
  // code
} else {
  // code
}
```

#### Loops

For loop:
```
for i = 0, 10 {
    print(i);
}
```

With step value:
```
for i = 0, 10, 2 {
    print(i);  // 0, 2, 4, 6, 8
}
```

While loop with break/continue support:
```
var i = 0;
while i < 10 {
    if i == 5 {
        continue;  // Skip iteration
    }
    if i == 8 {
        break;     // Exit loop
    }
    print(i);
    i = i + 1;
}
```

### Type Casting

Convert between different types:

```
// String to integer
var str_num = "42";
var num = to_int(str_num);

// String to float
var str_float = "3.14";
var float_num = to_float(str_float);

// Number to string
var num = 42;
var str = to_string(num);

// Value to list
var chars = to_list("hello");  // Creates a list of characters
```

### Built-in Functions

- `print(value)`: Display a value
- `clear()`: Clear the console
- `is_number(value)`: Check if value is a number
- `is_string(value)`: Check if value is a string
- `is_list(value)`: Check if value is a list
- `is_fun(value)`: Check if value is a function
- `len(list)`: Get length of a list
- `to_string(value)`: Convert value to string
- `to_int(value)`: Convert value to integer
- `to_float(value)`: Convert value to float
- `to_list(value)`: Convert value to list
- `typeof(value)`: Get the type of value

## Installation

Run the installation script:

```bash
./install_pip.sh
```

This sets up FunLang for both development and regular use by:
- Creating a venv with dependencies
- Installing in editable mode (changes take effect immediately)
- Adding to your PATH (use `funlang` anywhere)

Then reload your shell:
```bash
source ~/.zshrc  # or ~/.bashrc
```

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

## Running FunLang Programs

Once installed, use the `funlang` command:

### Interactive Mode
```bash
funlang
```

In interactive mode, you can use special commands:
- `run <code>` - Interpret code directly
- `compile <code>` - Compile code to LLVM IR

### Running a Script
```bash
funlang script.fl
```

### Using Language Configs
```bash
funlang --config turkish examples/turkish_example.fl
funlang --config spanish examples/spanish_example.fl
funlang --config emoji examples/example.fl
```

### Compilation Options

#### Compile to LLVM IR
```bash
funlang --compile script.fl
```
This generates a `.ll` file with LLVM intermediate representation.

#### Build Native Executable
```bash
funlang --build script.fl
```
This compiles the FunLang code to a native executable.

### Alternative: Run Directly (Development)

If you haven't installed the package, you can run directly:
```bash
python3 main.py                    # Interactive mode
python3 main.py script.fl          # Run a script
python3 main.py --config turkish script.fl
```

## Examples

Check the `examples/` directory for sample programs:
- `example.fl`: Basic language features
- `example2.fl`: Binary search with type casting
- `example3.fl`: Simple arithmetic
- `turkish_example.fl`: Full example using Turkish keywords
- `spanish_example.fl`: Full example using Spanish keywords

Try them with different language configs:
```bash
funlang --config turkish examples/turkish_example.fl
funlang --config spanish examples/spanish_example.fl
```

## Implementation

FunLang is implemented in Python with both interpreter and compiler backends:
1. **Lexer** (`lexer.py`): Converts source code into tokens
2. **Parser** (`parser.py`): Converts tokens into an Abstract Syntax Tree
3. **Interpreter** (`interpreter.py`): Executes the AST directly
4. **Code Generator** (`codegen.py`): Compiles AST to LLVM IR for native execution

## References

- https://github.com/davidcallanan/py-myopl-code
- https://ruslanspivak.com/lsbasi-part1/

## License

This project is open-source and available for educational purposes.
