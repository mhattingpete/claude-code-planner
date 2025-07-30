#!/bin/bash

# Parse continuous flag
CONTINUOUS=false
if [[ "${1:-}" == "--continuous" || "${1:-}" == "-c" ]]; then
    CONTINUOUS=true
    shift
fi

# Check for help flag
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    cat << 'EOF'
Continuous Claude CLI Runner

USAGE:
    ./scripts/continuous_claude.sh [--continuous|-c] [PROMPT] [OUTPUT_FILE] [DELAY_SECONDS]

FLAGS:
    -c, --continuous Enable continuous mode (runs in while loop)
    -h, --help      Show this help message

ARGUMENTS:
    PROMPT          The prompt to send to Claude (default: "Process the next task from the backlog directory")
    OUTPUT_FILE     File to append stream-json output (default: messages.jsonl)
    DELAY_SECONDS   Seconds to wait between iterations (default: 5, use 0 for no delay)

EXAMPLES:
    # Single run (default)
    ./scripts/continuous_claude.sh

    # Continuous mode: processes backlog tasks every 5 seconds
    ./scripts/continuous_claude.sh --continuous

    # Custom prompt and file in continuous mode
    ./scripts/continuous_claude.sh -c "Your prompt here" output.jsonl 10

    # Single run with custom prompt
    ./scripts/continuous_claude.sh "Your prompt" messages.jsonl
EOF
    exit 0
fi

PROMPT="${1:-"Process the next task sorted by priority from the backlog directory and set the task to done once completed and create a PR with a concise description. If the task is complex, break it down into smaller steps. If the task requires research, provide a list of resources to investigate as separate tasks."}"
OUTPUT_FILE="${2:-messages.jsonl}"
DELAY_SECONDS="${3:-5}"

iteration=1

if [[ "$CONTINUOUS" == true ]]; then
    echo "Starting continuous Claude execution"
    echo "Prompt: $PROMPT"
    echo "Output: $OUTPUT_FILE"
    echo ""

    while true; do
        echo "=== Iteration $iteration ==="
        echo "First read CLAUDE.md; then $PROMPT" | claude -p --dangerously-skip-permissions --verbose --output-format stream-json >> "$OUTPUT_FILE"
        echo "Completed iteration $iteration"
        ((iteration++))

        if [[ $DELAY_SECONDS -gt 0 ]]; then
            sleep "$DELAY_SECONDS"
        fi
    done
else
    echo "Running single Claude execution"
    echo "First read CLAUDE.md; then $PROMPT" | claude -p --dangerously-skip-permissions --verbose --output-format stream-json >> "$OUTPUT_FILE"
    echo "Completed single execution"
fi
