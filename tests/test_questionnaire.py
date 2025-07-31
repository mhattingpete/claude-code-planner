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

        assert app_design.name == "web-application"  # Intelligent default
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

    def test_safe_json_parse_empty_input(self, questionnaire):
        """Test _safe_json_parse with empty/invalid input."""
        # Test None input
        assert questionnaire._safe_json_parse(None) is None

        # Test empty string
        assert questionnaire._safe_json_parse("") is None

        # Test non-string input
        assert questionnaire._safe_json_parse(123) is None

    def test_safe_json_parse_invalid_json_structure(self, questionnaire):
        """Test _safe_json_parse with invalid JSON structure."""
        # Test missing brackets
        assert questionnaire._safe_json_parse('{"id": "test"}') is None

        # Test no JSON array found
        assert questionnaire._safe_json_parse("not json at all") is None

        # Test oversized input
        large_input = "[" + "x" * 50001 + "]"
        assert questionnaire._safe_json_parse(large_input) is None

    def test_safe_json_parse_valid_extraction(self, questionnaire):
        """Test _safe_json_parse extracting JSON from response text."""
        # Test extracting JSON array from text
        response_text = 'Here is the JSON: [{"id": "test", "text": "Test question"}] Hope this helps!'
        result = questionnaire._safe_json_parse(response_text)
        assert result is not None
        assert len(result) == 1
        assert result[0]["id"] == "test"

    def test_safe_json_parse_invalid_structure_validation(self, questionnaire):
        """Test _safe_json_parse structure validation."""
        # Test non-list JSON
        assert questionnaire._safe_json_parse('{"not": "a list"}') is None

        # Test list with non-dict items
        assert questionnaire._safe_json_parse('["not", "dicts"]') is None

        # Test dict missing required fields
        assert questionnaire._safe_json_parse('[{"missing": "id_and_text"}]') is None

        # Test oversized string values
        large_value = "x" * 1001
        assert (
            questionnaire._safe_json_parse(
                f'[{{"id": "test", "text": "{large_value}"}}]'
            )
            is None
        )

    def test_safe_json_parse_json_decode_error(self, questionnaire):
        """Test _safe_json_parse with JSON decode errors."""
        # Test malformed JSON
        assert questionnaire._safe_json_parse('[{"id": "test", "incomplete":}]') is None

        # Test invalid JSON syntax
        assert (
            questionnaire._safe_json_parse('[{id: "test", "text": "missing quotes"}]')
            is None
        )

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_general_exception(
        self, mock_query, questionnaire
    ):
        """Test _generate_questions with general exception."""
        # Mock general exception
        mock_query.side_effect = ValueError("Test error")

        questions = await questionnaire._generate_questions()

        # Should return default questions
        assert len(questions) == 4
        assert questions[0].id == "app_type"

    def test_display_welcome(self, questionnaire):
        """Test _display_welcome method."""
        # This tests the display method execution
        questionnaire._display_welcome()
        # If no exception is raised, the test passes

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_keyboard_interrupt(
        self, mock_query, questionnaire
    ):
        """Test keyboard interrupt in follow-up question generation."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        mock_query.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            await questionnaire._generate_follow_up_questions(parent_question, "Yes")

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_connection_error(
        self, mock_query, questionnaire
    ):
        """Test connection error in follow-up question generation."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        mock_query.side_effect = ConnectionError("Network error")

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "Yes"
        )

        assert questions == []

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_general_exception(
        self, mock_query, questionnaire
    ):
        """Test general exception in follow-up question generation."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        mock_query.side_effect = ValueError("Test error")

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "Yes"
        )

        assert questions == []

    @patch("claude_code_designer.questionnaire.IntPrompt.ask")
    def test_handle_multiple_choice_keyboard_interrupt(
        self, mock_prompt, questionnaire
    ):
        """Test keyboard interrupt in multiple choice handling."""
        question = Question(
            id="test",
            text="Choose option",
            type="multiple_choice",
            options=["Option 1", "Option 2"],
        )
        mock_prompt.side_effect = KeyboardInterrupt()

        with pytest.raises(KeyboardInterrupt):
            questionnaire._handle_multiple_choice(question)

    @patch("claude_code_designer.questionnaire.IntPrompt.ask")
    def test_handle_multiple_choice_general_exception(self, mock_prompt, questionnaire):
        """Test general exception in multiple choice handling."""
        question = Question(
            id="test",
            text="Choose option",
            type="multiple_choice",
            options=["Option 1", "Option 2"],
        )
        # First general exception, then valid choice
        mock_prompt.side_effect = [ValueError("Test error"), 1]

        result = questionnaire._handle_multiple_choice(question)

        assert result == "Option 1"
        assert mock_prompt.call_count == 2

    def test_process_question_unknown_type(self, questionnaire):
        """Test _process_question with unknown question type."""
        question = Question(
            id="test",
            text="Unknown type question",
            type="unknown_type",
        )

        with patch("claude_code_designer.questionnaire.Prompt.ask") as mock_prompt:
            mock_prompt.return_value = "default answer"
            result = questionnaire._process_question(question)

        assert result == "default answer"
        mock_prompt.assert_called_once_with("Answer", default="")

    def test_validate_collected_data_invalid_type(self, questionnaire):
        """Test _validate_collected_data with invalid data type."""
        questionnaire.collected_data = "not a dict"

        errors = questionnaire._validate_collected_data()

        assert "collected_data" in errors
        assert "must be a dictionary" in errors["collected_data"]

    def test_validate_collected_data_non_string_keys(self, questionnaire):
        """Test _validate_collected_data with non-string keys."""
        questionnaire.collected_data = {123: "value", "valid_key": "value"}

        errors = questionnaire._validate_collected_data()

        assert "123" in errors
        assert "must be strings" in errors["123"]

    def test_validate_collected_data_oversized_string(self, questionnaire):
        """Test _validate_collected_data with oversized string."""
        large_string = "x" * 10001
        questionnaire.collected_data = {"large_field": large_string}

        errors = questionnaire._validate_collected_data()

        assert "large_field" in errors
        assert "exceeds maximum length" in errors["large_field"]

    def test_validate_collected_data_control_characters(self, questionnaire):
        """Test _validate_collected_data with control characters."""
        invalid_string = "test\x00string"
        questionnaire.collected_data = {"invalid_field": invalid_string}

        errors = questionnaire._validate_collected_data()

        assert "invalid_field" in errors
        assert "invalid control characters" in errors["invalid_field"]

    def test_validate_collected_data_invalid_value_types(self, questionnaire):
        """Test _validate_collected_data with invalid value types."""
        questionnaire.collected_data = {
            "list_field": ["not", "allowed"],
            "dict_field": {"not": "allowed"},
        }

        errors = questionnaire._validate_collected_data()

        assert "list_field" in errors
        assert "dict_field" in errors

    def test_sanitize_string_value_various_types(self, questionnaire):
        """Test _sanitize_string_value with various input types."""
        # Test None
        assert questionnaire._sanitize_string_value(None) == ""

        # Test string with control characters
        dirty_string = "test\x08string\x00with\x0ccontrol"
        clean = questionnaire._sanitize_string_value(dirty_string)
        assert "\x08" not in clean
        assert "\x00" not in clean
        assert "\x0c" not in clean
        assert "teststring" in clean

        # Test numeric types
        assert questionnaire._sanitize_string_value(123) == "123"
        assert questionnaire._sanitize_string_value(45.67) == "45.67"
        assert questionnaire._sanitize_string_value(True) == "True"

        # Test oversized string
        large_string = "x" * 15000
        result = questionnaire._sanitize_string_value(large_string)
        assert len(result) == 10000

        # Test other types
        assert questionnaire._sanitize_string_value([1, 2, 3]) == "[1, 2, 3]"

    def test_split_and_clean_list_various_inputs(self, questionnaire):
        """Test _split_and_clean_list with various inputs."""
        # Test empty string
        assert questionnaire._split_and_clean_list("") == []

        # Test normal comma-separated values
        result = questionnaire._split_and_clean_list("one, two, three")
        assert result == ["one", "two", "three"]

        # Test with oversized items (should be filtered out)
        oversized_item = "x" * 1001
        result = questionnaire._split_and_clean_list(
            f"valid,{oversized_item},also_valid"
        )
        assert result == ["valid", "also_valid"]

        # Test with too many items (should be limited to 50)
        many_items = ",".join([f"item{i}" for i in range(100)])
        result = questionnaire._split_and_clean_list(many_items)
        assert len(result) == 50

    def test_split_and_clean_list_edge_cases(self, questionnaire):
        """Test _split_and_clean_list with edge cases containing commas."""
        # Test quoted values with commas
        result = questionnaire._split_and_clean_list(
            '"item, with comma", regular, "another, with comma"'
        )
        assert result == ["item, with comma", "regular", "another, with comma"]

        # Test single quoted value with comma
        result = questionnaire._split_and_clean_list('"single item, with comma"')
        assert result == ["single item, with comma"]

        # Test mixed quoted and unquoted
        result = questionnaire._split_and_clean_list(
            'unquoted, "quoted, item", another'
        )
        assert result == ["unquoted", "quoted, item", "another"]

        # Test empty quoted strings
        result = questionnaire._split_and_clean_list('"", valid, ""')
        assert result == ["valid"]

        # Test malformed quotes (CSV handles gracefully)
        result = questionnaire._split_and_clean_list('item1, "unclosed quote, item2')
        assert result == ["item1", "unclosed quote, item2"]

        # Test whitespace handling with quotes (strips quoted content)
        result = questionnaire._split_and_clean_list('  "  spaced item  "  ,  normal  ')
        assert result == ["spaced item", "normal"]

    def test_create_app_design_with_validation_errors(self, questionnaire):
        """Test _create_app_design with validation errors."""
        # Set invalid data that will trigger validation errors
        questionnaire.collected_data = {
            123: "invalid key",  # Non-string key
            "oversized": "x" * 10001,  # Oversized value
        }

        app_design = questionnaire._create_app_design()

        # Should still create a valid AppDesign with intelligent defaults
        assert app_design.name == "web-application"
        assert app_design.type == "web application"

    def test_create_app_design_empty_name_fallback(self, questionnaire):
        """Test _create_app_design with empty name fallback."""
        questionnaire.collected_data = {"app_name": "   "}  # Empty/whitespace name

        app_design = questionnaire._create_app_design()

        assert app_design.name == "web-application"

    def test_create_app_design_feature_extraction(self, questionnaire):
        """Test _create_app_design feature extraction from various fields."""
        questionnaire.collected_data = {
            "app_name": "Feature App",
            "app_type": "Web Application",
            "primary_purpose": "Testing",
            "key_features": "Auth, API, Dashboard",
            "main_goals": "MVP, Scale, Launch",
            "tech_stack_details": "Python, React, PostgreSQL",
            "project_constraints": "Budget: $10k, Time: 6 months",
        }

        app_design = questionnaire._create_app_design()

        assert "Auth" in app_design.primary_features
        assert "API" in app_design.primary_features
        assert "MVP" in app_design.goals
        assert "Scale" in app_design.goals
        assert "Python" in app_design.tech_stack
        assert "React" in app_design.tech_stack
        assert "Budget: $10k" in app_design.constraints

    def test_safe_json_parse_non_list_structure(self, questionnaire):
        """Test _safe_json_parse with non-list JSON structure (line 49)."""
        # Test valid JSON but not an array
        result = questionnaire._safe_json_parse('{"valid": "json", "but": "not array"}')
        assert result is None

    def test_create_app_design_empty_name_warning(self, questionnaire):
        """Test _create_app_design with empty name warning (lines 398-399)."""
        questionnaire.collected_data = {"app_name": ""}  # Empty name

        app_design = questionnaire._create_app_design()

        # Should use intelligent default name
        assert app_design.name == "web-application"

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_questions_message_without_content(
        self, mock_query, questionnaire
    ):
        """Test _generate_questions with message without content attribute (line 137)."""

        # Mock Claude SDK response with message object without content attribute
        async def mock_query_response():
            mock_message = Mock()
            # Remove content attribute to trigger line 137
            del mock_message.content
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_questions()

        # Should return default questions due to invalid JSON
        assert len(questions) == 4
        assert questions[0].id == "app_type"

    @patch("claude_code_designer.questionnaire.query")
    async def test_generate_follow_up_questions_message_without_content(
        self, mock_query, questionnaire
    ):
        """Test _generate_follow_up_questions with message without content attribute (line 278)."""
        parent_question = Question(
            id="parent",
            text="Parent question",
            type="multiple_choice",
            follow_up={"Yes": "follow_up_yes"},
        )

        # Mock Claude SDK response with message object without content attribute
        async def mock_query_response():
            mock_message = Mock()
            # Remove content attribute to trigger line 278
            del mock_message.content
            yield mock_message

        mock_query.return_value = mock_query_response()

        questions = await questionnaire._generate_follow_up_questions(
            parent_question, "Yes"
        )

        # Should return empty list due to invalid JSON
        assert questions == []

    @patch("claude_code_designer.questionnaire.query")
    async def test_run_questionnaire_end_to_end_with_follow_up(
        self, mock_query, questionnaire
    ):
        """Test complete run_questionnaire flow with follow-up questions."""
        # Mock initial questions
        initial_questions_json = json.dumps(
            [
                {
                    "id": "app_type",
                    "text": "What type of application?",
                    "type": "multiple_choice",
                    "options": ["Web App", "CLI Tool"],
                    "required": True,
                    "follow_up": {"Web App": "web_followup"},
                }
            ]
        )

        # Mock follow-up questions
        followup_questions_json = json.dumps(
            [
                {
                    "id": "web_framework",
                    "text": "Which web framework?",
                    "type": "text",
                    "options": None,
                    "required": False,
                    "follow_up": None,
                }
            ]
        )

        call_count = [0]

        async def mock_query_response(*args, **kwargs):
            call_count[0] += 1
            mock_message = Mock()
            if call_count[0] == 1:
                mock_message.content = initial_questions_json
            else:
                mock_message.content = followup_questions_json
            yield mock_message

        mock_query.side_effect = mock_query_response

        # Mock user inputs
        with (
            patch(
                "claude_code_designer.questionnaire.IntPrompt.ask"
            ) as mock_int_prompt,
            patch("claude_code_designer.questionnaire.Prompt.ask") as mock_text_prompt,
        ):
            mock_int_prompt.return_value = 1  # Select "Web App"
            mock_text_prompt.return_value = "Django"

            app_design = await questionnaire.run_questionnaire()

            assert (
                app_design.name == "web-application"
            )  # Intelligent default since no app_name
            assert questionnaire.collected_data["app_type"] == "Web App"
            assert questionnaire.collected_data["web_framework"] == "Django"

    def test_generate_intelligent_app_name_cli_tool(self, questionnaire):
        """Test intelligent app name generation for CLI tools."""
        questionnaire.collected_data = {"primary_purpose": "build automation tool"}

        name = questionnaire._generate_intelligent_app_name("CLI Tool")
        assert name == "utility-cli"

        questionnaire.collected_data = {
            "primary_purpose": "process manager for services"
        }
        name = questionnaire._generate_intelligent_app_name("cli tool")
        assert name == "process-manager"

        # Default CLI case
        questionnaire.collected_data = {}
        name = questionnaire._generate_intelligent_app_name("command line")
        assert name == "command-line-tool"

    def test_generate_intelligent_app_name_api_service(self, questionnaire):
        """Test intelligent app name generation for API services."""
        questionnaire.collected_data = {"primary_purpose": "user authentication system"}

        name = questionnaire._generate_intelligent_app_name("API Service")
        assert name == "auth-service"

        questionnaire.collected_data = {"primary_purpose": "database management system"}
        name = questionnaire._generate_intelligent_app_name("api")
        assert name == "data-service"

        # Default API case
        questionnaire.collected_data = {}
        name = questionnaire._generate_intelligent_app_name("service")
        assert name == "api-service"

    def test_generate_intelligent_app_name_mobile_app(self, questionnaire):
        """Test intelligent app name generation for mobile apps."""
        questionnaire.collected_data = {"primary_purpose": "social networking platform"}

        name = questionnaire._generate_intelligent_app_name("Mobile App")
        assert name == "social-mobile-app"

        questionnaire.collected_data = {
            "primary_purpose": "task management for productivity"
        }
        name = questionnaire._generate_intelligent_app_name("mobile")
        assert name == "productivity-app"

        # Default mobile case
        questionnaire.collected_data = {}
        name = questionnaire._generate_intelligent_app_name("mobile app")
        assert name == "mobile-application"

    def test_generate_intelligent_app_name_web_application(self, questionnaire):
        """Test intelligent app name generation for web applications."""
        questionnaire.collected_data = {"primary_purpose": "admin dashboard for users"}

        name = questionnaire._generate_intelligent_app_name("Web Application")
        assert name == "admin-dashboard"

        questionnaire.collected_data = {
            "primary_purpose": "ecommerce shop for products"
        }
        name = questionnaire._generate_intelligent_app_name("web app")
        assert name == "web-store"

        questionnaire.collected_data = {"primary_purpose": "blog content management"}
        name = questionnaire._generate_intelligent_app_name("web")
        assert name == "content-platform"

        # Default web case
        questionnaire.collected_data = {}
        name = questionnaire._generate_intelligent_app_name("unknown type")
        assert name == "web-application"
