#!/usr/bin/env python3
"""
Learning System for Design Assistant

Analyzes evaluation results to extract patterns and automatically improve
the design assistant through iterative learning and prompt optimization.
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from .conversation_evaluator import ConversationEvaluator


class LearningRule:
    """Represents a learned rule or pattern for improving design quality."""
    
    def __init__(
        self,
        rule_id: str,
        rule_type: str,
        condition: str,
        action: str,
        confidence: float,
        examples: list[str],
        created_at: str | None = None
    ):
        self.rule_id = rule_id
        self.rule_type = rule_type  # "prompt_addition", "behavior_change", "question_pattern"
        self.condition = condition  # When to apply this rule
        self.action = action       # What to do
        self.confidence = confidence  # How confident we are (0.0 to 1.0)
        self.examples = examples   # Example scenarios where this rule applies
        self.created_at = created_at or datetime.now().isoformat()
        self.usage_count = 0
        self.success_rate = 0.0
    
    def to_dict(self) -> dict[str, Any]:
        """Convert rule to dictionary for serialization."""
        return {
            "rule_id": self.rule_id,
            "rule_type": self.rule_type,
            "condition": self.condition,
            "action": self.action,
            "confidence": self.confidence,
            "examples": self.examples,
            "created_at": self.created_at,
            "usage_count": self.usage_count,
            "success_rate": self.success_rate
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearningRule":
        """Create rule from dictionary."""
        rule = cls(
            rule_id=data["rule_id"],
            rule_type=data["rule_type"],
            condition=data["condition"],
            action=data["action"],
            confidence=data["confidence"],
            examples=data.get("examples", []),
            created_at=data.get("created_at")
        )
        rule.usage_count = data.get("usage_count", 0)
        rule.success_rate = data.get("success_rate", 0.0)
        return rule


class LearningRuleExtractor:
    """Extracts learning rules from evaluation results and conversation patterns."""
    
    def __init__(self):
        # Pre-defined patterns for common issues and improvements
        self.issue_patterns = {
            "missing_architecture": [
                r"architecture.*not.*discussed",
                r"lack.*architectural.*guidance", 
                r"missing.*technology.*choices"
            ],
            "insufficient_detail": [
                r"too.*vague",
                r"needs.*more.*detail",
                r"lacks.*specific.*guidance"
            ],
            "missing_best_practices": [
                r"best.*practices.*not.*mentioned",
                r"security.*considerations.*missing",
                r"testing.*strategy.*absent"
            ],
            "poor_question_flow": [
                r"questions.*not.*relevant",
                r"follow.*up.*questions.*needed",
                r"clarification.*required"
            ]
        }
    
    async def extract_rules_from_evaluations(
        self,
        evaluations: list[dict[str, Any]]
    ) -> list[LearningRule]:
        """Extract learning rules from a batch of evaluations."""
        rules = []
        
        for evaluation in evaluations:
            if not evaluation.get("success", False):
                continue
            
            # Extract rules from conversation analysis
            conversation_rules = await self._extract_from_conversation(evaluation)
            rules.extend(conversation_rules)
            
            # Extract rules from evaluation feedback
            feedback_rules = await self._extract_from_feedback(evaluation)
            rules.extend(feedback_rules)
        
        # Consolidate and score rules
        consolidated_rules = self._consolidate_rules(rules)
        return consolidated_rules
    
    async def _extract_from_conversation(
        self, 
        evaluation: dict[str, Any]
    ) -> list[LearningRule]:
        """Extract rules from conversation content analysis."""
        rules = []
        
        # Analyze evaluation messages for patterns
        evaluation_text = ""
        if "evaluation_messages" in evaluation:
            for msg in evaluation["evaluation_messages"]:
                if isinstance(msg, dict) and "content" in msg:
                    evaluation_text += msg["content"] + " "
        
        # Check for common improvement patterns
        for issue_type, patterns in self.issue_patterns.items():
            for pattern in patterns:
                if re.search(pattern, evaluation_text, re.IGNORECASE):
                    rule = self._create_improvement_rule(issue_type, evaluation)
                    if rule:
                        rules.append(rule)
        
        return rules
    
    async def _extract_from_feedback(
        self,
        evaluation: dict[str, Any]
    ) -> list[LearningRule]:
        """Extract rules from evaluation feedback and scoring."""
        rules = []
        
        # Look for patterns in low-scoring areas
        if "scores" in evaluation:
            scores = evaluation["scores"]
            scenario = evaluation.get("scenario", {})
            
            # If architecture score is low, add architecture focus rule
            if scores.get("architecture_quality", 1.0) < 0.7:
                rule = LearningRule(
                    rule_id=f"arch_focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    rule_type="prompt_addition",
                    condition=f"project_type == '{scenario.get('type', 'any')}'",
                    action="Add emphasis on architectural decisions and technology stack rationale",
                    confidence=0.8,
                    examples=[scenario.get("name", "Unknown scenario")]
                )
                rules.append(rule)
            
            # If implementation detail is low, add detail focus rule  
            if scores.get("implementation_detail", 1.0) < 0.7:
                rule = LearningRule(
                    rule_id=f"detail_focus_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    rule_type="prompt_addition",
                    condition=f"scenario_type == '{scenario.get('type', 'any')}'",
                    action="Request more specific implementation examples and code structure details",
                    confidence=0.75,
                    examples=[scenario.get("name", "Unknown scenario")]
                )
                rules.append(rule)
        
        return rules
    
    def _create_improvement_rule(
        self,
        issue_type: str,
        evaluation: dict[str, Any]
    ) -> LearningRule | None:
        """Create a learning rule for a specific issue type."""
        scenario = evaluation.get("scenario", {})
        
        rule_templates = {
            "missing_architecture": {
                "action": "Always discuss architectural patterns, technology choices, and scalability considerations",
                "confidence": 0.9
            },
            "insufficient_detail": {
                "action": "Provide concrete examples, code snippets, and step-by-step implementation guidance",
                "confidence": 0.85
            },
            "missing_best_practices": {
                "action": "Include security best practices, testing strategies, and performance considerations",
                "confidence": 0.8
            },
            "poor_question_flow": {
                "action": "Ask more targeted follow-up questions based on user responses and project context",
                "confidence": 0.75
            }
        }
        
        template = rule_templates.get(issue_type)
        if not template:
            return None
        
        return LearningRule(
            rule_id=f"{issue_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            rule_type="behavior_change",
            condition=f"project_type == '{scenario.get('type', 'any')}'",
            action=template["action"],
            confidence=template["confidence"],
            examples=[scenario.get("name", "Unknown scenario")]
        )
    
    def _consolidate_rules(self, rules: list[LearningRule]) -> list[LearningRule]:
        """Consolidate similar rules and remove duplicates."""
        consolidated = {}
        
        for rule in rules:
            # Create a key based on rule type and condition
            key = f"{rule.rule_type}_{rule.condition}"
            
            if key in consolidated:
                # Merge similar rules
                existing = consolidated[key]
                existing.confidence = max(existing.confidence, rule.confidence)
                existing.examples.extend(rule.examples)
                existing.examples = list(set(existing.examples))  # Remove duplicates
            else:
                consolidated[key] = rule
        
        # Sort by confidence
        return sorted(consolidated.values(), key=lambda r: r.confidence, reverse=True)


class KnowledgeBase:
    """Stores and manages learned rules and patterns."""
    
    def __init__(self, knowledge_dir: str = "./learning_knowledge"):
        self.knowledge_dir = Path(knowledge_dir)
        self.knowledge_dir.mkdir(exist_ok=True)
        self.rules_file = self.knowledge_dir / "learning_rules.json"
        self.rules: list[LearningRule] = []
        self.load_rules()
    
    def load_rules(self):
        """Load existing rules from storage."""
        if self.rules_file.exists():
            try:
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.rules = [LearningRule.from_dict(rule_data) for rule_data in data.get("rules", [])]
            except Exception as e:
                print(f"Error loading rules: {e}")
                self.rules = []
    
    def save_rules(self):
        """Save rules to storage."""
        try:
            data = {
                "updated_at": datetime.now().isoformat(),
                "total_rules": len(self.rules),
                "rules": [rule.to_dict() for rule in self.rules]
            }
            
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving rules: {e}")
    
    def add_rules(self, new_rules: list[LearningRule]):
        """Add new rules to the knowledge base."""
        for new_rule in new_rules:
            # Check for duplicates
            existing = self.find_similar_rule(new_rule)
            if existing:
                # Update existing rule
                existing.confidence = max(existing.confidence, new_rule.confidence)
                existing.examples.extend(new_rule.examples)
                existing.examples = list(set(existing.examples))
            else:
                self.rules.append(new_rule)
        
        self.save_rules()
    
    def find_similar_rule(self, rule: LearningRule) -> LearningRule | None:
        """Find a similar existing rule."""
        for existing in self.rules:
            if (existing.rule_type == rule.rule_type and
                existing.condition == rule.condition and
                existing.action == rule.action):
                return existing
        return None
    
    def get_applicable_rules(
        self,
        scenario_type: str,
        project_type: str,
        min_confidence: float = 0.7
    ) -> list[LearningRule]:
        """Get rules applicable to a specific scenario."""
        applicable = []
        
        for rule in self.rules:
            if rule.confidence < min_confidence:
                continue
            
            # Simple condition matching (can be enhanced with more complex logic)
            if (f"scenario_type == '{scenario_type}'" in rule.condition or
                f"project_type == '{project_type}'" in rule.condition or
                rule.condition == "always"):
                applicable.append(rule)
        
        return sorted(applicable, key=lambda r: r.confidence, reverse=True)
    
    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics."""
        if not self.rules:
            return {"total_rules": 0}
        
        rule_types = {}
        confidence_levels = {"high": 0, "medium": 0, "low": 0}
        
        for rule in self.rules:
            rule_types[rule.rule_type] = rule_types.get(rule.rule_type, 0) + 1
            
            if rule.confidence >= 0.8:
                confidence_levels["high"] += 1
            elif rule.confidence >= 0.6:
                confidence_levels["medium"] += 1
            else:
                confidence_levels["low"] += 1
        
        return {
            "total_rules": len(self.rules),
            "rule_types": rule_types,
            "confidence_distribution": confidence_levels,
            "avg_confidence": sum(r.confidence for r in self.rules) / len(self.rules)
        }


