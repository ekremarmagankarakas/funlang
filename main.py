import sys
from run import run_file, run, compile_file, compile_to_llvm, build_executable


def main():
    # No arguments - run the shell
    if len(sys.argv) == 1:
        print("FunLang Shell - Type 'exit' to quit")
        print("Commands: 'compile <code>' to compile, 'run <code>' to interpret")
        while True:
            source = input('funlang > ')
            if source.lower() == 'exit':
                break

            if source.startswith('compile '):
                code = source[8:]
                llvm_ir, ast, tokens, error = compile_to_llvm('<stdin>', code)

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
                result, ast, tokens, error = run('<stdin>', code)

                if error:
                    print(error.as_string())
                else:
                    print("Result:", result)
            else:
                result, ast, tokens, error = run('<stdin>', source)

                if error:
                    print(error.as_string())
                else:
                    print("Result:", result)

    # Run or compile a file
    elif len(sys.argv) == 2:
        file_path = sys.argv[1]
        result, ast, tokens, error = run_file(file_path)

        if error:
            if isinstance(error, str):
                print(f"Error: {error}")
            else:
                print(error.as_string())
            sys.exit(1)

        if result is not None:
            print(result)

    # Compile a file with --compile flag
    elif len(sys.argv) == 3 and sys.argv[1] == '--compile':
        file_path = sys.argv[2]
        llvm_ir, ast, tokens, error = compile_file(file_path)

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
    elif len(sys.argv) == 3 and sys.argv[1] == '--build':
        file_path = sys.argv[2]
        executable, error = build_executable(file_path)

        if error:
            print(f"Build Error: {error}")
            sys.exit(1)

        if executable:
            print(f"Executable created: {executable}")

    # Invalid usage
    else:
        print("Usage:")
        print("  python main.py                    # Interactive shell")
        print("  python main.py <file.fl>          # Run file")
        print("  python main.py --compile <file.fl> # Compile to LLVM IR")
        print("  python main.py --build <file.fl>   # Build executable")
        sys.exit(1)


if __name__ == "__main__":
    main()
