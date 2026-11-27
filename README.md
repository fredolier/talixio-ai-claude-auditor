# Talixio repo assessor

Give it the Git URL of a repository that is developed with Claude Code. It clones the repository into
`targets/<name>/` and writes an independent diagnosis in `reports/`: does the code do what the project is
for, do the skills, commands and settings help or get in the way, and how can it get smaller and simpler
without losing what works. It never changes the repository it assesses.

This is the first version: the **report** only. See *Not built yet*.

## Run it

On the machine that can reach your GitLab:

1. Create a token that can only read: on GitLab, a project access token (or deploy token) with
   `read_repository` only. Export it in the shell that starts Claude Code, never in the chat:
   `export ASSESSOR_READ_TOKEN=…` (for a deploy token, also `export ASSESSOR_READ_USER=<its username>`).
   Public repositories need no token.
2. Start `claude` in this folder and accept the trust dialog: the project's allow rules apply only after it.
3. `/assess https://gitlab.example.com/group/repo.git [branch-or-commit]`
4. It fetches, then shows you its **goal statement** and waits. Correct it; everything after is judged
   against it. It then maps, assesses and writes `reports/<name>-<date>.md`, with the numbers it used in
   `reports/<name>-<date>-map.md`.

Optional: put session transcripts or examples of prompts in `evidence/<name>/`. They are not analysed by a
script yet (see below), but the assessor can read them.

If the scripts are not executable after cloning, run `chmod +x scripts/fetch.sh tests/selftest.sh` once.

Needs `git`, `python3` (standard library only) and Claude Code 2.1.285 or later. The Bash sandbox is built in
on macOS; on Linux install `bubblewrap` and `socat`. Run `tests/selftest.sh` once after installing, and again
after upgrading Claude Code or editing the settings.

An example is committed: `reports/claude-code-security-review-2026-11-26.md`, the assessor's report on a small
public repository, with its map beside it. Other reports stay local (`reports/` is git-ignored) because they
quote the target's code.

## What enforces each limit

| Limit | Enforced by |
|---|---|
| The target's `CLAUDE.md` and rules never load | `claudeMdExcludes` in `.claude/settings.json` |
| The target's skills are never discovered | `targets/` is in `.gitignore` (Claude Code skips git-ignored skill folders; observed, not documented, so `tests/selftest.sh` checks it) |
| No write into `targets/` | `Edit` deny rule (file tools and shell redirections); the sandbox makes it read-only for every Bash command; `fetch.sh` removes write permission from the files |
| No push of a target | deny rules on `git -C … push` and `cd` into `targets/`; `fetch.sh` sets a dead push URL; the token can only read; the sandbox has no network |
| No network except the fetch | the sandbox allows no domain, and only `scripts/fetch.sh` runs outside it; `curl`, `wget` and web search are denied; web fetch asks you each time |
| No installs | deny rules, and the sandbox has no network |
| The assessor cannot edit its own settings | `Edit` deny rule on `.claude/settings*.json`; you edit that file yourself |
| The token is never stored | a git credential helper names the variable; nothing is written to `.git/config` or to disk |

Known limits:

- Where the sandbox is unavailable (Linux without `bubblewrap`, Windows, Claude Code cloud sessions), Claude
  Code runs Bash without it, and the Bash limits rest on rules that match command text, which its
  documentation says are not a security boundary. To refuse to start instead, add
  `"failIfUnavailable": true` under `sandbox`.
- Under the sandbox, Bash can still write elsewhere in this folder (its default). The file tools ask first.
- Web fetch is left to ask rather than denied, so that a session changing the assessor can still read the
  Claude Code documentation. This could not be tested in the cloud session that built it, where web fetch is
  not a direct tool. To make it strict, add `"WebFetch"` to `deny`.
- A plain `git push` of the assessor's own repository is not denied: it asks. Denying it would stop cloud
  sessions from delivering changes to the assessor. To make it strict, add `"Bash(git push*)"` to `deny`.

## Layout

```
CLAUDE.md                 the assessor's stance and rules
.claude/settings.json     the enforced limits
.claude/skills/           assess (orchestrator), find-goal, review-code, review-claude-setup, simplify
scripts/fetch.sh          clone or update a target, read-only, token from the environment
scripts/map.py            sizes, Claude Code material, context estimate, call graph, duplication, growth
templates/report.md       the report's sections
tests/selftest.sh         isolation and read-only checks with a nested Claude Code session
targets/  evidence/  reports/     git-ignored
```

## Not built yet

- `scripts/transcripts.py`: tool calls from transcripts matched against the allow rules. Until then the
  permission review reads the configuration only and cannot count real prompts. The existing tools named in
  the brief (downscope, rippy-cli, cc-transcript, claude-config-doctor, claude-config-auditor, Clauditor) have
  not been evaluated.
- Fix instructions (level 2), merge requests (level 3), the benchmark and the improvement loop.
- Running a target's commands (`--help`, dry runs) in a disposable copy without network.
- Comparing a report with the previous one for the same target.
- `map.py` knows nothing of GitLab CI or other non-Claude automation, and its call graph is a text match:
  its tables are leads to verify by reading.
