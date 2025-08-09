# CLAUDE.md - Claude Code Designer

1. You MUST read the @README.md
2. You MUST read the @guidelines/agent-guidelines.md
3. You MUST read the @PRD.md for interface design goals

## Project Overview

Claude Code Designer is a simple Python CLI application that provides AI-powered interactive design assistance using the Claude Code SDK. The application prioritizes simplicity and minimal maintenance over complex features, following KISS principles with basic async patterns and straightforward architecture.

## Error Prevention Rules
**MANDATORY**: Whenever I make a mistake and correct it, I MUST immediately add a prevention rule below.

When agent makes mistakes or user requests general coding changes, add rules here to prevent future occurrences:

### Type Hints
- ALWAYS use built-in types for type hints: `list`, `dict`, `tuple`, `set` instead of `List`, `Dict`, `Tuple`, `Set`
- Use `Union` from typing only when necessary, prefer `X | Y` syntax for Python 3.10+

### Testing
- When updating implementation, ALWAYS update corresponding tests to match new interface
- Run tests with `uv run python -m pytest` (NOT `uv run pytest` or `PYTHONPATH=.`)
- Test file imports should match the actual module structure (`from src.module import Class`)
- ALWAYS verify class/function names exist before importing by checking the actual module file with Grep tool
- DO NOT assume class names - check `^class.*:` or `^def.*:` patterns in target files before writing imports

### Merge Conflicts
- When merging branches, always check if tests match the current implementation
- Prefer our branch's architectural decisions (logging, naming conventions, import structure)
- Update tests immediately after resolving conflicts to ensure they pass

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
├── __init__.py                  # Package initialization
├── cli.py                       # Command-line interface with all commands
├── design_assistant.py          # Core design assistant functionality
├── conversation_evaluator.py    # Conversation quality evaluation
├── simulator.py                 # Automated simulation system
├── learning_system.py           # Continuous learning from evaluations
└── save_claude_conversation.py  # Conversation history management

examples/
├── programmatic_usage.py        # Example of using DesignAssistant programmatically
├── evaluation_example.py        # Example of evaluating conversations
├── simulator_example.py         # Example of running simulations
└── learning_system_example.py   # Example of learning system usage
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
# Test design assistant CLI commands
uv run python -m claude_code_designer.cli --help
uv run python -m claude_code_designer.cli app --help
uv run python -m claude_code_designer.cli feature --help

# Test programmatic usage
uv run python -c "from claude_code_designer import DesignAssistant; print('✅ Import successful')"
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

### Design Assistant Architecture
- **App-Designer Subagent**: Uses specialized app-designer subagent for application and feature design
- **Conversation-Evaluator Subagent**: Uses specialized conversation-evaluator subagent for quality assessment
- **Interactive Sessions**: AI-powered conversations with expert domain knowledge
- **Conversation Storage**: JSON-based storage with timestamps and metadata
- **Programmatic Access**: DesignAssistant class for integration with other tools
- **Simple State Management**: Stateless conversations with preserved history
- **Automated Simulation**: DesignSimulator class for running synthetic test scenarios
- **Continuous Learning**: LearningSystem class for improving from evaluation results

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

### Using the Design Assistant

#### Interactive Application Design
```bash
# Start interactive application design
uv run python -m claude_code_designer.cli app

# Non-interactive with parameters
uv run python -m claude_code_designer.cli app --name "MyApp" --type web --non-interactive
```

#### Interactive Feature Design
```bash
# Start interactive feature design
uv run python -m claude_code_designer.cli feature

# Non-interactive with description
uv run python -m claude_code_designer.cli feature --description "OAuth login" --non-interactive
```

#### Evaluating Conversations
```bash
# Evaluate all conversations
uv run python -m claude_code_designer.cli evaluate

# Evaluate specific conversation
uv run python -m claude_code_designer.cli evaluate --conversation-file conversation_20250106.json
```

#### Running Simulations
```bash
# Run simulation with learning
uv run python -m claude_code_designer.cli simulate --cycles 5 --enable-learning

# Run app-only simulation
uv run python -m claude_code_designer.cli simulate --type app --cycles 3
```

#### Learning System
```bash
# Manually trigger learning
uv run python -m claude_code_designer.cli learn

# View knowledge statistics
uv run python -m claude_code_designer.cli knowledge-stats
```

#### Programmatic Usage
```python
from claude_code_designer import DesignAssistant, ConversationEvaluator
import asyncio

async def design_and_evaluate():
    # Design application
    assistant = DesignAssistant("./conversations")
    conversation = await assistant.design_application(
        project_name="MyApp",
        project_type="web",
        interactive=False
    )
    
    # Evaluate quality
    evaluator = ConversationEvaluator("./conversations", "./evaluations")
    evaluation = await evaluator.evaluate_conversation(conversation['file_path'])
    
    print(f"Quality score: {evaluation['scores']['overall']}/10")
    return conversation, evaluation

asyncio.run(design_and_evaluate())
```

#### Managing Conversations
```bash
# List saved conversations
uv run python -m claude_code_designer.cli list-conversations

# Conversations are saved as JSON files with timestamps
ls ./conversations/
```

### Adding Features (Consider if Really Needed)
1. **Design Modes**: Only add new design modes if absolutely essential - prefer improving existing app/feature modes
2. **Conversation Features**: Avoid adding complex conversation management - focus on simple save/list functionality
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
