---
allowed-tools: Bash(glab mr create:*), Bash(glab mr list:*), Bash(glab auth status:*), Bash(git status:*), Bash(git push:*), Bash(git branch:*), Bash(git diff:*), Bash(git log:*), Bash(glab issue view:*), Bash(gdate:*), Bash(jq:*)
description: Create merge requests with intelligent analysis and programmatic workflow
---

## Context

- Session ID: !`gdate +%s%N 2>/dev/null || date +%s%N 2>/dev/null || echo "$(date +%s)$(jot -r 1 100000 999999 2>/dev/null || shuf -i 100000-999999 -n 1 2>/dev/null || echo $RANDOM$RANDOM)"`
- Current branch: !`git branch --show-current 2>/dev/null || echo "unknown"`
- Git status: !`git status --porcelain 2>/dev/null | wc -l | tr -d ' ' || echo "0"` uncommitted changes
- Remote status: !`git status -b --porcelain 2>/dev/null | head -1 || echo "No remote tracking"`
- Recent commits: !`git log --oneline -5 2>/dev/null || echo "No commits found"`
- Existing MR: !`glab mr list --source-branch $(git branch --show-current 2>/dev/null || echo "main") --json 2>/dev/null | jq -r '.[0].iid // "none"' 2>/dev/null || echo "none"`
- GitLab auth: !`glab auth status 2>&1 | grep -q "Logged in" && echo "authenticated" || echo "not authenticated"`
- Arguments: $ARGUMENTS

## Your Task

STEP 1: Initialize MR creation session and validate prerequisites

- CREATE session state: `/tmp/mr-create-$SESSION_ID.json`
- VALIDATE session ID generation and file permissions
- SET initial state:
  ```json
  {
    "sessionId": "$SESSION_ID",
    "timestamp": "$(gdate -Iseconds 2>/dev/null || date -Iseconds)",
    "branch": "$(git branch --show-current)",
    "arguments": "$ARGUMENTS",
    "phase": "validation",
    "mr_config": {},
    "validation_results": {}
  }
  ```

TRY:

- VALIDATE GitLab authentication from Context
- VALIDATE git repository presence
- VALIDATE branch state and remote tracking
- SAVE validation results to session state

**Prerequisites Validation:**

IF GitLab auth != "authenticated":

- EXECUTE: `glab auth login`
- WAIT for authentication completion
- RETRY validation

IF git repository not detected:

- ERROR: "Not in a git repository. Navigate to project root or run `git init`."
- EXIT with error code

IF uncommitted changes > 0:

- WARN: "Uncommitted changes detected. Consider committing before creating MR."
- PROMPT: "Continue anyway? (y/n)"
- IF no: EXIT gracefully

CATCH (validation_failed):

- LOG specific validation failure to session state
- PROVIDE specific remediation instructions
- SAVE partial session state for recovery
- EXIT with helpful error message

STEP 2: Parse arguments and configure MR parameters

- PARSE $ARGUMENTS for MR configuration options
- SET default values for missing parameters
- VALIDATE parameter combinations
- UPDATE session state with MR configuration

**Argument Processing:**

```bash
# Parse common argument patterns
draft_mode=$(echo "$ARGUMENTS" | grep -q "draft" && echo "true" || echo "false")
target_branch=$(echo "$ARGUMENTS" | grep -oE 'target=([^\s]+)' | cut -d'=' -f2 || echo "main")
assignees=$(echo "$ARGUMENTS" | grep -oE 'assignees=([^\s]+)' | cut -d'=' -f2 || echo "")
labels=$(echo "$ARGUMENTS" | grep -oE 'labels=([^\s]+)' | cut -d'=' -f2 || echo "")
custom_title=$(echo "$ARGUMENTS" | grep -oE 'title="([^"]+)"' | sed 's/title="//;s/"$//' || echo "")
template=$(echo "$ARGUMENTS" | grep -oE 'template=([^\s]+)' | cut -d'=' -f2 || echo "")
milestone=$(echo "$ARGUMENTS" | grep -oE 'milestone=([^\s]+)' | cut -d'=' -f2 || echo "")
```

STEP 3: Intelligent change analysis and MR content generation

Think deeply about the optimal MR content generation strategy based on commit history, file changes, and project conventions.

TRY:

- ANALYZE commit history for conventional commit patterns
- EXAMINE file changes for scope and impact
- GENERATE intelligent MR title and description
- DETECT related issues from branch name or commits
- IDENTIFY appropriate reviewers from git history
- SAVE analysis results to session state

**Change Analysis Execution:**

