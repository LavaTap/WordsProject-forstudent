---
name: code-review
description: This skill should be used when users ask for code review, code analysis, code quality check, lint, or want to review Python scripts. The agent will examine code against Python best practices and provide improvement suggestions. Trigger phrases include "review code", "检查代码", "代码审查", "review script", "帮我看看这段代码", "代码分析".
---

# Code Review Skill

## Purpose

This skill invokes the Python Code Review Agent to analyze Python code, identify issues, and provide improvement recommendations based on Python coding standards and best practices.

## Usage

When the user triggers this skill (via `/code-review` command or relevant keywords), the code reviewer agent will:

1. **Accept user input** - The user can provide:
   - A specific file path to review
   - Code snippet pasted directly in chat
   - General request to review the current project

2. **Review Process**:
   - Scan overall code structure
   - Check code line by line against Python standards
   - Identify issues by severity (mandatory, suggestion, tip)
   - Provide specific improvement examples

3. **Output Format**:
   ```
   ### Issue [Level]: [Brief Description]
   - **Location**: Line X
   - **Rule**: [Specific rule violated]
   - **Current Code**: [Code snippet]
   - **Suggested Fix**: [Improved code]
   - **Explanation**: [Why this is an issue]
   ```

## Review Standards

The agent follows these Python standards:
- **Import conventions** - Use full package paths, no `from x import *`
- **Exception handling** - Use proper exception syntax, avoid bare `except:`
- **Code style** - 120 char line limit, 4-space indentation, proper naming
- **Documentation** - Docstrings for all public interfaces
- **Project structure** - Proper `__init__.py`, test file naming

## Example Triggers

- `/code-review`
- "review the code in app.py"
- "帮我审查 scripts/config.py"
- "check this Python script for issues"
- "代码质量分析"
