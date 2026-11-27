#!/usr/bin/env python3
"""Reproducible numbers about a target repository: sizes, Claude Code material, context estimate,
call graph (instructions -> commands -> code), duplication, growth. It reads tracked files and the
git history; it never imports or runs anything from the target.
Usage: python3 -I scripts/map.py targets/<name> [-o reports/<name>-<date>-map.md]"""
import json, re, subprocess, sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

T = Path(sys.argv[1]).resolve()
LANG = {"py": "Python", "sh": "Shell", "bash": "Shell", "js": "JavaScript", "mjs": "JavaScript", "cjs": "JavaScript",
        "ts": "TypeScript", "tsx": "TypeScript", "jsx": "JavaScript", "go": "Go", "rs": "Rust", "java": "Java",
        "rb": "Ruby", "php": "PHP", "cs": "C#", "c": "C", "h": "C", "cpp": "C++", "kt": "Kotlin", "swift": "Swift",
        "sql": "SQL", "html": "HTML", "css": "CSS", "scss": "CSS", "vue": "Vue", "md": "Markdown", "mdx": "Markdown",
        "rst": "Text", "txt": "Text", "json": "JSON", "yml": "YAML", "yaml": "YAML", "toml": "TOML"}
DOCS, DATA = {"Markdown", "Text"}, {"JSON", "YAML", "TOML"}
INSTR = {"memory", "rule", "skill", "command", "agent"}       # text the model reads as instructions
TESTS = re.compile(r"(^|/)(tests?|__tests__|specs?|e2e)/|(^|/)test_[^/]*$|[._-](test|spec)\.\w+$")
TOOLS = set("git npm npx pnpm yarn node python python3 pip uv pytest make docker gh glab jq grep rg sed awk curl "
            "wget cat ls find bash sh cargo go ruby bundle php composer mvn gradle dotnet kubectl rm mv cp mkdir "
            "chmod echo".split())
SUBDEF = re.compile(r"""add_parser\(\s*["']([\w-]+)|\.command\(\s*(?:name\s*=\s*)?["']([\w:-]+)""")
CASE = re.compile(r"^\s*([a-z][\w-]*(?:\|[a-z][\w-]*)*)\)", re.M)


def git(*args):
    return subprocess.run(["git", "-C", str(T), "-c", "core.quotePath=false", *args], capture_output=True, text=True, errors="replace", check=True).stdout


def kind(p, plugin):
    """What a path is on the Claude Code side, from the path alone (so it also works on history)."""
    parts = p.split("/"); name = parts[-1]; inc = ".claude" in parts
    def under(d): return (inc and d in parts[parts.index(".claude"):]) or (plugin and parts[0] == d)
    if name in ("CLAUDE.md", "CLAUDE.local.md", "AGENTS.md"): return "memory"
    if name == ".mcp.json": return "mcp"
    if inc and re.fullmatch(r"settings.*\.json", name): return "settings"
    if name == "SKILL.md": return "skill"
    if "skills" in parts[:-1] and (inc or plugin): return "skill" if name.endswith(".md") else "skill-code"
    if under("rules") and name.endswith(".md"): return "rule"
    if under("commands") and name.endswith(".md"): return "command"
    if under("agents") and name.endswith(".md"): return "agent"
    if under("hooks"): return "hook"
    if parts[0] == ".claude-plugin": return "plugin"
    return "claude-other" if inc else None


def category(p, k):
    if k: return "claude"
    lang = LANG.get(p.rsplit(".", 1)[-1].lower() if "." in p.split("/")[-1] else "", "Other")
    if TESTS.search(p): return "tests"
    return "docs" if lang in DOCS else "data" if lang in DATA else "code" if lang != "Other" else "other"


def read(p):
    f = T / p
    if f.is_symlink() or not f.is_file(): return None
    b = f.read_bytes()
    return None if b"\0" in b[:8192] else b.decode("utf-8", "replace")


def tok(text): return round(len(text) / 4)        # estimate: about 4 characters per token


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    return "\n".join(out + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]) + "\n"


def command_lines(text, scripts):
    """Shell commands quoted in an instruction file, as (head, subcommand, line)."""
    lines = [l for m in re.finditer(r"```[\w-]*\n(.*?)```", text, re.S) for l in m[1].splitlines()]
    lines += re.findall(r"`([^`\n]+)`", re.sub(r"```.*?```", "", text, flags=re.S))
    for line in lines:
        t = line.strip().lstrip("$>! ").split()
        while t and (re.fullmatch(r"\w+=\S*", t[0]) or t[0] == "sudo"): t = t[1:]
        if len(t) > 1 and t[0] in ("python", "python3", "bash", "sh", "node") and t[1].split("/")[-1] in scripts: t = t[1:]
        if not t: continue
        head = t[0].split("/")[-1]
        if head not in TOOLS and head not in scripts: continue
        sub = t[1] if len(t) > 1 and (re.fullmatch(r"[a-z][\w:-]*", t[1]) or t[1] == "-c") else ""
        yield head, sub, " ".join(t)


