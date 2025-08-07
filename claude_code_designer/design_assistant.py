#!/usr/bin/env python3
"""
Design Assistant Module

Contains the core design assistant functionality for applications and features.
Separated from CLI for better code organization and maintainability.
"""

from typing import Any

from rich.prompt import Prompt

from .learning_system import LearningSystem
from .save_claude_conversation import ConversationSaver


class DesignAssistant:
    """Core design assistant functionality that can be used programmatically."""

    def __init__(
        self, 
        conversation_dir: str = "./conversations",
        enable_learning: bool = True,
        learning_knowledge_dir: str = "./learning_knowledge"
    ):
        self.saver = ConversationSaver(conversation_dir)
        self.enable_learning = enable_learning
        
        if enable_learning:
            self.learning_system = LearningSystem(
                knowledge_dir=learning_knowledge_dir,
                evaluation_dir=conversation_dir.replace("conversations", "evaluations")
            )
        else:
            self.learning_system = None

    async def design_application(
        self,
        project_name: str | None = None,
        project_type: str | None = None,
        project_description: str | None = None,
        interactive: bool = True,
        max_turns: int = 15,
    ) -> dict[str, Any]:
        """
        Design a new application with Claude Code assistance.

        Args:
            project_name: Name of the project
            project_type: Type of application (web, cli, api, mobile, etc.)
            project_description: Description of the project
            interactive: Whether to run in interactive mode
            max_turns: Maximum conversation turns

        Returns:
            Dictionary containing conversation data
        """
        if interactive:
            project_name = project_name or Prompt.ask(
                "What's the name of your project?"
            )
            project_type = project_type or Prompt.ask(
                "What type of application are you building?",
                choices=["web", "cli", "api", "mobile", "desktop", "library", "other"],
                default="web",
            )

        design_prompt = self._build_design_prompt(
            project_name, project_type, project_description
        )

        return await self._run_design_with_subagent(
            prompt=design_prompt,
            subagent_type="app-designer",
            max_turns=max_turns,
            scenario_type="app",
            project_type=project_type or "web",
        )

    async def design_feature(
        self,
        feature_description: str | None = None,
        project_context: str | None = None,
        interactive: bool = True,
        max_turns: int = 10,
    ) -> dict[str, Any]:
        """
        Design a new feature with Claude Code assistance.

        Args:
            feature_description: Description of the feature to build
            project_context: Context about the existing project
            interactive: Whether to run in interactive mode
            max_turns: Maximum conversation turns

        Returns:
            Dictionary containing conversation data
        """
        if interactive:
            feature_description = feature_description or Prompt.ask(
                "Describe the feature you want to build"
            )
            project_context = project_context or Prompt.ask(
                "Provide context about your existing project (optional)", default=""
            )

        feature_prompt = self._build_feature_prompt(
            feature_description, project_context
        )

        return await self._run_design_with_subagent(
            prompt=feature_prompt,
            subagent_type="app-designer",
            max_turns=max_turns,
            scenario_type="feature",
            project_type="web",  # Could be inferred from context in the future
        )

    def _build_design_prompt(
        self,
        project_name: str | None,
        project_type: str | None,
        project_description: str | None,
    ) -> str:
        """Build the prompt for application design."""
        prompt_parts = [
            "I need help designing a new application.",
            f"Project name: {project_name or 'Not specified'}",
            f"Application type: {project_type or 'Not specified'}",
            f"Project description: {project_description or 'Not specified'}",
            "",
            "Please help me with:",
            "1. Architecture and technology choices",
            "2. Project structure and organization",
            "3. Key components and their responsibilities",
            "4. Development workflow and best practices",
            "5. Essential documentation (README, requirements, etc.)",
            "",
            "Please ask clarifying questions to better understand my needs and provide detailed guidance.",
        ]
        return "\n".join(prompt_parts)

    def _build_feature_prompt(
        self, feature_description: str | None, project_context: str | None
    ) -> str:
        """Build the prompt for feature design."""
        prompt_parts = [
            "I need help designing a new feature.",
            f"Feature description: {feature_description or 'Not specified'}",
        ]

        if project_context:
            prompt_parts.extend([f"Project context: {project_context}", ""])

        prompt_parts.extend(
            [
                "Please help me with:",
                "1. Feature architecture and design",
                "2. Implementation approach and code structure",
                "3. Integration with existing codebase",
                "4. Testing strategy",
                "5. Documentation updates needed",
                "",
                "Please analyze my codebase if needed and provide specific implementation guidance.",
            ]
        )

        return "\n".join(prompt_parts)

    async def _run_design_with_subagent(
        self,
        prompt: str,
        subagent_type: str,
        max_turns: int,
        scenario_type: str = "app",
        project_type: str = "web",
    ) -> dict[str, Any]:
        """Run design task using the specified subagent via Task tool."""
        print(f"Starting {subagent_type} design session...")
        
        # Show learning status
        if self.enable_learning and self.learning_system:
            stats = self.learning_system.get_knowledge_stats()
            if stats.get("total_rules", 0) > 0:
                print(f"  📚 Applying {stats['total_rules']} learned improvement rules")

        # Optimize the prompt for the specific subagent type
        optimized_prompt = self._optimize_prompt_for_subagent(
            prompt, subagent_type, scenario_type, project_type
        )

        return await self.saver.save_conversation(
            prompt=optimized_prompt,
            max_turns=max_turns,
        )

    def _optimize_prompt_for_subagent(
        self, 
        prompt: str, 
        subagent_type: str,
        scenario_type: str = "app",
        project_type: str = "web"
    ) -> str:
        """Optimize the prompt for the specific subagent type with learned improvements."""
        base_prompt = prompt
        
        if subagent_type == "app-designer":
            base_prompt = f"""I need comprehensive application design assistance. Use the {subagent_type} to create the design.

{prompt}

Please provide:
1. Complete architecture recommendations
2. Technology stack selection with rationale
3. Project structure and organization
4. Implementation guidance and best practices
5. Essential documentation (PRD.md, CLAUDE.md, README.md if applicable)

Follow KISS > SOLID > DRY principles and focus on maintainability over complexity.
Do not start implementing the feature yet."""
        
        # Apply learned improvements if learning is enabled
        if self.enable_learning and self.learning_system:
            enhanced_prompt = self.learning_system.get_enhanced_prompt(
                base_prompt, scenario_type, project_type
            )
            return enhanced_prompt
        
        return base_prompt
