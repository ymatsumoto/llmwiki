---
name: lint
description: Wikiの健康診断。矛盾・陳腐化した主張・孤立ページ・欠落ページ・壊れたリンク・不備frontmatterを検出し、次に読むべき文献や問うべき問いを提案する。定期的に、またWikiが乱れてきたと感じたときに使う。--fix で承認済みの修正を適用。
---

# Wiki の健康診断 (Lint)

Wikiが成長しても健全さを保つための点検。検出 → 報告 → （承認を得て）修正の順で進む。

## 手順

1. **機械チェックを実行**: `python3 .claude/skills/lint/lint.py` を走らせる。決定論的な項目を一括検査し、`[hard]`（適合違反）／`[info]`（参考情報）に分けて出す。`RESULT: OK ✅` は `[hard]` が全て 0 のとき。そのうえで LLM が意味的項目（矛盾・陳腐化の中身）を担当する。`Grep` で相対 markdown リンク（`](../` 等）や frontmatter の Concept ID を横断的に拾ってもよい。

   スクリプトが見る `[hard]`: OKF 適合（frontmatter/`type`）、ローカル必須（`title`/`description`/`generated.by`+`at`）、時刻形式（UTC オフセット付き ISO 8601）、**v0.1 残存フィールド**（`timestamp`/`updated`/`url`/`key_sources`/`arising_from`/`inspired_by`/`related_sources`/本文 `## 引用 (Citations)`）、語彙（`status` は lifecycle、`stage` は種別ごと）、provenance（`sources[].resource` の存在と解決・`id` 重複・`[^id]` 脚注の裏付け）、壊れリンク／壊れ Concept ID、アイデア接地・反証条件、`Attested Computation` の `runtime`、index/log の形式と同期、**KaTeX**（未対応コマンド・波括弧の対応・`\left`/`\right` の対応・二重添字）。
   `[info]`: 孤立ページ、`stale_after` 超過、`deprecated` ページ、trust tier の内訳、KaTeX の作法（2文字以上の添字に波括弧が無い・対応しない裸の `$`）。

2. **以下を検出して報告**（機械チェック＋LLM判断）:
   - **矛盾 (contradictions)** [LLM]: 異なるページ間で衝突する主張。新ソースが旧主張を覆していないか。矛盾は消さず両論併記し `> **警告:**` で明示（`CLAUDE.md` §9）。
   - **陳腐化 (stale)** [script+LLM]: `now >= stale_after` のページ（script）に加え、新しいソースに取って代わられた主張・`generated.at` が古いまま放置されたトピック（LLM）。
   - **孤立ページ (orphans)** [script]: inbound リンク（相対 md リンク / frontmatter Concept ID / 他ページの `sources[].resource`）が無いページ。
   - **欠落ページ (missing)** [LLM]: 何度も言及されるのにページが無い概念・課題。
   - **壊れたリンク** [script]: 解決しない相対 md リンク / Concept ID / `sources[].resource`（対応ファイルが無い）。
   - **OKF 不備** [script]: frontmatter が parseable でない、`type`/`title`/`description`/`generated` の欠落、時刻が UTC オフセット付き ISO 8601 でない、`status`/`stage` の値が規約外。
   - **v0.1 残存** [script]: 退役フィールド（`okf-conformance` skill の移行表）が残っているページ。見つけたら v0.2 形式へ移す。
   - **provenance 不備** [script]: `sources[].resource` の欠落・未解決、`id` 重複、対応する `sources` エントリの無い `[^id]` 脚注。
   - **未確認ページ (trust)** [script+LLM]: `verified` の無いページ（既定であり異常ではない）。重要ページが長く unverified なら人間に確認を促す。**LLM が自分で `verified` を書いてはいけない**（`CLAUDE.md` §0 ルール7）。
   - **接地なしアイデア** [script]: `addresses` が空、または存在しない problem を指す idea。
   - **反証条件なしアイデア** [script]: `## 反証条件` が空の idea。
   - **citekey 不整合** [LLM]: ソースページの citekey（=ファイル名）と `raw/refs.bib` のエントリが食い違う/欠落。
   - **index/log の齟齬** [script]: `wiki/index.md` に載っていないページ、`wiki/log.md` に記録の無い大きな変更。
   - **KaTeX 不備** [script]: 数式内の `\コマンド` が `katex_commands.txt`（KaTeX サポート表のキャッシュ）に無い、波括弧や `\left`/`\right` の対応が取れない、二重添字（`x_a_b`）。KaTeX は未対応コマンドを**静かに壊さず赤いエラーで表示**するので、機械的に弾けるものは弾く（`CLAUDE.md` §9）。**最頻の失敗は markdown のエスケープを数式内に持ち込むこと**（`\*` `\_` は KaTeX に存在しない。`$...$` の内側は markdown として解釈されないのでエスケープ不要）。`[info]` 側は「2文字以上の添字に波括弧が無い」（`a_ij` はエラーにならないが意図と違う描画になる）と「対応しない裸の `$`」（未閉じの数式、または `\$` のエスケープ漏れ）。

