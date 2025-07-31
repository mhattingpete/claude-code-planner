"""Interactive question system for gathering application requirements."""

import json
from typing import Any

from claude_code_sdk import query
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table

from .models import AppDesign, Question


class InteractiveQuestionnaire:
    """Handles interactive question generation and user input collection."""

    def __init__(self) -> None:
        self.console = Console()
        self.collected_data: dict[str, Any] = {}

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
            border_style="blue",
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
            async for message in query(prompt=prompt):
                if hasattr(message, "content"):
                    questions_json += message.content
                else:
                    questions_json += str(message)

            # Parse JSON and create Question objects
            questions_data = json.loads(questions_json.strip())
            return [Question(**q) for q in questions_data]

        except KeyboardInterrupt:
            self.console.print(
                "\n[yellow]Question generation interrupted by user[/yellow]"
            )
            raise
        except json.JSONDecodeError:
            self.console.print(
                "[yellow]Invalid JSON response from Claude. Using default questions.[/yellow]"
            )
            return self._get_default_questions()
        except ConnectionError:
            self.console.print(
                "[yellow]Network connection error. Using default questions.[/yellow]"
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
                options=["Web Application", "CLI Tool", "API Service", "Mobile App"],
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
            border_style="cyan",
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
            except Exception:
                self.console.print("[red]Invalid choice. Please enter a number.[/red]")

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
            async for message in query(prompt=prompt):
                if hasattr(message, "content"):
                    questions_json += message.content
                else:
                    questions_json += str(message)

            questions_data = json.loads(questions_json.strip())
            return [Question(**q) for q in questions_data]

        except KeyboardInterrupt:
            raise
        except json.JSONDecodeError:
            self.console.print(
                "[dim]Unable to generate follow-up questions due to invalid response[/dim]"
            )
            return []
        except ConnectionError:
            self.console.print(
                "[dim]Unable to generate follow-up questions due to connection error[/dim]"
            )
            return []
        except Exception:
            return []

    def _create_app_design(self) -> AppDesign:
        """Convert collected data into AppDesign model."""

        # Extract basic information
        name = self.collected_data.get("app_name", "My Application")
        app_type = self.collected_data.get("app_type", "Web Application").lower()
        description = self.collected_data.get("primary_purpose", "")
        target_audience = self.collected_data.get("target_audience")

        # Extract features and goals from various fields
        primary_features = []
        goals = []
        tech_stack = []
        constraints = []

        # Process all collected data
        for key, value in self.collected_data.items():
            if value and isinstance(value, str):
                if "feature" in key.lower():
                    primary_features.extend([f.strip() for f in value.split(",")])
                elif "goal" in key.lower() or "objective" in key.lower():
                    goals.extend([g.strip() for g in value.split(",")])
                elif "tech" in key.lower() or "stack" in key.lower():
                    tech_stack.extend([t.strip() for t in value.split(",")])
                elif "constraint" in key.lower() or "limitation" in key.lower():
                    constraints.extend([c.strip() for c in value.split(",")])

        return AppDesign(
            name=name,
            type=app_type,
            description=description,
            primary_features=primary_features,
            tech_stack=tech_stack,
            target_audience=target_audience,
            goals=goals,
            constraints=constraints,
            additional_info=self.collected_data,
        )
