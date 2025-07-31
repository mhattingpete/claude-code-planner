"""Interactive question system for gathering application requirements."""

import json
import re
from typing import Any

from claude_code_sdk import query
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from .constants import (
    ALLOWED_CONTROL_CHARS,
    DEFAULT_APP_DESCRIPTION,
    DEFAULT_APP_TYPE,
    DEFAULT_QUESTION_OPTIONS,
    INTELLIGENT_APP_NAMES,
    INVALID_CONTROL_CHARS,
    MAX_FIELD_LENGTH,
    MAX_ITEM_LENGTH,
    MAX_JSON_SIZE,
    MAX_LIST_ITEMS,
    PANEL_STYLES,
)
from .models import AppDesign, Question


class InteractiveQuestionnaire:
    """Handles interactive question generation and user input collection."""

    def __init__(self) -> None:
        self.console = Console()
        self.collected_data: dict[str, Any] = {}

    def _safe_json_parse(self, json_string: str) -> list[dict[str, Any]] | None:
        """Safely parse JSON input with validation."""
        if not json_string or not isinstance(json_string, str):
            return None

        # Remove potential harmful content and validate basic structure
        json_string = json_string.strip()

        # Basic validation: must start with [ and end with ]
        if not (json_string.startswith("[") and json_string.endswith("]")):
            # Try to extract JSON array from response
            match = re.search(r"\[.*\]", json_string, re.DOTALL)
            if not match:
                return None
            json_string = match.group(0)

        # Length check to prevent memory exhaustion
        if len(json_string) > MAX_JSON_SIZE:
            return None

        try:
            # Parse with strict validation
            parsed_data = json.loads(json_string)

            # Validate structure: must be a list
            if not isinstance(parsed_data, list):
                return None

            # Validate each item is a dict with expected keys
            for item in parsed_data:
                if not isinstance(item, dict):
                    return None
                # Basic required fields validation
                if "id" not in item or "text" not in item:
                    return None
                # Sanitize string values
                for _key, value in item.items():
                    if isinstance(value, str) and len(value) > MAX_ITEM_LENGTH:
                        return None

            return parsed_data

        except (json.JSONDecodeError, ValueError, TypeError):
            return None

    async def run_questionnaire(self) -> AppDesign:
        """Run the complete questionnaire process and return AppDesign."""

        self._display_welcome()

        # Generate initial questions using Claude
        questions = await self._generate_questions()

        # Process each question
        for question in questions:
            answer = self._process_question(question)
            self.collected_data[question.id] = answer

            # Generate follow-up questions if needed
            if question.follow_up and answer in question.follow_up:
                follow_up_questions = await self._generate_follow_up_questions(
                    question, answer
                )
                for fq in follow_up_questions:
                    follow_up_answer = self._process_question(fq)
                    self.collected_data[fq.id] = follow_up_answer

        # Convert collected data to AppDesign
        return self._create_app_design()

    def _display_welcome(self) -> None:
        """Display welcome message."""
        welcome_panel = Panel.fit(
            "[bold blue]Welcome to Claude Code Designer[/bold blue]\n\n"
            "Let's design your application...",
            title="Getting Started",
            border_style=PANEL_STYLES["welcome"],
        )
        self.console.print(welcome_panel)
        self.console.print()

    async def _generate_questions(self) -> list[Question]:
        """Generate initial questions using Claude Code SDK."""
        prompt = """Generate 4-5 essential questions for designing a software application.
        Return questions in this exact JSON format:
        [
          {
            "id": "app_type",
            "text": "What type of application?",
            "type": "multiple_choice",
            "options": ["Web Application", "CLI Tool", "API Service", "Mobile App"],
            "required": true,
            "follow_up": null
          },
          ...
        ]

        Keep questions simple and focused on core application details:
        - Application type
        - Primary purpose/features
        - Target audience
        - Technology preferences
        - Key constraints

        Make questions concise and actionable."""

        try:
            questions_json = ""
            query_stream = query(prompt=prompt)
            try:
                async for message in query_stream:
                    if hasattr(message, "content"):
                        questions_json += message.content
                    else:
                        questions_json += str(message)
            finally:
                if hasattr(query_stream, "aclose"):
                    await query_stream.aclose()

            # Parse JSON safely and create Question objects
            questions_data = self._safe_json_parse(questions_json)
            if not questions_data:
                self.console.print(
                    "[yellow]Invalid or unsafe JSON response from Claude. Using default questions.[/yellow]"
                )
                return self._get_default_questions()
            return [Question(**q) for q in questions_data]

        except KeyboardInterrupt:
            self.console.print(
                "\n[yellow]Question generation interrupted by user[/yellow]"
            )
            raise
        except ConnectionError:
            self.console.print(
                "[yellow]Network connection error. Using default questions.[/yellow]"
            )
            return self._get_default_questions()
        except (ValueError, TypeError) as e:
            self.console.print(
                f"[yellow]Invalid response format: {e}. Using default questions.[/yellow]"
            )
            return self._get_default_questions()
        except Exception as e:
            self.console.print(
                f"[yellow]Error generating questions: {e}. Using default questions.[/yellow]"
            )
            return self._get_default_questions()

    def _get_default_questions(self) -> list[Question]:
        """Fallback default questions if Claude generation fails."""
        return [
            Question(
                id="app_type",
                text="What type of application?",
                type="multiple_choice",
                options=DEFAULT_QUESTION_OPTIONS["app_type"],
                required=True,
            ),
            Question(
                id="app_name",
                text="What is your application name?",
                type="text",
                required=True,
            ),
            Question(
                id="primary_purpose",
                text="What is the primary purpose of your application?",
                type="text",
                required=True,
            ),
            Question(
                id="target_audience",
                text="Who is your target audience?",
                type="text",
                required=False,
            ),
        ]

    def _process_question(self, question: Question) -> str:
        """Process a single question and get user input."""

        # Display question
        question_panel = Panel.fit(
            f"[bold]{question.text}[/bold]",
            title=f"Question {question.id}",
            border_style=PANEL_STYLES["question"],
        )
        self.console.print(question_panel)

        if question.type == "multiple_choice" and question.options:
            return self._handle_multiple_choice(question)
        elif question.type == "text":
            return self._handle_text_input(question)
        else:
            return Prompt.ask("Answer", default="")

    def _handle_multiple_choice(self, question: Question) -> str:
        """Handle multiple choice questions with rich display."""
        if not question.options:
            return ""

        # Display options in a table
        table = Table(show_header=False, box=None)
        table.add_column("Option", style="bold")

        for i, option in enumerate(question.options, 1):
            table.add_row(f"{i}. {option}")

        self.console.print(table)
        self.console.print()

        while True:
            try:
                choice = IntPrompt.ask("Select option", default=1, show_default=True)
                if 1 <= choice <= len(question.options):
                    return question.options[choice - 1]
                else:
                    self.console.print(
                        f"[red]Please choose 1-{len(question.options)}[/red]"
                    )
            except KeyboardInterrupt:
                raise
            except (ValueError, TypeError):
                self.console.print("[red]Invalid choice. Please enter a number.[/red]")
            except Exception:
                self.console.print(
                    "[red]Unexpected input error. Please try again.[/red]"
                )

    def _handle_text_input(self, question: Question) -> str:
        """Handle text input questions."""
        return Prompt.ask("Answer", default="" if not question.required else None)

    async def _generate_follow_up_questions(
        self, parent_question: Question, answer: str
    ) -> list[Question]:
        """Generate follow-up questions based on previous answer."""
        if not parent_question.follow_up or answer not in parent_question.follow_up:
            return []

        prompt = f"""Based on the user's answer "{answer}" to "{parent_question.text}",
        generate 1-2 relevant follow-up questions in JSON format:
        [
          {{
            "id": "follow_up_{parent_question.id}_1",
            "text": "Follow-up question text",
            "type": "text",
            "options": null,
            "required": false,
            "follow_up": null
          }}
        ]

        Keep follow-up questions specific and helpful for application design."""

        try:
            questions_json = ""
            query_stream = query(prompt=prompt)
            try:
                async for message in query_stream:
                    if hasattr(message, "content"):
                        questions_json += message.content
                    else:
                        questions_json += str(message)
            finally:
                if hasattr(query_stream, "aclose"):
                    await query_stream.aclose()

            questions_data = self._safe_json_parse(questions_json)
            if not questions_data:
                self.console.print(
                    "[dim]Unable to generate follow-up questions due to invalid or unsafe response[/dim]"
                )
                return []
            return [Question(**q) for q in questions_data]

        except KeyboardInterrupt:
            raise
        except ConnectionError:
            self.console.print(
                "[dim]Unable to generate follow-up questions due to connection error[/dim]"
            )
            return []
        except (ValueError, TypeError):
            self.console.print(
                "[dim]Invalid response format for follow-up questions[/dim]"
            )
            return []
        except Exception:
            return []

    def _validate_collected_data(self) -> dict[str, str]:
        """Validate and sanitize collected data."""
        validation_errors = {}

        if not isinstance(self.collected_data, dict):
            validation_errors["collected_data"] = "Collected data must be a dictionary"
            return validation_errors

        # Validate each field
        for key, value in self.collected_data.items():
            if not isinstance(key, str):
                validation_errors[str(key)] = "All keys must be strings"
                continue

            # Validate string length limits
            if isinstance(value, str):
                if len(value) > MAX_FIELD_LENGTH:
                    validation_errors[key] = (
                        f"Field '{key}' exceeds maximum length ({MAX_FIELD_LENGTH:,} characters)"
                    )
                # Sanitize potential dangerous characters
                if any(char in value for char in INVALID_CONTROL_CHARS):
                    validation_errors[key] = (
                        f"Field '{key}' contains invalid control characters"
                    )
            elif value is not None and not isinstance(value, str | int | float | bool):
                validation_errors[key] = (
                    f"Field '{key}' must be a string, number, boolean, or None"
                )

        return validation_errors

    def _sanitize_string_value(self, value: Any) -> str:
        """Safely convert and sanitize a value to string."""
        if value is None:
            return ""
        if isinstance(value, str):
            # Remove control characters and limit length
            sanitized = "".join(
                char
                for char in value
                if ord(char) >= 32 or char in ALLOWED_CONTROL_CHARS
            )
            return sanitized[:MAX_FIELD_LENGTH]
        if isinstance(value, int | float | bool):
            return str(value)
        # For other types, convert safely
        return str(value)[:MAX_FIELD_LENGTH]

    def _split_and_clean_list(self, value: str) -> list[str]:
        """Split string value and clean up the resulting list."""
        if not value:
            return []

        import csv
        import io

        items = []
        try:
            # Use CSV reader to handle quoted values and commas properly
            csv_reader = csv.reader(io.StringIO(value.strip()), skipinitialspace=True)
            for row in csv_reader:
                for item in row:
                    cleaned = item.strip()
                    # Remove surrounding quotes if they exist (for fallback cases)
                    if (
                        cleaned.startswith('"')
                        and cleaned.endswith('"')
                        and len(cleaned) > 1
                    ):
                        cleaned = cleaned[1:-1]
                    if cleaned and len(cleaned) <= MAX_ITEM_LENGTH:
                        items.append(cleaned)
        except csv.Error:
            # Fallback to simple splitting if CSV parsing fails
            for item in value.split(","):
                cleaned = item.strip()
                # Remove surrounding quotes if they exist
                if (
                    cleaned.startswith('"')
                    and cleaned.endswith('"')
                    and len(cleaned) > 1
                ):
                    cleaned = cleaned[1:-1]
                if cleaned and len(cleaned) <= MAX_ITEM_LENGTH:
                    items.append(cleaned)

        return items[:MAX_LIST_ITEMS]

    def _generate_intelligent_app_name(self, app_type: str) -> str:
        """Generate contextually appropriate app name based on type and purpose."""
        app_type = app_type.lower()
        purpose = self._sanitize_string_value(
            self.collected_data.get("primary_purpose", "")
        ).lower()

        # Determine the app category
        if "cli" in app_type or "command" in app_type:
            category = "cli"
        elif "api" in app_type or "service" in app_type:
            category = "api"
        elif "mobile" in app_type:
            category = "mobile"
        else:
            category = "web"

        # Find matching purpose keywords
        category_names = INTELLIGENT_APP_NAMES[category]
        for keyword, name in category_names.items():
            if keyword != "default" and keyword in purpose:
                return name

        # Return default for category
        return category_names["default"]

    def _create_app_design(self) -> AppDesign:
        """Convert collected data into AppDesign model with validation."""

        # Validate collected data first
        validation_errors = self._validate_collected_data()
        if validation_errors:
            error_msg = "\n".join(
                [f"- {field}: {error}" for field, error in validation_errors.items()]
            )
            self.console.print(f"[red]Data validation errors:\n{error_msg}[/red]")
            self.console.print(
                "[yellow]Using default values for invalid fields...[/yellow]"
            )

        # Extract and sanitize basic information with intelligent defaults
        app_type_raw = self._sanitize_string_value(
            self.collected_data.get("app_type", DEFAULT_APP_TYPE)
        )
        app_type = app_type_raw.lower() if app_type_raw else DEFAULT_APP_TYPE.lower()

        name = self._sanitize_string_value(
            self.collected_data.get(
                "app_name", self._generate_intelligent_app_name(app_type)
            )
        )
        if not name.strip():
            name = self._generate_intelligent_app_name(app_type)

        description = self._sanitize_string_value(
            self.collected_data.get("primary_purpose", "")
        )
        target_audience = self._sanitize_string_value(
            self.collected_data.get("target_audience")
        )

        # Extract features and goals from various fields with validation
        primary_features = []
        goals = []
        tech_stack = []
        constraints = []

        # Process all collected data safely
        for key, value in self.collected_data.items():
            if not isinstance(key, str):
                continue

            sanitized_value = self._sanitize_string_value(value)
            if sanitized_value:
                key_lower = key.lower()
                if "feature" in key_lower:
                    primary_features.extend(self._split_and_clean_list(sanitized_value))
                elif "goal" in key_lower or "objective" in key_lower:
                    goals.extend(self._split_and_clean_list(sanitized_value))
                elif "tech" in key_lower or "stack" in key_lower:
                    tech_stack.extend(self._split_and_clean_list(sanitized_value))
                elif "constraint" in key_lower or "limitation" in key_lower:
                    constraints.extend(self._split_and_clean_list(sanitized_value))

        # Validate required fields
        if not name.strip():
            self.console.print(
                "[yellow]Warning: Application name is empty, using intelligent default[/yellow]"
            )
            name = self._generate_intelligent_app_name(app_type)

        try:
            return AppDesign(
                name=name,
                type=app_type,
                description=description,
                primary_features=primary_features,
                tech_stack=tech_stack,
                target_audience=target_audience if target_audience else None,
                goals=goals,
                constraints=constraints,
                additional_info=self.collected_data,
            )
        except (ValueError, TypeError) as e:
            self.console.print(f"[red]Invalid data for AppDesign: {e}[/red]")
            self.console.print(
                "[yellow]Using minimal default configuration...[/yellow]"
            )
            # Return minimal valid AppDesign as fallback
            return AppDesign(
                name=INTELLIGENT_APP_NAMES["web"]["default"],
                type=DEFAULT_APP_TYPE.lower(),
                description=DEFAULT_APP_DESCRIPTION,
                primary_features=[],
                tech_stack=[],
                target_audience=None,
                goals=[],
                constraints=[],
                additional_info={},
            )
        except Exception as e:
            self.console.print(f"[red]Error creating AppDesign: {e}[/red]")
            self.console.print(
                "[yellow]Using minimal default configuration...[/yellow]"
            )
            # Return minimal valid AppDesign as fallback
            return AppDesign(
                name=INTELLIGENT_APP_NAMES["web"]["default"],
                type=DEFAULT_APP_TYPE.lower(),
                description=DEFAULT_APP_DESCRIPTION,
                primary_features=[],
                tech_stack=[],
                target_audience=None,
                goals=[],
                constraints=[],
                additional_info={},
            )
