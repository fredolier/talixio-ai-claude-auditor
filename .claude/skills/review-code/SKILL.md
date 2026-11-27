---
name: review-code
description: Judge each part of an assessed repository against its confirmed goal - skills, commands, hooks, scripts and code areas - with a verdict and evidence. Reads the code of the commands the skills rely on. Step 5 of an assessment.
---
Work from the confirmed goal, the intended design and the map. Fill the report's sections 3 to 5.

**A verdict for each part** (each skill, command, hook, script and area of the code): which part of the goal
it serves, or none; *keep*, *simplify*, *merge*, *remove*, or *restore* (the history shows something the
original had and lost); and the evidence.

**The commands behind the skills.** Skills lean on commands that do the hard work, and a problem can sit in a
command as much as in a skill. Read each command's code, not only how the skills describe it:
- what it does: inputs, outputs, what it reads and writes, and anything else it changes (git, network, files
  outside the project);
- who calls it, and whether anything does (the map lists unreferenced scripts and subcommands as leads);
- overlap: whether another command or a plain tool already does the job;
- its contract: whether what the skills say it does matches the code. Where they disagree, the model works
  around it, and those workarounds are typically the improvised shell commands that prompt for permission;
- how it fails: exit codes and error messages. An unclear error, or output the model must parse with `jq`,
  `grep` or `python -c`, makes the model improvise or ask;
- where it stops the run: interactive input, confirmations, gates that wait for a person, output ending in a
  question;
- what it costs: how much it prints, since output fills the model's context.

You only read. To confirm a reading by running `--help` or a dry run, ask the user first, and use a
disposable copy with no network.

**Code review against the goal:** what matches it, what is missing, what is over-built (beyond the need,
unused, duplicated, dead), real defects, and which tests protect behaviour that matters and which are only
ceremony. Give the file and line for each. Do not report style.
