#!/usr/bin/env python3
"""Wiki health check (OKF v0.2). Pure stdlib — no external deps.

Run from anywhere: resolves the repo root from this file's location
(.claude/skills/lint/lint.py -> repo root is three levels up).

Checks (hard = counted in RESULT):
  - OKF conformance   : parseable frontmatter, non-empty `type` (spec §11)
  - locally required  : `title`, `description`, `generated.by`, `generated.at`
  - timestamp format  : every OKF time-valued key is ISO 8601 with UTC offset
  - legacy v0.1 fields: timestamp / updated / url / key_sources / arising_from /
                        inspired_by / related_sources / body `## 引用 (Citations)`
  - vocabularies      : `status` (draft|stable|deprecated), `stage` per type
  - project root      : `root`, when present, is a directory name that really is an
                        ancestor of the page (not a path)
  - provenance        : sources[].resource present and resolving; unique ids;
                        every body `[^id]` footnote backed by a sources entry
  - broken links      : relative markdown links whose target file is missing
  - broken concept-ids: frontmatter link-list Concept IDs with no page
  - idea grounding    : ideas must have non-empty `addresses` + 反証条件 section
  - computations      : `type: Attested Computation` requires `runtime`
  - index sync        : pages missing from / extra in wiki/index.md, okf_version
  - log format        : `## YYYY-MM-DD` headings, newest first

Informational (reported, never fails the run):
  - orphans, stale (`now >= stale_after`), trust tiers, deprecated pages
  - KaTeX style: multi-char sub/superscript without braces, stray `$`
  - pages without `root` (the field is tool metadata, so its absence is not a fault)
"""
import os, re, glob
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
WIKI = os.path.join(REPO, "wiki")
INDEX = os.path.join(WIKI, "index.md")
LOG = os.path.join(WIKI, "log.md")
RESERVED = {"index.md", "log.md"}
OKF_VERSION = "0.2"
# `root` names the project root as a *directory name* — the nearest ancestor so called —
# which is why the one literal is correct at every depth. Validate that shape and that
# such an ancestor exists, rather than a fixed name: a path there is depth- or
# machine-dependent and silently resolves elsewhere (CLAUDE.md §3.0).


def ancestor_named(path, name):
    d = os.path.dirname(os.path.abspath(path))
    while True:
        if os.path.basename(d) == name:
            return True
        parent = os.path.dirname(d)
        if parent == d:
            return False
        d = parent

# frontmatter fields holding bare Concept IDs (lateral relations, not provenance)
LINK_FIELDS = {
    "concepts", "methods", "problems", "entities", "related", "solves",
    "addresses", "addressed_by", "ideas", "open_problems", "related_problems",
    "related_ideas", "related_methods",
}
# retired in v0.2 -> see okf-conformance skill for the migration table
LEGACY_FIELDS = {
    "timestamp": "generated.at",
    "updated": "generated.at",
    "url": "resource",
    "key_sources": "sources (relation: key-source)",
    "arising_from": "sources (relation: arising-from)",
    "inspired_by": "sources (relation: inspired-by)",
    "related_sources": "sources",
}
STATUS_VALUES = {"draft", "stable", "deprecated"}
STAGE_VALUES = {
    "source":  {"to-read", "skimmed", "read", "deep-read"},
    "topic":   {"active", "mature", "dormant"},
    "problem": {"open", "partially-addressed", "solved"},
    "idea":    {"seed", "developing", "promising", "validated", "parked", "discarded"},
}
TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$')

files = [f for f in glob.glob(os.path.join(WIKI, "**/*.md"), recursive=True)
         if os.path.basename(f) not in RESERVED]


def cid(path):                       # absolute md path -> Concept ID
    return os.path.relpath(path, WIKI)[:-3]


valid_ids = {cid(f) for f in files}


def split_front(content):
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', content, re.S)
    return (m.group(1), m.group(2)) if m else (None, content)


