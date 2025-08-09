#!/usr/bin/env python3
"""
Design Assistant Simulator

Automatically generates test scenarios and runs design sessions to test and improve
the design assistant through continuous evaluation and feedback loops.
"""

import asyncio
import json
import random
from datetime import datetime
from pathlib import Path
from typing import Any

from .conversation_evaluator import ConversationEvaluator
from .design_assistant import DesignAssistant
from .learning_system import LearningSystem


class TestScenario:
    """Represents a test scenario for the design assistant."""

    def __init__(
        self,
        scenario_type: str,
        name: str,
        description: str,
        parameters: dict[str, Any],
    ):
        self.scenario_type = scenario_type  # "app" or "feature"
        self.name = name
        self.description = description
        self.parameters = parameters
        self.timestamp = datetime.now().isoformat()


class ScenarioGenerator:
    """Generates realistic test scenarios for design assistant testing."""

    APP_SCENARIOS = [
        {
            "name": "E-commerce Platform",
            "type": "web",
            "description": "Build a scalable e-commerce platform with user management, product catalog, shopping cart, and payment processing",
        },
        {
            "name": "Task Management CLI",
            "type": "cli",
            "description": "Command-line task management tool with projects, tags, due dates, and reporting",
        },
        {
            "name": "Real-time Chat API",
            "type": "api",
            "description": "RESTful API with WebSocket support for real-time messaging, user authentication, and room management",
        },
        {
            "name": "Mobile Fitness Tracker",
            "type": "mobile",
            "description": "Cross-platform mobile app for tracking workouts, nutrition, and health metrics with social features",
        },
        {
            "name": "Document Processing Service",
            "type": "api",
            "description": "Microservice for processing documents with OCR, text extraction, and format conversion capabilities",
        },
        {
            "name": "Desktop Media Player",
            "type": "desktop",
            "description": "Multi-platform desktop application for playing and organizing music and video files with playlist support",
        },
        {
            "name": "Analytics Dashboard",
            "type": "web",
            "description": "Business intelligence dashboard with data visualization, real-time metrics, and customizable reports",
        },
        {
            "name": "DevOps Automation Library",
            "type": "library",
            "description": "Python library for automating deployment pipelines, infrastructure provisioning, and monitoring",
        },
    ]

    FEATURE_SCENARIOS = [
        {
            "description": "OAuth authentication with Google, GitHub, and Microsoft providers",
            "context": "Existing React web application with Node.js backend using JWT tokens",
        },
        {
            "description": "Real-time notifications system with email, SMS, and push notifications",
            "context": "E-commerce platform built with Django and PostgreSQL",
        },
        {
            "description": "Advanced search with filters, sorting, and autocomplete",
            "context": "Product catalog application using Elasticsearch and Vue.js frontend",
        },
        {
            "description": "File upload and processing with virus scanning and thumbnail generation",
            "context": "Document management system built with FastAPI and MongoDB",
        },
        {
            "description": "Multi-tenant architecture with data isolation and role-based access",
            "context": "SaaS application currently using single-tenant PostgreSQL database",
        },
        {
            "description": "Caching layer with Redis for improved performance",
            "context": "High-traffic API built with Express.js and MySQL experiencing slow response times",
        },
        {
            "description": "Automated testing pipeline with unit, integration, and E2E tests",
            "context": "React Native mobile app with minimal test coverage",
        },
        {
            "description": "Data export functionality supporting CSV, JSON, and PDF formats",
            "context": "Analytics dashboard with large datasets and complex reporting needs",
        },
    ]

    def generate_app_scenario(self) -> TestScenario:
        """Generate a random application design scenario."""
        scenario_data = random.choice(self.APP_SCENARIOS)
        return TestScenario(
            scenario_type="app",
            name=scenario_data["name"],
            description=scenario_data["description"],
            parameters={
                "project_name": scenario_data["name"],
                "project_type": scenario_data["type"],
                "project_description": scenario_data["description"],
                "interactive": False,
                "max_turns": random.randint(8, 15),
            },
        )

    def generate_feature_scenario(self) -> TestScenario:
        """Generate a random feature design scenario."""
        scenario_data = random.choice(self.FEATURE_SCENARIOS)
        return TestScenario(
            scenario_type="feature",
            name=f"Feature: {scenario_data['description'][:50]}...",
            description=scenario_data["description"],
            parameters={
                "feature_description": scenario_data["description"],
                "project_context": scenario_data["context"],
                "interactive": False,
                "max_turns": random.randint(6, 12),
            },
        )

    def generate_random_scenario(self) -> TestScenario:
        """Generate a random scenario (app or feature)."""
        if random.choice([True, False]):
            return self.generate_app_scenario()
        else:
            return self.generate_feature_scenario()


