# Claude Code Designer

Simple, minimal-maintenance CLI for generating essential project documentation using Claude Code SDK

## Features

- **Simple Questionnaire**: Essential questions to capture core project details
- **Minimal Document Generation**: Creates only the documentation you need: PRD, CLAUDE.md, and README
- **Clean Terminal Interface**: Straightforward CLI without unnecessary complexity
- **Basic Output Options**: Simple controls for document generation and location

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

### Basic Usage

Start the interactive design process:

```bash
claude-designer design
```

### Advanced Options

```bash
# Specify output directory
claude-designer design --output-dir ./my-project

# Skip specific documents
claude-designer design --skip-prd --skip-claude-md

# Get help
claude-designer --help
claude-designer info
```

### What It Looks Like

```bash
$ claude-designer design

  Getting Started  
 Welcome to Claude 
 Code Designer     
                   
 Let's design your 
 application...    
                   

  Question app_type  
 What type of        
 application?        
                     

  1. Web Application
  2. CLI Tool
  3. API Service
  4. Mobile App

Select option [1]: 2

# ... more questions ...

  Design Summary  
 Application: my-cli-tool 
 Type: cli tool          
 Tech Stack: Python      
 Features: CLI, Config   
                         

Generate project documents? [y/N]: y

✅ Successfully generated 3 documents!
   Output directory: /current/directory
```

## Generated Documents

### PRD.md
Essential Product Requirements Document with:
- Concise summary and core goals
- Basic requirements without over-specification
- Simple success metrics
- Minimal timeline estimates

### CLAUDE.md
Simple technical guidelines:
- Basic development rules focused on maintainability
- Essential commands and workflows
- Simple architecture principles (KISS > SOLID > DRY)
- Minimal maintenance procedures

### README.md
Clear project documentation:
- Simple installation steps
- Basic usage examples
- Essential information only
- No unnecessary complexity

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

- **`models.py`**: Defines what data we collect and how we validate it
- **`questionnaire.py`**: Handles the conversation with users and collects their answers
- **`generator.py`**: Takes those answers and creates beautiful documents
- **`cli.py`**: The command-line interface that ties everything together

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
- Interactive questionnaire that asks the right questions
- Generates three essential documents every project needs
- Clean, simple interface that doesn't get in your way
- Reliable integration with Claude AI