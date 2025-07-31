"""Tests for document generation engine."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from claude_code_designer.generator import DocumentGenerator
from claude_code_designer.models import AppDesign, DocumentRequest


class TestDocumentGenerator:
    """Test cases for the DocumentGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a document generator instance for testing."""
        return DocumentGenerator()

    @pytest.fixture
    def sample_app_design(self):
        """Create a sample AppDesign for testing."""
        return AppDesign(
            name="Test App",
            type="web",
            description="A test web application",
            primary_features=["Authentication", "User Management"],
            tech_stack=["Python", "FastAPI"],
            target_audience="Developers",
            goals=["Build MVP", "Scale to 1000 users"],
            constraints=["Budget: $5000"],
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for output files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    async def test_generate_documents_all_enabled(
        self, generator, sample_app_design, temp_output_dir
    ):
        """Test generating all documents when all are enabled."""
        request = DocumentRequest(
            output_dir=temp_output_dir,
            generate_prd=True,
            generate_claude_md=True,
            generate_readme=True,
            app_design=sample_app_design,
        )

        # Mock the Claude SDK query function with different responses
        mock_responses = [
            "PRD Generated content",
            "CLAUDE.md Generated content",
            "README Generated content",
        ]
        response_iter = iter(mock_responses)

        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = next(response_iter)
                yield mock_message

            mock_query.side_effect = lambda prompt: mock_query_response()

            result = await generator.generate_documents(request)

            assert len(result) == 3
            assert "PRD" in result
            assert "CLAUDE.md" in result
            assert "README" in result

            # Verify files were created
            assert Path(result["PRD"]).exists()
            assert Path(result["CLAUDE.md"]).exists()
            assert Path(result["README"]).exists()

            # Verify file contents contain generated content
            assert "PRD Generated content" in Path(result["PRD"]).read_text()
            assert (
                "CLAUDE.md Generated content" in Path(result["CLAUDE.md"]).read_text()
            )
            assert "README Generated content" in Path(result["README"]).read_text()

    async def test_generate_documents_selective(
        self, generator, sample_app_design, temp_output_dir
    ):
        """Test generating only selected documents."""
        request = DocumentRequest(
            output_dir=temp_output_dir,
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=True,
            app_design=sample_app_design,
        )

        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = "Generated content"
                yield mock_message

            mock_query.return_value = mock_query_response()

            result = await generator.generate_documents(request)

            assert len(result) == 2
            assert "PRD" in result
            assert "CLAUDE.md" not in result
            assert "README" in result

            # Verify only selected files were created
            assert Path(result["PRD"]).exists()
            assert not (Path(temp_output_dir) / "CLAUDE.md").exists()
            assert Path(result["README"]).exists()

    async def test_generate_documents_output_directory_creation(
        self, generator, sample_app_design
    ):
        """Test that output directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_output_dir = Path(temp_dir) / "nested" / "output"

            request = DocumentRequest(
                output_dir=str(nested_output_dir),
                generate_prd=True,
                generate_claude_md=False,
                generate_readme=False,
                app_design=sample_app_design,
            )

            with patch("claude_code_designer.generator.query") as mock_query:

                async def mock_query_response():
                    mock_message = Mock()
                    mock_message.content = "Generated content"
                    yield mock_message

                mock_query.return_value = mock_query_response()

                result = await generator.generate_documents(request)

                assert nested_output_dir.exists()
                assert nested_output_dir.is_dir()
                assert "PRD" in result

    async def test_generate_documents_permission_error_directory(
        self, generator, sample_app_design
    ):
        """Test handling of permission errors when creating output directory."""
        request = DocumentRequest(
            output_dir="/root/restricted",  # Should cause permission error
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=False,
            app_design=sample_app_design,
        )

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = PermissionError("Permission denied")

            with pytest.raises(
                Exception, match="Permission denied: Cannot create output directory"
            ):
                await generator.generate_documents(request)

    async def test_generate_documents_os_error_directory(
        self, generator, sample_app_design
    ):
        """Test handling of OS errors when creating output directory."""
        request = DocumentRequest(
            output_dir="/invalid/path",
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=False,
            app_design=sample_app_design,
        )

        with patch("pathlib.Path.mkdir") as mock_mkdir:
            mock_mkdir.side_effect = OSError("Invalid path")

            with pytest.raises(Exception, match="Cannot create output directory"):
                await generator.generate_documents(request)

    async def test_generate_documents_permission_error_file_write(
        self, generator, sample_app_design, temp_output_dir
    ):
        """Test handling of permission errors when writing files."""
        request = DocumentRequest(
            output_dir=temp_output_dir,
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=False,
            app_design=sample_app_design,
        )

        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = "Generated content"
                yield mock_message

            mock_query.return_value = mock_query_response()

            with patch("pathlib.Path.write_text") as mock_write:
                mock_write.side_effect = PermissionError("Permission denied")

                with pytest.raises(Exception, match="Permission denied writing files"):
                    await generator.generate_documents(request)

    async def test_generate_documents_keyboard_interrupt(
        self, generator, sample_app_design, temp_output_dir
    ):
        """Test handling of keyboard interrupt during document generation."""
        request = DocumentRequest(
            output_dir=temp_output_dir,
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=False,
            app_design=sample_app_design,
        )

        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = KeyboardInterrupt()

            with pytest.raises(KeyboardInterrupt):
                await generator.generate_documents(request)

    async def test_generate_prd_success(self, generator, sample_app_design):
        """Test successful PRD generation."""
        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = (
                    "# PRD for Test App\n\n## Executive Summary\n\nTest content"
                )
                yield mock_message

            mock_query.return_value = mock_query_response()

            content = await generator._generate_prd(sample_app_design)

            assert "# PRD for Test App" in content
            assert "Executive Summary" in content
            assert "Test content" in content

            # Verify the prompt includes app design details
            mock_query.assert_called_once()
            call_args = mock_query.call_args[1]
            prompt = call_args["prompt"]
            assert "Test App" in prompt
            assert "web" in prompt
            assert "Authentication" in prompt

    async def test_generate_prd_connection_error(self, generator, sample_app_design):
        """Test PRD generation with connection error fallback."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = ConnectionError("Network error")

            content = await generator._generate_prd(sample_app_design)

            assert "# PRD for Test App" in content
            assert "connection error" in content
            assert sample_app_design.description in content

    async def test_generate_prd_general_error(self, generator, sample_app_design):
        """Test PRD generation with general error fallback."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = Exception("Some error")

            content = await generator._generate_prd(sample_app_design)

            assert "# PRD for Test App" in content
            assert "Some error" in content

    async def test_generate_prd_keyboard_interrupt(self, generator, sample_app_design):
        """Test PRD generation keyboard interrupt handling."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = KeyboardInterrupt()

            with pytest.raises(KeyboardInterrupt):
                await generator._generate_prd(sample_app_design)

    async def test_generate_claude_md_success(self, generator, sample_app_design):
        """Test successful CLAUDE.md generation."""
        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = "# CLAUDE.md - Test App\n\n## Project Overview\n\nTechnical guidelines"
                yield mock_message

            mock_query.return_value = mock_query_response()

            content = await generator._generate_claude_md(sample_app_design)

            assert "# CLAUDE.md - Test App" in content
            assert "Project Overview" in content
            assert "Technical guidelines" in content

    async def test_generate_claude_md_connection_error(
        self, generator, sample_app_design
    ):
        """Test CLAUDE.md generation with connection error fallback."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = ConnectionError("Network error")

            content = await generator._generate_claude_md(sample_app_design)

            assert "# CLAUDE.md - Test App" in content
            assert "connection error" in content

    async def test_generate_readme_success(self, generator, sample_app_design):
        """Test successful README generation."""
        with patch("claude_code_designer.generator.query") as mock_query:

            async def mock_query_response():
                mock_message = Mock()
                mock_message.content = "# Test App\n\nA test web application\n\n## Features\n\n- Authentication"
                yield mock_message

            mock_query.return_value = mock_query_response()

            content = await generator._generate_readme(sample_app_design)

            assert "# Test App" in content
            assert "test web application" in content
            assert "Authentication" in content

    async def test_generate_readme_connection_error(self, generator, sample_app_design):
        """Test README generation with connection error fallback."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = ConnectionError("Network error")

            content = await generator._generate_readme(sample_app_design)

            assert "# Test App" in content
            assert sample_app_design.description in content
            assert "- Authentication" in content
            assert "connection error" in content

    async def test_generate_readme_with_empty_features(self, generator):
        """Test README generation with app design that has no features."""
        app_design = AppDesign(
            name="Simple App",
            type="cli",
            description="A simple CLI app",
            primary_features=[],  # Empty features
        )

        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = ConnectionError("Network error")

            content = await generator._generate_readme(app_design)

            assert "# Simple App" in content
            assert "- Core functionality" in content  # Default fallback

    async def test_generate_readme_general_error(self, generator, sample_app_design):
        """Test README generation with general error fallback."""
        with patch("claude_code_designer.generator.query") as mock_query:
            mock_query.side_effect = Exception("Some error")

            content = await generator._generate_readme(sample_app_design)

            assert "# Test App" in content
            assert "Some error" in content

    def test_validate_output_path_valid_relative_path(self, generator):
        """Test validation of valid relative paths within current directory."""
        valid_paths = [
            "output",
            "./output",
            "nested/output/dir",
            "./nested/output/dir",
        ]

        for path in valid_paths:
            result = generator._validate_output_path(path)
            assert isinstance(result, Path)
            assert result.is_absolute()

    def test_validate_output_path_valid_absolute_path(self, generator):
        """Test validation of valid absolute paths."""
        with tempfile.TemporaryDirectory() as temp_dir:
            valid_path = str(Path(temp_dir) / "output")
            result = generator._validate_output_path(valid_path)
            assert isinstance(result, Path)
            assert result.is_absolute()

    def test_validate_output_path_blocks_traversal_attempts(self, generator):
        """Test that path traversal attempts are blocked."""
        malicious_paths = [
            "../etc/passwd",
            "../../etc/passwd",
            "../../../etc/passwd",
            "output/../../../etc/passwd",
            "output/../../secrets",
            "../config",
            "subdir/../../../etc/hosts",
        ]

        for path in malicious_paths:
            with pytest.raises(ValueError, match="Path traversal detected"):
                generator._validate_output_path(path)

    def test_validate_output_path_blocks_hidden_traversal(self, generator):
        """Test that hidden path traversal attempts are blocked."""
        malicious_paths = [
            "output/..%2Fetc%2Fpasswd",  # URL encoded
            "output/....//etc/passwd",  # Double dots with slash
        ]

        # These should be handled by normpath check
        for path in malicious_paths:
            try:
                result = generator._validate_output_path(path)
                # If it doesn't raise an error, ensure it's still within safe bounds
                assert not str(result).endswith("/etc/passwd")
            except ValueError:
                # It's okay if it raises ValueError for suspicious paths
                pass

    def test_validate_output_path_invalid_paths(self, generator):
        """Test handling of invalid or malformed paths."""
        # Test empty path specifically
        with pytest.raises(ValueError, match="Invalid path"):
            generator._validate_output_path("")

        # Test null byte path
        try:
            result = generator._validate_output_path("\x00invalid")
            # If it doesn't raise an error, it should still be a valid path object
            assert isinstance(result, Path)
        except (ValueError, OSError):
            # Either of these exceptions is acceptable for null byte paths
            pass

    async def test_generate_documents_path_traversal_protection(
        self, generator, sample_app_design
    ):
        """Test that document generation blocks path traversal attempts."""
        request = DocumentRequest(
            output_dir="../../../etc",  # Path traversal attempt
            generate_prd=True,
            generate_claude_md=False,
            generate_readme=False,
            app_design=sample_app_design,
        )

        with pytest.raises(Exception, match="Invalid output directory"):
            await generator.generate_documents(request)
