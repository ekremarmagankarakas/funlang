import sys
from run import run_file, run, compile_file, compile_to_llvm, build_executable
from src.config import LanguageConfig


def main():
    # Parse arguments for --config flag
    config = None
    args = sys.argv[1:]
    
    # Check for --config flag
    if '--config' in args:
        config_index = args.index('--config')
        if config_index + 1 < len(args):
            config_path = args[config_index + 1]
            try:
                config = LanguageConfig(config_path)
                print(f"Loaded configuration from: {config_path}")
            except Exception as e:
                print(f"Error loading config: {e}")
                sys.exit(1)
            # Remove --config and its argument from args
            args.pop(config_index)  # Remove --config
            args.pop(config_index)  # Remove config_path
        else:
            print("Error: --config requires a file path")
            sys.exit(1)
    
    # No arguments - run the shell
    if len(args) == 0:
        print("FunLang Shell - Type 'exit' to quit")
        print("Commands: 'compile <code>' to compile, 'run <code>' to interpret")
        while True:
            source = input('funlang > ')
            if source.lower() == 'exit':
                break

            if source.startswith('compile '):
                code = source[8:]
                llvm_ir, ast, tokens, error = compile_to_llvm('<stdin>', code, config)

                if error:
                    if isinstance(error, str):
                        print(f"Compilation Error: {error}")
                    else:
                        print(error.as_string())
                else:
                    print("LLVM IR:")
                    print(llvm_ir)
            elif source.startswith('run '):
                code = source[4:]
                result, ast, tokens, error = run('<stdin>', code, config)

                if error:
                    print(error.as_string())
                else:
                    print("Result:", result)
            else:
                result, ast, tokens, error = run('<stdin>', source, config)

                if error:
                    print(error.as_string())
                else:
                    print("Result:", result)

    # Run interactive shell development mode
    elif len(args) == 1 and args[0] == '--dev':
        print("FunLang Development Shell - Type 'exit' to quit")
        print("Commands: 'compile <code>' to compile, 'run <code>' to interpret")
        while True:
            source = input('funlang-dev > ')
            if source.lower() == 'exit':
                break

            if source.startswith('compile '):
                code = source[8:]
                llvm_ir, ast, tokens, error = compile_to_llvm('<stdin>', code, config)

                if error:
                    if isinstance(error, str):
                        print(f"Compilation Error: {error}")
                    else:
                        print(error.as_string())

                print("Lexer Tokens:", tokens)
                print("AST:", ast)
                print("LLVM IR:", llvm_ir)
            elif source.startswith('run '):
                code = source[4:]
                result, ast, tokens, error = run('<stdin>', code, config)

                if error:
                    print(error.as_string())

                print("Lexer Tokens:", tokens)
                print("AST:", ast)
                print("Result:", result)
            else:
                result, ast, tokens, error = run('<stdin>', source, config)

                if error:
                    print(error.as_string())

                print("Lexer Tokens:", tokens)
                print("AST:", ast)
                print("Result:", result)

    # Run a file
    elif len(args) == 1:
        file_path = args[0]
        result, ast, tokens, error = run_file(file_path, config)

        if error:
            if isinstance(error, str):
                print(f"Error: {error}")
            else:
                print(error.as_string())
            sys.exit(1)

        if result is not None:
            print(result)

    # Compile a file with --compile flag
    elif len(args) == 2 and args[0] == '--compile':
        file_path = args[1]
        llvm_ir, ast, tokens, error = compile_file(file_path, config)

        if error:
            if isinstance(error, str):
                print(f"Compilation Error: {error}")
            else:
                print(error.as_string())
            sys.exit(1)

        if llvm_ir:
            output_file = file_path.replace('.fl', '.ll')
            with open(output_file, 'w') as f:
                f.write(llvm_ir)
            print(f"LLVM IR written to {output_file}")

    # Build executable with --build flag
    elif len(args) == 2 and args[0] == '--build':
        file_path = args[1]
        executable, error = build_executable(file_path, config)

        if error:
            print(f"Build Error: {error}")
            sys.exit(1)

        if executable:
            print(f"Executable created: {executable}")

    # Invalid usage
    else:
        print("Usage:")
        print("  python main.py [--config <config.json>]                    # Interactive shell")
        print("  python main.py [--config <config.json>] <file.fl>          # Run file")
        print("  python main.py [--config <config.json>] --compile <file.fl> # Compile to LLVM IR")
        print("  python main.py [--config <config.json>] --build <file.fl>   # Build executable")
        sys.exit(1)


if __name__ == "__main__":
    main()
