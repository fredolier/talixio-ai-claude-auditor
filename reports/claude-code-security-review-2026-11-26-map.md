# Map of claude-code-security-review

Target commit `0c6a49f1fa56a1d472575da86a94dbc1edb78eda` (2026-02-11), 42 tracked files. Assessor version `01dd3d9`. Tokens are estimated as characters / 4.

## 1. Sizes

| Category | Language | Files | Lines | Bytes |
|---|---|---|---|---|
| claude | Markdown | 1 | 190 | 10837 |
| code | JavaScript | 1 | 246 | 8968 |
| code | Python | 13 | 2389 | 97616 |
| data | JSON | 1 | 9 | 200 |
| data | YAML | 3 | 418 | 16103 |
| docs | Markdown | 4 | 378 | 16513 |
| docs | Text | 3 | 69 | 3322 |
| other | Other | 3 | 47 | 1418 |
| tests | JavaScript | 1 | 570 | 20428 |
| tests | Python | 12 | 4205 | 156484 |

## 2. Claude Code material

| Kind | File | Lines | Est. tokens | of which description |
|---|---|---|---|---|
| command | `.claude/commands/security-review.md` | 190 | 2709 | 18 |

Instruction files: 1, 190 lines, about 2709 tokens in total. Loaded in every session, estimated: 0 tokens of root memory and rule files, plus 18 tokens of skill, command and agent descriptions. Counts by kind: {'command': 1}; skills (SKILL.md): 0.


## 3. Call graph: instructions -> commands -> code

Commands quoted in instruction files (code blocks and backticks), most used first:

| Command | Uses | In files | Code behind it |
|---|---|---|---|

Scripts and executables, and how many files name them (a text match on the file name):

| Script | Lines | Instruction files | Other files | Note |
|---|---|---|---|---|
| `claudecode/audit.py` | 9 | 0 | 3 |  |
| `scripts/comment-pr-findings.js` | 246 | 0 | 2 |  |

## 4. Duplication between instruction files

Lines of 50+ characters that appear in two or more instruction files: 0 of 79 (counted once per file).

## 5. Growth

12 commits on the first-parent line, from 2025-08-04 to 2026-02-11. Sizes in bytes.

| Date | Commit | Files | Skills | Instructions | Code | Tests | Docs |
|---|---|---|---|---|---|---|---|
| 2025-08-04 | `c19afa74` | 41 | 0 | 10837 | 106530 | 176864 | 19059 |
| 2025-08-10 | `4a121e45` | 41 | 0 | 10837 | 106532 | 176864 | 19059 |
| 2025-08-11 | `7af83704` | 41 | 0 | 10837 | 106532 | 176864 | 19000 |
| 2025-08-12 | `5f7f7824` | 41 | 0 | 10837 | 106532 | 176864 | 19000 |
| 2025-08-12 | `c51ac4fc` | 41 | 0 | 10837 | 106532 | 176864 | 19000 |
| 2025-08-19 | `3ac4c63d` | 41 | 0 | 10837 | 106532 | 176864 | 19000 |
| 2025-08-19 | `7793a300` | 42 | 0 | 10837 | 106532 | 176864 | 19000 |
| 2025-08-19 | `38875871` | 42 | 0 | 10837 | 106532 | 176864 | 19182 |
| 2025-08-19 | `0fc84e79` | 42 | 0 | 10837 | 106532 | 176864 | 19182 |
| 2025-08-25 | `68982a6b` | 42 | 0 | 10837 | 106532 | 176864 | 19275 |
| 2025-11-25 | `25e460eb` | 42 | 0 | 10837 | 106584 | 176912 | 19835 |
| 2026-02-11 | `0c6a49f1` | 42 | 0 | 10837 | 106584 | 176912 | 19835 |

When each piece of Claude Code material first appeared (removed skills, commands and CLAUDE.md files included):

| First commit | File | Kind | Now |
|---|---|---|---|
| 2025-08-04 | `.claude/commands/security-review.md` | command |  |

Top-level directories by first appearance: `.claude` 2025-08-04, `.github` 2025-08-04, `(root files)` 2025-08-04, `claudecode` 2025-08-04, `docs` 2025-08-04, `examples` 2025-08-04, `scripts` 2025-08-04
