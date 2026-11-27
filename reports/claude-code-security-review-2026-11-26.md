# Assessment of claude-code-security-review

| | |
|---|---|
| Target | https://github.com/anthropics/claude-code-security-review.git, commit `0c6a49f1fa56a1d472575da86a94dbc1edb78eda` (2026-02-11) |
| Assessed on | 2026-11-26, assessor version `01dd3d9` |
| Inputs given | The repository only. No transcripts, no examples in `evidence/claude-code-security-review/`, no stated priority. Instruction from the user: mostly a code review, with a short setup review. |
| Goal confirmed by | **not confirmed.** Proof run; the repository's owner was not available. The user told me on 2026-11-26 to proceed with the goal statement as drafted. |

**In short:** The repository is a small, stable GitHub Action whose design matches its goal, and it has not grown
since its release. Its weak point is not size but *silent failure*: by reading the code, the two customisation
inputs and the timeout input do nothing for most users, a failed scan is reported as zero findings with a green
check, and a failed first scan blocks every later scan of the same PR. The biggest gain is about six small fixes
at the boundary between `action.yml` and the Python code, where no test looks. Keep the two-stage false-positive
filter, the prompt-injection warning, the pinned actions and the test suites. Nothing was run; every defect
below is a reading of the code.

Each finding gives its evidence (`file:line`, a commit, or a transcript entry), a confidence (high, medium,
low), the smallest fix, and the risk of that fix. Numbers come from `claude-code-security-review-2026-11-26-map.md`
or from a command quoted next to them.

## 1. Goal

**Stated goal:**

- "An AI-powered security review GitHub Action using Claude to analyze code changes for security
  vulnerabilities." (`README.md:3`, repeated as the action description in `action.yml:2`)
- "Diff-Aware Scanning: For PRs, only analyzes changed files"; "PR Comments: Automatically comments on PRs
  with security findings"; "False Positive Filtering: Advanced filtering to reduce noise and focus on real
  vulnerabilities" (`README.md:8-12`)
- "The false positive filtering can also be tuned as needed for a given project's security goals."
  (`README.md:118`), with custom scan and filtering instructions as action inputs (`README.md:60-61`)
- A second deliverable: the `/security-review` slash command, which "provides the same security analysis
  capabilities as the GitHub Action workflow" inside Claude Code, and which users copy from
  `.claude/commands/security-review.md` to customise (`README.md:141-148`)
- A stated limit: "This action is not hardened against prompt injection attacks and should only be used to
  review trusted PRs." (`README.md:45`, added in `4e12dbc`, 2025-11-25)

**Original intent:** The history starts with one squashed commit, `c19afa7` "Initial release" (2025-08-04),
which already contains 41 of today's 42 files (`git show --stat c19afa7`; map, section 5). The first README
opens with the same sentence as today's (`git show c19afa7:README.md`). The 29 commits since
(`git rev-list --count HEAD` = 30) change 7 files, +123/-67 lines (`git diff --stat c19afa7 HEAD`): default
model, a fail-fast on a missing API key, a self-scan workflow (`sast.yml`), the prompt-injection warning,
`--disallowed-tools` for `ps`, and pinning action versions. Whatever came before the release is not in this
repository, so intent earlier than the release cannot be read here.

**Goal statement** (confidence: high on what it is for, medium on the success measures, which the repository
describes but does not quantify):

- **What it is for.** Give a team an automatic security review of each pull request: Claude Code reads the
  diff in the context of the repository, and only findings likely to be real and exploitable reach the PR as
  line comments. Second, publish the same review as a customisable `/security-review` command.
