"""Document generation engine using Claude Code SDK."""

from pathlib import Path

from claude_code_sdk import query

from .models import AppDesign, DocumentRequest


class DocumentGenerator:
    """Generates project documents using Claude Code SDK."""

    async def generate_documents(self, request: DocumentRequest) -> dict[str, str]:
        """Generate all requested documents and save to output directory.

        Args:
            request: Document generation request with app design and options

        Returns:
            Dictionary mapping document names to their file paths
        """
        try:
            output_dir = Path(request.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
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
                prd_path = output_dir / "PRD.md"
                prd_path.write_text(prd_content, encoding="utf-8")
                generated_files["PRD"] = str(prd_path)

            if request.generate_claude_md:
                claude_md_content = await self._generate_claude_md(request.app_design)
                claude_md_path = output_dir / "CLAUDE.md"
                claude_md_path.write_text(claude_md_content, encoding="utf-8")
                generated_files["CLAUDE.md"] = str(claude_md_path)

            if request.generate_readme:
                readme_content = await self._generate_readme(request.app_design)
                readme_path = output_dir / "README.md"
                readme_path.write_text(readme_content, encoding="utf-8")
                generated_files["README"] = str(readme_path)

        except KeyboardInterrupt:
            raise
        except PermissionError as e:
            raise Exception(
                f"Permission denied writing files to {output_dir}: {e}"
            ) from e
        except OSError as e:
            raise Exception(f"Error writing files to {output_dir}: {e}") from e

        return generated_files

    async def _generate_prd(self, design: AppDesign) -> str:
        """Generate PRD.md content based on app design."""
        prompt = f"""Generate a Product Requirements Document (PRD) for the following application:

Application Name: {design.name}
Type: {design.type}
Description: {design.description}
Primary Features: {", ".join(design.primary_features)}
Tech Stack: {", ".join(design.tech_stack)}
Target Audience: {design.target_audience or "Not specified"}
Goals: {", ".join(design.goals)}
Constraints: {", ".join(design.constraints)}

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
            async for message in query(prompt=prompt):
                if hasattr(message, "content"):
                    content += message.content
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            content = f"# PRD for {design.name}\n\n## Executive Summary\n\n{design.description}\n\n*Note: Full PRD generation failed due to connection error. Please regenerate when connection is restored.*"
        except Exception as e:
            content = f"# PRD for {design.name}\n\n## Executive Summary\n\n{design.description}\n\n*Note: PRD generation encountered an error: {str(e)}*"

        return content

    async def _generate_claude_md(self, design: AppDesign) -> str:
        """Generate CLAUDE.md technical guidelines."""
        prompt = f"""Generate a CLAUDE.md technical guidelines document for this application:

Application Name: {design.name}
Type: {design.type}
Tech Stack: {", ".join(design.tech_stack)}
Primary Features: {", ".join(design.primary_features)}

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
            async for message in query(prompt=prompt):
                if hasattr(message, "content"):
                    content += message.content
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            content = f"# CLAUDE.md - {design.name}\n\n## Project Overview\n\n{design.description}\n\n*Note: Full CLAUDE.md generation failed due to connection error. Please regenerate when connection is restored.*"
        except Exception as e:
            content = f"# CLAUDE.md - {design.name}\n\n## Project Overview\n\n{design.description}\n\n*Note: CLAUDE.md generation encountered an error: {str(e)}*"

        return content

    async def _generate_readme(self, design: AppDesign) -> str:
        """Generate README.md user documentation."""
        prompt = f"""Generate a README.md file for this application:

Application Name: {design.name}
Type: {design.type}
Description: {design.description}
Primary Features: {", ".join(design.primary_features)}
Tech Stack: {", ".join(design.tech_stack)}
Target Audience: {design.target_audience or "General users"}

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
            async for message in query(prompt=prompt):
                if hasattr(message, "content"):
                    content += message.content
        except KeyboardInterrupt:
            raise
        except ConnectionError:
            features = (
                "\n".join([f"- {f}" for f in design.primary_features])
                if design.primary_features
                else "- Core functionality"
            )
            content = f"# {design.name}\n\n{design.description}\n\n## Features\n\n{features}\n\n*Note: Full README generation failed due to connection error. Please regenerate when connection is restored.*"
        except Exception as e:
            content = f"# {design.name}\n\n{design.description}\n\n*Note: README generation encountered an error: {str(e)}*"

        return content
