---
name: simplify
description: Explain where and why an assessed repository moved away from its goal, and plan the way back - what to delete, merge, restore or move into a script, ordered by gain for effort. Steps 6 and 7 of an assessment.
---
Fill the report's sections 7 and 8 from the verdicts already written.

**Divergence.** Where the repository moved away from its goal; when (the map's growth tables, then
`git -C targets/<name> log` on the files concerned); and the likely reason, for example a rule added after
each failure, or a skill added beside one that already did the job. Name the habit to stop, so the drift does
not come back. Mark a reason you inferred as inferred.

**Plan back to the goal.** The main deliverable. Changes ordered by gain for effort, each one small enough to
review and reverse on its own:
- what to delete, merge, restore, or move from instructions into a script;
- the target size (instruction lines and estimated tokens, number of skills), next to today's from the map;
- what must be kept: name the stages of rigour, and the tests and gates that protect them. A change that makes
  the repository smaller but drops one of these is a regression, not a simplification;
- for each change: the evidence, the expected gain, the risk, and how to check it worked.

Put the small, safe changes first and the big simplifications last. If the honest conclusion is that a part is
already the right size, say so.
