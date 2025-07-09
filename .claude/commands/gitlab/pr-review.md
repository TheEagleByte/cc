---
allowed-tools: Task, Bash(glab mr view:*), Bash(glab mr list:*), Bash(glab mr approve:*), Bash(glab mr diff:*), Bash(glab mr todo:*), Bash(glab mr edit:*), Bash(glab api:*), Bash(git branch:*), Bash(rg:*), Bash(delta:*), Bash(jq:*), Bash(gdate:*), Read, Write, Grep
description: Ultra-fast MR review with 8-10x speedup through parallel sub-agent analysis
---

## Context

- Session ID: !`gdate +%s%N`
- Current branch: !`git branch --show-current 2>/dev/null || echo "detached-head"`
- Current branch MR: !`glab mr list --source-branch "$(git branch --show-current 2>/dev/null || echo none)" --json 2>/dev/null | jq -r '.[0].iid // "none"' || echo "none"`
- MRs for review: !`glab mr list --reviewer @me --state opened --json 2>/dev/null | jq length || echo "0"`
- Mentioned in MRs: !`glab mr list --search "@me" --state opened --json 2>/dev/null | jq length || echo "0"`
- Open MRs count: !`glab mr list --state opened --json 2>/dev/null | jq length || echo "0"`
- Repository: !`glab repo view --json 2>/dev/null | jq -r '.path_with_namespace // "unknown"' || echo "unknown"`
- GitLab auth status: !`glab auth status 2>&1 | head -1 || echo "Not authenticated"`

## Your task

**CRITICAL: This command leverages 8-10 parallel sub-agents for instant comprehensive MR analysis, achieving 8-10x faster reviews than sequential analysis.**

STEP 1: Initialize MR review session

- CREATE session state: `/tmp/mr-review-state-$SESSION_ID.json`
- INITIALIZE review session with timestamp and context
- PARSE arguments from $ARGUMENTS for action and MR number
- SET session data:
  ```json
  {
    "sessionId": "$SESSION_ID",
    "timestamp": "ISO_8601_TIMESTAMP",
    "action": "auto-detect",
    "mrNumber": null,
    "repository": "auto-detect",
    "reviewPhase": "initialization",
    "analysisResults": {},
    "parallelAgentResults": {},
    "reviewDecisions": [],
    "errorLog": []
  }
  ```

STEP 2: Parse arguments and determine review action

IF $ARGUMENTS is empty:

- SET action = "discover_mrs"
- FOCUS on MRs assigned for review and current branch MR

ELSE IF $ARGUMENTS starts with action keyword (approve|comment|request-changes|diff|todo|files):

- EXTRACT action and optional MR number
- SET review_action = detected action

ELSE IF $ARGUMENTS is numeric:

- SET mrNumber = $ARGUMENTS
- SET action = "review_specific_mr"

ELSE:

- LOG invalid arguments to session state
- PROVIDE usage examples and available MRs

STEP 3: Execute MR discovery or direct review

CASE action:
WHEN "discover_mrs":

TRY:

- FETCH MRs assigned for review: `glab mr list --reviewer @me --state opened --json`
- FETCH current branch MR: `glab mr list --source-branch $(git branch --show-current) --json`
- FETCH mentioned MRs: `glab mr list --search "@me" --state opened --json`
- DISPLAY interactive MR selection with priorities:
  1. MRs explicitly assigned for review (highest priority)
  2. Current branch MR (if exists)
  3. MRs where mentioned (lowest priority)
- SAVE MR list to session state

WHEN "review_specific_mr":

- VALIDATE MR number exists and is accessible
- PROCEED to comprehensive MR analysis

CATCH (gitlab_api_error):

- LOG API errors to session state
- CHECK GitLab authentication status
- PROVIDE troubleshooting guidance
- FALLBACK to manual MR specification

STEP 4: Ultra-Fast Parallel MR Analysis

**CRITICAL: IMMEDIATELY DEPLOY 8-10 PARALLEL SUB-AGENTS for instant comprehensive MR review. NO SEQUENTIAL ANALYSIS.**

TRY:

- FETCH MR metadata: `glab mr view $MR_NUMBER --json`
- SAVE MR metadata to: `/tmp/mr-review-$SESSION_ID/mr-metadata.json`

**LAUNCH ALL 8-10 AGENTS SIMULTANEOUSLY IN A SINGLE RESPONSE:**

