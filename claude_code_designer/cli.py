#!/usr/bin/env python3
"""
Claude Code Design Assistant

Interactive CLI tool for designing applications and features using Claude Code SDK.
Saves conversation history and supports both CLI and programmatic usage.
"""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from .conversation_evaluator import ConversationEvaluator
from .design_assistant import DesignAssistant
from .learning_system import LearningSystem
from .simulator import DesignSimulator

console = Console()


@click.group()
@click.option(
    "--conversation-dir",
    default="./conversations",
    help="Directory to save conversations",
)
@click.pass_context
def cli(ctx, conversation_dir):
    """Claude Code Design Assistant - Help design applications and features."""
    ctx.ensure_object(dict)
    ctx.obj["assistant"] = DesignAssistant(conversation_dir)


@cli.command()
@click.option("--name", help="Project name")
@click.option(
    "--type", "project_type", help="Project type (web, cli, api, mobile, etc.)"
)
@click.option("--description", "project_description", help="Project description")
@click.option("--max-turns", default=15, help="Maximum conversation turns")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.pass_context
def app(ctx, name, project_type, project_description, max_turns, non_interactive):
    """Design a new application."""
    console.print(Panel.fit("🚀 Application Design Assistant", style="bold blue"))

    assistant = ctx.obj["assistant"]

    async def run_design():
        return await assistant.design_application(
            project_name=name,
            project_type=project_type,
            project_description=project_description,
            interactive=not non_interactive,
            max_turns=max_turns,
        )

    try:
        conversation = asyncio.run(run_design())
        console.print(
            f"✅ Design session completed with {conversation['output']['message_count']} messages"
        )
    except KeyboardInterrupt:
        console.print("\n❌ Design session interrupted by user")
    except Exception as e:
        console.print(f"❌ Error: {e}")


@cli.command()
@click.option("--description", help="Feature description")
@click.option("--context", help="Project context")
@click.option("--max-turns", default=10, help="Maximum conversation turns")
@click.option("--non-interactive", is_flag=True, help="Run in non-interactive mode")
@click.pass_context
def feature(ctx, description, context, max_turns, non_interactive):
    """Design a new feature for an existing project."""
    console.print(Panel.fit("⚡ Feature Design Assistant", style="bold green"))

    assistant = ctx.obj["assistant"]

    async def run_design():
        return await assistant.design_feature(
            feature_description=description,
            project_context=context,
            interactive=not non_interactive,
            max_turns=max_turns,
        )

    try:
        conversation = asyncio.run(run_design())
        console.print(
            f"✅ Feature design completed with {conversation['output']['message_count']} messages"
        )
    except KeyboardInterrupt:
        console.print("\n❌ Feature design interrupted by user")
    except Exception as e:
        console.print(f"❌ Error: {e}")


@cli.command()
@click.argument("conversation_dir", default="./conversations")
def list_conversations(conversation_dir):
    """List saved conversations."""
    conversations_path = Path(conversation_dir)
    if not conversations_path.exists():
        console.print(f"❌ Conversations directory not found: {conversation_dir}")
        return

    json_files = list(conversations_path.glob("*.json"))
    if not json_files:
        console.print(f"📂 No conversations found in {conversation_dir}")
        return

    console.print(f"📋 Found {len(json_files)} conversations in {conversation_dir}:")
    for file in sorted(json_files):
        console.print(f"  • {file.name}")


@cli.command()
@click.option(
    "--conversation-dir",
    default="./conversations",
    help="Directory with conversations to evaluate",
)
@click.option(
    "--evaluation-dir", default="./evaluations", help="Directory to save evaluations"
)
@click.option("--conversation-file", help="Evaluate specific conversation file")
def evaluate(conversation_dir, evaluation_dir, conversation_file):
    """Evaluate conversation quality and agent performance."""
    console.print(Panel.fit("📊 Conversation Evaluator", style="bold purple"))

    evaluator = ConversationEvaluator(conversation_dir, evaluation_dir)

    async def run_evaluation():
        if conversation_file:
            # Evaluate specific conversation
            file_path = Path(conversation_dir) / conversation_file
            if not file_path.exists():
                console.print(f"❌ Conversation file not found: {file_path}")
                return

            evaluation = await evaluator.evaluate_conversation(file_path)

            # Save evaluation
            eval_file = Path(evaluation_dir) / f"{file_path.stem}_evaluation.json"
            eval_file.parent.mkdir(exist_ok=True)
            with open(eval_file, "w", encoding="utf-8") as f:
                import json

                json.dump(evaluation, f, indent=2, ensure_ascii=False)

            console.print(f"✅ Evaluation completed: {eval_file.name}")
        else:
            # Evaluate all conversations
            evaluations = await evaluator.evaluate_all_conversations()
            if evaluations:
                console.print(
                    f"✅ Completed evaluation of {len(evaluations)} conversations"
                )
                console.print(f"📁 Results saved to: {evaluation_dir}")
            else:
                console.print("❌ No conversations found to evaluate")

    try:
        asyncio.run(run_evaluation())
    except KeyboardInterrupt:
        console.print("\n❌ Evaluation interrupted by user")
    except Exception as e:
        console.print(f"❌ Error: {e}")