def unquote(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        v = v[1:-1]
    return v.strip()


def scalar(front, key):
    """Top-level scalar value, or None. Ignores nested/indented keys."""
    m = re.search(r'^%s:[ \t]*(.*)$' % re.escape(key), front, re.M)
    return unquote(m.group(1)) if m else None


def flow_pairs(text):
    """`{ a: 1, b: 2 }` or `a: 1, b: 2` -> dict (values must not contain commas)."""
    text = text.strip().lstrip("{").rstrip("}")
    out = {}
    for part in text.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = unquote(v)
    return out


def block(front, key):
    """Lines belonging to a top-level block field (`key:` then indented lines)."""
    lines = front.split("\n")
    for i, line in enumerate(lines):
        if re.match(r'^%s:[ \t]*$' % re.escape(key), line) or \
           re.match(r'^%s:[ \t]*\S' % re.escape(key), line):
            head = line.split(":", 1)[1].strip()
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and not nxt[0].isspace():
                    break
                body.append(nxt)
            return head, "\n".join(body)
    return None, None


def parse_sources(front):
    """-> list of dicts. Accepts flow (`- { id: x, ... }`) and block items."""
    head, body = block(front, "sources")
    if head is None:
        return []
    text = body if not head else head + "\n" + (body or "")
    items, cur = [], None
    for line in text.split("\n"):
        if re.match(r'^\s*-\s', line):
            if cur is not None:
                items.append(cur)
            cur = re.sub(r'^\s*-\s', '', line)
        elif cur is not None and line.strip():
            cur += "," + line.strip()
    if cur is not None:
        items.append(cur)
    out = []
    for it in items:
        d = {}
        for k in ("id", "resource", "relation", "last_modified", "author", "usage_count"):
            m = re.search(r'(?:^|[{,]\s*)%s:\s*([^,}\n]+)' % k, it)
            if m:
                d[k] = unquote(m.group(1))
        out.append(d)
    return out


def verified_events(front):
    head, body = block(front, "verified")
    if head is None:
        return []
    if head.startswith("{"):
        return [flow_pairs(head)]
    return [flow_pairs(re.sub(r'^\s*-\s', '', l))
            for l in (body or "").split("\n") if l.strip().startswith("-")]


def resolve(srcdir, path):
    """Resolve a relative path-valued field. Returns abs path, or None for URLs."""
    if re.match(r'^[a-z][a-z0-9+.-]*://', path) or path.startswith("mailto:"):
        return None
    return os.path.normpath(os.path.join(srcdir, path.split("#")[0]))


broken_links, broken_ids = [], []
missing_frontmatter, no_type, no_title, no_description = [], [], [], []
no_generated, bad_time, legacy, bad_status, bad_stage = [], [], [], [], []
bad_root, no_root = [], []
src_no_resource, src_unresolved, src_dup_id, bad_footnote = [], [], [], []
ungrounded_ideas, no_falsification, comp_no_runtime = [], [], []
orphan_exempt, stale, deprecated = set(), [], []
katex_unknown, katex_syntax, katex_brace_hint, katex_stray_dollar = [], [], [], []
tiers = {"unverified": 0, "machine-confirmed": 0, "human-reviewed": 0}
linked_to = set()
now = datetime.now(timezone.utc)


def check_time(me, key, val):
    if val and not TS_RE.match(val):
        bad_time.append((me, "%s: %s" % (key, val)))


for f in sorted(files):
    content = open(f, encoding="utf-8").read()
    me, srcdir = cid(f), os.path.dirname(f)
    front, body = split_front(content)

    if front is None:
        missing_frontmatter.append(me)
        front = ""
    else:
        ptype = scalar(front, "type") or ""
        if not ptype:
            no_type.append(me)
        if not scalar(front, "title"):
            no_title.append(me)
        if not scalar(front, "description"):
            no_description.append(me)

        # trust: generated / verified
        ghead, _ = block(front, "generated")
        g = flow_pairs(ghead) if ghead else {}
        if not g.get("by") or not g.get("at"):
            no_generated.append(me)
        check_time(me, "generated.at", g.get("at"))
        vs = verified_events(front)
        for v in vs:
            check_time(me, "verified.at", v.get("at"))
        if not vs:
            tiers["unverified"] += 1
        elif any(str(v.get("by", "")).startswith("human:") for v in vs):
            tiers["human-reviewed"] += 1
        else:
            tiers["machine-confirmed"] += 1

        # lifecycle / freshness
        st = scalar(front, "status")
        if st and st not in STATUS_VALUES:
            bad_status.append((me, st))
        if st == "deprecated":
            deprecated.append(me)
        sa = scalar(front, "stale_after")
        check_time(me, "stale_after", sa)
        if sa and TS_RE.match(sa):
            if datetime.fromisoformat(sa.replace("Z", "+00:00")) <= now:
                stale.append((me, sa))

        # stage vocabulary
        stg = scalar(front, "stage")
        allowed = STAGE_VALUES.get(ptype)
        if stg is not None:
            if allowed is None:
                bad_stage.append((me, "%s は stage を持たない (%s)" % (ptype, stg)))
            elif stg not in allowed:
                bad_stage.append((me, stg))

        # project root (tool metadata; absent is fine, wrong is not)
        rt = scalar(front, "root")
        if rt is None:
            no_root.append(me)
        elif "/" in rt or rt in (".", ".."):
            bad_root.append((me, "%s (パスではなくディレクトリ名で書く)" % rt))
        elif not ancestor_named(f, rt):
            bad_root.append((me, "%s (この名前の祖先ディレクトリが無い)" % rt))

        # retired v0.1 fields
        for old, new in LEGACY_FIELDS.items():
            if re.search(r'^%s:' % re.escape(old), front, re.M):
                legacy.append((me, "%s -> %s" % (old, new)))

        # provenance
        seen_ids = set()
        for s in parse_sources(front):
            sid = s.get("id")
            if sid:
                if sid in seen_ids:
                    src_dup_id.append((me, sid))
                seen_ids.add(sid)
            res = s.get("resource")
            if not res:
                src_no_resource.append((me, sid or "(id なし)"))
                continue
            tgt = resolve(srcdir, res)
            if tgt is None or "/" not in res:      # URL or scope descriptor
                continue
            if os.path.exists(tgt):
                if tgt.endswith(".md") and tgt.startswith(WIKI + os.sep):
                    linked_to.add(cid(tgt))
            else:
                src_unresolved.append((me, res))
        for fn in set(re.findall(r'\[\^([^\]]+)\]', body)):
            if fn not in seen_ids:
                bad_footnote.append((me, fn))

        # lateral relations: bare Concept IDs
        for line in front.split("\n"):
            fm = re.match(r'^(\w+):\s*\[(.*)\]\s*$', line)
            if not fm or fm.group(1) not in LINK_FIELDS:
                continue
            for tok in (unquote(t) for t in fm.group(2).split(",")):
                if not tok or "/" not in tok:
                    continue
                linked_to.add(tok)
                if tok not in valid_ids:
                    broken_ids.append((me, tok))

        # Attested Computation
        if ptype == "Attested Computation":
            if not scalar(front, "runtime"):
                comp_no_runtime.append(me)
            for key in ("computation",):
                p = scalar(front, key)
                if p:
                    tgt = resolve(srcdir, p)
                    if tgt and not os.path.exists(tgt):
                        broken_links.append((me, "%s: %s" % (key, p)))
            for key in ("executor", "attester"):
                head, _ = block(front, key)
                if head:
                    p = flow_pairs(head).get("resource")
                    if p:
                        tgt = resolve(srcdir, p)
                        if tgt and not os.path.exists(tgt):
                            broken_links.append((me, "%s.resource: %s" % (key, p)))

        # idea-specific
        if ptype == "idea":
            am = re.search(r'^addresses:\s*\[(.*?)\]', front, re.M)
            if not am or not am.group(1).strip():
                ungrounded_ideas.append(me)
            if "## 反証条件" not in body or \
               not body.split("## 反証条件")[1].split("## ")[0].strip():
                no_falsification.append(me)

    # legacy body citations section
    if re.search(r'^##\s*引用\s*\(Citations\)', body, re.M):
        legacy.append((me, "本文 `## 引用 (Citations)` -> sources + [^id] 脚注"))

    # body relative markdown links
    for url in re.findall(r'\[[^\]^][^\]]*\]\(([^)]+)\)', body):
        if url.startswith("#"):
            continue
        tgt = resolve(srcdir, url)
        if tgt is None or not tgt.endswith(".md"):
            continue
        if os.path.exists(tgt):
            if tgt.startswith(WIKI + os.sep):
                linked_to.add(cid(tgt))
        else:
            broken_links.append((me, url))

orphans = [cid(f) for f in sorted(files)
           if cid(f) not in linked_to and cid(f) != "overview"]

# ---- reserved files -------------------------------------------------------
index_problems = []
index_ids = set()
if not os.path.exists(INDEX):
    index_problems.append("wiki/index.md が無い")
else:
    itext = open(INDEX, encoding="utf-8").read()
    ifront, ibody = split_front(itext)
    if ifront is None:
        index_problems.append("bundle root の index.md に `okf_version` frontmatter が無い")
    else:
        keys = [l.split(":")[0] for l in ifront.split("\n") if l.strip() and not l[0].isspace()]
        if keys != ["okf_version"]:
            index_problems.append("index.md の frontmatter は okf_version のみ許可 (現状: %s)" % keys)
        if unquote(scalar(ifront, "okf_version") or "") != OKF_VERSION:
            index_problems.append("okf_version が \"%s\" でない" % OKF_VERSION)
    for url in re.findall(r'\[[^\]]*\]\(([^)]+)\)', ibody):
        if url.endswith(".md") and not re.match(r'^[a-z]+://', url):
            index_ids.add(url[:-3])

log_problems = []
if not os.path.exists(LOG):
    log_problems.append("wiki/log.md が無い")
else:
    ltext = open(LOG, encoding="utf-8").read()
    if split_front(ltext)[0] is not None:
        log_problems.append("log.md に frontmatter がある（置かない）")
    heads = re.findall(r'^##\s+(.*)$', ltext, re.M)
    bad = [h for h in heads if not re.match(r'^\d{4}-\d{2}-\d{2}$', h.strip())]
    if bad:
        log_problems.append("日付見出しが ISO 形式でない: %s" % ", ".join(bad[:3]))
    dates = [h.strip() for h in heads if re.match(r'^\d{4}-\d{2}-\d{2}$', h.strip())]
    if dates != sorted(dates, reverse=True):
        log_problems.append("日付見出しが新しい順に並んでいない")

actual_ids = {cid(f) for f in files if cid(f) != "overview"}
missing_in_index = sorted(actual_ids - index_ids)
extra_in_index = sorted(i for i in index_ids if i not in valid_ids and i != "overview")

# ---------------------------------------------------------------- KaTeX (§9)
# 数式は KaTeX で描画される（VS Code 組み込みプレビュー / mdExplorer）。未対応の
# コマンドは静かに壊れず赤いエラーになるので、機械的に弾けるものは弾く。
# markdown のエスケープを数式内に持ち込むのが最頻の失敗（`\*` `\_` は KaTeX に無い）。
KATEX_LIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "katex_commands.txt")
katex_known = set()
if os.path.exists(KATEX_LIST):
    katex_known = {l.strip() for l in open(KATEX_LIST, encoding="utf-8")
                   if l.strip() and not l.startswith("#")}