class DesignSimulator:
    """Main simulator class that orchestrates the test-design-evaluate loop."""

    def __init__(
        self,
        conversation_dir: str = "./simulation_conversations",
        evaluation_dir: str = "./simulation_evaluations",
        results_dir: str = "./simulation_results",
        learning_knowledge_dir: str = "./learning_knowledge",
        enable_learning: bool = True,
    ):
        self.conversation_dir = Path(conversation_dir)
        self.evaluation_dir = Path(evaluation_dir)
        self.results_dir = Path(results_dir)
        self.learning_knowledge_dir = Path(learning_knowledge_dir)
        self.enable_learning = enable_learning

        # Create directories
        self.conversation_dir.mkdir(exist_ok=True)
        self.evaluation_dir.mkdir(exist_ok=True)
        self.results_dir.mkdir(exist_ok=True)
        self.learning_knowledge_dir.mkdir(exist_ok=True)

        # Initialize components
        self.design_assistant = DesignAssistant(
            str(self.conversation_dir),
            enable_learning=enable_learning,
            learning_knowledge_dir=str(self.learning_knowledge_dir),
        )
        self.evaluator = ConversationEvaluator(
            str(self.conversation_dir), str(self.evaluation_dir)
        )
        self.scenario_generator = ScenarioGenerator()

        if enable_learning:
            self.learning_system = LearningSystem(
                str(self.learning_knowledge_dir), str(self.evaluation_dir)
            )
        else:
            self.learning_system = None

    async def run_single_cycle(
        self, scenario: TestScenario | None = None
    ) -> dict[str, Any]:
        """Run a single test-design-evaluate cycle."""
        if scenario is None:
            scenario = self.scenario_generator.generate_random_scenario()

        print(f"🎯 Running simulation cycle: {scenario.name}")
        print(f"   Type: {scenario.scenario_type}")
        print(f"   Description: {scenario.description}")

        cycle_results = {
            "scenario": {
                "type": scenario.scenario_type,
                "name": scenario.name,
                "description": scenario.description,
                "parameters": scenario.parameters,
                "timestamp": scenario.timestamp,
            },
            "design_session": None,
            "evaluation": None,
            "success": False,
            "error": None,
        }

        try:
            # Step 1: Run design session
            print("  📝 Running design session...")
            if scenario.scenario_type == "app":
                design_result = await self.design_assistant.design_application(
                    **scenario.parameters
                )
            else:
                design_result = await self.design_assistant.design_feature(
                    **scenario.parameters
                )

            cycle_results["design_session"] = design_result

            # Step 2: Evaluate the conversation
            print("  📊 Evaluating conversation...")
            conversation_file = Path(design_result["file_path"])
            if conversation_file.exists():
                evaluation_result = await self.evaluator.evaluate_conversation(
                    conversation_file
                )
                cycle_results["evaluation"] = evaluation_result

                # Step 3: Learn from the evaluation (if learning is enabled)
                if self.enable_learning and self.learning_system:
                    print("  🧠 Learning from evaluation...")
                    # Get the corresponding evaluation file
                    eval_file = Path(
                        str(conversation_file)
                        .replace("conversations", "evaluations")
                        .replace(".json", "_evaluation.json")
                    )
                    if eval_file.exists():
                        await self.learning_system.learn_from_evaluations([eval_file])

                        # Show learning stats
                        stats = self.learning_system.get_knowledge_stats()
                        print(
                            f"    📚 Knowledge base now has {stats.get('total_rules', 0)} rules"
                        )

            cycle_results["success"] = True
            print("  ✅ Cycle completed successfully")

        except Exception as e:
            cycle_results["error"] = str(e)
            print(f"  ❌ Cycle failed: {e}")

        return cycle_results

    async def run_simulation_loop(
        self,
        max_cycles: int = 10,
        delay_seconds: float = 5.0,
        scenario_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Run multiple simulation cycles in a loop."""
        print(f"🚀 Starting simulation loop with {max_cycles} cycles")
        print(f"   Conversation dir: {self.conversation_dir}")
        print(f"   Evaluation dir: {self.evaluation_dir}")
        print(f"   Results dir: {self.results_dir}")
        print()

        all_results = []

        for cycle_num in range(1, max_cycles + 1):
            print(f"🔄 Cycle {cycle_num}/{max_cycles}")

            # Generate scenario based on type preference
            if scenario_type == "app":
                scenario = self.scenario_generator.generate_app_scenario()
            elif scenario_type == "feature":
                scenario = self.scenario_generator.generate_feature_scenario()
            else:
                scenario = self.scenario_generator.generate_random_scenario()

            # Run the cycle
            cycle_result = await self.run_single_cycle(scenario)
            cycle_result["cycle_number"] = cycle_num
            all_results.append(cycle_result)

            # Save intermediate results
            await self._save_simulation_results(
                all_results,
                f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            )

            # Wait before next cycle (except for last cycle)
            if cycle_num < max_cycles:
                print(f"  ⏱️  Waiting {delay_seconds}s before next cycle...\n")
                await asyncio.sleep(delay_seconds)
            else:
                print()

        print("🎉 Simulation loop completed!")
        self._print_simulation_summary(all_results)

        return all_results

    async def _save_simulation_results(
        self, results: list[dict[str, Any]], filename: str
    ):
        """Save simulation results to file."""
        results_file = self.results_dir / filename

        summary = {
            "simulation_metadata": {
                "total_cycles": len(results),
                "timestamp": datetime.now().isoformat(),
                "conversation_dir": str(self.conversation_dir),
                "evaluation_dir": str(self.evaluation_dir),
            },
            "cycles": results,
            "summary": self._generate_summary_stats(results),
        }

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

    def _generate_summary_stats(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate summary statistics from simulation results."""
        if not results:
            return {}

        successful_cycles = [r for r in results if r["success"]]
        failed_cycles = [r for r in results if not r["success"]]

        app_scenarios = [r for r in results if r["scenario"]["type"] == "app"]
        feature_scenarios = [r for r in results if r["scenario"]["type"] == "feature"]

        return {
            "total_cycles": len(results),
            "successful_cycles": len(successful_cycles),
            "failed_cycles": len(failed_cycles),
            "success_rate": len(successful_cycles) / len(results) if results else 0,
            "scenario_breakdown": {
                "app_scenarios": len(app_scenarios),
                "feature_scenarios": len(feature_scenarios),
            },
            "avg_design_messages": sum(
                r["design_session"]["output"]["message_count"]
                for r in successful_cycles
                if r["design_session"]
            )
            / len(successful_cycles)
            if successful_cycles
            else 0,
        }

    def _print_simulation_summary(self, results: list[dict[str, Any]]):
        """Print a summary of simulation results."""
        stats = self._generate_summary_stats(results)

        print("📊 Simulation Summary:")
        print(f"   Total cycles: {stats['total_cycles']}")
        print(f"   Successful: {stats['successful_cycles']}")
        print(f"   Failed: {stats['failed_cycles']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   App scenarios: {stats['scenario_breakdown']['app_scenarios']}")
        print(
            f"   Feature scenarios: {stats['scenario_breakdown']['feature_scenarios']}"
        )
        print(f"   Avg messages per design: {stats['avg_design_messages']:.1f}")
