---
name: assess
description: Assess a repository developed with Claude Code, from outside. Fetches it, finds its goal, maps it, judges each part against the goal and writes a report.
argument-hint: <git-url> [branch-or-commit]
disable-model-invocation: true
---
Assess `$ARGUMENTS`. Keep this order: the goal comes first because every later judgement is made against it.

1. **Fetch.** Run `scripts/fetch.sh <url> [ref]`. It prints the target's name and commit. If access is
   refused, stop and tell the user to set `ASSESSOR_READ_TOKEN` in their shell; never ask for it in chat.
2. **Open the report.** Copy `templates/report.md` to `reports/<name>-<date>.md` and fill it in as you go, so
   later steps never depend on your memory of earlier ones. List what the user gave you (transcripts or
   examples in `evidence/<name>/`, what they care about most) and what they did not.
3. **Goal.** Follow the `find-goal` skill. Then **stop**: show the goal statement and the intended design, ask
   the user to correct them, and wait. Record in the report who confirmed the goal, or that nobody did.
4. **Map.** Run `python3 -I scripts/map.py targets/<name> -o reports/<name>-<date>-map.md` and read the result.
   Its tables are heuristics about text: a match is a lead to verify by reading, not a finding.
5. **Assess each part against the goal.** Follow `review-code`, then `review-claude-setup`.
6. **Divergence and plan.** Follow `simplify`.
7. **Close the report.** Check that each finding has its evidence, confidence, smallest fix and the risk of
   that fix; that the numbers match the map; and that the gaps section says what you could not tell and why.
   Then give the user the report's path and its five most important points.