def main():
    out = []; w = out.append
    modes = dict((l.split("\t")[1], l.split()[0]) for l in git("ls-files", "-s").splitlines())
    plugin = any(p.startswith(".claude-plugin/") for p in modes)
    files = {}                                     # path -> (kind, category, text or None)
    for p in sorted(modes):
        k = kind(p, plugin); files[p] = (k, category(p, k), read(p))
    assessor = subprocess.run(["git", "-C", str(Path(__file__).parent), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True).stdout.strip() or "uncommitted"
    w(f"# Map of {T.name}\n\nTarget commit `{git('rev-parse', 'HEAD').strip()}` ({git('log', '-1', '--format=%as').strip()}), "
      f"{len(files)} tracked files. Assessor version `{assessor}`. Tokens are estimated as characters / 4.\n")

    # 1. Sizes
    w("## 1. Sizes\n")
    agg = defaultdict(lambda: [0, 0, 0])
    for p, (k, c, text) in files.items():
        lang = "(binary)" if text is None else LANG.get(p.rsplit(".", 1)[-1].lower(), "Other")
        a = agg[(c, lang)]; a[0] += 1; a[1] += 0 if text is None else text.count("\n"); a[2] += (T / p).lstat().st_size
    w(table(["Category", "Language", "Files", "Lines", "Bytes"], [(c, l, *v) for (c, l), v in sorted(agg.items())]))

    # 2. Claude Code material
    w("## 2. Claude Code material\n")
    mat = [(p, k, text) for p, (k, c, text) in files.items() if k]
    desc_tok = 0; rows = []
    for p, k, text in mat:
        text = text or ""; fm = re.match(r"---\n(.*?)\n---\n", text, re.S)
        d = re.search(r"^description:\s*(.*?)(?=^\S[\w-]*:|\Z)", fm[1] if fm else "", re.S | re.M)
        d = tok(d[1]) if d and k in INSTR else 0; desc_tok += d
        rows.append((k, f"`{p}`", text.count("\n"), tok(text) if k in INSTR else "", d or ""))
    w(table(["Kind", "File", "Lines", "Est. tokens", "of which description"], sorted(rows)))
    instr = {p: text for p, k, text in mat if k in INSTR and text}
    always = sum(tok(t) for p, t in instr.items() if files[p][0] in ("memory", "rule") and p.count("/") <= 1)
    w(f"Instruction files: {len(instr)}, {sum(t.count(chr(10)) for t in instr.values())} lines, about "
      f"{sum(map(tok, instr.values()))} tokens in total. Loaded in every session, estimated: {always} tokens of root "
      f"memory and rule files, plus {desc_tok} tokens of skill, command and agent descriptions. "
      f"Counts by kind: {dict(Counter(k for _, k, _ in mat))}; skills (SKILL.md): {sum(p.endswith('SKILL.md') for p in files)}.\n")
    for p, k, text in mat:
        if k not in ("settings", "mcp", "hook") or not p.endswith(".json"): continue
        try: j = json.loads(text)
        except Exception as e: w(f"- `{p}`: not valid JSON ({e})"); continue
        perms = j.get("permissions", {}) if isinstance(j, dict) else {}
        w(f"- `{p}`: keys {sorted(j)}" + (f"; defaultMode `{perms.get('defaultMode', 'default')}`" if k == "settings" else ""))
        for mode in ("allow", "ask", "deny"):
            if perms.get(mode): w(f"  - {mode} ({len(perms[mode])}): " + ", ".join(f"`{r}`" for r in perms[mode]))
        for event, groups in (j.get("hooks") or {}).items() if isinstance(j.get("hooks"), dict) else []:
            for g in groups:
                w(f"  - hook {event} [{g.get('matcher', '*')}]: " + ", ".join(f"`{h.get('command', h.get('type'))}`" for h in g.get("hooks", [])))
    w("")

    # 3. Call graph
    w("## 3. Call graph: instructions -> commands -> code\n")
    scripts = {}                                   # command name -> path of the tracked file behind it
    for p, (k, c, text) in files.items():
        if text is None or c in ("docs", "data") or k in INSTR or p.endswith((".json", ".html", ".md")): continue
        exe = modes[p] == "100755" or re.search(r"(^|/)(bin|scripts?|tools|hooks)/", p)
        if c == "code" or exe: scripts[p.split("/")[-1]] = p
        if exe: scripts.setdefault(p.split("/")[-1].rsplit(".", 1)[0], p)
    heads = defaultdict(set); used_tokens = Counter(); n_cmd = Counter()
    for p, text in instr.items():
        for head, sub, line in command_lines(text, scripts):
            heads[(head, sub)].add(p); n_cmd[(head, sub)] += 1; used_tokens.update(set(line.split()))
    w("Commands quoted in instruction files (code blocks and backticks), most used first:\n")
    w(table(["Command", "Uses", "In files", "Code behind it"],
            [(f"`{h} {s}`".replace(" `", "`"), n, len(heads[(h, s)]), f"`{scripts[h]}`" if h in scripts else "")
             for (h, s), n in n_cmd.most_common(60)]))
    alltext = {p: t for p, (k, c, t) in files.items() if t}
    rows = []
    for p in sorted(set(scripts.values())):
        if not (modes[p] == "100755" or re.search(r"(^|/)(bin|scripts?|tools|hooks)/", p)) or files[p][1] == "tests": continue
        name = p.split("/")[-1]
        by_instr = sum(name in t for q, t in instr.items()); by_other = sum(name in t for q, t in alltext.items() if q != p and q not in instr)
        rows.append((f"`{p}`", alltext[p].count("\n"), by_instr, by_other, "unreferenced" if by_instr + by_other == 0 else ""))
    w("Scripts and executables, and how many files name them (a text match on the file name):\n")
    w(table(["Script", "Lines", "Instruction files", "Other files", "Note"], rows))
    rows = []
    for p, text in alltext.items():
        if files[p][1] not in ("code", "claude", "other") or p in instr: continue
        names = {x for m in SUBDEF.finditer(text) for x in m.groups() if x}
        if p.endswith((".sh", ".bash")) or "." not in p.split("/")[-1]: names |= {x for m in CASE.finditer(text) for x in m[1].split("|")}
        if names: rows.append((f"`{p}`", ", ".join(f"{n} ({used_tokens[n]})" for n in sorted(names))))
    if rows:
        w("Subcommands defined in code (pattern match), with the number of instruction files whose quoted commands use the word; (0) is a dead candidate to check by reading:\n")
        w(table(["File", "Subcommands (uses)"], rows))

    # 4. Duplication
    w("## 4. Duplication between instruction files\n")
    where = defaultdict(set)
    for p, text in instr.items():
        for line in text.splitlines():
            n = " ".join(line.lower().split())
            if len(n) >= 50: where[n].add(p)
    pairs = Counter(pair for fs in where.values() if len(fs) > 1 for pair in combinations(sorted(fs), 2))
    long_lines = sum(len(fs) for fs in where.values())
    w(f"Lines of 50+ characters that appear in two or more instruction files: {sum(len(fs) for fs in where.values() if len(fs) > 1)} "
      f"of {long_lines} (counted once per file).\n")
    if pairs: w(table(["File A", "File B", "Shared lines"], [(f"`{a}`", f"`{b}`", n) for (a, b), n in pairs.most_common(15)]))

    # 5. Growth
    w("## 5. Growth\n")
    commits = [l.split() for l in git("log", "--first-parent", "--reverse", "--format=%H %as").splitlines()]
    step = max(1, (len(commits) - 1) // 11) if len(commits) > 1 else 1
    sample = commits[::step] + ([commits[-1]] if (len(commits) - 1) % step else [])
    rows = []
    for sha, date in sample:
        b = Counter(); n = Counter()
        for l in git("ls-tree", "-r", "-l", sha).splitlines():
            meta, p = l.split("\t", 1); size = meta.split()[3]; k = kind(p, plugin); c = "instructions" if k in INSTR else category(p, k)
            b[c] += int(size) if size.isdigit() else 0; n["files"] += 1; n["skills"] += p.endswith("SKILL.md")
        rows.append((date, f"`{sha[:8]}`", n["files"], n["skills"], b["instructions"], b["code"], b["tests"], b["docs"]))
    w(f"{len(commits)} commits on the first-parent line, from {commits[0][1]} to {commits[-1][1]}. Sizes in bytes.\n")
    w(table(["Date", "Commit", "Files", "Skills", "Instructions", "Code", "Tests", "Docs"], rows))
    born, died = {}, {}
    for status, store in (("A", born), ("D", died)):
        date = ""
        for l in git("log", "--reverse", f"--diff-filter={status}", "--format=@%as", "--name-only").splitlines():
            if l.startswith("@"): date = l[1:]
            elif l and (status == "D" or l not in store): store[l] = date
    rows = [(born[p], f"`{p}`", kind(p, plugin), "" if p in files else f"removed {died.get(p, '?')}")
            for p in born if kind(p, plugin) in INSTR | {"settings", "hook", "mcp"} and (p in files or p.endswith(("SKILL.md", "CLAUDE.md")) or "/commands/" in p)]
    w("When each piece of Claude Code material first appeared (removed skills, commands and CLAUDE.md files included):\n")
    w(table(["First commit", "File", "Kind", "Now"], sorted(rows)))
    tops = {}
    for p, d in born.items(): tops.setdefault(p.split("/")[0] if "/" in p else "(root files)", d)
    w("Top-level directories by first appearance: " + ", ".join(f"`{t}` {d}" for t, d in sorted(tops.items(), key=lambda x: x[1])) + "\n")

    text = "\n".join(out)
    if "-o" in sys.argv: Path(sys.argv[sys.argv.index("-o") + 1]).write_text(text); print(f"wrote {sys.argv[sys.argv.index('-o') + 1]}")
    else: print(text)


main()
