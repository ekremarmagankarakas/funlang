# FunLang - A Simple Programming Language

FunLang is a lightweight, interpreted programming language designed for learning compiler/interpreter concepts. 

## Features

- **Dynamic Typing**: Variables don't need type declarations
- **First-class Functions**: Functions are values that can be passed around
- **Control Flow**: If/elif/else statements, for and while loops
- **Data Structures**: Numbers (integers and floats), strings, and lists
- **Type Casting**: Convert between different data types
- **Built-in Functions**: Several utility functions included

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

var result = add(5, 3);
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

While loop:
```
var i = 0;
while i < 10 {
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

## Running FunLang Programs

### Interactive Mode
```
python3 main.py
```

### Running a Script
```
python3 main.py script.fl
```

## Examples

Check the `examples/` directory for sample programs:
- `example.fl`: Basic language features
- `example2.fl`: Binary search with type casting

## Implementation

FunLang is implemented in Python with a classic interpreter design:
1. **Lexer** (`lexer.py`): Converts source code into tokens
2. **Parser** (`parser.py`): Converts tokens into an Abstract Syntax Tree
3. **Interpreter** (`interpreter.py`): Executes the AST

## References

- https://github.com/davidcallanan/py-myopl-code
- https://ruslanspivak.com/lsbasi-part1/

## License

This project is open-source and available for educational purposes.
