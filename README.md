# Claude Code Designer

Interactive AI-powered design assistant using Claude Code SDK for application and feature design guidance

## Features

- **Interactive Design Assistant**: AI-powered application and feature design guidance using app-designer subagent
- **Clean Terminal Interface**: Straightforward CLI without unnecessary complexity  
- **Conversation History**: Automatically saves design sessions for future reference
- **Programmatic API**: Use design assistant functionality from other Python scripts

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js (for Claude Code CLI)
- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`

### Install from PyPI (Coming Soon)

```bash
pip install claude-code-designer
```

### Install from Source

```bash
git clone https://github.com/anthropics/claude-code-designer
cd claude-code-designer
uv sync --dev
```

## Usage

### Design Assistant (New!)

Get AI-powered help designing applications and features:

```bash
# Design a new application interactively
uv run python -m claude_code_designer.cli app

# Design a new feature
uv run python -m claude_code_designer.cli feature

# Non-interactive mode with parameters
uv run python -m claude_code_designer.cli app --name "MyApp" --type web --non-interactive

# List saved conversation history
uv run python -m claude_code_designer.cli list-conversations
```


### Programmatic Usage

Use the design assistant from other Python scripts:

```python
from claude_code_designer import DesignAssistant
import asyncio

async def design_my_app():
    assistant = DesignAssistant("./conversations")
    
    # Design a new application
    conversation = await assistant.design_application(
        project_name="TaskTracker Pro",
        project_type="web",
        interactive=False,
        max_turns=10
    )
    
    print(f"Design completed with {conversation['output']['message_count']} messages")

asyncio.run(design_my_app())
```

### What It Looks Like

```bash
$ uv run python -m claude_code_designer.cli app

🚀 Application Design Assistant

What's the name of your project? TaskTracker Pro
What type of application are you building? [web/cli/api/mobile/desktop/library/other] (web): web

Starting app-designer design session...
Starting conversation with prompt: I need comprehensive application design assistance...
Received message: TextMessage
Received message: ToolUseMessage
...

✅ Design session completed with 8 messages
Conversation saved to: ./conversations/20250106_123456_I_need_comprehensive_application.json
```

## Configuration

Claude Code Designer follows your existing Claude Code CLI configuration. Ensure you're authenticated:

```bash
claude auth login
```

## For Developers

### Setting Up Your Dev Environment

```bash
# Get the source code
git clone https://github.com/anthropics/claude-code-designer
cd claude-code-designer

# Install everything you need
uv sync --dev
```

### Testing Your Changes

```bash
# Run the test suite
uv run pytest
```

### Keeping Code Clean

```bash
# Check for issues and fix formatting
uv run ruff check .
uv run ruff format .
```

### Installing Your Local Version

```bash
# Install your development version
uv pip install -e .
```

## How It's Built

- **`cli.py`**: Interactive design assistant and command-line interface
- **`save_claude_conversation.py`**: Saves conversation history for future reference

## Want to Help?

**Our Philosophy**: Every change should make things simpler, not more complicated.

1. Fork the repository on GitHub
2. Make a small, focused improvement
3. Test that your change works
4. Clean up your code with: `uv run ruff check --fix .`
5. Send us a pull request

### What We Value

- **Simple Solutions**: We prefer code that's easy to understand over code that's clever
- **Focused Features**: We say "no" to most new features to keep things simple
- **Easy Maintenance**: Every line of code needs to be maintained forever
- **Keep It Simple**: Simple code beats fancy design patterns every time

## Technical Requirements

- **Python 3.11+** - The programming language we're built on
- **Claude Code SDK** - How we talk to Claude AI
- **Click 8.1+** - Makes our command-line interface nice to use
- **Rich 13.0+** - Adds colors and formatting to the terminal
- **Pydantic 2.0+** - Helps us validate data properly

## License

MIT License - see LICENSE file for details.

## Need Help?

- **Found a Bug?** Tell us about it on GitHub Issues
- **Want a Feature?** Suggest it on GitHub (but remember, we keep things simple!)
- **Questions?** Check out PRD.md for project details or CLAUDE.md for technical info

## Version History

### v0.1.0 (First Release)
- Interactive design assistant for applications and features
- Conversation history saving and management
- Programmatic API for integration with other tools
- Clean, simple interface that doesn't get in your way
- Reliable integration with Claude AI