class DesignAgentUpdater:
    """Updates the design agent's behavior based on learned rules."""
    
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def generate_enhanced_prompt(
        self,
        base_prompt: str,
        scenario_type: str,
        project_type: str
    ) -> str:
        """Generate an enhanced prompt with learned improvements."""
        applicable_rules = self.knowledge_base.get_applicable_rules(
            scenario_type, project_type
        )
        
        if not applicable_rules:
            return base_prompt
        
        # Build enhancement sections
        prompt_additions = []
        behavior_changes = []
        
        for rule in applicable_rules[:5]:  # Limit to top 5 rules
            if rule.rule_type == "prompt_addition":
                prompt_additions.append(f"- {rule.action}")
            elif rule.rule_type == "behavior_change":
                behavior_changes.append(f"- {rule.action}")
        
        enhanced_prompt = base_prompt
        
        if prompt_additions:
            enhanced_prompt += f"""

LEARNED IMPROVEMENTS (apply these based on previous feedback):
{chr(10).join(prompt_additions)}"""
        
        if behavior_changes:
            enhanced_prompt += f"""

BEHAVIOR GUIDELINES (learned from past evaluations):
{chr(10).join(behavior_changes)}"""
        
        return enhanced_prompt
    
    def get_dynamic_instructions(
        self,
        scenario_type: str,
        project_type: str
    ) -> list[str]:
        """Get dynamic instructions based on learned rules."""
        applicable_rules = self.knowledge_base.get_applicable_rules(
            scenario_type, project_type
        )
        
        instructions = []
        for rule in applicable_rules:
            if rule.confidence >= 0.8:
                instructions.append(rule.action)
        
        return instructions


