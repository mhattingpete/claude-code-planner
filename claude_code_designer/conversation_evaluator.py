#!/usr/bin/env python3
"""
Conversation Evaluator

Analyzes saved conversations to evaluate agent performance, quality of responses,
and alignment with user requests using the conversation-evaluator subagent.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from claude_code_sdk import ClaudeCodeOptions, Message, query


class ConversationEvaluator:
    """Evaluates saved conversations for agent performance and response quality."""

    def __init__(
        self,
        conversation_dir: str = "./conversations",
        evaluation_dir: str = "./evaluations",
    ):
        self.conversation_dir = Path(conversation_dir)
        self.evaluation_dir = Path(evaluation_dir)
        self.evaluation_dir.mkdir(exist_ok=True)

    async def evaluate_conversation(self, conversation_file: Path) -> dict[str, Any]:
        """
        Evaluate a single conversation using the conversation-evaluator subagent.

        Args:
            conversation_file: Path to the conversation JSON file

        Returns:
            Dictionary containing evaluation results
        """
        print(f"Evaluating conversation: {conversation_file.name}")

        # Load the conversation data
        with open(conversation_file, encoding="utf-8") as f:
            conversation_data = json.load(f)

        # Build evaluation prompt
        evaluation_prompt = self._build_evaluation_prompt(conversation_data)

        # Use Task tool to launch conversation-evaluator subagent
        return await self._run_evaluation_task(
            evaluation_prompt, conversation_file.stem
        )

    async def evaluate_all_conversations(self) -> list[dict[str, Any]]:
        """
        Evaluate all conversations in the conversation directory.

        Returns:
            List of evaluation results for each conversation
        """
        if not self.conversation_dir.exists():
            print(f"❌ Conversation directory not found: {self.conversation_dir}")
            return []

        json_files = list(self.conversation_dir.glob("*.json"))
        if not json_files:
            print(f"📂 No conversations found in {self.conversation_dir}")
            return []

        print(f"📋 Evaluating {len(json_files)} conversations...")

        evaluations = []
        for file in sorted(json_files):
            try:
                evaluation = await self.evaluate_conversation(file)
                evaluations.append(evaluation)

                # Save individual evaluation
                evaluation_file = self.evaluation_dir / f"{file.stem}_evaluation.json"
                with open(evaluation_file, "w", encoding="utf-8") as f:
                    json.dump(evaluation, f, indent=2, ensure_ascii=False)

                print(f"✅ Evaluation saved: {evaluation_file.name}")

            except Exception as e:
                print(f"❌ Error evaluating {file.name}: {e}")
                continue

        # Save summary evaluation
        summary = self._create_evaluation_summary(evaluations)
        summary_file = (
            self.evaluation_dir
            / f"evaluation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"📊 Summary evaluation saved: {summary_file.name}")
        return evaluations

    def _build_evaluation_prompt(self, conversation_data: dict[str, Any]) -> str:
        """Build the evaluation prompt for the conversation-evaluator subagent."""
        input_data = conversation_data.get("input", {})
        output_data = conversation_data.get("output", {})
        messages = output_data.get("messages", [])

        prompt_parts = [
            "Please evaluate this conversation between a user and an AI design assistant.",
            "",
            "## Original User Request:",
            f"Prompt: {input_data.get('prompt', 'Not available')}",
            f"Max turns: {input_data.get('options', {}).get('max_turns', 'Not specified')}",
            f"System prompt: {input_data.get('options', {}).get('system_prompt', 'Default used')}",
            "",
            "## Conversation Messages:",
        ]

        # Add message details
        for i, message in enumerate(
            messages[:10]
        ):  # Limit to first 10 messages to avoid token limits
            message_type = message.get("type", "Unknown")
            message_content = message.get("content", "")[:500]  # Truncate long content
            prompt_parts.append(f"Message {i + 1} ({message_type}): {message_content}")
            if len(message_content) == 500:
                prompt_parts.append("[Content truncated...]")
            prompt_parts.append("")

        if len(messages) > 10:
            prompt_parts.append(f"[{len(messages) - 10} additional messages not shown]")
            prompt_parts.append("")

        prompt_parts.extend(
            [
                "## Evaluation Criteria:",
                "",
                "Please analyze and provide scores (1-10) and explanations for:",
                "",
                "1. **Request Fulfillment** (1-10): Did the agent address what the user asked for?",
                "2. **Response Quality** (1-10): Was the guidance helpful, accurate, and well-structured?",
                "3. **Appropriateness** (1-10): Were the responses appropriate for the context and request?",
                "4. **Completeness** (1-10): Did the agent provide comprehensive assistance?",
                "5. **Communication Style** (1-10): Was the communication clear and professional?",
                "",
                "## Additional Analysis:",
                "- What did the agent do well?",
                "- What could be improved?",
                "- Were there any concerning responses or behaviors?",
                "- Did the conversation achieve its intended purpose?",
                "",
                "Please provide your evaluation in a structured format with scores and detailed explanations.",
            ]
        )

        return "\n".join(prompt_parts)

    async def _run_evaluation_task(
        self, evaluation_prompt: str, conversation_id: str
    ) -> dict[str, Any]:
        """Run the evaluation using the conversation-evaluator subagent via Task tool."""
        print(f"Running evaluation task for: {conversation_id}")

        messages: list[Message] = []

        # Use the conversation-evaluator subagent optimized prompt
        optimized_prompt = f"""Please analyze this conversation for agent performance and quality. Use the conversation-evaluator for the evaluation.

