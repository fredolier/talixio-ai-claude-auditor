---
name: find-goal
description: Find what an assessed repository is for (its stated goal and its original intent from the git history) and derive the simplest design that meets that goal. Steps 2 and 3 of an assessment.
---
Work on `targets/<name>`, read-only. Write the result into the report's sections 1 and 2.

1. **Stated goal.** What the repository says it is for today: README, specs, epics, scenario files, `CLAUDE.md`.
   Quote the sentences you rely on, with file and line.
2. **Original intent.** What it was for at the start. Read the first commits
   (`git -C targets/<name> log --reverse --format='%h %as %s'`), the first versions of the README and `CLAUDE.md`
   (`git -C targets/<name> show <commit>:<path>`), and what the first skills did. Early versions often state
   the goal more plainly than later ones, and a stated goal can itself have drifted.
3. **Goal statement**, in a few lines:
   - what the repository is for;
   - what success looks like, with the measures it should improve (for a workflow: better software, rigour
     kept, fewer interruptions);
   - what must not be lost;
   - where the stated goal and the original intent differ, and which one you took and why.
4. **Intended design.** From the goal alone, the parts the repository needs and what each one is for: for a
   workflow, its stages (such as spec, validation, stories, implementation, review, defects), what each skill
   should do in them, and the few commands they need. This is a sketch of the simplest thing that meets the
   goal, to compare with what is there. It is not a rewrite, and it must not be reverse-engineered from the
   current layout.

If the sources disagree or say too little, write the goal you think most likely, mark it as uncertain, and
put the question to the user at the checkpoint.