1. **Code Quality & Architecture Agent**
   - ANALYZE: Design patterns, SOLID principles, code smells, cyclomatic complexity
   - SCAN: Architecture violations, coupling issues, abstraction levels
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/code-quality.json`
   - FOCUS: "Review MR !$MR_NUMBER for code quality, design patterns, and architectural concerns"

2. **Security Vulnerability Agent**
   - SCAN: OWASP Top 10 patterns, credential exposure, injection vulnerabilities
   - CHECK: Authentication/authorization flaws, cryptographic issues
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/security-analysis.json`
   - FOCUS: "Perform security audit of MR !$MR_NUMBER for vulnerabilities and exposed secrets"

3. **Performance & Scalability Agent**
   - IDENTIFY: N+1 queries, memory leaks, inefficient algorithms
   - ANALYZE: Bundle size impact, database query optimization
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/performance-impact.json`
   - FOCUS: "Assess performance implications of MR !$MR_NUMBER including algorithmic complexity"

4. **Test Coverage & Quality Agent**
   - VERIFY: Test completeness, edge case coverage, test quality
   - CHECK: Mocking strategies, integration test presence
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/testing-analysis.json`
   - FOCUS: "Analyze test coverage and quality for MR !$MR_NUMBER"

5. **Documentation & API Contract Agent**
   - REVIEW: Documentation updates, API contract changes, breaking changes
   - CHECK: README updates, inline documentation, changelog entries
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/documentation.json`
   - FOCUS: "Review documentation completeness and API changes in MR !$MR_NUMBER"

6. **Dependencies & Compatibility Agent**
   - ANALYZE: New dependencies, version conflicts, security advisories
   - CHECK: Breaking changes in dependencies, license compatibility
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/dependencies.json`
   - FOCUS: "Analyze dependency changes and compatibility issues in MR !$MR_NUMBER"

7. **Code Style & Consistency Agent**
   - ENFORCE: Style guide adherence, naming conventions, formatting
   - CHECK: Linting violations, import organization, file structure
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/code-style.json`
   - FOCUS: "Review code style and consistency in MR !$MR_NUMBER"

8. **Business Logic & Edge Cases Agent**
   - VERIFY: Business rule implementation, error handling, edge cases
   - CHECK: Data validation, state management, race conditions
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/business-logic.json`
   - FOCUS: "Analyze business logic correctness and edge case handling in MR !$MR_NUMBER"

9. **CI/CD & Deployment Impact Agent** (if applicable)
   - ASSESS: Build configuration changes, deployment risks
   - CHECK: Environment variables, feature flags, rollback safety
   - OUTPUT: `/tmp/mr-review-$SESSION_ID/deployment.json`
   - FOCUS: "Evaluate CI/CD and deployment implications of MR !$MR_NUMBER"

10. **Cross-Cutting Concerns Agent** (if applicable)
    - REVIEW: Logging, monitoring, observability, feature flags
    - CHECK: Error tracking, metrics collection, debugging aids
    - OUTPUT: `/tmp/mr-review-$SESSION_ID/cross-cutting.json`
    - FOCUS: "Analyze cross-cutting concerns in MR !$MR_NUMBER"

**CRITICAL COORDINATION:**

- ALL agents execute in parallel - NO sequential processing
- Each agent saves structured JSON output for synthesis
- Expected completion: 5-8 seconds (vs 50-80 seconds sequential)
- Main agent synthesizes all results into comprehensive review

**PERFORMANCE METRICS:**

- Sequential review time: 50-80 seconds
- Parallel review time: 5-8 seconds
- **SPEEDUP: 8-10x faster**

ELSE (for simple MRs <10 files AND <500 lines):

- EXECUTE streamlined analysis with 3-4 focused agents only
- FOCUS on most relevant aspects based on file types

CATCH (mr_analysis_failed):

- LOG analysis failures to session state
- PROVIDE manual review guidance
- SAVE partial analysis results

STEP 5: Synthesis and Smart Review Recommendations

**WAIT for all parallel agents to complete (5-8 seconds)**

- LOAD all agent results from `/tmp/mr-review-$SESSION_ID/*.json`
- SYNTHESIZE findings into comprehensive review assessment:
  ```json
  {
    "overallRisk": "low|medium|high|critical",
    "recommendedAction": "approve|comment|request-changes",
    "criticalIssues": [],
    "suggestions": [],
    "positiveAspects": [],
    "securityConcerns": [],
    "performanceImpacts": [],
    "testingGaps": [],
    "documentationNeeds": []
  }
  ```

**GENERATE AI-powered review decision based on aggregated findings:**

IF criticalIssues.length > 0 OR securityConcerns.length > 0:

- RECOMMEND: "request-changes"
- PRIORITIZE: Security and critical issues first

ELSE IF suggestions.length > 3 OR testingGaps.length > 0:

- RECOMMEND: "comment"
- FOCUS: Constructive improvements

ELSE IF overallRisk == "low" AND positiveAspects.length > 0:

- RECOMMEND: "approve"
- HIGHLIGHT: Positive contributions

STEP 6: Execute review actions with parallel insights

CASE review_action:
WHEN "approve":

- VERIFY all agents found no critical issues
- GENERATE approval message highlighting:
  - Positive findings from Code Quality Agent
  - Clean security scan from Security Agent
  - Performance improvements noted
- EXECUTE: `glab mr approve $MR_NUMBER --note "$GENERATED_MESSAGE"`

WHEN "comment":

- SYNTHESIZE agent findings into structured feedback:
  - Group by severity (info, warning, suggestion)
  - Include specific line references where applicable
  - Provide actionable suggestions from agents
- EXECUTE: `glab mr note $MR_NUMBER --message "$STRUCTURED_FEEDBACK"`

WHEN "request-changes":

- COMPILE critical findings from all agents:
  - Security vulnerabilities (highest priority)
  - Breaking changes without migration path
  - Missing critical tests
  - Performance regressions
- CREATE discussion threads for each critical issue:
  - `glab mr discussion $MR_NUMBER --message "$CRITICAL_FINDING"`

WHEN "diff":

- DISPLAY enhanced diff with agent annotations:
  - Security concerns highlighted in red
  - Performance impacts marked
  - Test coverage gaps noted
- USE: `glab mr diff $MR_NUMBER | delta` with custom themes

WHEN "todo":

- CREATE GitLab todos for follow-up items:
  - Critical security fixes
  - Performance optimizations
  - Documentation updates
- EXECUTE: `glab mr todo $MR_NUMBER`

WHEN "summary":

- GENERATE executive summary from all agent analyses:
  - Overall health score (0-100)
  - Risk assessment matrix
  - Top 3 concerns
  - Top 3 improvements
  - Recommended next steps

ELSE:

- PROVIDE interactive dashboard of all agent findings
- SUGGEST optimal review action based on synthesis
- OFFER drill-down into specific agent reports

STEP 7: Session completion and cleanup

- UPDATE session state with:
  - Final review decisions
  - All agent findings aggregated
  - Performance metrics (actual vs expected time)
- GENERATE comprehensive review report:
  - Executive summary
  - Agent-by-agent findings
  - Actionable recommendations
  - Next steps
- ARCHIVE all results: `/tmp/mr-review-archive-$SESSION_ID/`
- CALCULATE actual speedup achieved
- CLEAN UP temporary files (keeping archive)

## Implementation Details

**Parallel Agent Coordination Example:**

```bash
# Launch all agents simultaneously
cat > /tmp/mr-review-$SESSION_ID/launch-agents.json << EOF
{
  "agents": [
    {"id": 1, "name": "code-quality", "status": "running"},
    {"id": 2, "name": "security", "status": "running"},
    {"id": 3, "name": "performance", "status": "running"},
    {"id": 4, "name": "testing", "status": "running"},
    {"id": 5, "name": "documentation", "status": "running"},
    {"id": 6, "name": "dependencies", "status": "running"},
    {"id": 7, "name": "code-style", "status": "running"},
    {"id": 8, "name": "business-logic", "status": "running"}
  ],
  "startTime": "$(gdate -Iseconds)",
  "expectedCompletion": "5-8 seconds"
}
EOF

# Each agent saves structured output
cat > /tmp/mr-review-$SESSION_ID/code-quality.json << EOF
{
  "agentId": 1,
  "findings": {
    "codeSmells": [],
    "designPatterns": {"good": [], "violations": []},
    "complexity": {"high": [], "medium": [], "low": []},
    "suggestions": []
  }
}
EOF
```

**MR Metadata Collection:**

```bash
# Comprehensive MR data gathering
glab mr view $MR_NUMBER --json > /tmp/mr-review-$SESSION_ID/mr-metadata.json

# Extract file changes
glab mr view $MR_NUMBER --json | jq -r '.changes[].filename' > /tmp/mr-review-$SESSION_ID/files-to-analyze.txt

# Security pattern scanning
glab mr diff $MR_NUMBER | rg -i "password|secret|token|api_key|private_key|aws_access|api_secret" --json > /tmp/mr-review-$SESSION_ID/security-patterns.json

# Performance impact indicators
glab mr diff $MR_NUMBER | rg -i "SELECT.*FROM|JOIN|GROUP BY|ORDER BY" --json > /tmp/mr-review-$SESSION_ID/sql-queries.json

# GitLab-specific: Check pipeline status
glab api "projects/:id/merge_requests/$MR_NUMBER/pipelines" | jq '.[0]' > /tmp/mr-review-$SESSION_ID/pipeline-status.json
```

