"""Tests for interactive questionnaire system."""

import json
from unittest.mock import Mock, patch

import pytest

from claude_code_designer.models import AppDesign, Question
from claude_code_designer.questionnaire import InteractiveQuestionnaire


class TestInteractiveQuestionnaire:
    """Test cases for the InteractiveQuestionnaire class."""

    @pytest.fixture
    def questionnaire(self):
        """Create a questionnaire instance for testing."""
        return InteractiveQuestionnaire()

    @pytest.fixture
    def sample_questions_json(self):
        """Sample questions in JSON format for mocking Claude responses."""
        return json.dumps(
            [
                {
                    "id": "app_type",
                    "text": "What type of application?",
                    "type": "multiple_choice",
                    "options": ["Web Application", "CLI Tool", "API Service"],
                    "required": True,
                    "follow_up": None,
                },
                {
                    "id": "app_name",
                    "text": "What is your application name?",
                    "type": "text",
                    "options": None,
                    "required": True,
                    "follow_up": None,
                },
            ]
        )

    def test_init(self, questionnaire):
        """Test questionnaire initialization."""
        assert questionnaire.console is not None
        assert questionnaire.collected_data == {}

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_success(
        self, mock_query, questionnaire, sample_questions_json
    ):
        """Test successful question generation using Claude SDK."""

        # Mock Claude SDK response
        async def mock_query_response():
            mock_message = Mock()
            mock_message.content = sample_questions_json
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_questions()

        assert len(questions) == 2
        assert isinstance(questions[0], Question)
        assert questions[0].id == "app_type"
        assert questions[0].text == "What type of application?"
        assert questions[0].type == "multiple_choice"
        assert questions[0].options == ["Web Application", "CLI Tool", "API Service"]
        assert questions[1].id == "app_name"
        assert questions[1].type == "text"

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_json_decode_error(
        self, mock_query, questionnaire
    ):
        """Test fallback to default questions when JSON decode fails."""

        # Mock Claude SDK response with invalid JSON
        async def mock_query_response():
            mock_message = Mock()
            mock_message.content = "Invalid JSON response"
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_questions()

        # Should return default questions
        assert len(questions) == 4
        assert questions[0].id == "app_type"
        assert questions[1].id == "app_name"
        assert questions[2].id == "primary_purpose"
        assert questions[3].id == "target_audience"

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_connection_error(self, mock_query, questionnaire):
        """Test fallback to default questions when connection fails."""
        # Mock connection error
        mock_query.side_effect = ConnectionError("Network error")

        questions = await questionnaire._generate_questions()

        # Should return default questions
        assert len(questions) == 4
        assert questions[0].id == "app_type"

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_keyboard_interrupt(
        self, mock_query, questionnaire
    ):
        """Test keyboard interrupt handling during question generation."""
        # Mock keyboard interrupt
        mock_query.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            await questionnaire._generate_questions()

    def test_get_default_questions(self, questionnaire):
        """Test default questions generation."""
        questions = questionnaire._get_default_questions()

        assert len(questions) == 4
        assert questions[0].id == "app_type"
        assert questions[0].type == "multiple_choice"
        assert questions[0].options == [
            "Web Application",
            "CLI Tool",
            "API Service",
            "Mobile App",
        ]
        assert questions[1].id == "app_name"
        assert questions[1].type == "text"
        assert questions[2].id == "primary_purpose"
        assert questions[3].id == "target_audience"
        assert questions[3].required is False

    @patch("claude_code_designer.questionnaire.IntPrompt.ask")
    def test_handle_multiple_choice_valid_selection(self, mock_prompt, questionnaire):
        """Test handling multiple choice questions with valid selection."""
        question = Question(
            id="test",
            text="Choose option",
            type="multiple_choice",
            options=["Option 1", "Option 2", "Option 3"],
        )
        mock_prompt.return_value = 2

        result = questionnaire._handle_multiple_choice(question)

        assert result == "Option 2"
        mock_prompt.assert_called_once()

    @patch("claude_code_designer.questionnaire.IntPrompt.ask")
    def test_handle_multiple_choice_invalid_then_valid_selection(
        self, mock_prompt, questionnaire
    ):
        """Test handling multiple choice with invalid selection followed by valid one."""
        question = Question(
            id="test",
            text="Choose option",
            type="multiple_choice",
            options=["Option 1", "Option 2"],
        )
        # First invalid, then valid
        mock_prompt.side_effect = [5, 1]

        result = questionnaire._handle_multiple_choice(question)

        assert result == "Option 1"
        assert mock_prompt.call_count == 2

    def test_handle_multiple_choice_no_options(self, questionnaire):
        """Test handling multiple choice question without options."""
        question = Question(
            id="test", text="Choose option", type="multiple_choice", options=None
        )

        result = questionnaire._handle_multiple_choice(question)

        assert result == ""

    @patch("claude_code_designer.questionnaire.Prompt.ask")
    def test_handle_text_input_required(self, mock_prompt, questionnaire):
        """Test handling required text input."""
        question = Question(id="test", text="Enter text", type="text", required=True)
        mock_prompt.return_value = "User input"

        result = questionnaire._handle_text_input(question)

        assert result == "User input"
        mock_prompt.assert_called_once_with("Answer", default=None)

    @patch("claude_code_designer.questionnaire.Prompt.ask")
    def test_handle_text_input_optional(self, mock_prompt, questionnaire):
        """Test handling optional text input."""
        question = Question(id="test", text="Enter text", type="text", required=False)
        mock_prompt.return_value = "User input"

        result = questionnaire._handle_text_input(question)

        assert result == "User input"
        mock_prompt.assert_called_once_with("Answer", default="")

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_success(
        self, mock_query, questionnaire
    ):
        """Test successful follow-up question generation."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        follow_up_json = json.dumps(
            [
                {
                    "id": "follow_up_parent_1",
                    "text": "Follow-up question?",
                    "type": "text",
                    "options": None,
                    "required": False,
                    "follow_up": None,
                }
            ]
        )

        async def mock_query_response():
            mock_message = Mock()
            mock_message.content = follow_up_json
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "Yes"
        )

        assert len(questions) == 1
        assert questions[0].id == "follow_up_parent_1"
        assert questions[0].text == "Follow-up question?"

    async def test_generate_follow_up_questions_no_follow_up(self, questionnaire):
        """Test when parent question has no follow-up configuration."""
        parent_question = Question(
            id="parent", text="Parent question", type="text", follow_up=None
        )

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "any answer"
        )

        assert questions == []

    async def test_generate_follow_up_questions_answer_not_in_follow_up(
        self, questionnaire
    ):
        """Test when answer is not in follow-up configuration."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "No"
        )

        assert questions == []

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_json_error(
        self, mock_query, questionnaire
    ):
        """Test follow-up question generation with JSON decode error."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        async def mock_query_response():
            mock_message = Mock()
            mock_message.content = "Invalid JSON"
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "Yes"
        )

        assert questions == []

    def test_create_app_design_basic_data(self, questionnaire):
        """Test creating AppDesign from collected data."""
        questionnaire.collected_data = {
            "app_name": "My Test App",
            "app_type": "Web Application",
            "primary_purpose": "Testing application design",
            "target_audience": "Developers",
        }

        app_design = questionnaire._create_app_design()

        assert isinstance(app_design, AppDesign)
        assert app_design.name == "My Test App"
        assert app_design.type == "web application"
        assert app_design.description == "Testing application design"
        assert app_design.target_audience == "Developers"

    def test_create_app_design_with_features_and_goals(self, questionnaire):
        """Test creating AppDesign with features and goals from collected data."""
        questionnaire.collected_data = {
            "app_name": "Feature App",
            "app_type": "CLI Tool",
            "primary_purpose": "CLI testing",
            "features": "Authentication, User Management, Reporting",
            "goals": "MVP, Scale to 1000 users",
            "tech_stack": "Python, FastAPI, PostgreSQL",
            "constraints": "Budget: $5000, Timeline: 3 months",
        }

        app_design = questionnaire._create_app_design()

        assert app_design.name == "Feature App"
        assert app_design.type == "cli tool"
        assert "Authentication" in app_design.primary_features
        assert "User Management" in app_design.primary_features
        assert "MVP" in app_design.goals
        assert "Scale to 1000 users" in app_design.goals
        assert "Python" in app_design.tech_stack
        assert "Budget: $5000" in app_design.constraints

    def test_create_app_design_minimal_data(self, questionnaire):
        """Test creating AppDesign with minimal collected data."""
        questionnaire.collected_data = {}

        app_design = questionnaire._create_app_design()

        assert app_design.name == "My Application"  # Default
        assert app_design.type == "web application"  # Default
        assert app_design.description == ""  # Default empty
        assert app_design.target_audience is None
        assert app_design.primary_features == []
        assert app_design.goals == []
        assert app_design.tech_stack == []
        assert app_design.constraints == []

    def test_create_app_design_includes_additional_info(self, questionnaire):
        """Test that AppDesign includes all collected data in additional_info."""
        questionnaire.collected_data = {
            "app_name": "Test App",
            "app_type": "API Service",
            "primary_purpose": "API testing",
            "custom_field": "custom_value",
            "another_field": "another_value",
        }

        app_design = questionnaire._create_app_design()

        assert app_design.additional_info == questionnaire.collected_data
        assert app_design.additional_info["custom_field"] == "custom_value"
        assert app_design.additional_info["another_field"] == "another_value"
