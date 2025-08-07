#!/usr/bin/env python3
"""
Example of the Learning System in action.

This demonstrates how the learning system extracts patterns from evaluations
and improves the design assistant over time.
"""

import asyncio
import json
from pathlib import Path

from claude_code_designer.learning_system import LearningSystem, LearningRule
from claude_code_designer.design_assistant import DesignAssistant
from claude_code_designer.simulator import DesignSimulator


async def demo_learning_system():
    """Demonstrate the complete learning system workflow."""
    print("🧠 Learning System Demonstration")
    print("=" * 50)
    
    # Setup directories
    learning_dir = "./demo_learning_knowledge"
    conversations_dir = "./demo_conversations"
    evaluations_dir = "./demo_evaluations"
    
    # Clean up any existing demo files
    import shutil
    for dir_path in [learning_dir, conversations_dir, evaluations_dir]:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
    
    # Initialize learning system
    learning_system = LearningSystem(learning_dir, evaluations_dir)
    
    print("1️⃣ Creating sample learning rules...")
    
    # Create some sample learning rules manually (normally these would be extracted from evaluations)
    sample_rules = [
        LearningRule(
            rule_id="architecture_focus_001",
            rule_type="prompt_addition",
            condition="project_type == 'web'",
            action="Always discuss scalability concerns and microservices vs monolith trade-offs for web applications",
            confidence=0.9,
            examples=["E-commerce Platform", "Analytics Dashboard"]
        ),
        LearningRule(
            rule_id="security_emphasis_001", 
            rule_type="behavior_change",
            condition="scenario_type == 'feature'",
            action="Include security considerations and authentication patterns when designing new features",
            confidence=0.85,
            examples=["OAuth authentication", "File upload system"]
        ),
        LearningRule(
            rule_id="testing_strategy_001",
            rule_type="prompt_addition", 
            condition="project_type == 'api'",
            action="Provide detailed testing strategies including unit tests, integration tests, and API contract testing",
            confidence=0.8,
            examples=["Real-time Chat API", "Document Processing Service"]
        )
    ]
    
    # Add rules to knowledge base
    learning_system.knowledge_base.add_rules(sample_rules)
    
    stats = learning_system.get_knowledge_stats()
    print(f"   📚 Added {stats['total_rules']} learning rules to knowledge base")
    print(f"   📈 Average confidence: {stats['avg_confidence']:.2f}")
    
    print("\n2️⃣ Testing design assistant without learning...")
    
    # Create design assistant without learning
    basic_assistant = DesignAssistant(conversations_dir, enable_learning=False)
    
    # Test basic prompt
    basic_prompt = basic_assistant._optimize_prompt_for_subagent(
        "I want to build a web application for task management",
        "app-designer",
        "app",
        "web"
    )
    
    print("   Basic prompt length:", len(basic_prompt))
    print("   Contains 'scalability':", "scalability" in basic_prompt.lower())
    
    print("\n3️⃣ Testing design assistant with learning enabled...")
    
    # Create design assistant with learning
    learning_assistant = DesignAssistant(
        conversations_dir, 
        enable_learning=True, 
        learning_knowledge_dir=learning_dir
    )
    
    # Test enhanced prompt
    enhanced_prompt = learning_assistant._optimize_prompt_for_subagent(
        "I want to build a web application for task management",
        "app-designer", 
        "app",
        "web"
    )
    
    print("   Enhanced prompt length:", len(enhanced_prompt))
    print("   Contains 'scalability':", "scalability" in enhanced_prompt.lower())
    print("   Contains learned improvements:", "LEARNED IMPROVEMENTS" in enhanced_prompt)
    
    print("\n4️⃣ Showing applicable rules for different scenarios...")
    
    # Test rule application for different scenarios
    scenarios = [
        ("app", "web", "Web Application"),
        ("feature", "api", "API Feature"),
        ("app", "cli", "CLI Tool")
    ]
    
    for scenario_type, project_type, description in scenarios:
        applicable_rules = learning_system.knowledge_base.get_applicable_rules(
            scenario_type, project_type
        )
        print(f"   {description} ({scenario_type}/{project_type}): {len(applicable_rules)} applicable rules")
        
        for rule in applicable_rules[:2]:  # Show first 2 rules
            print(f"     - {rule.action[:60]}... (confidence: {rule.confidence})")
    
    print("\n5️⃣ Knowledge base statistics...")
    
    stats = learning_system.get_knowledge_stats()
    print(f"   📊 Total rules: {stats['total_rules']}")
    print(f"   📈 Average confidence: {stats['avg_confidence']:.2f}")
    print(f"   🎯 High confidence rules: {stats['confidence_distribution']['high']}")
    print(f"   📋 Rule types: {dict(stats['rule_types'])}")
    
    print("\n✅ Learning system demonstration completed!")
    
    # Cleanup
    print("\n🧹 Cleaning up demo files...")
    for dir_path in [learning_dir, conversations_dir, evaluations_dir]:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)


async def demo_rule_extraction():
    """Demonstrate how learning rules are extracted from evaluations."""
    print("\n🔍 Rule Extraction Demonstration")
    print("=" * 50)
    
    from claude_code_designer.learning_system import LearningRuleExtractor
    
    # Create sample evaluation data (this would normally come from real evaluations)
    sample_evaluations = [
        {
            "success": True,
            "scenario": {
                "type": "app",
                "name": "E-commerce Platform"
            },
            "scores": {
                "architecture_quality": 0.6,  # Low score - should trigger architecture rule
                "implementation_detail": 0.8
            },
            "evaluation_messages": [
                {
                    "content": "The design lacks architectural guidance and needs more detail on technology choices. Best practices for security were not mentioned."
                }
            ]
        },
        {
            "success": True,
            "scenario": {
                "type": "feature", 
                "name": "OAuth Authentication"
            },
            "scores": {
                "architecture_quality": 0.9,
                "implementation_detail": 0.5  # Low score - should trigger detail rule
            },
            "evaluation_messages": [
                {
                    "content": "Good architectural thinking but the implementation is too vague and needs more specific guidance."
                }
            ]
        }
    ]
    
    extractor = LearningRuleExtractor()
    rules = await extractor.extract_rules_from_evaluations(sample_evaluations)
    
    print(f"   📝 Extracted {len(rules)} learning rules from sample evaluations:")
    
    for i, rule in enumerate(rules, 1):
        print(f"   {i}. {rule.rule_type}: {rule.action[:60]}...")
        print(f"      Condition: {rule.condition}")
        print(f"      Confidence: {rule.confidence}")
        print()
    
    print("✅ Rule extraction demonstration completed!")


if __name__ == "__main__":
    print("🚀 Claude Code Designer Learning System Examples")
    print("=" * 60)
    
    # Run demonstrations
    asyncio.run(demo_learning_system())
    asyncio.run(demo_rule_extraction())
    
    print("\n🎉 All learning system demonstrations completed!")
    print("💡 Try running: uv run python -m claude_code_designer.cli simulate --cycles 3 --enable-learning")