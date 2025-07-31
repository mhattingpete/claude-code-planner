"""Constants for Claude Code Designer."""

# Document types and file names
DOCUMENT_TYPES = {
    "PRD": "PRD.md",
    "CLAUDE_MD": "CLAUDE.md",
    "README": "README.md",
}

# Limits and constraints
MAX_JSON_SIZE = 50000  # 50KB limit for JSON parsing
MAX_FIELD_LENGTH = 10000  # 10KB limit per field
MAX_ITEM_LENGTH = 1000  # Maximum length for individual list items
MAX_LIST_ITEMS = 50  # Maximum number of items in a list

# Default values
DEFAULT_OUTPUT_DIR = "."
DEFAULT_APP_TYPE = "Web Application"
DEFAULT_APP_DESCRIPTION = "A software application"

# Default questions structure
DEFAULT_QUESTION_OPTIONS = {
    "app_type": ["Web Application", "CLI Tool", "API Service", "Mobile App"],
}

# Error message templates
ERROR_MESSAGES = {
    "connection": "Network connection error. Please check your internet connection and try again.",
    "authentication": "Please run 'claude auth login' to authenticate with Claude Code CLI.",
    "rate_limit": "Rate limit exceeded. Please wait a few minutes before trying again.",
    "timeout": "Check your internet connection and try again. If the problem persists, Claude services may be temporarily unavailable.",
    "default": "Check your Claude Code CLI installation with 'claude --version' and ensure you're authenticated with 'claude auth status'.",
}

# File encoding
DEFAULT_ENCODING = "utf-8"

# Console styling
PANEL_STYLES = {
    "welcome": "blue",
    "question": "cyan",
    "summary": "green",
    "info": "blue",
}

# Control characters to filter out
INVALID_CONTROL_CHARS = ["\x00", "\x08", "\x0b", "\x0c"]
ALLOWED_CONTROL_CHARS = ["\n", "\t"]

# Intelligent app name defaults
INTELLIGENT_APP_NAMES = {
    "cli": {
        "tool": "utility-cli",
        "process": "process-manager",
        "default": "command-line-tool",
    },
    "api": {
        "data": "data-service",
        "auth": "auth-service",
        "default": "api-service",
    },
    "mobile": {
        "social": "social-mobile-app",
        "productivity": "productivity-app",
        "default": "mobile-application",
    },
    "web": {
        "dashboard": "admin-dashboard",
        "shop": "web-store",
        "blog": "content-platform",
        "default": "web-application",
    },
}
