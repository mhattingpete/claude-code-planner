"""Click-based CLI interface for Claude Code Designer."""

import asyncio
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .constants import DEFAULT_OUTPUT_DIR, PANEL_STYLES
from .generator import DocumentGenerator
from .models import AppDesign, DocumentRequest
from .questionnaire import InteractiveQuestionnaire

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """Claude Code Designer - Generate project documentation using Claude Code SDK."""
    pass


@main.command()
@click.option(
    "--output-dir",
    default=DEFAULT_OUTPUT_DIR,
    help="Output directory for generated documents",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, path_type=Path),
)
@click.option("--skip-prd", is_flag=True, help="Skip PRD.md generation")
@click.option("--skip-claude-md", is_flag=True, help="Skip CLAUDE.md generation")
@click.option("--skip-readme", is_flag=True, help="Skip README.md generation")
def design(
    output_dir: Path,
    skip_prd: bool,
    skip_claude_md: bool,
    skip_readme: bool,
) -> None:
    """Start the interactive design process."""
    try:
        asyncio.run(
            _run_design_process(
                output_dir=output_dir,
                skip_prd=skip_prd,
                skip_claude_md=skip_claude_md,
                skip_readme=skip_readme,
            )
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Design process interrupted by user[/yellow]")
        raise click.Abort() from None
    except Exception as e:
        console.print(f"\n[red]Error during design process: {e}[/red]")
        raise click.Abort() from e


async def _run_design_process(
    output_dir: Path,
    skip_prd: bool,
    skip_claude_md: bool,
    skip_readme: bool,
) -> None:
    """Run the complete design process."""
    try:
        # Initialize questionnaire and run it
        questionnaire = InteractiveQuestionnaire()
        app_design = await questionnaire.run_questionnaire()

        # Display design summary
        _display_design_summary(app_design)

        # Confirm generation
        if not click.confirm("\nGenerate project documents?", default=False):
            console.print("[yellow]Document generation cancelled[/yellow]")
            return

        # Create document request
        doc_request = DocumentRequest(
            output_dir=str(output_dir.resolve()),
            generate_prd=not skip_prd,
            generate_claude_md=not skip_claude_md,
            generate_readme=not skip_readme,
            app_design=app_design,
        )

        # Generate documents
        console.print("\n[blue]Generating documents...[/blue]")
        generator = DocumentGenerator()
        generated_files = await generator.generate_documents(doc_request)

        # Display results
        _display_generation_results(generated_files, output_dir)

    except KeyboardInterrupt:
        raise
    except ConnectionError:
        console.print(
            "\n[red]Network connection error. Please check your internet connection and try again.[/red]"
        )
        raise click.Abort() from None
    except OSError as e:
        console.print(f"\n[red]File system error: {e}[/red]")
        raise click.Abort() from e
    except ValueError as e:
        console.print(f"\n[red]Configuration error: {e}[/red]")
        raise click.Abort() from e
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        raise click.Abort() from e


def _display_design_summary(app_design: AppDesign) -> None:
    """Display summary of collected design information."""
    summary_panel = Panel.fit(
        f"[bold]Application:[/bold] {app_design.name}\n"
        f"[bold]Type:[/bold] {app_design.type}\n"
        f"[bold]Description:[/bold] {app_design.description}\n"
        f"[bold]Features:[/bold] {', '.join(app_design.primary_features) or 'None specified'}\n"
        f"[bold]Tech Stack:[/bold] {', '.join(app_design.tech_stack) or 'None specified'}",
        title="Design Summary",
        border_style=PANEL_STYLES["summary"],
    )
    console.print(summary_panel)


def _display_generation_results(
    generated_files: dict[str, str], output_dir: Path
) -> None:
    """Display the results of document generation."""
    if not generated_files:
        console.print("[yellow]No documents were generated[/yellow]")
        return

    # Success message
    success_message = (
        f"[green]✓ Successfully generated {len(generated_files)} documents![/green]"
    )
    console.print(success_message)
    console.print(f"[dim]Output directory: {output_dir.resolve()}[/dim]")

    # Table of generated files
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Document", style="cyan")
    table.add_column("File Path", style="dim")

    for doc_name, file_path in generated_files.items():
        table.add_row(doc_name, file_path)

    console.print(table)


@main.command()
def info() -> None:
    """Display information about Claude Code Designer."""
    info_panel = Panel.fit(
        "[bold blue]Claude Code Designer[/bold blue]\n\n"
        "Simple CLI for generating essential project documentation\n"
        "using the Claude Code SDK.\n\n"
        "[bold]Commands:[/bold]\n"
        "  design    Start interactive design process\n"
        "  info      Show this information\n\n"
        "[bold]Options for design command:[/bold]\n"
        "  --output-dir PATH     Output directory (default: current)\n"
        "  --skip-prd           Skip PRD.md generation\n"
        "  --skip-claude-md     Skip CLAUDE.md generation\n"
        "  --skip-readme        Skip README.md generation\n\n"
        "[bold]Examples:[/bold]\n"
        "  claude-designer design\n"
        "  claude-designer design --output-dir ./my-project\n"
        "  claude-designer design --skip-prd --skip-readme",
        title="Information",
        border_style=PANEL_STYLES["info"],
    )
    console.print(info_panel)


if __name__ == "__main__":
    main()