3. **健康レポートを提示**: カテゴリごとに件数と具体例を表で。深刻なものから順に。

4. **修正を提案**: 各問題に対する具体的な修正案を出す。
   - `--fix` が指定され、かつ人間が承認したものだけ適用する。
   - **破壊的操作（削除・大規模リネーム）は必ず個別に確認**（`CLAUDE.md` §0）。削除の前に `status: deprecated` で残す選択肢を先に提示する。
   - 適用したら `wiki/index.md`/`wiki/log.md` を更新し、`lint.py` を再実行して `OK ✅` を確認。

5. **能動的提案（lintの価値の半分）**:
   - 埋めるべき**ギャップ**に対し、探すべき文献（→ `/web-survey`）を提案。
   - 蓄積された課題から、立てるべき**新しい問い**や展開できる**アイデア**（→ `/idea`）を提案。
   - 育成が止まっている idea（`seed` のまま古い）を指摘し、次の一手を促す。

6. **wiki/log.md に追記**（OKF §9, 新しい順）:
   ```markdown
   ## YYYY-MM-DD
   * **Lint**: 健康診断 — Findings: 矛盾 N / 孤立 N / 欠落 N / 壊れリンク N / OKF不備 N / v0.1残存 N。Fixed: 適用した修正（あれば）。Suggested: 探すべき文献・問い。
   ```

## KaTeX コマンド表の再生成

`katex_commands.txt` は KaTeX 公式ドキュメントから生成したキャッシュ（オフラインで動かすため同梱）。KaTeX が版を上げたら再生成する:

```bash
cd .claude/skills/lint
for f in supported.md support_table.md; do
  curl -sL -o "/tmp/katex_$f" "https://raw.githubusercontent.com/KaTeX/KaTeX/main/docs/$f"
done
python3 - <<'PYEOF'
import re, datetime
doc = open('/tmp/katex_supported.md').read() + open('/tmp/katex_support_table.md').read()
cmds = lambda t: set(re.findall(r'\\[a-zA-Z]+', t)) | set(re.findall(r'\\[^a-zA-Z\s]', t))
ok, notsup = cmds(doc), set()
for line in doc.split('\n'):
    if re.search(r'not supported', line, re.I):
        notsup |= cmds(line)
final = (ok - notsup) | {r'\begin', r'\end', '\\\\', r'\ '}
open('katex_commands.txt', 'w').write(
    "# KaTeX サポートコマンド（lint.py 用キャッシュ / 生成日 %s）\n" % datetime.date.today()
    + "\n".join(sorted(final)) + "\n")
print(len(final), "commands")
PYEOF
```

このリストは**網羅の保証ではない**。lint が「未対応」と報告したものは <https://katex.org/docs/supported.html> で最終確認する（新しく正当なコマンドを使ったなら表を再生成する）。

## Args
`$ARGUMENTS` — `--fix`（承認済み修正を適用）、または特定カテゴリ/ディレクトリに絞る指定。空なら全体を診断のみ。