```bash
# Get default branch (fallback chain)
default_branch=$(git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}' || echo "main")

# Analyze commits and changes
commit_messages=$(git log --pretty=format:"%s" origin/$default_branch...HEAD 2>/dev/null || echo "")
file_changes=$(git diff --name-status origin/$default_branch...HEAD 2>/dev/null || echo "")
change_summary=$(git diff --stat origin/$default_branch...HEAD 2>/dev/null || echo "")

# Extract issue numbers from branch or commits
issue_numbers=$(echo "$(git branch --show-current)\n$commit_messages" | grep -oE '#[0-9]+' | sort -u || echo "")

# Check for existing MR
existing_mr=$(glab mr list --source-branch $(git branch --show-current) 2>/dev/null | jq -r '.[0].iid // "none"' 2>/dev/null || echo "none")
```

**Title Generation Logic:**

IF custom_title provided:

- USE custom_title as MR title

ELSE IF single commit with conventional format:

- EXTRACT title from commit message
- VALIDATE conventional commit format

ELSE:

- ANALYZE file changes for primary scope
- GENERATE title based on change patterns
- FORMAT: "type(scope): description"

CATCH (analysis_failed):

- LOG analysis failure details
- FALLBACK to generic title generation
- CONTINUE with available information

STEP 4: Handle existing MR or create new MR

IF existing_mr != "none":

- LOG: "MR !$existing_mr already exists for this branch"
- PROMPT: "Update existing MR or create new one? (update/new/cancel)"
- CASE user_choice:
  - "update": EXECUTE MR update workflow
  - "new": CONTINUE with new MR creation
  - "cancel": EXIT gracefully

ELSE:

- PROCEED with new MR creation

STEP 5: Execute MR creation with intelligent content

- ENSURE branch is pushed to remote
- BUILD MR body from template or generate intelligently
- COLLECT all MR parameters (title, body, assignees, labels, etc.)
- EXECUTE `glab mr create` with generated content
- SAVE MR details to session state

**MR Creation Execution:**

```bash
# Ensure branch is pushed
git push -u origin $(git branch --show-current) 2>/dev/null || echo "Branch already pushed"

# Build MR creation command
glab mr create \
  --title "$generated_title" \
  --description "$(cat <<'EOF'
## Summary

$generated_summary

## Changes

$change_list

## Test Plan

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Issues

$issue_links
EOF
)" \
  $(test "$draft_mode" = "true" && echo "--draft" || echo "") \
  --assignee @me \
  $(test -n "$assignees" && echo "--assignee $assignees" || echo "") \
  $(test -n "$labels" && echo "--label $labels" || echo "") \
  $(test -n "$milestone" && echo "--milestone $milestone" || echo "") \
  --target-branch "$target_branch" \
  --remove-source-branch
```

TRY:

- EXECUTE MR creation command with all parameters
- CAPTURE MR URL and number from output
- VALIDATE MR creation success
- UPDATE session state with MR details

CATCH (mr_creation_failed):

- LOG specific failure reason (auth, network, validation, etc.)
- PROVIDE targeted remediation steps
- SAVE session state with failure details
- OFFER retry with corrected parameters

STEP 6: Post-creation workflow and cleanup

- DISPLAY MR creation success message with URL
- SAVE final session state with completion status
- OPTIONALLY trigger CI/CD workflows if detected
- CLEAN UP temporary session files

**Advanced Features Integration:**

**Smart Reviewer Detection:**

IF git history available:

- ANALYZE recent commits to files in changeset
- EXTRACT frequent contributors as potential reviewers
- SUGGEST reviewers if not explicitly provided

**Issue Linking:**

FOR EACH issue number detected:

- VALIDATE issue exists with `glab issue view`
- ADD appropriate linking keywords ("Closes #123", "Related to #456")
- INCLUDE issue context in MR description

**Template Support:**

IF template specified:

- VALIDATE template exists in `.gitlab/merge_request_templates/`
- LOAD template content for MR body
- MERGE template with generated content

**CI/CD Integration:**

IF test files or deployment configs changed:

- ADD CI trigger comments to MR body
- SUGGEST appropriate test commands
- INCLUDE deployment environment requests

FINALLY:

- ARCHIVE session data: `/tmp/mr-create-archive-$SESSION_ID.json`
- REPORT completion status with metrics
- CLEAN UP temporary files (EXCEPT archived data)
- LOG session completion timestamp

## Usage Examples

- `/mr` - Create MR with intelligent defaults
- `/mr draft` - Create draft MR for work in progress
- `/mr assignees=alice,bob` - Add specific assignees
- `/mr target=develop` - Target different branch
- `/mr labels=bug,priority::high` - Add labels
- `/mr title="Custom MR title"` - Override generated title
- `/mr template=feature` - Use specific MR template
- `/mr milestone=v2.0` - Assign to milestone

## Error Recovery

- **Authentication failed**: Automatically runs `glab auth login`
- **Branch not pushed**: Automatically pushes with tracking
- **Existing MR detected**: Offers update or new MR options
- **Network issues**: Provides retry with exponential backoff
- **Validation errors**: Specific remediation for each error type

## State Management

- Session state tracks progress through each step
- Resumable from last successful checkpoint
- Automatic cleanup of stale session files
- Comprehensive error logging for debugging