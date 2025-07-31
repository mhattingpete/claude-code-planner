"""Click-based CLI interface for Claude Code Designer."""

import click


@click.group()
@click.version_option()
def main():
    """Claude Code Designer - Generate project documentation using Claude Code SDK."""
    pass


@main.command()
@click.option("--output-dir", default=".", help="Output directory for generated documents")
def design(output_dir: str):
    """Start the interactive design process."""
    click.echo("Claude Code Designer - Design process starting...")
    click.echo(f"Output directory: {output_dir}")


if __name__ == "__main__":
    main()