{evaluation_prompt}

Focus on providing:
1. Specific scores (1-10) for each evaluation criterion
2. Concrete examples from the conversation
3. Actionable improvement recommendations
4. Assessment of whether the agent met user expectations

Use your expertise in conversation analysis to provide objective, constructive feedback."""

        options = ClaudeCodeOptions(
            max_turns=5,
        )

        try:
            async for message in query(prompt=optimized_prompt, options=options):
                messages.append(message)
                print(f"Received evaluation message: {type(message).__name__}")

        except KeyboardInterrupt:
            print("\\nEvaluation interrupted by user")
        except Exception as e:
            print(f"Error during evaluation: {e}")
            raise

        # Structure the evaluation result
        evaluation_result = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "evaluation_prompt": evaluation_prompt,
            "evaluation_messages": [
                {
                    "type": type(msg).__name__,
                    "content": str(msg.content)
                    if hasattr(msg, "content")
                    else str(msg),
                    "metadata": self._serialize_message_metadata(msg),
                }
                for msg in messages
            ],
            "message_count": len(messages),
            "subagent_used": "conversation-evaluator",
        }

        return evaluation_result

    def _serialize_message_metadata(self, msg: Message) -> dict[str, Any]:
        """Safely serialize message metadata to JSON-compatible format."""
        try:
            metadata = getattr(msg, "__dict__", {})
            # Convert to JSON-serializable format
            serialized = {}
            for key, value in metadata.items():
                try:
                    # Test if value is JSON serializable
                    json.dumps(value)
                    serialized[key] = value
                except (TypeError, ValueError):
                    # If not serializable, convert to string
                    serialized[key] = str(value)
            return serialized
        except Exception:
            return {"error": "Could not serialize metadata"}

    def _create_evaluation_summary(
        self, evaluations: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create a summary of all evaluations."""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_conversations": len(evaluations),
            "successful_evaluations": len(
                [e for e in evaluations if e.get("message_count", 0) > 0]
            ),
            "evaluation_overview": [
                {
                    "conversation_id": eval_data.get("conversation_id"),
                    "message_count": eval_data.get("message_count", 0),
                    "timestamp": eval_data.get("timestamp"),
                }
                for eval_data in evaluations
            ],
        }

    async def get_conversation_insights(self) -> dict[str, Any]:
        """Get insights about conversation patterns and quality."""
        evaluation_files = list(self.evaluation_dir.glob("*_evaluation.json"))

        if not evaluation_files:
            return {"message": "No evaluations found. Run evaluations first."}

        insights_prompt = """Analyze the evaluation data and provide insights about:
        1. Common patterns in successful conversations
        2. Areas where the design assistant performs well
        3. Common issues or areas for improvement
        4. Recommendations for better user experience

        Focus on actionable insights that could improve the design assistant."""

        # This would be implemented to analyze multiple evaluation files
        # For now, return a placeholder
        return {
            "total_evaluations": len(evaluation_files),
            "insights_prompt": insights_prompt,
            "message": "Insights analysis would be implemented here",
        }


async def main():
    """Example usage of the ConversationEvaluator."""
    evaluator = ConversationEvaluator()

    # Evaluate all conversations
    evaluations = await evaluator.evaluate_all_conversations()

    if evaluations:
        print(f"\\n📊 Completed evaluation of {len(evaluations)} conversations")
        print("Check the ./evaluations directory for detailed results")
    else:
        print("\\n❌ No conversations to evaluate")


if __name__ == "__main__":
    asyncio.run(main())
