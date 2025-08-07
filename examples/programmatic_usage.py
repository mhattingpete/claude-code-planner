#!/usr/bin/env python3
"""
Example of using the Design Assistant programmatically from other Python scripts.
"""

import asyncio

from claude_code_designer import DesignAssistant


async def design_example_app():
    """Example: Design a new web application programmatically."""
    assistant = DesignAssistant("./example_conversations")

    # Design a new application
    conversation = await assistant.design_application(
        project_name="TaskTracker Pro",
        project_type="web",
        interactive=False,  # Non-interactive mode
        max_turns=10
    )

    print(f"Application design completed with {conversation['output']['message_count']} messages")
    return conversation


async def design_example_feature():
    """Example: Design a new feature programmatically."""
    assistant = DesignAssistant("./example_conversations")

    # Design a new feature
    conversation = await assistant.design_feature(
        feature_description="User authentication with OAuth providers",
        project_context="Existing React web application with Node.js backend",
        interactive=False,  # Non-interactive mode
        max_turns=8
    )

    print(f"Feature design completed with {conversation['output']['message_count']} messages")
    return conversation


async def custom_design_session():
    """Example: Custom design session with specific project description."""
    assistant = DesignAssistant("./example_conversations")

    # Instead of system prompt, use project description to guide the app-designer subagent
    project_description = """E-commerce platform focused on scalability and cloud-native architecture.
    Requirements:
    - Microservices architecture
    - Container orchestration capabilities
    - Event-driven architecture patterns
    - Comprehensive observability and monitoring
    - Enterprise-grade security best practices"""

    conversation = await assistant.design_application(
        project_name="E-commerce Platform",
        project_type="api",
        project_description=project_description,
        interactive=False,
        max_turns=12
    )

    print(f"Custom design session completed with {conversation['output']['message_count']} messages")
    return conversation


if __name__ == "__main__":
    # Run examples
    print("🚀 Starting application design example...")
    asyncio.run(design_example_app())

    print("\n⚡ Starting feature design example...")
    asyncio.run(design_example_feature())

    print("\n🎯 Starting custom design session example...")
    asyncio.run(custom_design_session())