@cli.command()
@click.option("--cycles", default=3, help="Number of simulation cycles to run")
@click.option("--delay", default=2.0, help="Delay between cycles in seconds")
@click.option(
    "--type",
    "scenario_type",
    type=click.Choice(["app", "feature"]),
    help="Type of scenarios to generate (app, feature, or mixed)",
)
@click.option(
    "--conversation-dir",
    default="./simulation_conversations",
    help="Directory for simulation conversations",
)
@click.option(
    "--evaluation-dir",
    default="./simulation_evaluations",
    help="Directory for simulation evaluations",
)
@click.option(
    "--results-dir",
    default="./simulation_results",
    help="Directory for simulation results",
)
@click.option(
    "--learning-dir",
    default="./learning_knowledge",
    help="Directory for learning knowledge base",
)
@click.option(
    "--enable-learning/--disable-learning",
    default=True,
    help="Enable/disable learning from evaluations",
)
def simulate(
    cycles,
    delay,
    scenario_type,
    conversation_dir,
    evaluation_dir,
    results_dir,
    learning_dir,
    enable_learning,
):
    """Run automated design simulation and evaluation cycles."""
    console.print(Panel.fit("🔬 Design Assistant Simulator", style="bold cyan"))

    simulator = DesignSimulator(
        conversation_dir, evaluation_dir, results_dir, learning_dir, enable_learning
    )

    async def run_simulation():
        return await simulator.run_simulation_loop(
            max_cycles=cycles, delay_seconds=delay, scenario_type=scenario_type
        )

    try:
        results = asyncio.run(run_simulation())
        console.print(f"✅ Simulation completed with {len(results)} cycles")
        console.print(f"📁 Results saved to: {results_dir}")
    except KeyboardInterrupt:
        console.print("\n❌ Simulation interrupted by user")
    except Exception as e:
        console.print(f"❌ Error: {e}")


@cli.command()
@click.option(
    "--knowledge-dir",
    default="./learning_knowledge",
    help="Directory containing learning knowledge base",
)
@click.option(
    "--evaluation-dir",
    default="./simulation_evaluations",
    help="Directory containing evaluation files to learn from",
)
def learn(knowledge_dir, evaluation_dir):
    """Manually trigger learning from existing evaluation files."""
    console.print(Panel.fit("🧠 Learning System", style="bold magenta"))

    learning_system = LearningSystem(knowledge_dir, evaluation_dir)

    async def run_learning():
        await learning_system.learn_from_evaluations()
        stats = learning_system.get_knowledge_stats()

        console.print("📊 Learning completed!")
        console.print(f"   Total rules: {stats.get('total_rules', 0)}")
        console.print(
            f"   High confidence rules: {stats.get('confidence_distribution', {}).get('high', 0)}"
        )
        console.print(f"   Average confidence: {stats.get('avg_confidence', 0):.2f}")

        if stats.get("rule_types"):
            console.print("   Rule types:")
            for rule_type, count in stats["rule_types"].items():
                console.print(f"     - {rule_type}: {count}")

    try:
        asyncio.run(run_learning())
    except KeyboardInterrupt:
        console.print("\n❌ Learning interrupted by user")
    except Exception as e:
        console.print(f"❌ Error: {e}")


@cli.command()
@click.option(
    "--knowledge-dir",
    default="./learning_knowledge",
    help="Directory containing learning knowledge base",
)
def knowledge_stats(knowledge_dir):
    """Show learning system knowledge base statistics."""
    console.print(Panel.fit("📚 Knowledge Base Statistics", style="bold blue"))

    learning_system = LearningSystem(knowledge_dir)
    stats = learning_system.get_knowledge_stats()

    if stats.get("total_rules", 0) == 0:
        console.print("❌ No learning rules found. Run some simulations first!")
        return

    console.print(f"📊 Total learning rules: {stats['total_rules']}")
    console.print(f"📈 Average confidence: {stats.get('avg_confidence', 0):.2f}")

    console.print("\n🎯 Confidence distribution:")
    confidence = stats.get("confidence_distribution", {})
    console.print(f"   • High (≥0.8): {confidence.get('high', 0)}")
    console.print(f"   • Medium (0.6-0.8): {confidence.get('medium', 0)}")
    console.print(f"   • Low (<0.6): {confidence.get('low', 0)}")

    if stats.get("rule_types"):
        console.print("\n📋 Rule types:")
        for rule_type, count in stats["rule_types"].items():
            console.print(f"   • {rule_type}: {count}")


if __name__ == "__main__":
    cli()