MATH_ENVS = ("aligned|align|alignat|alignedat|array|cases|dcases|rcases|split|"
             "gathered|gather|matrix|pmatrix|bmatrix|Bmatrix|vmatrix|Vmatrix|"
             "smallmatrix|subarray|darray|equation|CD")


def math_spans(content):
    """[(kind, text)] for every math span in a page. Code is stripped first."""
    out = []
    for m in re.finditer(r'```math\s*\n(.*?)```', content, re.S):     # ```math fence
        out.append(("fence", m.group(1)))
    rest = re.sub(r'```math\s*\n.*?```', '', content, flags=re.S)
    rest = re.sub(r'```.*?```', '', rest, flags=re.S)                 # other fences
    rest = re.sub(r'`[^`\n]*`', '', rest)                             # inline code
    for m in re.finditer(r'\$\$(.+?)\$\$', rest, re.S):
        out.append(("display", m.group(1)))
    rest = re.sub(r'\$\$.+?\$\$', '', rest, flags=re.S)
    inline = r'(?<![\$\\])\$(?!\s)([^\$\n]*?)(?<!\s)\$(?!\$)'
    for m in re.finditer(inline, rest):
        out.append(("inline", m.group(1)))
    rest = re.sub(inline, '', rest)
    for m in re.finditer(r'\\begin\{(%s)\}(.*?)\\end\{\1\}' % MATH_ENVS, rest, re.S):
        out.append(("env", m.group(0)))                               # $$ なしの環境も描画される
    # 数式として消費されずに残った裸の $（未閉じの数式か、エスケープ忘れ）
    for m in re.finditer(r'(?<!\\)\$', re.sub(r'\\begin\{(%s)\}.*?\\end\{\1\}' % MATH_ENVS,
                                              '', rest, flags=re.S)):
        out.append(("stray$", m.group(0)))
    return out