class LearningSystem:
    """Main learning system coordinator."""
    
    def __init__(
        self,
        knowledge_dir: str = "./learning_knowledge",
        evaluation_dir: str = "./simulation_evaluations"
    ):
        self.knowledge_base = KnowledgeBase(knowledge_dir)
        self.rule_extractor = LearningRuleExtractor()
        self.agent_updater = DesignAgentUpdater(self.knowledge_base)
        self.evaluation_dir = Path(evaluation_dir)
    
    async def learn_from_evaluations(self, evaluation_files: list[Path] | None = None):
        """Learn from evaluation results and update the knowledge base."""
        if evaluation_files is None:
            # Load all evaluation files
            evaluation_files = list(self.evaluation_dir.glob("*.json"))
        
        if not evaluation_files:
            print("No evaluation files found for learning")
            return
        
        print(f"Learning from {len(evaluation_files)} evaluation files...")
        
        # Load evaluations
        evaluations = []
        for file in evaluation_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    evaluation = json.load(f)
                    evaluations.append(evaluation)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        if not evaluations:
            print("No valid evaluations loaded")
            return
        
        # Extract learning rules
        new_rules = await self.rule_extractor.extract_rules_from_evaluations(evaluations)
        
        if new_rules:
            print(f"Extracted {len(new_rules)} learning rules")
            self.knowledge_base.add_rules(new_rules)
            
            # Print rule summary
            for rule in new_rules[:3]:  # Show top 3 rules
                print(f"  - {rule.rule_type}: {rule.action[:60]}...")
        else:
            print("No new learning rules extracted")
    
    def get_enhanced_prompt(
        self,
        base_prompt: str,
        scenario_type: str,
        project_type: str
    ) -> str:
        """Get an enhanced prompt with learned improvements."""
        return self.agent_updater.generate_enhanced_prompt(
            base_prompt, scenario_type, project_type
        )
    
    def get_knowledge_stats(self) -> dict[str, Any]:
        """Get learning system statistics."""
        return self.knowledge_base.get_stats()