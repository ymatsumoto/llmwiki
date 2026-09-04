---
name: query
description: Wiki に対して研究上の問いを投げ、関連ページを読んで引用付きで合成回答する。価値ある回答は新しいWikiページとして filing する。「〜について整理して」「どの研究が〜を扱っているか」等の問いに使う。
---

# Wiki への問い合わせ (Query)

Wikiの蓄積を使って問いに答える。**RAGのように毎回ゼロから探すのではなく、既に統合された知識を活用**するのが要点。良い回答は揮発させず、Wikiに還元する。

## 手順

1. **索引を読む**: `wiki/index.md` を読み、問いに関連するページを特定する。`grep`/`Grep` でキーワード（用語・著者・citekey）を横断検索してもよい。

2. **関連ページを精読**: 候補ページを実際に読む。ソースページの主張は出典に基づくので、必要なら元の `raw/` まで遡って裏を取る。**`raw/` の読み方は `read-raw-sources` skill に従う** — PDF は同 §2 の2パス抽出（本文は素の `pdftotext`、表の数値は `-layout`）を使い、Readツールでのページ描画は図・複雑な表・スキャンPDFに限る。数値や配列を引用するときは必ずテキスト層を根拠にする。

3. **合成して回答**: 単なる抜粋でなく**統合**して答える。
   - すべての主張に出典を付ける。Wiki内に source ページがあれば `([citekey](相対パス/sources/<citekey>.md))`、無い外部資料は filing 先ページの `sources` に足して `[^id]` 脚注で紐付ける（`CLAUDE.md` §4.2）。
   - 比較は表、論証は散文、列挙は箇条書き（`CLAUDE.md` §9）。
   - Wiki内に答えが無い／薄い部分は **正直に「ギャップ」として明示**する。

4. **回答形式を選ぶ**: 問いに応じて — markdownの解説、比較表、Marpスライド、matplotlib図など。重い生成物は人間に形式を確認。

5. **filing 判断（重要）**: 回答が「非自明な分析・比較・発見した接続」を含むなら、揮発させずWikiに残す。
   - 比較・分析 → `wiki/topics/<slug>.md` または新しい `wiki/concepts/<slug>.md`
   - 新たに見えた課題 → `wiki/problems/<slug>.md`（stubでも可）
   - 新規ページは `type`/`title`/`description`/`generated`/`root: research` 必須、provenance は `sources`、横の関係は Concept ID、本文は相対リンク。内容が薄い stub なら `status: draft`。人間に「この回答を <ページ> として保存しますか？」と確認してから filing。

6. **ギャップの記録**: 回答中に判明した欠落（ページが無い・矛盾が未解決・問いに答えられない）を控える。重要なら problem stub を作るか、`/web-survey` / `/ingest` を提案。

7. **wiki/log.md に追記**（OKF §9, 新しい順）:
   ```markdown
   ## YYYY-MM-DD
   * **Query**: <問い> — Consulted: [x](concepts/x.md), [y](sources/y.md)。Filed: no（会話のみ）/ [新ページ](dir/slug.md)。Gaps: 見つかった欠落・次の一手。
   ```
   （filing した場合は `wiki/index.md` も更新）

## Args
`$ARGUMENTS` — 問い。空なら何を知りたいか尋ねる。
