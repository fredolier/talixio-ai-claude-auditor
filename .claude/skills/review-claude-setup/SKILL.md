---
name: review-claude-setup
description: Review the Claude Code side of an assessed repository - permissions and hooks, where and why the workflow stops to ask, and the quality of its instructions. Step 5 of an assessment.
---
Read every settings file, hook, `CLAUDE.md`, skill, command and agent the map lists. Fill the report's section 6.

**Permissions.** The settings layers, the allow, ask and deny rules, the hooks, and their conflicts. Then
compare with the commands the instructions make the model run (map, section 3): each command no allow rule
covers is a likely prompt. Give the smallest fix for each pattern, or say why none exists. Without
transcripts in `evidence/<name>/` this is a reading of the configuration, not a count of real prompts: say so.

Facts about Claude Code checked against its documentation on 2026-11-26 (code.claude.com/docs/en/permissions,
/settings, /memory, /skills, /hooks). If a judgement needs a rule that is not here, say you could not check it.
- Rules are evaluated deny, then ask, then allow; a deny in any layer cannot be overridden by an allow.
  Layers: managed, command line, `.claude/settings.local.json`, `.claude/settings.json`, `~/.claude/settings.json`.
- Bash rules match the command text, with `*` anywhere. A compound command (`&&`, `||`, `;`, `|`) is split:
  an allow needs every part allowed. `Bash(git push *)` does not match `git -C dir push`. So commands that
  vary in form (`cd x && …`, pipes into `jq` or `python -c`, inline scripts) defeat allow rules and prompt.
- `Edit(...)` rules cover every file-editing tool. Path forms: `//abs`, `~/home`, `/from-project-root`, `./cwd`.
- Deny rules hold in every permission mode. A hook can block a call (exit 2), but cannot override a deny.
- A `CLAUDE.md` or `.claude/rules/` in a subdirectory loads when a file there is first read; nested
  `.claude/skills/` are discovered the same way. Skill descriptions are in context in every session.

**Autonomy.** Where the workflow stops to ask, and why: questions written into skills, gates that wait for a
person, commands that end in a question. Grade each stop with the decision levels in `CLAUDE.md`: which
should the workflow have decided itself (L1 to L4 once the spec is approved), and which human gates are
designed in and worth keeping.

**Instruction quality.** Contradictions between files; unclear or competing skills (two that claim the same
trigger); duplicated text (map, section 4); and instructions that leave the model to improvise shell commands
that change every time, where a fixed command would do.

Flag, and never recommend: allow rules for pushes, deletions or installs, bypass permission modes, an agent
allowed to edit its own `.claude/settings*.json`, credentials in files.
