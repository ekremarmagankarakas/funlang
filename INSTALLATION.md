# FunLang Installation Guide

FunLang is installed in **development mode** with dual access:
- ✅ Available globally via PATH
- ✅ Editable for development work

## How It Works

The setup uses a single venv installation that serves both purposes:

```
venv/bin/funlang (installed with pip install -e .)
         ↓
    Added to PATH in ~/.zshrc
         ↓
   Use 'funlang' anywhere!
```

Since it's installed with `-e` (editable mode), any code changes take effect immediately.

---

## Usage

### Regular Use (Anywhere)

Just use `funlang` from any directory:

```bash
funlang --config turkish examples/turkish_example.fl
funlang --config spanish examples/spanish_example.fl
funlang my_script.fl
```

The command is available because `venv/bin` is in your PATH.

### Development Work

When editing FunLang code:

```bash
# Option 1: Activate venv for IDE/editor support
source venv/bin/activate
# ... edit code ...
deactivate

# Option 2: Just edit directly (changes take effect immediately)
# ... edit code in your editor ...
```

**No reinstall needed!** Changes to Python files take effect immediately because it's installed with `pip install -e .`

Test your changes:
```bash
funlang your_test_script.fl
```

---

## Installation (If Starting Fresh)

If you need to reinstall or set up on a new machine:

```bash
# 1. Create and activate venv
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies and funlang in editable mode
pip install -r requirements.txt
pip install -e .

# 3. Add venv/bin to PATH in ~/.zshrc
echo 'export PATH="/Users/ekremarmagankarakas/Workspace/funlang/venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Done! Now 'funlang' works anywhere
```

---

## Verify Installation

```bash
# Check command location
which funlang
# Should show: /Users/.../Workspace/funlang/venv/bin/funlang

# Test it works
funlang --config turkish examples/turkish_example.fl
```

---

## How This Differs From Normal Installs

**Normal pip install:**
- Copies code to site-packages
- Must reinstall after every code change

**This setup (pip install -e .):**
- Creates a link to your source code
- Changes take effect immediately
- Perfect for development + daily use

---

## Troubleshooting

**"funlang: command not found"**

Your PATH might not be set. Check:
```bash
grep "funlang/venv/bin" ~/.zshrc
```

If missing, add it:
```bash
echo 'export PATH="/Users/ekremarmagankarakas/Workspace/funlang/venv/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Import errors or missing dependencies**

Reinstall in the venv:
```bash
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
deactivate
```

---

## Uninstall

```bash
# Remove from PATH (edit ~/.zshrc and remove the funlang line)

# Uninstall package
source venv/bin/activate
pip uninstall funlang
deactivate
```