for f in sorted(files):
    me = cid(f)
    content = open(f, encoding="utf-8").read()
    for kind, t in math_spans(content):
        if kind == "stray$":
            katex_stray_dollar.append((me, "対応しない $（未閉じの数式 or \\$ のエスケープ漏れ）"))
            continue
        excerpt = " ".join(t.split())[:60]
        if katex_known:
            for c in re.findall(r'\\[a-zA-Z]+', t) + re.findall(r'\\[^a-zA-Z\s]', t):
                if c not in katex_known:
                    katex_unknown.append((me, "%s（%s: %s）" % (c, kind, excerpt)))
        if t.count("{") - t.count(r"\{") != t.count("}") - t.count(r"\}"):
            katex_syntax.append((me, "波括弧の対応が取れない（%s: %s）" % (kind, excerpt)))
        if t.count(r"\left") != t.count(r"\right"):
            katex_syntax.append((me, "\\left と \\right の数が違う（%s: %s）" % (kind, excerpt)))
        for m in re.finditer(r'(?:\{[^{}]*\}|\\[a-zA-Z]+|[A-Za-z0-9])([_^])'
                             r'(?:\{[^{}]*\}|\\[a-zA-Z]+|[A-Za-z0-9])\1', t):
            katex_syntax.append((me, "二重%s（%s: %s）"
                                 % ("添字" if m.group(1) == "_" else "上付き", kind, excerpt)))
        for m in re.finditer(r'[_^](?!\{)([A-Za-z0-9]{2,})', t):
            katex_brace_hint.append((me, "%s → 波括弧を付ける（%s: %s）"
                                     % (m.group(0), kind, excerpt)))



