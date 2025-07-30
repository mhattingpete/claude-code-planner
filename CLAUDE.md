# CLAUDE.md - Claude Code Designer

1. You MUST read the @README.md
2. You MUST read the @guidelines/agent-guidelines.md
3. You MUST read the @PRD.md for interface design goals

## Project Overview

Claude Code Designer is a simple Python CLI application that generates essential project documentation using the Claude Code SDK. The application prioritizes simplicity and minimal maintenance over complex features, following KISS principles with basic async patterns and straightforward architecture.

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js (for Claude Code CLI)
- uv package manager

### Initial Setup
```bash
git clone <repository>
cd claude-code-designer
uv sync --dev
```

### Environment Requirements
```bash
# Install Claude Code CLI globally
npm install -g @anthropic-ai/claude-code

# Authenticate Claude Code
claude auth login
```

## Project Structure

```
claude_code_designer/
├── __init__.py          # Package initialization
├── models.py            # Pydantic data models
├── questionnaire.py     # Interactive question system
├── generator.py         # Document generation engine
└── cli.py              # Click-based CLI interface
```

## Common Commands

### Development
```bash
# Install dependencies
uv sync --dev

# Run linting
uv run ruff check .
uv run ruff format .
uv run ruff check --fix

# Run tests
uv run pytest
uv run pytest --cov=claude_code_designer

# Local installation
uv pip install -e .
```

### Testing the CLI
```bash
# Test basic functionality
python hello.py

# Test CLI commands
uv run python -m claude_code_designer.cli --help
uv run python -m claude_code_designer.cli design --help
```

## Architecture Principles

### Simplicity First
- Minimal abstractions - avoid over-engineering
- Simple document templates without complex inheritance
- Basic prompt strategies focusing on essential content

### Minimal Maintenance Design
- Straightforward question flow with minimal dynamic complexity
- Essential async patterns only - no premature optimization
- Simple error handling without extensive recovery mechanisms

## Code Quality Standards

### Type Hints
- All functions must have type hints
- Use modern Python syntax: `list[str]` instead of `List[str]`
- Optional types: `str | None` instead of `Optional[str]`

### Error Handling
```python
# Preferred pattern for SDK interactions
try:
    async for message in query(prompt=prompt, options=options):
        # Process message
        pass
except KeyboardInterrupt:
    # Handle user interruption
    pass
except Exception as e:
    # Log and handle errors gracefully
    pass
```

### Pydantic Models
- Use Pydantic for all data validation
- Provide clear docstrings for model fields
- Use Field() for complex validation and defaults

## Common Workflows

### Adding Features (Consider if Really Needed)
1. **Question Types**: Only add if absolutely essential - prefer simplifying existing questions
2. **Document Types**: Avoid adding new types - focus on improving the three core documents
3. **General Rule**: Every new feature increases maintenance overhead - default to "no" unless critical

### Debugging Claude Code SDK Issues
```python
# Add debug logging to see API responses
import logging
logging.basicConfig(level=logging.DEBUG)

# Check message structure
async for message in query(prompt=prompt, options=options):
    print(f"Message type: {type(message)}")
    print(f"Message content: {message.content}")
```

## Common Errors and Solutions

### "No solution found when resolving dependencies"
```bash
# Check available versions
uv tree
# Update pyproject.toml with correct version constraints
```

### "claude command not found"
```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Check PATH includes npm global binaries
npm config get prefix
```

### Claude Code SDK Connection Issues
```bash
# Verify authentication
claude auth status

# Check API connectivity
claude api test
```

### Import Errors in Development
```bash
# Ensure package is installed in development mode
uv pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"
```

## Testing Approach

### Unit Tests
- Test individual functions in isolation
- Mock Claude Code SDK responses
- Validate Pydantic model behavior

### Integration Tests
- Test CLI command execution
- Test document generation end-to-end
- Test question flow logic

### Manual Testing
```bash
# Test different question flows
claude-designer design --output-dir ./test-output

# Test error scenarios
# - Interrupt with Ctrl+C
# - Invalid directory permissions
# - Network connectivity issues
```

## Minimal Maintenance Approach

### Simple Rate Handling
- Basic retry logic - avoid complex exponential backoff
- Simple progress indication without fancy animations
- Fail gracefully rather than implementing complex recovery

### Resource Management
- Basic async cleanup - don't over-optimize
- Simple memory patterns - avoid premature optimization
- Fast startup through minimal dependencies

## Deployment Guidelines

### Package Distribution
```bash
# Build package
uv build

# Check package contents
tar -tzf dist/*.tar.gz
```

### Version Management
- Update `__init__.py` version
- Update `pyproject.toml` version
- Tag releases in git: `git tag v0.1.0`

## Security Considerations

- Never log or store API keys
- Validate all user inputs
- Sanitize file paths for output directories
- Follow principle of least privilege

## Code Review Checklist

- [ ] Code follows KISS principle - no unnecessary complexity
- [ ] Essential type hints only (not exhaustive)
- [ ] Simple error handling - fail fast when appropriate
- [ ] Basic async usage without over-abstraction
- [ ] Minimal Pydantic validation - sensible defaults
- [ ] Basic tests for core functionality
- [ ] Simple linting compliance

## Contributing Guidelines

1. **Simplicity First**: Every contribution should reduce complexity, not add it
2. **Minimal Features**: Default to "no" for new features - focus on core functionality
3. **Low Maintenance**: Consider long-term maintenance cost of every change
4. **Essential Tests**: Test core paths, avoid test bloat
5. **Clear Intent**: Simple, direct code over clever abstractions
6. **Small Changes**: Prefer many small, focused changes to large refactors

## Troubleshooting

### Development Issues
- Check Python version: `python --version`
- Verify uv installation: `uv --version`
- Check package installation: `uv pip list`

### Runtime Issues
- Enable debug logging: `export CLAUDE_CODE_DEBUG=1`
- Check CLI permissions: `ls -la $(which claude-designer)`
- Verify working directory permissions
