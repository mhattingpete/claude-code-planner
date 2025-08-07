#!/usr/bin/env python3
"""
Claude Code Conversation Saver

Saves both input prompts and output responses from Claude Code SDK interactions.
Stores conversations in JSON format with timestamps and metadata.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import anyio
from claude_code_sdk import ClaudeCodeOptions, Message, query


class ConversationSaver:
    def __init__(self, output_dir: str = "./conversations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def _generate_filename(self, prompt: str) -> str:
        """Generate a filename based on timestamp and prompt preview."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_preview = "".join(
            c for c in prompt[:30] if c.isalnum() or c.isspace()
        ).strip()
        prompt_preview = "_".join(prompt_preview.split())
        return f"{timestamp}_{prompt_preview}.json"

    async def save_conversation(
        self,
        prompt: str,
        max_turns: int = 10,
        cwd: str | None = None,
        allowed_tools: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Save a complete conversation with Claude Code SDK.

        Args:
            prompt: The input prompt to send to Claude
            max_turns: Maximum number of conversation turns
            cwd: Working directory for Claude
            allowed_tools: List of allowed tools

        Returns:
            Dictionary containing the complete conversation data
        """
        print(f"Starting conversation with prompt: {prompt[:50]}...")

        messages: list[Message] = []

        options = ClaudeCodeOptions(
            max_turns=max_turns,
            cwd=cwd,
            allowed_tools=allowed_tools,
        )

        try:
            async for message in query(prompt=prompt, options=options):
                messages.append(message)
                print(f"Received message: {type(message).__name__}")

        except KeyboardInterrupt:
            print("\nConversation interrupted by user")
        except Exception as e:
            print(f"Error during conversation: {e}")

        conversation_data = {
            "timestamp": datetime.now().isoformat(),
            "input": {
                "prompt": prompt,
                "options": {
                    "max_turns": max_turns,
                    "cwd": cwd,
                    "allowed_tools": allowed_tools,
                },
            },
            "output": {
                "message_count": len(messages),
                "messages": [
                    {
                        "type": type(msg).__name__,
                        "content": str(msg.content)
                        if hasattr(msg, "content")
                        else str(msg),
                        "metadata": getattr(msg, "__dict__", {}),
                    }
                    for msg in messages
                ],
            },
        }

        filename = self._generate_filename(prompt)
        filepath = self.output_dir / filename

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(conversation_data, f, indent=2, ensure_ascii=False)

        print(f"Conversation saved to: {filepath}")
        return conversation_data


async def main():
    """Example usage of the ConversationSaver."""
    saver = ConversationSaver()

    # Example conversation
    prompt = "Write a simple Python function to calculate fibonacci numbers"

    conversation = await saver.save_conversation(
        prompt=prompt, max_turns=5, allowed_tools=["Read", "Write", "Bash"]
    )

    print(f"Saved conversation with {conversation['output']['message_count']} messages")


if __name__ == "__main__":
    anyio.run(main)