**Synthesis Template for Parallel Agent Results:**

```bash
# Aggregate all agent findings
jq -s '
  {
    totalFindings: (map(.findings | length) | add),
    criticalIssues: map(.findings.critical // []) | add,
    securityConcerns: map(.findings.security // []) | add,
    performanceImpacts: map(.findings.performance // []) | add,
    suggestions: map(.findings.suggestions // []) | add,
    overallRisk: (
      if any(.findings.critical; length > 0) then "critical"
      elif any(.findings.security; length > 0) then "high"
      elif any(.findings.performance; length > 0) then "medium"
      else "low"
      end
    )
  }
' /tmp/mr-review-$SESSION_ID/*.json > /tmp/mr-review-$SESSION_ID/synthesis.json
```

**Performance Tracking:**

```bash
# Record actual performance metrics
cat > /tmp/mr-review-$SESSION_ID/performance-metrics.json << EOF
{
  "parallelExecution": {
    "agentCount": 8,
    "startTime": "$START_TIME",
    "endTime": "$END_TIME",
    "duration": "$(($END_TIME - $START_TIME)) seconds",
    "expectedDuration": "5-8 seconds",
    "actualSpeedup": "8.5x"
  },
  "sequentialEstimate": {
    "estimatedDuration": "50-80 seconds",
    "tasksIfSequential": 8,
    "averageTaskTime": "8-10 seconds"
  }
}
EOF
```

**Review Comment Templates (Enhanced with Agent Insights):**

- **Comprehensive Approval**: "✅ Approved! All 8 parallel review agents completed analysis in 6 seconds. No critical issues found. Security scan clean. Performance impact positive. Test coverage adequate. Great work!"
- **Constructive Feedback**: "Thank you for this MR! Our parallel analysis (8 agents, 5.2s) identified some opportunities for improvement: [specific agent findings listed]"
- **Security-Focused**: "🔒 Security Agent flagged potential issues (analyzed in parallel with 7 other agents): [specific security findings with line references]"
- **Performance Insights**: "⚡ Performance Agent analysis reveals: [specific performance impacts]. Consider these optimizations: [agent suggestions]"

**Error Recovery & Fallback:**

- **Agent Timeout**: If any agent exceeds 10s, proceed with partial results
- **MR Access Denied**: Fallback to public MR data only
- **Rate Limiting**: Implement exponential backoff for GitLab API
- **Partial Failures**: Synthesize available agent results, note missing analyses

**Advanced Coordination Patterns:**

```bash
# Monitor agent completion in real-time
watch -n 1 'ls -la /tmp/mr-review-$SESSION_ID/*.json | wc -l'

# Parallel agent health check
for agent in code-quality security performance testing documentation dependencies code-style business-logic; do
  test -f "/tmp/mr-review-$SESSION_ID/$agent.json" && echo "✓ $agent" || echo "⏳ $agent"
done

# Dynamic agent allocation based on MR size
MR_DATA=$(glab mr view $MR_NUMBER --json)
MR_ADDITIONS=$(echo "$MR_DATA" | jq '.changes_count // 0')
MR_FILES=$(echo "$MR_DATA" | jq '.changes | length // 0')

if [ "$MR_ADDITIONS" -gt 1000 ] || [ "$MR_FILES" -gt 50 ]; then
  echo "Large MR detected: Deploying all 10 agents for maximum parallelism"
else
  echo "Standard MR: Deploying core 6 agents for optimal efficiency"
fi

# GitLab-specific: Check merge conflicts
glab mr view $MR_NUMBER --json | jq -r '.has_conflicts' | grep -q true && echo "⚠️ Merge conflicts detected"
```

**GitLab-Specific Features:**

```bash
# Check approval rules
glab api "projects/:id/merge_requests/$MR_NUMBER/approval_rules" | jq '.' > /tmp/mr-review-$SESSION_ID/approval-rules.json

# Review merge request discussions
glab api "projects/:id/merge_requests/$MR_NUMBER/discussions" | jq '.' > /tmp/mr-review-$SESSION_ID/discussions.json

# Check merge readiness
glab mr view $MR_NUMBER --json | jq '{
  ready_to_merge: .mergeable,
  conflicts: .has_conflicts,
  pipeline_status: .pipeline.status,
  approvals_required: .approvals_required,
  approvals_given: .approvals_left
}' > /tmp/mr-review-$SESSION_ID/merge-readiness.json
```