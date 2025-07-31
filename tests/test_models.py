"""Tests for Pydantic data models."""

import pytest
from pydantic import ValidationError

from claude_code_designer.models import AppDesign, DocumentRequest, Question


class TestQuestion:
    """Test cases for the Question model."""

    def test_question_valid_data(self):
        """Test Question creation with valid data."""
        question = Question(
            id="test_id",
            text="What is your preference?",
            type="multiple_choice",
            options=["Option 1", "Option 2"],
            required=True,
        )

        assert question.id == "test_id"
        assert question.text == "What is your preference?"
        assert question.type == "multiple_choice"
        assert question.options == ["Option 1", "Option 2"]
        assert question.required is True
        assert question.follow_up is None

    def test_question_minimal_required_fields(self):
        """Test Question creation with only required fields."""
        question = Question(
            id="minimal",
            text="Simple question?",
            type="text",
        )

        assert question.id == "minimal"
        assert question.text == "Simple question?"
        assert question.type == "text"
        assert question.options is None
        assert question.required is True  # Default value
        assert question.follow_up is None

    def test_question_with_follow_up(self):
        """Test Question creation with follow-up configuration."""
        follow_up_config = {"Yes": "follow_up_yes", "No": "follow_up_no"}
        question = Question(
            id="with_followup",
            text="Do you need follow-up?",
            type="multiple_choice",
            options=["Yes", "No"],
            follow_up=follow_up_config,
        )

        assert question.follow_up == follow_up_config

    def test_question_missing_required_fields(self):
        """Test Question validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            Question()

        error = exc_info.value
        assert "id" in str(error)
        assert "text" in str(error)
        assert "type" in str(error)

    def test_question_invalid_required_type(self):
        """Test Question validation with invalid required field type."""
        with pytest.raises(ValidationError):
            Question(
                id="test",
                text="Test question",
                type="text",
                required="not_a_boolean",  # Should be boolean
            )


class TestAppDesign:
    """Test cases for the AppDesign model."""

    def test_app_design_valid_data(self):
        """Test AppDesign creation with valid data."""
        app_design = AppDesign(
            name="My App",
            type="web",
            description="A web application",
            primary_features=["Authentication", "User Management"],
            tech_stack=["Python", "FastAPI"],
            target_audience="Developers",
            goals=["Build MVP", "Scale to 1000 users"],
            constraints=["Budget: $5000", "Timeline: 3 months"],
            additional_info={"custom_field": "custom_value"},
        )

        assert app_design.name == "My App"
        assert app_design.type == "web"
        assert app_design.description == "A web application"
        assert app_design.primary_features == ["Authentication", "User Management"]
        assert app_design.tech_stack == ["Python", "FastAPI"]
        assert app_design.target_audience == "Developers"
        assert app_design.goals == ["Build MVP", "Scale to 1000 users"]
        assert app_design.constraints == ["Budget: $5000", "Timeline: 3 months"]
        assert app_design.additional_info == {"custom_field": "custom_value"}

    def test_app_design_minimal_required_fields(self):
        """Test AppDesign creation with only required fields."""
        app_design = AppDesign(
            name="Minimal App",
            type="cli",
            description="A CLI tool",
        )

        assert app_design.name == "Minimal App"
        assert app_design.type == "cli"
        assert app_design.description == "A CLI tool"
        assert app_design.primary_features == []  # Default factory
        assert app_design.tech_stack == []  # Default factory
        assert app_design.target_audience is None
        assert app_design.goals == []  # Default factory
        assert app_design.constraints == []  # Default factory
        assert app_design.additional_info == {}  # Default factory

    def test_app_design_missing_required_fields(self):
        """Test AppDesign validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            AppDesign()

        error = exc_info.value
        assert "name" in str(error)
        assert "type" in str(error)
        assert "description" in str(error)

    def test_app_design_default_factories(self):
        """Test that default factories create independent instances."""
        app1 = AppDesign(name="App1", type="web", description="First app")
        app2 = AppDesign(name="App2", type="api", description="Second app")

        app1.primary_features.append("Feature 1")
        app1.additional_info["key"] = "value"

        # app2 should not be affected by changes to app1
        assert app2.primary_features == []
        assert app2.additional_info == {}


class TestDocumentRequest:
    """Test cases for the DocumentRequest model."""

    def test_document_request_valid_data(self):
        """Test DocumentRequest creation with valid data."""
        app_design = AppDesign(
            name="Test App",
            type="web",
            description="Test application",
        )

        doc_request = DocumentRequest(
            output_dir="/path/to/output",
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=True,
            app_design=app_design,
            custom_templates={"prd": "custom_prd_template"},
        )

        assert doc_request.output_dir == "/path/to/output"
        assert doc_request.generate_prd is True
        assert doc_request.generate_claude_md is False
        assert doc_request.generate_readme is True
        assert doc_request.app_design == app_design
        assert doc_request.custom_templates == {"prd": "custom_prd_template"}

    def test_document_request_default_values(self):
        """Test DocumentRequest creation with default values."""
        app_design = AppDesign(
            name="Test App",
            type="web",
            description="Test application",
        )

        doc_request = DocumentRequest(
            output_dir="/path/to/output",
            app_design=app_design,
        )

        assert doc_request.generate_prd is True  # Default
        assert doc_request.generate_claude_md is True  # Default
        assert doc_request.generate_readme is True  # Default
        assert doc_request.custom_templates is None

    def test_document_request_missing_required_fields(self):
        """Test DocumentRequest validation with missing required fields."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentRequest()

        error = exc_info.value
        assert "output_dir" in str(error)
        assert "app_design" in str(error)

    def test_document_request_nested_app_design_validation(self):
        """Test that DocumentRequest validates nested AppDesign."""
        with pytest.raises(ValidationError) as exc_info:
            DocumentRequest(
                output_dir="/path/to/output",
                app_design={"invalid": "data"},  # Should be AppDesign instance
            )

        error = exc_info.value
        assert "app_design" in str(error)

    def test_document_request_invalid_boolean_fields(self):
        """Test DocumentRequest validation with invalid boolean fields."""
        app_design = AppDesign(
            name="Test App",
            type="web",
            description="Test application",
        )

        with pytest.raises(ValidationError):
            DocumentRequest(
                output_dir="/path/to/output",
                app_design=app_design,
                generate_prd="not_a_boolean",  # Should be boolean
            )