- **Success looks like.** Real vulnerabilities introduced by a PR are reported on the right line with an
  explanation and a fix; few false positives (the README's main claim over traditional SAST); a failed or
  timed-out run is visible and never reads as "no findings"; a user can install it with the Quick Start alone
  and tune it with two text files; the action does not itself widen the attack surface of the repository
  that uses it.
- **Must not be lost.** The false-positive filtering (hard rules plus a Claude pass), the customisation
  inputs, the prompt-injection warning and hardening, the pinned action versions, the test suites, and the
  eval tooling that lets the prompt be checked against real PRs.
- **Stated goal against original intent.** No difference found: the stated goal has not moved since the
  release. I took the stated goal.

**Assumptions taken where the user could not answer** (both are also in section 9):

- *Action prompt and slash command.* Unknown whether they are meant to stay in sync. Cautious assumption: they
  may differ on purpose, so I recommend no merge and no deletion; I report where they have drifted and ask for
  a decision.
- *Eval tooling.* Unknown whether it is part of the goal. Cautious assumption: it is, so it is kept and no
  removal is proposed.

## 2. Intended design, next to what is there

Derived from the goal alone.

| Part the goal needs | What it is for | What is there | Gap |
|---|---|---|---|
| Action definition | Inputs, setup, run the review, expose outputs, fail visibly | `action.yml` | Fails invisibly (5.2, 5.3); one input not wired (5.4) |
| PR context fetch | Diff and metadata of the PR, minus excluded directories | `GitHubActionClient` in `claudecode/github_action_audit.py:40-186` | First 100 files only (5.9) |
| Audit prompt | One prompt: what to look for, what to ignore, output format, plus the user's custom instructions | `claudecode/prompts.py`; a near copy in `.claude/commands/security-review.md` | Custom file not found (5.1); invalid JSON example (5.2); copies drifted (5.15) |
| Claude Code runner | Run Claude Code with a timeout and restricted tools, parse the JSON | `SimpleClaudeRunner` in `claudecode/github_action_audit.py:189-344`, `claudecode/json_parser.py` | Tools not restricted (5.6); unparseable reply counts as clean (5.2) |
| False-positive filter | Deterministic exclusions, then a Claude pass per finding, tunable | `claudecode/findings_filter.py`, `claudecode/claude_api_client.py` | Matches the design; rules too broad in places (5.7), can switch itself off (5.8) |
| PR commenter | Post surviving findings on the right lines, without duplicates across runs | `scripts/comment-pr-findings.js` | Posts once per PR at most (5.5); loses findings off the diff (5.10) |
| Slash command | The same review for local use, customisable | `.claude/commands/security-review.md` | Right size; small issues in section 6 |
| Customisation docs and examples | Let users tune scanning and filtering | `docs/` (2 files), `examples/` (2 files) | The documented usage is the case that does not work (5.1) |
| Tests | Guard parsing, filtering and commenting | 12 `claudecode/test_*.py`, 1 `scripts/*.bun.test.js` | Nothing tests the `action.yml` to Python boundary |
| Evals | Check prompt changes against real PRs | `claudecode/evals/` | Runs one PR and counts findings; no expected results |
| CI for the repo itself | Run tests; scan its own PRs | `.github/workflows/` (2 files) | Matches |

Not needed by the goal: root `__init__.py`, `claudecode/audit.py`, and the leftovers listed in 5.16.

## 3. Verdict for each part

| Part | Serves | Verdict | Evidence | Confidence |
|---|---|---|---|---|
| `action.yml` | Running the review on a PR | **Keep, fix** the failure path and the unwired input | 5.2, 5.3, 5.4 | high |
| `claudecode/github_action_audit.py` | Fetch, run, filter, output | **Keep, simplify**: remove the unused module-level `run_security_audit` (`:433-454`); fix 5.1, 5.2, 5.4, 5.9 | read in full | high |
| `claudecode/prompts.py` | The audit prompt | **Keep**; fix the JSON example; the exclusion list is given twice (`:61-64`, `:166-171`) | read in full | high |
| `claudecode/findings_filter.py` | Few false positives | **Keep**; narrow three rules (5.7) | read in full | high |
| `claudecode/claude_api_client.py` | Claude pass of the filter | **Keep, simplify**: unused `get_claude_api_client` (`:357-374`); 5.8, 5.12 | read in full | high |
| `claudecode/json_parser.py` | Parsing Claude's reply | **Keep** as is | read in full | high |
| `claudecode/constants.py`, `logger.py` | Shared values, logging to stderr | **Keep** as is; nothing wrong found | read in full | high |
| `claudecode/audit.py`, root `__init__.py` | Nothing | **Remove** | No non-test file references `claudecode.audit` (`git grep -n -E "claudecode\.audit\|audit\.py"`; the map's "3 other files" are text matches on `github_action_audit.py`). Root file is one comment, "# SAST package" | high for `audit.py`; medium for the root file (an import path could rely on it) |
| `scripts/comment-pr-findings.js` | Findings on the PR | **Keep, fix** 5.5, 5.9, 5.10, 5.13 | read in full | high |
| `.claude/commands/security-review.md` | The local review | **Keep** at its size | section 6 | high |
| `docs/`, `examples/` | Customisation | **Keep**; correct once 5.1 is fixed | `docs/custom-filtering-instructions.md:17`, `docs/custom-security-scan-instructions.md:23` | high |
| `claudecode/evals/` | Checking the prompt on real PRs | **Keep** (assumption above); fix 5.14; `EvalCase`/`EvalResult` are defined twice (`run_eval.py:15-43`, `eval_engine.py:25-53`) | read in full | medium |
| Python tests | Guarding parsing and filtering | **Keep**; add boundary tests (section 8) | 173 test functions (`git grep -c -E "^\s*(def\|async def) test_"`); only one of the 12 files read in full | medium |
| JS tests | Guarding the commenter | **Keep** | 11 tests by a pattern count (`^\s*(test\|it)\(`); not read | low |
| `.github/workflows/test-claudecode.yml` | Running the tests | **Keep** as is | read in full | high |
| `.github/workflows/sast.yml` | Scanning its own PRs | **Keep**; excludes `tests/vulnerable`, which does not exist (`:23`) | read in full | high |
| `pytest.ini` | Test configuration | **Simplify**: `testpaths = tests` (`:2`) names a directory that does not exist; CI and the README pass `claudecode` explicitly | `README.md:161`, `test-claudecode.yml:45` | high |

## 4. The commands behind the skills

The target has no skills. These are the commands its action, its slash command and its docs rely on.

| Command | What it does | Called by | Contract, failures, stops | Finding |
|---|---|---|---|---|
| `python -u claudecode/github_action_audit.py` | Reads `GITHUB_REPOSITORY`, `PR_NUMBER`, `GITHUB_TOKEN`, `ANTHROPIC_API_KEY` and the option variables; calls the GitHub API, runs `claude`, calls the Claude API; prints one JSON document on stdout, logs on stderr | `action.yml:242`, `evals/eval_engine.py:416-434` | Exit 0 clean, 1 for "a HIGH finding" *and* for "general error", 2 for configuration or unexpected error (`constants.py:17-19`, `github_action_audit.py:637`). The caller cannot tell success from failure by exit code and looks for an `error` key instead. No interactive stop | 5.2 |
| `claude --output-format json --model … --disallowed-tools 'Bash(ps:*)'` | Runs the review in the PR checkout, prompt on stdin, up to 3 attempts | `github_action_audit.py:224-241` | Timeout is the 1200 s constant; a reply with no parseable findings is returned as success with an empty list (`:289-312`) | 5.2, 5.4, 5.6 |
| `node scripts/comment-pr-findings.js` | Reads `findings.json` in the current directory, lists PR files and comments through `gh api`, posts one review, adds two reactions per comment | `action.yml:329` | Exits 1 only on an unexpected error; returns silently when the file is unreadable, when no finding maps to the diff, or when any earlier bot comment exists | 5.5, 5.10, 5.13 |
| `python -m claudecode.evals.run_eval owner/repo#N` | Clones the repository into `~/code/audit`, makes a worktree for the PR, runs the audit script there, writes `eval_results/pr_*.json` | A person (`evals/README.md:26`) | Writes outside the project (`eval_engine.py:66-70`); stores the GitHub token in the clone (5.14); exit 0 or 1 | 5.14 |
| `git status`, `git diff --name-only origin/HEAD...`, `git log --no-decorate origin/HEAD...`, `git diff --merge-base origin/HEAD` | Give the slash command its context | `.claude/commands/security-review.md:11-29` | All four are covered by the command's `allowed-tools` (`:2`). Three need `origin/HEAD` to be set | section 6 |
| `claudecode/audit.py` | Calls `main()` | Nothing | none | Remove (section 3) |

## 5. Code review

Nothing here was run. "High" means the code path is unambiguous on reading; how often it happens in practice
cannot be told without run logs.

| # | Finding | Evidence | Confidence | Smallest fix | Risk of the fix |
|---|---|---|---|---|---|
| 5.1 | **The two customisation inputs are silently ignored when given as the docs say.** The scan step does `cd "$ACTION_PATH"` before starting Python, and Python opens the two files relative to its current directory, so a path relative to the user's repository is looked up in the action's directory. A file that is not found is skipped without a message. | `action.yml:220-221`; `github_action_audit.py:533-534`, `:544-545`; documented usage with relative paths in `docs/custom-filtering-instructions.md:17` and `docs/custom-security-scan-instructions.md:23`. No test names either variable (`git grep -n -E "FALSE_POSITIVE_FILTERING_INSTRUCTIONS\|CUSTOM_SECURITY_SCAN_INSTRUCTIONS\|REPO_PATH" -- "claudecode/test_*"` is empty) | high | Resolve a relative path against `REPO_PATH`; exit with an error when a path was given and the file is missing | Low. Workflows that pass a wrong path today would start to fail, which is the point |
| 5.2 | **A failed scan reads as "no findings".** (a) Any error is a `::warning::`, `findings_count=0`, and the step succeeds. (b) A reply from Claude that cannot be parsed, or has no `findings` key, is returned as success with an empty list; `review_completed: False` is set but nothing reads it. (c) The prompt's "exact schema" example is itself invalid JSON (trailing comma), which invites such a reply. (d) Exit code 1 means both "HIGH finding" and "error", so a correct run with a HIGH finding prints "ClaudeCode exited with code 1". | (a) `action.yml:242-272`; (b) `github_action_audit.py:289-312`, and `git grep -n review_completed` finds no reader outside tests; (c) `prompts.py:148`; (d) `constants.py:18`, `github_action_audit.py:637`, `action.yml:245` | high for the paths, unknown frequency | Remove the comma; return failure when the reply has no parseable findings; give the step a non-zero exit (or an output such as `scan-status`) when the result has an `error` key | A provider outage turns PR checks red. Offer an input to choose warning or failure if that is not wanted |
| 5.3 | **A failed first scan blocks every later scan of the PR.** The "already ran" marker is written and saved to the cache before the scan starts; any later push finds it and disables the scan. With 5.2 the PR is then never reviewed and every check is green. | `action.yml:123-155` (marker saved before `:176`), `action.yml:104-106` | high | Save the marker after a scan that succeeded | Medium: the early save exists to stop two concurrent runs both commenting (`action.yml:123`). Keep the reservation but record the status and rerun when it is not "done" |
| 5.4 | **The `claudecode-timeout` input does nothing.** The action exports `CLAUDE_TIMEOUT`; no Python code reads it, and the runner is built with no argument, so the timeout is always 1200 s. | `action.yml:190`, `:217`; `github_action_audit.py:390`, `:198-201`; `constants.py:22`; `git grep -n CLAUDE_TIMEOUT` finds only `action.yml` | high | Read the variable in `initialize_clients` and pass it as `timeout_minutes` | Low |
| 5.5 | **Only the first push of a PR is reviewed, and comments are posted at most once.** By default later pushes are skipped (documented as a trade-off). With `run-every-commit: true` the scan runs again, but the commenter stops as soon as one earlier bot comment exists, so new findings never reach the PR. | `action.yml:104-106`, `README.md:59`; `scripts/comment-pr-findings.js:176-188` | high on behaviour; medium on intent | Compare per finding (path, line, category) instead of all-or-nothing | Medium: more comments on long PRs, the noise the design avoids. Check with the evals before changing the default |
| 5.6 | **In the action, Claude Code runs with no tool allow-list, on the PR's own checkout, with the GitHub token and the API key in its environment.** Only `ps` is disallowed, while the slash command restricts itself to read-only tools. The README states the limit honestly. | `github_action_audit.py:224-241` (no `env=`), `action.yml:181-184`; `.claude/commands/security-review.md:2`; `README.md:45`; `505701d` | medium: I could not check what headless Claude Code permits by default, or whether it loads settings from the checkout | Give the CLI the same read-only tool list as the slash command; start it with an environment that has no `GITHUB_TOKEN` | Low to medium: the review may lose a tool it used for context. Compare findings on a few PRs before and after |
| 5.7 | **Three hard rules can drop real findings before Claude sees them.** Memory-safety findings are dropped unless the file ends in `.c`, `.cc`, `.cpp` or `.h` (so `.hpp`, `.cxx`, `.hh`, `.m`, unsafe Rust). Keyword rules match anywhere in the description, so a finding that mentions "denial of service" or "close connection" as a side remark is dropped whole. Every finding in a `.md` file is dropped. | `findings_filter.py:134-143`; `:31-51` with `:105-121`; `:93-94`. The second stage already carries the same exclusions as text (`claude_api_client.py:243-259`) | high on behaviour, medium on impact | Add the missing extensions; apply keyword rules to the `category` field, or leave those cases to the Claude pass | More false positives. Measure on known PRs first |
| 5.8 | **The Claude pass can switch itself off without notice.** Start-up validation calls a fixed, dated model (`claude-3-5-haiku-20241022`); if that call fails for any reason, filtering by Claude is disabled for the run with only a log line, and every finding is posted. | `claude_api_client.py:59-72`; `findings_filter.py:187-195` | high on the path; I could not check whether that model is still served | Validate with the configured model, or drop the validation: a failed call per finding already keeps the finding (`findings_filter.py:297-306`) | Low |
| 5.9 | **Large PRs are cut at 100 files, and existing comments at one page.** The comment says "with pagination support"; there is none. A finding in a file past the first 100 is skipped as "not in PR diff". | `github_action_audit.py:77-81`; `scripts/comment-pr-findings.js:108`, `:137-140`, `:177`; a test pins the single-page URL (`test_github_client.py:100`) | high | `gh api --paginate` in the script; follow the `Link` header in Python | Low |
| 5.10 | **Findings on lines outside the diff disappear from the PR.** One bad line makes the whole review call fail; the per-comment fallback then logs each failure and moves on. They remain only in the artifact. | `scripts/comment-pr-findings.js:190-239` | high on the path, medium on frequency | Post one summary comment listing the findings that could not be placed | Low |
| 5.11 | **A file whose diff contains `@generated` anywhere is removed from the diff given to Claude**, though it stays in the file list. Ordinary code that mentions the word is hidden; a test records this as expected. | `github_action_audit.py:169-174`; `test_github_client.py:252-254` | medium | Match the marker only in the first lines of the file | Low |
| 5.12 | **The filter reads whatever path a finding names**, absolute or with `..`, with no size limit, and sends the content to the Claude API. The path comes from model output. | `claude_api_client.py:220-235`, `:323-349` | high on the path, low severity (content is sent to the API, not posted) | Resolve the path and require it to be inside `REPO_PATH`; cap the size | None expected |
| 5.13 | **Result files are written into the reviewed repository's root**, and the commenter reads `findings.json` from there. When a scan fails no file is produced, so a `findings.json` committed in the reviewed repository would be read instead. | `action.yml:293-303`; `scripts/comment-pr-findings.js:96-97` | medium (depends on the step's working directory, not run) | Write to `$RUNNER_TEMP` and pass the path in a variable | Low; the artifact paths at `action.yml:313-316` must follow |
| 5.14 | **The eval tool writes the GitHub token into a file.** The clone URL embeds the token, which git stores in the clone's configuration under `~/code/audit`. | `claudecode/evals/eval_engine.py:235-241`, `:66-70` | high | Clone with the plain URL and supply the token through a credential helper or `gh` | Low |
| 5.15 | **The review rules exist in three places and have drifted.** Of the slash command's 78 distinct lines of 50+ characters, 30 are identical in `prompts.py` and 10 in `claude_api_client.py` (counted with a `python3 -I -c` snippet: for each file, the set of stripped lines of 50+ characters after removing the `> ` quote prefix, then the set intersections). The rest differ: the command excludes regex injection, documentation files and missing audit logs and names Angular (`security-review.md:153-156`, `:164`); the API prompt has two precedents the command lacks (`claude_api_client.py:283-284`). No commit since the release touched any of the three files (`git log -- <the three files>` shows only `c19afa7`). | as cited | high on the drift; whether it matters depends on the open question | Decide whether they must match. If yes, one test that compares the shared block is enough; do not merge the files | None for the decision; a merge would risk the README's promise that users can copy one file (`README.md:147`) |
| 5.16 | **Leftovers that nothing uses.** `PyGithub` is installed on every run and never imported; `SILENCE_CLAUDECODE_COMMENTS` is always `false`; `EVAL_MODE` is set and never read; the commenter and the eval engine handle `finding.extra`, `finding.start`, `finding.path` and `check_id`, which the prompt's schema never produces; a "check sampling" comment with no sampling; the missing-key message names a different repository. | `requirements.txt:5` with `git grep -n -E "import github\|from github"`, whose only three matches are `from claudecode import github_action_audit` in tests; `action.yml:95`, `:115`, `:326`, `comment-pr-findings.js:120-125`; `eval_engine.py:413`, `run_eval.py:83`; `comment-pr-findings.js:130-157`, `eval_engine.py:372-376`; `action.yml:97`; `action.yml:210` | high | Delete each | Low; run the suites afterwards |
| 5.17 | **Installs are not pinned, next to actions that are.** `40616dd` pinned every `uses:` to a commit hash, but the action still installs the latest Claude Code and open-ended Python ranges on each run, and the Quick Start tells users to follow `@main`. The action also needs `sudo apt-get`, which the README does not state. | `action.yml:170-173`, `:68`; `claudecode/requirements.txt:5-15`; `README.md:37` | high | Pin the Claude Code version and the Python packages; show a tag or hash in the Quick Start | Pins go stale; needs a routine to raise them |

**What matches the goal and must stay:** the two-stage filter that keeps a finding whenever the filter itself
fails (`github_action_audit.py:479-483`, `findings_filter.py:297-306`); the prompt passed on stdin and the
`gh` calls built as argument arrays, with no shell (`github_action_audit.py:234-241`,
`comment-pr-findings.js:25-38`); workflow values passed through `env:` instead of inline templates
(`7e7ae56`); the retry without the diff when the prompt is too long (`github_action_audit.py:590-595`).

**Tests.** 4205 lines of Python tests for 2389 lines of Python code, and 570 lines of JavaScript tests for 246
(map, section 1). The hard-rule, JSON-parser and commenter suites guard behaviour that matters. Three leads on
weak tests, from the one file I read and from searches: `test_integration.py:62-80` fails when the Claude CLI
is absent and otherwise asserts only conditionally; `test_github_client.py:100` and `:252-254` pin two of the
defects above as expected behaviour; no test covers the custom-instruction paths, the timeout variable or the
`PROMPT_TOO_LONG` retry (searches quoted in 5.1 and 5.4; `git grep -n PROMPT_TOO_LONG -- "claudecode/test_*"`
is empty). The other eleven Python test files and the JavaScript test file were not read line by line.

## 6. Claude Code setup

Short by request. The Claude Code material is one file: `.claude/commands/security-review.md`, 190 lines, about
2709 tokens, of which 18 are in context in every session (map, section 2). There is no `CLAUDE.md`, settings
file, hook, skill or agent. Without transcripts this is a reading of the configuration, not a count of prompts.

### Permissions

- No settings layer exists, so there is no allow, ask or deny rule to conflict, and none of the unsafe patterns
  (allowing pushes, deletions or installs, bypass modes, self-edited settings, credentials in files) appears in
  the Claude Code material. The one credential-in-a-file case is in the eval code (5.14).
- The command's `allowed-tools` (`security-review.md:2`) is read-only and covers the four commands it runs
  (`:11`, `:17`, `:23`, `:29`). No likely prompt. Confidence: high.
- `Bash(git remote show:*)` is allowed but nothing in the text uses it, and it contacts the remote. Smallest
  fix: remove it from the list. Risk: none found. Confidence: medium.
- The action's own invocation of Claude Code is less restricted than this command: see 5.6.

### Autonomy

- The command asks the user nothing and ends with the report (`security-review.md:191`). The action has no
  interactive stop. Nothing to grade as an unnecessary question.
- One human gate is designed in and worth keeping: the README's advice to require approval before workflows
  run on outside contributions (`README.md:45`). This is an L6 decision (safety) and rightly left to a person.
- Two decisions the action takes itself are product decisions (L4) exposed as inputs, which is the right
  place: scanning once per PR, and commenting or not (`action.yml:6-9`, `:36-39`). The first is only half
  selectable, see 5.5.

### Instruction quality

| Finding | Evidence | Confidence | Smallest fix | Risk |
|---|---|---|---|---|
| Two thresholds for the first pass: "more than 80% confident", then a scale that reports from 0.7 | `security-review.md:39` against `:125-129`; same in `prompts.py:58` against `:157-161` | high | Keep one number | Changes how many findings reach the filter; check on known PRs |
| Two items numbered 16 | `security-review.md:154-155` | high | Renumber | None |
| "Do not use the bash tool" sits in a block whose scope (the filtering sub-tasks) is only implied, while the command grants git through Bash | `security-review.md:136` against `:2` | medium | Say "in this sub-task" | None |
| The sub-task prompt must "include all of the above", so the model re-emits the instructions | `security-review.md:187` | medium on cost; not measured | None proposed: the sub-task needs the text, and no fixed command can pass it | n/a |
| Three of the four context commands need `origin/HEAD`; a clone without it gives the model an empty diff or an error | `security-review.md:17`, `:23`, `:29` | medium: I could not check how Claude Code treats a failing inline command | Say in the README that `origin/HEAD` must be set | None |
| The text says "all code changes in the PR" for what is the local branch | `security-review.md:32`, `:36` | high, minor | Reword | None |

The file is the right size for what it does. I found no contradiction with another instruction file, because
there is none; its overlap with the Python prompts is 5.15.

## 7. Divergence

**The repository has not drifted since its release.** Instructions are 10837 bytes at every commit; code went
from 106530 to 106584 bytes and tests from 176864 to 176912 over 12 first-parent commits (map, section 5). The
stated goal is word for word the original one. There is no accumulation of rules or skills to undo.

What separates it from its goal was there on day one:

- **A larger tool cut down by deletion (inferred).** The names and leftovers point to an internal scanner that
  was trimmed for release: "# SAST package" (`__init__.py:1`), `@anthropic-ai/sast-scripts`
  (`scripts/package.json:2`), fields of another scanner's output format (`comment-pr-findings.js:130-157`),
  "check sampling" (`action.yml:97`), "like pr_audit does" (`eval_engine.py:66`), a job renamed away from
  "semgrep" (`f7483ce`). The cut left wiring that goes nowhere (5.4, 5.16).
- **No test crosses from `action.yml` into the code.** The inputs that do not work (5.1, 5.4) and the failure
  path (5.2, 5.3) all sit at that boundary, and all 13 test files stay on one side of it. This is a fact about
  where the defects are; that it is the cause is my inference.
- **Little maintenance (fact), reason unknown.** One functional change to the code since August 2025
  (`505701d`); the default and validation models are dated 2025 and 2024 (`constants.py:8`,
  `claude_api_client.py:62`); the three prompt copies were never touched again (5.15).

**The habit to stop:** adding or keeping an action input without one test that sets it in the workflow and
observes it in the result. And for the prompts: changing one copy without deciding what happens to the others.

## 8. Plan back to the goal

Small and safe first. Each change stands alone and can be reverted alone. "How to check" names a test to add,
since I ran nothing.

| # | Change | Gain | Effort | Risk | How to check |
|---|---|---|---|---|---|
| 1 | Resolve the two custom-instruction paths against `REPO_PATH`; error when a given file is missing (5.1) | Customisation works as documented | small | low | A test that sets a relative path with a different working directory and sees the text in the prompt |
| 2 | Read `CLAUDE_TIMEOUT` in `initialize_clients` (5.4) | The input works | small | low | A test that sets the variable and reads `timeout_seconds` |
| 3 | Remove the trailing comma in the prompt's JSON example (5.2c) | Fewer unparseable replies | one character | none | Parse the example in `test_prompts.py` |
| 4 | Treat a reply without parseable findings as a failure; separate the exit code for "HIGH finding" from "error" (5.2b, d) | A broken scan is no longer a clean one | small | low; `eval_engine.py:450-456` relies on code 1 and must follow | Existing tests at `test_claude_runner.py:328-352` change from "empty" to "failed" |
| 5 | Make a failed scan visible: failing step or a `scan-status` output, chosen by an input (5.2a) | Green means reviewed | small | medium: red checks during outages | Run the action on a PR with a wrong API key |
| 6 | Mark the PR as done only after a successful scan (5.3) | A failed scan is retried on the next push | small | medium: concurrent runs | Two pushes, the first with a forced failure |
| 7 | Delete the leftovers of 5.16, `claudecode/audit.py`, root `__init__.py`, the two unused functions, `testpaths` | Less to read; one install fewer per run | small | low | Test suites still pass |
| 8 | Validate the filter with the configured model, or drop the validation (5.8) | Filtering cannot switch off unnoticed | small | low | A test where validation fails and filtering stays on |
| 9 | Paginate file and comment lists; summary comment for findings off the diff (5.9, 5.10) | No finding lost on large PRs | medium | low | A PR with more than 100 files; a finding on an unchanged line |
| 10 | Keep finding paths inside the repository; move result files to `$RUNNER_TEMP`; stop storing the token in the eval clone (5.12, 5.13, 5.14) | Safer by construction | medium | low | Tests with `../` and absolute paths; inspect the clone's configuration |
| 11 | Give the action's Claude Code run the slash command's read-only tool list and an environment without the GitHub token (5.6) | Narrower attack surface | small to write, needs a comparison run | medium: may lose context | Same PRs through the eval tool before and after |
| 12 | Pin Claude Code and the Python packages; show a tag in the Quick Start (5.17) | Reproducible runs, same standard as `40616dd` | small, then recurring | pins go stale | A scheduled update |
| 13 | Narrow the three hard rules (5.7); match `@generated` only at the top of a file (5.11) | Fewer real findings dropped | small | more false positives | Needs labelled PRs, see section 9 |
| 14 | Decide whether the three prompt copies must match; if yes, add one comparing test (5.15) | No further drift | a decision, then small | none | The test |
| 15 | Per-finding duplicate check, so later pushes can be reviewed and commented (5.5) | Vulnerabilities added after the first push are seen | medium | noise on long PRs | Evals, then opt-in through `run-every-commit` first |

**Size today and target:** 1 instruction file, 190 lines, about 2709 tokens, 0 skills (map, section 2). Target:
the same; the slash command is already the right size and I propose no cut to it. Code: 2389 lines of Python
and 246 of JavaScript today (map, section 1). Change 7 removes a little; I give no target number because I did
not count the lines it removes. Honest conclusion: this repository does not need to become smaller, it needs
its inputs and its failure path to work.

**To keep:** the two-stage filter and its rule of keeping a finding when the filter fails; the customisation
inputs and their docs; the prompt-injection warning and the advice to gate outside contributions
(`README.md:45`); the hash-pinned actions (`40616dd`); the hard-rule, JSON-parser and commenter test suites;
both CI workflows, including the self-scan; the eval tool. None of the fifteen changes removes any of these.

## 9. Gaps

- **Nobody confirmed the goal.** Sections 3 to 8 are judged against my reading of the README. If the owner
  weighs things differently (for example, a quiet failure preferred to a red check), 5.2 and plan items 4 to 6
  change in severity, not in fact.
- **Open question: must the action's prompts and the slash command match?** I assumed they may differ on
  purpose and proposed no merge (5.15). The owner's answer settles it. Related: the README says Claude Code
  ships `/security-review` by default (`README.md:141`); whether the shipped command equals this file cannot
  be told from the repository.
- **Open question: is the eval tool part of the goal?** I assumed yes and kept it. Either way it holds no
  labelled cases and no expected results (`evals/README.md:36-44`), so the README's central claim, fewer false
  positives, cannot be checked from the repository, and neither can the risk of plan items 11, 13 and 15.
  A small set of PRs with known answers would settle all three.
- **Nothing was run**: not the action, the tests, the eval tool or the slash command. I ran only
  `scripts/fetch.sh`, `scripts/map.py`, read-only `git log/show/diff/grep/rev-list/ls-files` on the target, and
  one line-comparison snippet over three files (5.15). Every defect is a reading. A run in a disposable copy
  would confirm 5.1 to 5.4 quickly; the test suite alone would confirm change 7.
- **No transcripts or run logs.** I cannot say how often a scan fails, how often Claude returns unparseable
  JSON, how many findings the hard rules drop, or what the slash command costs in tokens per use. Transcript
  analysis is not built in this assessor yet.
- **Claude Code behaviour I could not check** against the documented facts I have: what tools a headless run
  may use with no allow-list and whether it loads settings from the checked-out PR (5.6); how a failing inline
  `!` command is handled (section 6); whether the `Task` and `LS` tool names in `security-review.md:2` are
  current.
- **External facts I could not check** (no network by design): whether the default model
  `claude-opus-4-1-20250805` and the validation model `claude-3-5-haiku-20241022` are still served (5.8);
  which tools are preinstalled on GitHub's runners (`action.yml:68`, `:173`).
- **Tests were sampled, not reviewed.** I read `test_integration.py` in full and searched the others; the
  verdicts on the test suites carry medium or low confidence for that reason. Test counts are a pattern match
  on function names.
- **History before the release is absent**, so the "cut down from a larger tool" explanation in section 7 is
  an inference from names in the code.
- **Not built in this assessor:** fix instructions, merge requests, the benchmark loop, and comparison with a
  previous report. This is the first report on this target.
