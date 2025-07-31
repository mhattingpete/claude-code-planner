---
id: task-017
title: Improve error message quality
status: Done
assignee: []
created_date: '2025-07-31'
updated_date: '2025-07-31'
labels: []
dependencies: []
---

## Description

Generic error messages in generator.py:100-102 don't help users troubleshoot issues effectively

## Acceptance Criteria

- [x] Error messages are specific and actionable
- [x] Users can understand what went wrong
- [x] Troubleshooting guidance is provided in error messages

## Implementation Plan

1. Analyze current generic error messages in generator.py
2. Identify specific error types that need better messaging  
3. Create specific, actionable error messages for file writing operations
4. Improve error messages for Claude API failures to include troubleshooting steps
5. Update exception handling to provide clearer context about what failed and why
6. Test error scenarios to ensure messages are helpful

## Implementation Notes

Improved error messages throughout generator.py with specific, actionable guidance:

1. Enhanced file writing error messages with specific troubleshooting steps for permission errors, disk space issues, and missing directories
2. Added intelligent error detection for Claude API failures with specific troubleshooting guidance for authentication, rate limiting, timeouts, and connection issues  
3. All error messages now provide clear context about what went wrong and specific steps users can take to resolve issues
4. Error messages include relevant CLI commands (claude auth login, claude --version, etc.) for quick troubleshooting

Files modified:
- claude_code_designer/generator.py: Enhanced error handling in generate_documents(), _generate_prd(), _generate_claude_md(), and _generate_readme() methods
