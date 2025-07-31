---
id: task-020
title: Improve exception handling specificity
status: Done
assignee: []
created_date: '2025-07-31'
updated_date: '2025-07-31'
labels: []
dependencies: []
---

## Description

Some exception handlers use broad 'except Exception' clauses instead of specific exception types, reducing debugging effectiveness

## Acceptance Criteria

- [x] Specific exception types are used where possible
- [x] Exception handling is more targeted
- [x] Debugging information is preserved and useful

## Implementation Plan

1. Analyze each broad exception handler to identify specific exception types
2. Replace 'except Exception' with specific exception types where possible
3. Keep broad exception handling only where truly generic handling is needed
4. Ensure error messages remain informative
5. Run tests to verify no regressions
6. Run linting to ensure code quality

## Implementation Notes

Improved exception handling specificity across all modules:

1. **cli.py**: Added specific handlers for OSError and ValueError in _run_design_process
2. **generator.py**: Added (PermissionError, OSError) and (ValueError, TypeError) handlers for all document generation methods
3. **questionnaire.py**: Added specific exception handlers for ValueError/TypeError in multiple methods

**Approach taken:**
- Analyzed each broad 'except Exception' clause
- Added more specific exception types before the general Exception handler
- Maintained existing fallback behavior and error messages
- Preserved debugging information while providing more targeted error handling

**Files modified:**
- claude_code_designer/cli.py: Added OSError and ValueError handlers
- claude_code_designer/generator.py: Added specific handlers for system and data errors  
- claude_code_designer/questionnaire.py: Added ValueError/TypeError handlers in 4 locations

**Testing:**
- All 103 tests pass
- Code coverage maintained at 87%
- Ruff linting passes with no issues
