#!/bin/bash

# FunLang Installation Script

# Check if running as root for system-wide install
if [ "$EUID" -eq 0 ]; then
    INSTALL_DIR="/usr/local/bin"
    LIB_DIR="/usr/local/lib/funlang"
    echo "Installing FunLang system-wide..."
else
    # User install
    INSTALL_DIR="$HOME/.local/bin"
    LIB_DIR="$HOME/.local/lib/funlang"
    echo "Installing FunLang for current user..."
    
    # Create directories if they don't exist
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$(dirname "$LIB_DIR")"
fi

# Copy FunLang files to library directory
echo "Copying FunLang files to $LIB_DIR..."
mkdir -p "$LIB_DIR"
cp -r src/ "$LIB_DIR/"
cp main.py "$LIB_DIR/"
cp run.py "$LIB_DIR/"
cp requirements.txt "$LIB_DIR/"

# Create wrapper script
echo "Creating funlang executable..."
cat > "$INSTALL_DIR/funlang" << 'EOF'
#!/usr/bin/env python3

import sys
import os

# Add FunLang library directory to Python path
if os.path.exists('/usr/local/lib/funlang'):
    sys.path.insert(0, '/usr/local/lib/funlang')
elif os.path.exists(os.path.expanduser('~/.local/lib/funlang')):
    sys.path.insert(0, os.path.expanduser('~/.local/lib/funlang'))
else:
    print("Error: FunLang installation not found!")
    sys.exit(1)

from main import main

if __name__ == "__main__":
    main()
EOF

# Make executable
chmod +x "$INSTALL_DIR/funlang"

echo "Installation complete!"
echo ""
if [ "$EUID" -ne 0 ]; then
    echo "Make sure $INSTALL_DIR is in your PATH:"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
    echo "Add this line to your ~/.bashrc or ~/.zshrc to make it permanent."
    echo ""
fi

echo "You can now use 'funlang' command:"
echo "  funlang                        # Interactive shell"
echo "  funlang script.fl              # Run FunLang script"
echo "  funlang --compile script.fl    # Compile to LLVM IR"
echo "  funlang --build script.fl      # Build executable"
echo ""
echo "Dependencies needed for compilation:"
echo "  pip install llvmlite"
echo "  # Also need: llvm, clang"