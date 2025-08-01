"""Document generation engine using Claude Code SDK."""

import os
from pathlib import Path

from claude_code_sdk import query

from .constants import DEFAULT_ENCODING, DOCUMENT_TYPES, ERROR_MESSAGES
from .models import AppDesign, DocumentRequest


class DocumentGenerator:
    """Generates project documents using Claude Code SDK."""

    def _validate_output_path(self, path: str) -> Path:
        """Validate and sanitize output directory path to prevent path traversal.

        Args:
            path: User-provided output directory path

        Returns:
            Validated Path object

        Raises:
            ValueError: If path contains path traversal attempts or is invalid
        """
        # Check for obviously invalid paths upfront
        if not path or path.isspace():
            raise ValueError("Invalid path: empty or whitespace-only path")

        try:
            # Additional check for common path traversal patterns in the original string
            normalized_path = os.path.normpath(path)
            if ".." in normalized_path or normalized_path.startswith("../"):
                raise ValueError(f"Path traversal detected in path: {path}")

            # Convert to absolute path and resolve any symbolic links
            resolved_path = Path(path).resolve()

            # Get current working directory as base
            cwd = Path.cwd().resolve()

            # Check if the resolved path is within or equal to current directory tree
            try:
                resolved_path.relative_to(cwd)
            except ValueError as e:
                # Path is outside current directory tree, check if it's a valid absolute path
                if not resolved_path.is_absolute():
                    raise ValueError(f"Invalid path: {path}") from e

                # For absolute paths, ensure they don't contain obvious traversal patterns
                path_parts = resolved_path.parts
                if any(part in (".", "..") for part in path_parts):
                    raise ValueError(f"Path traversal detected in path: {path}") from e

            return resolved_path

        except (OSError, RuntimeError) as e:
            raise ValueError(f"Invalid path: {path} - {e}") from e

    async def generate_documents(self, request: DocumentRequest) -> dict[str, str]:
        """Generate all requested documents and save to output directory.

        Args:
            request: Document generation request with app design and options

        Returns:
            Dictionary mapping document names to their file paths
        """
        try:
            # Validate output directory path to prevent path traversal
            output_dir = self._validate_output_path(request.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        except ValueError as e:
            raise Exception(f"Invalid output directory: {e}") from e
        except PermissionError as e:
            raise Exception(
                f"Permission denied: Cannot create output directory {request.output_dir}"
            ) from e
        except OSError as e:
            raise Exception(
                f"Cannot create output directory {request.output_dir}: {e}"
            ) from e

        generated_files = {}

        try:
            if request.generate_prd:
                prd_content = await self._generate_prd(request.app_design)
                prd_path = output_dir / f"messages_{DOCUMENT_TYPES['PRD']}"
                prd_path.write_text(prd_content, encoding=DEFAULT_ENCODING)
                generated_files["PRD"] = str(prd_path)

            if request.generate_claude_md:
                claude_md_content = await self._generate_claude_md(request.app_design)
                claude_md_path = output_dir / f"messages_{DOCUMENT_TYPES['CLAUDE_MD']}"
                claude_md_path.write_text(claude_md_content, encoding=DEFAULT_ENCODING)
                generated_files["CLAUDE.md"] = str(claude_md_path)

            if request.generate_readme:
                readme_content = await self._generate_readme(request.app_design)
                readme_path = output_dir / f"messages_{DOCUMENT_TYPES['README']}"
                readme_path.write_text(readme_content, encoding=DEFAULT_ENCODING)
                generated_files["README"] = str(readme_path)

        except KeyboardInterrupt:
            raise
        except PermissionError as e:
            raise Exception(
                f"Permission denied writing files to '{output_dir}'. "
                f"Please check that you have write access to this directory or try a different output location. "
                f"You can specify a different directory with --output-dir. Error details: {e}"
            ) from e
        except OSError as e:
            if e.errno == 28:  # No space left on device
                raise Exception(
                    f"Not enough disk space to write files to '{output_dir}'. "
                    f"Please free up disk space or choose a different output directory. Error details: {e}"
                ) from e
            elif e.errno == 2:  # No such file or directory
                raise Exception(
                    f"Output directory '{output_dir}' does not exist. "
                    f"Please create the directory first or choose an existing directory. Error details: {e}"
                ) from e
            else:
                raise Exception(
                    f"Failed to write files to '{output_dir}'. "
                    f"This might be due to filesystem issues, insufficient permissions, or disk space. "
                    f"Try using a different output directory with --output-dir. Error details: {e}"
                ) from e

        return generated_files

    async def _generate_prd(self, design: AppDesign) -> str:
        """Generate PRD.md content based on app design."""
        # Ensure string fields are strings and list fields are lists
        name = str(design.name) if design.name else "Application"
        app_type = str(design.type) if design.type else ""
        description = str(design.description) if design.description else ""
        target_audience = (
            str(design.target_audience) if design.target_audience else "Not specified"
        )

        primary_features = (
            design.primary_features
            if isinstance(design.primary_features, list)
            else [design.primary_features]
            if design.primary_features
            else []
        )
        tech_stack = (
            design.tech_stack
            if isinstance(design.tech_stack, list)
            else [design.tech_stack]
            if design.tech_stack
            else []
        )
        goals = (
            design.goals
            if isinstance(design.goals, list)
            else [design.goals]
            if design.goals
            else []
        )
        constraints = (
            design.constraints
            if isinstance(design.constraints, list)
            else [design.constraints]
            if design.constraints
            else []
        )

        prompt = f"""Generate a Product Requirements Document (PRD) for the following application:

Application Name: {name}
Type: {app_type}
Description: {description}
Primary Features: {", ".join(primary_features)}
Tech Stack: {", ".join(tech_stack)}
Target Audience: {target_audience}
Goals: {", ".join(goals)}
Constraints: {", ".join(constraints)}

Create a comprehensive PRD following this structure:
1. Executive Summary
2. Problem Statement
3. Goals and Objectives
4. Target Audience
5. User Stories and Requirements
6. Functional Requirements
7. Non-Functional Requirements
8. Technical Constraints
9. Timeline and Milestones

Keep it concise but comprehensive. Focus on essential requirements without over-specification."""

        content = ""
        try:
            query_stream = query(prompt=prompt)
            try:
                async for message in query_stream:
                    # Handle different message types from Claude Code SDK
                    if hasattr(message, "content") and message.content:
                        # Handle list of TextBlocks or similar
                        if isinstance(message.content, list):
                            for block in message.content:
                                if hasattr(block, "text"):
                                    content += str(block.text)
                        else:
                            content += str(message.content)
                    elif hasattr(message, "text") and message.text:
                        content += str(message.text)
                    elif hasattr(message, "data") and isinstance(message.data, dict):
                        # Skip system messages and other non-content messages
                        continue
            finally:
                if hasattr(query_stream, "aclose"):
                    await query_stream.aclose()
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            content = f"# PRD for {name}\n\n## Executive Summary\n\n{description}\n\n*Note: Full PRD generation failed due to connection error. Please regenerate when connection is restored.*"
        except (PermissionError, OSError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            content = f"# PRD for {name}\n\n## Executive Summary\n\n{description}\n\n*Note: PRD generation failed due to a system error. {troubleshooting} Error details: {str(e)}*"
        except (ValueError, TypeError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            content = f"# PRD for {name}\n\n## Executive Summary\n\n{description}\n\n*Note: PRD generation failed due to invalid data. {troubleshooting} Error details: {str(e)}*"
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "unauthorized" in error_msg:
                troubleshooting = ERROR_MESSAGES["authentication"]
            elif "rate limit" in error_msg or "too many requests" in error_msg:
                troubleshooting = ERROR_MESSAGES["rate_limit"]
            elif "timeout" in error_msg or "connection" in error_msg:
                troubleshooting = ERROR_MESSAGES["timeout"]
            else:
                troubleshooting = ERROR_MESSAGES["default"]

            content = f"# PRD for {name}\n\n## Executive Summary\n\n{description}\n\n*Note: PRD generation failed due to an API error. {troubleshooting} Error details: {str(e)}*"

        return content

    async def _generate_claude_md(self, design: AppDesign) -> str:
        """Generate CLAUDE.md technical guidelines."""
        # Ensure string fields are strings and list fields are lists
        name = str(design.name) if design.name else "Application"
        description = str(design.description) if design.description else ""
        app_type = str(design.type) if design.type else ""

        tech_stack = (
            design.tech_stack
            if isinstance(design.tech_stack, list)
            else [design.tech_stack]
            if design.tech_stack
            else []
        )
        primary_features = (
            design.primary_features
            if isinstance(design.primary_features, list)
            else [design.primary_features]
            if design.primary_features
            else []
        )

        prompt = f"""Generate a CLAUDE.md technical guidelines document for this application:

Application Name: {name}
Type: {app_type}
Tech Stack: {", ".join(tech_stack)}
Primary Features: {", ".join(primary_features)}

Create technical guidelines following this structure:
1. Project Overview
2. Development Setup
3. Common Commands
4. Architecture Principles
5. Code Quality Standards
6. Testing Approach
7. Deployment Guidelines

Focus on:
- KISS principles over complex patterns
- Essential commands and workflows
- Simple, maintainable code standards
- Basic testing requirements
- Minimal maintenance approach"""

        content = ""
        try:
            query_stream = query(prompt=prompt)
            try:
                async for message in query_stream:
                    # Handle different message types from Claude Code SDK
                    if hasattr(message, "content") and message.content:
                        # Handle list of TextBlocks or similar
                        if isinstance(message.content, list):
                            for block in message.content:
                                if hasattr(block, "text"):
                                    content += str(block.text)
                        else:
                            content += str(message.content)
                    elif hasattr(message, "text") and message.text:
                        content += str(message.text)
                    elif hasattr(message, "data") and isinstance(message.data, dict):
                        # Skip system messages and other non-content messages
                        continue
            finally:
                if hasattr(query_stream, "aclose"):
                    await query_stream.aclose()
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            content = f"# CLAUDE.md - {name}\n\n## Project Overview\n\n{description}\n\n*Note: Full CLAUDE.md generation failed due to connection error. Please regenerate when connection is restored.*"
        except (PermissionError, OSError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            content = f"# CLAUDE.md - {name}\n\n## Project Overview\n\n{description}\n\n*Note: CLAUDE.md generation failed due to a system error. {troubleshooting} Error details: {str(e)}*"
        except (ValueError, TypeError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            content = f"# CLAUDE.md - {name}\n\n## Project Overview\n\n{description}\n\n*Note: CLAUDE.md generation failed due to invalid data. {troubleshooting} Error details: {str(e)}*"
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "unauthorized" in error_msg:
                troubleshooting = ERROR_MESSAGES["authentication"]
            elif "rate limit" in error_msg or "too many requests" in error_msg:
                troubleshooting = ERROR_MESSAGES["rate_limit"]
            elif "timeout" in error_msg or "connection" in error_msg:
                troubleshooting = ERROR_MESSAGES["timeout"]
            else:
                troubleshooting = ERROR_MESSAGES["default"]

            content = f"# CLAUDE.md - {name}\n\n## Project Overview\n\n{description}\n\n*Note: CLAUDE.md generation failed due to an API error. {troubleshooting} Error details: {str(e)}*"

        return content

    async def _generate_readme(self, design: AppDesign) -> str:
        """Generate README.md user documentation."""
        # Ensure string fields are strings and list fields are lists
        name = str(design.name) if design.name else "Application"
        app_type = str(design.type) if design.type else ""
        description = str(design.description) if design.description else ""
        target_audience = (
            str(design.target_audience) if design.target_audience else "General users"
        )

        tech_stack = (
            design.tech_stack
            if isinstance(design.tech_stack, list)
            else [design.tech_stack]
            if design.tech_stack
            else []
        )
        primary_features = (
            design.primary_features
            if isinstance(design.primary_features, list)
            else [design.primary_features]
            if design.primary_features
            else []
        )

        prompt = f"""Generate a README.md file for this application:

Application Name: {name}
Type: {app_type}
Description: {description}
Primary Features: {", ".join(primary_features)}
Tech Stack: {", ".join(tech_stack)}
Target Audience: {target_audience}

Create a clear, user-focused README with:
1. Project title and brief description
2. Features list
3. Installation instructions
4. Usage examples
5. Configuration (if needed)
6. Contributing guidelines
7. License information

Keep it simple and focused on user needs. Avoid unnecessary technical complexity."""

        content = ""
        try:
            query_stream = query(prompt=prompt)
            try:
                async for message in query_stream:
                    # Handle different message types from Claude Code SDK
                    if hasattr(message, "content") and message.content:
                        # Handle list of TextBlocks or similar
                        if isinstance(message.content, list):
                            for block in message.content:
                                if hasattr(block, "text"):
                                    content += str(block.text)
                        else:
                            content += str(message.content)
                    elif hasattr(message, "text") and message.text:
                        content += str(message.text)
                    elif hasattr(message, "data") and isinstance(message.data, dict):
                        # Skip system messages and other non-content messages
                        continue
            finally:
                if hasattr(query_stream, "aclose"):
                    await query_stream.aclose()
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            features = (
                "\n".join([f"- {f}" for f in primary_features])
                if primary_features
                else "- Core functionality"
            )
            content = f"# {name}\n\n{description}\n\n## Features\n\n{features}\n\n*Note: Full README generation failed due to connection error. Please regenerate when connection is restored.*"
        except (PermissionError, OSError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            features = (
                "\n".join([f"- {f}" for f in primary_features])
                if primary_features
                else "- Core functionality"
            )
            content = f"# {name}\n\n{description}\n\n## Features\n\n{features}\n\n*Note: README generation failed due to a system error. {troubleshooting} Error details: {str(e)}*"
        except (ValueError, TypeError) as e:
            troubleshooting = ERROR_MESSAGES["default"]
            features = (
                "\n".join([f"- {f}" for f in primary_features])
                if primary_features
                else "- Core functionality"
            )
            content = f"# {name}\n\n{description}\n\n## Features\n\n{features}\n\n*Note: README generation failed due to invalid data. {troubleshooting} Error details: {str(e)}*"
        except Exception as e:
            error_msg = str(e).lower()
            if "authentication" in error_msg or "unauthorized" in error_msg:
                troubleshooting = ERROR_MESSAGES["authentication"]
            elif "rate limit" in error_msg or "too many requests" in error_msg:
                troubleshooting = ERROR_MESSAGES["rate_limit"]
            elif "timeout" in error_msg or "connection" in error_msg:
                troubleshooting = ERROR_MESSAGES["timeout"]
            else:
                troubleshooting = ERROR_MESSAGES["default"]

            features = (
                "\n".join([f"- {f}" for f in primary_features])
                if primary_features
                else "- Core functionality"
            )
            content = f"# {name}\n\n{description}\n\n## Features\n\n{features}\n\n*Note: README generation failed due to an API error. {troubleshooting} Error details: {str(e)}*"

        return content
