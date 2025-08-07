#!/usr/bin/env python3
"""
Example of using the ConversationEvaluator programmatically.
"""

import asyncio

from claude_code_designer import ConversationEvaluator


async def evaluate_conversations_example():
    """Example: Evaluate all saved conversations programmatically."""
    evaluator = ConversationEvaluator("./conversations", "./evaluations")

    print("🔍 Starting conversation evaluation...")

    # Evaluate all conversations
    evaluations = await evaluator.evaluate_all_conversations()

    if evaluations:
        print(f"✅ Successfully evaluated {len(evaluations)} conversations")
        print("📊 Evaluation results saved to ./evaluations/")

        # Print summary
        successful = len([e for e in evaluations if e.get("message_count", 0) > 0])
        print(f"📈 {successful}/{len(evaluations)} evaluations completed successfully")
    else:
        print("❌ No conversations found to evaluate")


async def evaluate_specific_conversation():
    """Example: Evaluate a specific conversation file."""
    from pathlib import Path

    evaluator = ConversationEvaluator("./conversations", "./evaluations")

    # Find the first conversation file
    conversation_dir = Path("./conversations")
    if conversation_dir.exists():
        json_files = list(conversation_dir.glob("*.json"))
        if json_files:
            conversation_file = json_files[0]
            print(f"🔍 Evaluating specific conversation: {conversation_file.name}")

            evaluation = await evaluator.evaluate_conversation(conversation_file)

            print(f"✅ Evaluation completed with {evaluation.get('message_count', 0)} evaluation messages")
        else:
            print("❌ No conversation files found")
    else:
        print("❌ Conversations directory not found")


if __name__ == "__main__":
    print("📊 Conversation Evaluation Examples")
    print("=" * 40)

    # Run the examples
    print("\n1. Evaluating all conversations:")
    asyncio.run(evaluate_conversations_example())

    print("\n2. Evaluating specific conversation:")
    asyncio.run(evaluate_specific_conversation())
