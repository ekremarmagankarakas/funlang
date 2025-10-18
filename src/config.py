# src/config.py
import json


class LanguageConfig:
    """Manages custom keyword and operator configurations"""

    DEFAULT_CONFIG = {
        "keywords": {
            "fun": "fun",
            "var": "var",
            "int": "int",
            "float": "float",
            "string": "string",
            "list": "list",
            "and": "and",
            "or": "or",
            "not": "not",
            "if": "if",
            "elif": "elif",
            "else": "else",
            "for": "for",
            "while": "while",
            "return": "return",
            "break": "break",
            "continue": "continue",
        },
        "builtins": {
            "print": "print",
            "clear": "clear",
            "is_string": "is_string",
            "is_number": "is_number",
            "is_list": "is_list",
            "is_fun": "is_fun",
            "len": "len",
            "to_string": "to_string",
            "to_int": "to_int",
            "to_float": "to_float",
            "to_list": "to_list",
            "typeof": "typeof",
            "elos": "elos",
        },
    }

    def __init__(self, config_path=None):
        """Load configuration from file or use defaults"""
        self.config = self.DEFAULT_CONFIG.copy()

        if config_path:
            self.load_config(config_path)

        # Build reverse mappings for the lexer
        self.keyword_to_type = {}
        self.builtin_to_type = {}
        self._build_mappings()

    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = json.load(f)

            # Merge with defaults
            if "keywords" in user_config:
                self.config["keywords"].update(user_config["keywords"])
            if "builtins" in user_config:
                self.config["builtins"].update(user_config["builtins"])

            # Validate configuration
            self._validate_config()

        except FileNotFoundError:
            raise Exception(f"Config file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON in config file: {e}")

    def _validate_config(self):
        """Ensure no conflicts in the configuration"""
        all_words = set()

        # Check for duplicates across keywords and builtins
        for word in self.config["keywords"].values():
            if word in all_words:
                raise Exception(f"Duplicate keyword: '{word}'")
            all_words.add(word)

        for word in self.config["builtins"].values():
            if word in all_words:
                raise Exception(
                    f"Builtin function name conflicts with keyword: '{word}'"
                )
            all_words.add(word)

    def _build_mappings(self):
        """Build reverse mappings from custom words to token types"""
        from src.token import KeywordType, BuiltInFunctionType

        # Map custom keywords to their token types
        keyword_mapping = {
            "fun": KeywordType.FUN,
            "var": KeywordType.VAR,
            "int": KeywordType.INT_TYPE,
            "float": KeywordType.FLOAT_TYPE,
            "string": KeywordType.STRING_TYPE,
            "list": KeywordType.LIST_TYPE,
            "and": KeywordType.AND,
            "or": KeywordType.OR,
            "not": KeywordType.NOT,
            "if": KeywordType.IF,
            "elif": KeywordType.ELIF,
            "else": KeywordType.ELSE,
            "for": KeywordType.FOR,
            "while": KeywordType.WHILE,
            "return": KeywordType.RETURN,
            "break": KeywordType.BREAK,
            "continue": KeywordType.CONTINUE,
        }

        for internal_name, token_type in keyword_mapping.items():
            custom_word = self.config["keywords"][internal_name]
            self.keyword_to_type[custom_word] = token_type

        # Map custom builtin names to their token types
        builtin_mapping = {
            "print": BuiltInFunctionType.PRINT,
            "clear": BuiltInFunctionType.CLEAR,
            "is_string": BuiltInFunctionType.IS_STRING,
            "is_number": BuiltInFunctionType.IS_NUMBER,
            "is_list": BuiltInFunctionType.IS_LIST,
            "is_fun": BuiltInFunctionType.IS_FUN,
            "len": BuiltInFunctionType.LEN,
            "to_string": BuiltInFunctionType.TO_STRING,
            "to_int": BuiltInFunctionType.TO_INT,
            "to_float": BuiltInFunctionType.TO_FLOAT,
            "to_list": BuiltInFunctionType.TO_LIST,
            "typeof": BuiltInFunctionType.TYPEOF,
            "elos": BuiltInFunctionType.ELOS,
        }

        for internal_name, token_type in builtin_mapping.items():
            custom_word = self.config["builtins"][internal_name]
            self.builtin_to_type[custom_word] = token_type

    def get_keyword_type(self, word):
        """Get the token type for a custom keyword"""
        return self.keyword_to_type.get(word)

    def get_builtin_type(self, word):
        """Get the token type for a custom builtin function"""
        return self.builtin_to_type.get(word)

    def get_custom_word(self, token_type):
        """Get the custom word for a token type (for error messages)"""

        # Search in keywords
        for internal_name, custom_word in self.config["keywords"].items():
            if self.keyword_to_type.get(custom_word) == token_type:
                return custom_word

        # Search in builtins
        for internal_name, custom_word in self.config["builtins"].items():
            if self.builtin_to_type.get(custom_word) == token_type:
                return custom_word

        return None
