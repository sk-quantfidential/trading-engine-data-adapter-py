# chore(epic-TSE-0003/foundation): add git quality standards scripts and hooks

## Summary
**Epic**: TSE-0003 - Trading Data Adapter Foundation
**Milestone**: Repository Infrastructure
**Behavior**: Add git quality standards for workflow enforcement

This PR establishes git quality standards for the trading-data-adapter-py repository by adding automated pre-push hooks, validation scripts, and workflow enforcement tools. This ensures consistent workflow across all 9 repositories in the Trading Ecosystem multi-component project.

### What Changed
- Added 4 git quality standards scripts from global ~/.claude/skills
- Installed pre-push hook for automated validation
- Renamed branch from `feature/epic-TSE-0003.0-data-adapter-foundation` to `feature/epic-TSE-0003-data-adapter-foundation` to comply with naming convention

### Why This Matters
- Enforces consistent branch naming across all team members
- Prevents accidental commits to protected branches (main/master)
- Validates PR documentation exists before push
- Catches workflow violations before CI/CD
- Establishes replicable pattern for remaining 8 repositories

---

## Quality Assurance

### Core Checks
- [x] Scripts copied from verified source: `~/.claude/skills/foundations/git_quality_standards/`
- [x] Pre-push hook installed successfully
- [x] Branch name validated: ✅ `feature/epic-TSE-0003-data-adapter-foundation`
- [x] Hook installation script output verified
- [x] No tests to run (infrastructure scripts only)

### Pre-Push Hook Validation
The installed hook validates:
1. ✅ Protected branch check (prevents pushing from main/master)
2. ✅ Branch naming convention (type/epic-XXX-9999-milestone-behavior)
3. ✅ PR documentation exists (docs/prs/{branch-name}.md)
4. ✅ PR has required sections (Summary, Quality Assurance, etc.)
5. ✅ TODO.md updates (when applicable)

### Manual Testing
- [x] Tested branch name validation: ✅ Passes with corrected name
- [x] Tested hook installation: ✅ Installed to .git/hooks/pre-push
- [x] Verified scripts are executable: ✅ chmod +x applied
- [x] Created this PR documentation: ✅ Follows template

---

## Security & Dependencies

### Security Considerations
- Data flow or permission changes: ✅ None - workflow scripts only
- External calls/URLs: ✅ None - local validation scripts
- Dynamic code or risky APIs: ❌ No eval, exec, or subprocess with untrusted input

### Dependency Health
- [x] No dependency changes in this PR
- [x] Secrets: none added (bash scripts only)
- [x] No security exceptions needed

### Scripts Security Review
- ✅ Scripts sourced from verified ~/.claude/skills/ (trusted)
- ✅ Bash scripts reviewed for safe practices
- ✅ No network calls or external dependencies
- ✅ File operations are local and safe

---

## Deployment

### Deployment Notes
- **No environment variables needed**
- **No migrations required**
- **No configuration changes**

### Installation for New Developers

```bash
# Hooks are automatically installed for existing clones
# For new clones, run:
./scripts/install-git-hooks.sh
```

### Rollback Plan
- [x] Safe to revert via git - no production impact
- Scripts can be removed without affecting code functionality
- Hook can be disabled with `git push --no-verify` if needed

---

## Breaking Changes
- [x] No breaking changes
- Additive only - adds workflow validation
- Developers may see push blocked if:
  - On protected branch (main/master)
  - Branch name doesn't follow convention
  - Missing PR documentation

**Migration**: Developers should ensure:
1. Branch names follow `type/epic-XXX-9999-milestone-behavior` format
2. PR documentation exists in `docs/prs/` before pushing
3. Run `./scripts/install-git-hooks.sh` after pulling this PR

---

## Files Changed

### Added Files
- `scripts/README.md` (documentation for scripts)
- `scripts/install-git-hooks.sh` (hook installation script)
- `scripts/pre-push-hook.sh` (pre-push validation logic)
- `scripts/validate-repository.sh` (repository validation)
- `docs/prs/chore-epic-TSE-0003-foundation-add-git-quality-standards.md` (this file)

### Modified Files
- None (all additions)

### Git Hooks Modified
- `.git/hooks/pre-push` (installed by script, not tracked in git)

---

## Next Steps

After merge:
1. Replicate this setup across remaining 8 repositories:
   - audit-correlator-go
   - audit-data-adapter-go
   - custodian-simulator-go
   - custodian-data-adapter-go
   - exchange-simulator-go
   - exchange-data-adapter-go
   - market-data-simulator-go
   - market-data-adapter-go
   - risk-monitor-py
   - risk-data-adapter-py
   - trading-system-engine-py
   - test-coordinator-py
   - test-coordinator-data-adapter-py
   - protobuf-schemas
   - orchestrator-docker
   - project-plan

2. Validate workflow compliance across all repos
3. Update project-plan/CLAUDE.md with standardized workflow reference

---

## Related PRs
- First repository in multi-component project to adopt git quality standards
- Pattern will be replicated to remaining 15+ repositories

---

## Linked Issues
- Related to Trading Ecosystem standardization initiative
- Implements git workflow from ~/.claude/skills/foundations/git_quality_standards
- Supports TSE-0003 epic (Trading Data Adapter Foundation)

---

## References
- **Skill Documentation**: `~/.claude/skills/foundations/git_quality_standards/SKILL.md`
- **Workflow Checklist**: `~/.claude/skills/foundations/git_workflow_checklist/SKILL.md`
- **Project Plan**: `../project-plan/CLAUDE.md`
- **Component Context**: `./.claude_component_context.md`
