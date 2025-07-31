---
id: task-018
title: Fix string splitting edge cases
status: Done
assignee:
  - '@claude'
created_date: '2025-07-31'
updated_date: '2025-07-31'
labels: []
dependencies: []
---

## Description

Simple string splitting on commas in questionnaire.py:264-270 doesn't handle edge cases like values containing commas

## Acceptance Criteria

- [x] String parsing handles comma-containing values correctly
- [x] Edge cases in user input are handled
- [x] Robust parsing mechanism is implemented

## Implementation Plan

1. Analyze the current string splitting implementation in _split_and_clean_list method
2. Identify edge cases where simple comma splitting fails (e.g., quoted values)
3. Implement robust parsing using csv.reader or shlex for proper handling
4. Add validation and error handling for malformed input
5. Write tests to verify the fix handles edge cases correctly

## Implementation Notes

Fixed string splitting edge cases in _split_and_clean_list method by:

1. Replaced simple comma splitting with CSV reader for proper handling of quoted values
2. Added skipinitialspace=True to handle whitespace around fields
3. Implemented fallback to simple splitting for CSV parsing errors
4. Added logic to remove surrounding quotes when necessary
5. Comprehensive test coverage for edge cases including:
   - Quoted values containing commas
   - Mixed quoted and unquoted values
   - Empty quoted strings
   - Malformed quotes
   - Whitespace handling

The solution now correctly handles cases like 'item1, "item, with comma", item3' while maintaining backward compatibility with simple comma-separated values.
