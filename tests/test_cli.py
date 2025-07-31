"""Integration tests for CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from click.testing import CliRunner

from claude_code_designer.cli import design, info, main
from claude_code_designer.models import AppDesign


class TestCLI:
    """Test cases for CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def sample_app_design(self):
        """Create a sample AppDesign for testing."""
        return AppDesign(
            name="Test CLI App",
            type="cli",
            description="A test CLI application",
            primary_features=["Command parsing", "Configuration"],
            tech_stack=["Python", "Click"],
            target_audience="Developers",
            goals=["Build functional CLI"],
            constraints=["Simple implementation"],
        )

    def test_main_command_group(self, runner):
        """Test the main command group shows help."""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Claude Code Designer" in result.output
        assert "design" in result.output
        assert "info" in result.output

    def test_info_command(self, runner):
        """Test the info command displays information."""
        result = runner.invoke(info)

        assert result.exit_code == 0
        assert "Claude Code Designer" in result.output
        assert "Commands:" in result.output
        assert "design" in result.output
        assert "Examples:" in result.output

    def test_design_command_help(self, runner):
        """Test the design command help output."""
        result = runner.invoke(design, ["--help"])

        assert result.exit_code == 0
        assert "Start the interactive design process" in result.output
        assert "--output-dir" in result.output
        assert "--skip-prd" in result.output
        assert "--skip-claude-md" in result.output
        assert "--skip-readme" in result.output

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    @patch("claude_code_designer.cli.DocumentGenerator")
    @patch("click.confirm")
    def test_design_command_success(
        self,
        mock_confirm,
        mock_generator_class,
        mock_questionnaire_class,
        runner,
        sample_app_design,
    ):
        """Test successful design command execution."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.return_value = sample_app_design
            mock_questionnaire_class.return_value = mock_questionnaire

            # Mock generator
            mock_generator = AsyncMock()
            mock_generator.generate_documents.return_value = {
                "PRD": f"{temp_dir}/PRD.md",
                "CLAUDE.md": f"{temp_dir}/CLAUDE.md",
                "README": f"{temp_dir}/README.md",
            }
            mock_generator_class.return_value = mock_generator

            # Mock user confirmation
            mock_confirm.return_value = True

            # Create expected files
            for filename in ["PRD.md", "CLAUDE.md", "README.md"]:
                Path(temp_dir) / filename

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 0
            mock_questionnaire.run_questionnaire.assert_called_once()
            mock_generator.generate_documents.assert_called_once()
            mock_confirm.assert_called_once()

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    @patch("click.confirm")
    def test_design_command_user_cancellation(
        self, mock_confirm, mock_questionnaire_class, runner, sample_app_design
    ):
        """Test design command when user cancels generation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.return_value = sample_app_design
            mock_questionnaire_class.return_value = mock_questionnaire

            # Mock user cancellation
            mock_confirm.return_value = False

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 0
            assert "Document generation cancelled" in result.output
            mock_questionnaire.run_questionnaire.assert_called_once()

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    @patch("claude_code_designer.cli.DocumentGenerator")
    @patch("click.confirm")
    def test_design_command_with_skip_options(
        self,
        mock_confirm,
        mock_generator_class,
        mock_questionnaire_class,
        runner,
        sample_app_design,
    ):
        """Test design command with skip options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.return_value = sample_app_design
            mock_questionnaire_class.return_value = mock_questionnaire

            # Mock generator
            mock_generator = AsyncMock()
            mock_generator.generate_documents.return_value = {
                "CLAUDE.md": f"{temp_dir}/CLAUDE.md"
            }
            mock_generator_class.return_value = mock_generator

            # Mock user confirmation
            mock_confirm.return_value = True

            result = runner.invoke(
                design, ["--output-dir", temp_dir, "--skip-prd", "--skip-readme"]
            )

            assert result.exit_code == 0

            # Verify DocumentRequest was created with correct skip options
            call_args = mock_generator.generate_documents.call_args[0][0]
            assert call_args.generate_prd is False
            assert call_args.generate_claude_md is True
            assert call_args.generate_readme is False

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    def test_design_command_keyboard_interrupt(self, mock_questionnaire_class, runner):
        """Test design command handling of keyboard interrupt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire to raise KeyboardInterrupt
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.side_effect = KeyboardInterrupt()
            mock_questionnaire_class.return_value = mock_questionnaire

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 1  # click.Abort exit code
            assert "Design process interrupted by user" in result.output

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    def test_design_command_connection_error(self, mock_questionnaire_class, runner):
        """Test design command handling of connection error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire to raise ConnectionError
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.side_effect = ConnectionError(
                "Network error"
            )
            mock_questionnaire_class.return_value = mock_questionnaire

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 1  # click.Abort exit code
            assert "Network connection error" in result.output

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    def test_design_command_general_error(self, mock_questionnaire_class, runner):
        """Test design command handling of general errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire to raise general exception
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.side_effect = Exception("Some error")
            mock_questionnaire_class.return_value = mock_questionnaire

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 1  # click.Abort exit code
            assert "Unexpected error: Some error" in result.output

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    @patch("claude_code_designer.cli.DocumentGenerator")
    @patch("click.confirm")
    def test_design_command_generator_error(
        self,
        mock_confirm,
        mock_generator_class,
        mock_questionnaire_class,
        runner,
        sample_app_design,
    ):
        """Test design command handling of generator errors."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.return_value = sample_app_design
            mock_questionnaire_class.return_value = mock_questionnaire

            # Mock generator to raise error
            mock_generator = AsyncMock()
            mock_generator.generate_documents.side_effect = Exception(
                "Generation failed"
            )
            mock_generator_class.return_value = mock_generator

            # Mock user confirmation
            mock_confirm.return_value = True

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 1  # click.Abort exit code
            assert "Unexpected error: Generation failed" in result.output

    def test_design_command_default_output_dir(self, runner):
        """Test design command uses current directory as default."""
        # Just test that the command can be invoked with default options
        # We'll mock the async components to avoid actual execution
        with patch("claude_code_designer.cli.asyncio.run") as mock_run:
            mock_run.side_effect = KeyboardInterrupt()

            result = runner.invoke(design)

            # Should handle the KeyboardInterrupt and show interrupted message
            assert result.exit_code == 1
            assert "Design process interrupted by user" in result.output

    @patch("claude_code_designer.cli.InteractiveQuestionnaire")
    @patch("claude_code_designer.cli.DocumentGenerator")
    @patch("click.confirm")
    def test_design_command_no_files_generated(
        self,
        mock_confirm,
        mock_generator_class,
        mock_questionnaire_class,
        runner,
        sample_app_design,
    ):
        """Test design command when no files are generated."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Mock questionnaire
            mock_questionnaire = AsyncMock()
            mock_questionnaire.run_questionnaire.return_value = sample_app_design
            mock_questionnaire_class.return_value = mock_questionnaire

            # Mock generator to return no files
            mock_generator = AsyncMock()
            mock_generator.generate_documents.return_value = {}
            mock_generator_class.return_value = mock_generator

            # Mock user confirmation
            mock_confirm.return_value = True

            result = runner.invoke(design, ["--output-dir", temp_dir])

            assert result.exit_code == 0
            assert "No documents were generated" in result.output

    def test_main_version_option(self, runner):
        """Test the main command version option."""
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        # Version should be displayed (exact format may vary)
        assert len(result.output.strip()) > 0

    def test_design_command_output_dir_path_validation(self, runner):
        """Test design command with valid output directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a subdirectory to test path creation
            output_path = Path(temp_dir) / "output"

            with patch("claude_code_designer.cli.asyncio.run") as mock_run:
                mock_run.side_effect = KeyboardInterrupt()

                result = runner.invoke(design, ["--output-dir", str(output_path)])

                # Should accept the path and proceed (then get interrupted)
                assert result.exit_code == 1
                assert "Design process interrupted by user" in result.output
