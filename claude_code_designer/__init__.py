"""Claude Code Designer - A CLI tool for generating project documentation using Claude Code SDK."""

__version__ = "0.1.0"
__author__ = "Anthropic"
__email__ = "support@anthropic.com"

from .conversation_evaluator import ConversationEvaluator
from .design_assistant import DesignAssistant
from .save_claude_conversation import ConversationSaver

__all__ = ["__version__", "__author__", "__email__", "DesignAssistant", "ConversationSaver", "ConversationEvaluator"]
