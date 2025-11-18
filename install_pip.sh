#!/bin/bash

# FunLang Installation Script
# Sets up FunLang for both development and regular use

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}FunLang Installation${NC}"
echo "===================="
echo ""

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv "$SCRIPT_DIR/venv"
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate venv
source "$SCRIPT_DIR/venv/bin/activate"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Dependencies installed"

# Install funlang in editable mode
echo "Installing FunLang in editable mode..."
pip install -e "$SCRIPT_DIR" > /dev/null 2>&1
echo -e "${GREEN}✓${NC} FunLang installed (editable mode)"

deactivate

# Add to PATH if not already there
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ] || [ -f "$HOME/.zshrc" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ] || [ -f "$HOME/.bashrc" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    SHELL_CONFIG="$HOME/.profile"
fi

PATH_LINE="export PATH=\"$SCRIPT_DIR/venv/bin:\$PATH\""

if ! grep -q "funlang/venv/bin" "$SHELL_CONFIG" 2>/dev/null; then
    echo ""
    echo "Adding funlang to PATH in $SHELL_CONFIG..."
    echo "" >> "$SHELL_CONFIG"
    echo "# FunLang" >> "$SHELL_CONFIG"
    echo "$PATH_LINE" >> "$SHELL_CONFIG"
    echo -e "${GREEN}✓${NC} Added to PATH"
    echo ""
    echo -e "${YELLOW}Run this to use funlang now:${NC}"
    echo "  source $SHELL_CONFIG"
else
    echo -e "${GREEN}✓${NC} Already in PATH"
fi

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Reload your shell: ${YELLOW}source $SHELL_CONFIG${NC}"
echo "  2. Verify: ${YELLOW}which funlang${NC}"
echo "  3. Test: ${YELLOW}funlang --config turkish examples/turkish_example.fl${NC}"
echo ""
echo -e "${BLUE}This setup gives you:${NC}"
echo "  ✓ Use 'funlang' command anywhere"
echo "  ✓ Code changes take effect immediately (editable mode)"
echo "  ✓ Perfect for both development and regular use"
echo ""
