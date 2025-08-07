#!/bin/bash

# Parse flags
CONTINUOUS=false
OUTPUT_FILE=""
DELAY_SECONDS=5

while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--continuous)
            CONTINUOUS=true
            shift
            ;;
        -o|--output-file)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            cat << 'EOF'
Continuous Claude CLI Runner

USAGE:
    ./continuous_claude.sh [FLAGS] [PROMPT] [DELAY_SECONDS]

FLAGS:
    -c, --continuous        Enable continuous mode (runs in while loop)
    -o, --output-file FILE  File to append stream-json output (default: display in terminal)
    -h, --help             Show this help message

ARGUMENTS:
    PROMPT          The prompt to send to Claude (default: "Process the next task sorted by priority from the backlog directory and set the task to done once completed and create a PR with a concise description. If the task is complex, break it down into smaller steps. If the task requires research, provide a list of resources to investigate as separate tasks.")
    DELAY_SECONDS   Seconds to wait between iterations in continuous mode (default: 5, use 0 for no delay)

EXAMPLES:
    # Single run to terminal (default)
    ./continuous_claude.sh

    # Single run with output to file
    ./continuous_claude.sh -o messages.jsonl

    # Continuous mode to terminal
    ./continuous_claude.sh --continuous

    # Continuous mode with output to file
    ./continuous_claude.sh -c -o output.jsonl

    # Custom prompt with file output
    ./continuous_claude.sh -o results.jsonl "Your prompt here"

    # Continuous mode with custom delay
    ./continuous_claude.sh -c "Your prompt" 10
EOF
            exit 0
            ;;
        -*)
            echo "Unknown flag: $1"
            exit 1
            ;;
        *)
            break
            ;;
    esac
done

PROMPT="${1:-"Process the next task sorted by priority from the backlog directory and set the task to done once completed and create a PR with a concise description. If the task is complex, break it down into smaller steps. If the task requires research, provide a list of resources to investigate as separate tasks."}"
if [[ -n "$2" ]]; then
    DELAY_SECONDS="$2"
fi

iteration=1

# Build the claude command based on output destination
if [[ -n "$OUTPUT_FILE" ]]; then
    claude_cmd="echo \"First read @CLAUDE.md; then $PROMPT\" | claude -p --dangerously-skip-permissions --verbose --output-format stream-json >> \"$OUTPUT_FILE\""
    output_destination="file: $OUTPUT_FILE"
else
    claude_cmd="echo \"First read @CLAUDE.md; then $PROMPT\" | claude -p --dangerously-skip-permissions"
    output_destination="terminal"
fi

if [[ "$CONTINUOUS" == true ]]; then
    echo "Starting continuous Claude execution"
    echo "Prompt: $PROMPT"
    echo "Output: $output_destination"
    echo ""

    while true; do
        echo "=== Iteration $iteration ==="
        eval "$claude_cmd"
        echo "Completed iteration $iteration"
        ((iteration++))

        if [[ $DELAY_SECONDS -gt 0 ]]; then
            sleep "$DELAY_SECONDS"
        fi
    done
else
    echo "Running single Claude execution"
    echo "Output: $output_destination"
    eval "$claude_cmd"
    echo "Completed single execution"
fi