def section(title, items, fmt=lambda x: x):
    print("- %s: %d" % (title, len(items)))
    for it in items:
        print("    %s" % fmt(it))


pair = lambda x: "%s -> %s" % (x[0], x[1])

print("=== Wiki health check (OKF v%s) ===" % OKF_VERSION)
print("pages: %d  |  valid concept-ids: %d" % (len(files), len(valid_ids)))
print("- 矛盾 (contradictions): LLMによる確認が必要")
print("\n[hard]")
section("frontmatter不備 (欠落)", missing_frontmatter)
section("type欠落 (OKF必須)", no_type)
section("title欠落", no_title)
section("description欠落", no_description)
section("generated 欠落/不完全 (by+at)", no_generated)
section("時刻形式が不正 (ISO 8601 + offset)", bad_time, pair)
section("v0.1 残存フィールド", legacy, pair)
section("status の値が規約外", bad_status, pair)
section("stage の値が規約外", bad_stage, pair)
section("root の値が規約外", bad_root, pair)
section("sources: resource 欠落", src_no_resource, pair)
section("sources: resource が解決しない", src_unresolved, pair)
section("sources: id 重複", src_dup_id, pair)
section("脚注に対応する sources エントリが無い", bad_footnote, pair)
section("壊れリンク (broken md links)", broken_links, pair)
section("壊れConcept-ID (frontmatter)", broken_ids, pair)
section("接地なしアイデア", ungrounded_ideas)
section("反証条件なしアイデア", no_falsification)
section("runtime 欠落 (Attested Computation)", comp_no_runtime)
section("index未掲載ページ", missing_in_index)
section("index余分な項目", extra_in_index)
section("index.md の形式 (OKF §8)", index_problems)
section("log.md の形式 (OKF §9)", log_problems)
section("数式: KaTeX未対応コマンド", katex_unknown, pair)
section("数式: 構文エラー (括弧/二重添字)", katex_syntax, pair)

print("\n[info]")
section("孤立 (orphans)", orphans)
section("陳腐化 (now >= stale_after)", stale, pair)
section("deprecated ページ", deprecated)
section("root 未記載", no_root)
section("数式: 添字に波括弧なし (2文字以上)", katex_brace_hint, pair)
section("数式: 対応しない $", katex_stray_dollar, pair)
print("- trust tiers: unverified %d / machine-confirmed %d / human-reviewed %d"
      % (tiers["unverified"], tiers["machine-confirmed"], tiers["human-reviewed"]))

hard = [missing_frontmatter, no_type, no_title, no_description, no_generated,
        bad_time, legacy, bad_status, bad_stage, bad_root, src_no_resource, src_unresolved,
        src_dup_id, bad_footnote, broken_links, broken_ids, ungrounded_ideas,
        no_falsification, comp_no_runtime, missing_in_index, extra_in_index,
        index_problems, log_problems, katex_unknown, katex_syntax]
ok = not any(hard)
print("\nRESULT:", "OK ✅ (OKF v%s conformant, links resolve, index synced)" % OKF_VERSION
      if ok else "問題あり — 上記 [hard] を確認")
