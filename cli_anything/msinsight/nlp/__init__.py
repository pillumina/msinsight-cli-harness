"""
Natural language processing layer for MindStudio Insight CLI.

This package provides natural language understanding and command
execution capabilities.
"""

from .intent_recognizer import IntentRecognizer, Intent, IntentType
from .command_executor import CommandExecutor

__all__ = [
    "IntentRecognizer",
    "Intent",
    "IntentType",
    "CommandExecutor"
]
