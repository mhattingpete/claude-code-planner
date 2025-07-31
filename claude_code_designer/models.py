"""Pydantic data models for Claude Code Designer."""

from typing import Any

from pydantic import BaseModel, Field


class Question(BaseModel):
    """Model representing a single question in the questionnaire."""

    id: str = Field(..., description="Unique identifier for the question")
    text: str = Field(..., description="The question text to display")
    type: str = Field(..., description="Type of question (multiple_choice, text, etc.)")
    options: list[str] | None = Field(
        None, description="Available options for multiple choice questions"
    )
    required: bool = Field(True, description="Whether this question is required")
    follow_up: dict[str, str] | None = Field(
        None, description="Follow-up questions based on answers"
    )


class AppDesign(BaseModel):
    """Model capturing all application design information."""

    name: str = Field(..., description="Application name")
    type: str = Field(..., description="Type of application (web, cli, api, mobile)")
    description: str = Field(..., description="Brief description of the application")
    primary_features: list[str] = Field(
        default_factory=list, description="List of primary features"
    )
    tech_stack: list[str] = Field(
        default_factory=list, description="Technology stack preferences"
    )
    target_audience: str | None = Field(None, description="Primary target audience")
    goals: list[str] = Field(
        default_factory=list, description="Primary goals and objectives"
    )
    constraints: list[str] = Field(
        default_factory=list, description="Technical or business constraints"
    )
    additional_info: dict[str, Any] = Field(
        default_factory=dict, description="Additional design information"
    )


class DocumentRequest(BaseModel):
    """Model for document generation configuration."""

    output_dir: str = Field(
        ..., description="Directory where documents should be generated"
    )
    generate_prd: bool = Field(True, description="Whether to generate PRD.md")
    generate_claude_md: bool = Field(True, description="Whether to generate CLAUDE.md")
    generate_readme: bool = Field(True, description="Whether to generate README.md")
    app_design: AppDesign = Field(
        ..., description="Application design data to use for generation"
    )
    custom_templates: dict[str, str] | None = Field(
        None, description="Custom templates for documents"
    )
