---
name: ingest
description: raw/ 配下のソース（PDF論文・Web記事・メモ・進捗）を読み、要約ページを作成し、概念/手法/課題/トピック/索引/ログを更新してWikiに統合する。新しい論文・記事・メモを取り込みたいときに使う。
---

# ソースをWikiに取り込む (Ingest)

`raw/` 配下のソースを読み込み、`CLAUDE.md` のスキーマに従ってWikiへ統合する。
1回の ingest は通常 **5〜15ページ**に波及する。

## 0. 準備

セッション開始チェックリスト（`CLAUDE.md` §10）が未実施なら先に行う: `wiki/log.md` の先頭（新しい順・`grep "^## " wiki/log.md | head`）と `wiki/index.md` を読む。

## 1. ソースの特定

- `$ARGUMENTS` にファイル名があればそれを使う。
- 無ければ `raw/papers/`・`raw/web/`・`raw/memos/`・`raw/progress/` を一覧し、最も新しい未取り込みファイル（`wiki/log.md` の ingest 履歴に無いもの）を提案、または人間に選ばせる。
- 種別（`kind`）を判定: `papers/`→paper、`web/`→web、`memos/`→memo、`progress/`→progress。

## 2. ソースを読む（種別ごとに手順が異なる）

> 読み方の正準手順は **`read-raw-sources` skill（raw ソースの読み方）** にある。全 skill 共通なので、迷ったらそちらに従う。

- **PDF論文**: **`read-raw-sources` §2 の2パス抽出を必ず行う**。単一の方式では本文か表のどちらかが必ず壊れるため、両方をスクラッチパッドへ出力してから読む。
  ```bash
  SP=<スクラッチパッド>
  pdftotext          raw/papers/<citekey>.pdf "$SP/<citekey>.txt"         # 本文の通読用（段組が正しい順序）
  pdftotext -layout  raw/papers/<citekey>.pdf "$SP/<citekey>.layout.txt"  # 表・数値の回収用（列が揃う）
  ```
  - **本文は `.txt`（素）で読む** — `-layout` の本文は左右カラムが同一行に混線し、文を読み落とす／取り違える。
  - **表の数値は `.layout.txt` から取る** — `.txt` 側の表は崩壊しているので信用しない。要約に転記する数値はこちらが根拠。
  - 20ページ超なら **abstract → intro → conclusion** を先に読み、全体像を掴んでから method / results を読む。
  - **Readツール（ページ画像）は `read-raw-sources` §3 の場合に限る** — 図が要点を握るとき、2パスの両方で崩れる複雑な表、スキャンPDF。該当ページだけを開く（`raw/assets/` に切り出された図があれば併読）。
  - `raw/` は読み取り専用。抽出テキストを `raw/` に置かない。
- **Web記事**: `raw/web/*.md`（Web Clipper等で取り込み済みmarkdown）を読む。インライン画像は本文を読んだ後に必要なものだけ別途確認。`raw/` にまだ無くURLだけ与えられた場合は WebFetch で取得し、人間に「`raw/web/` に保存してよいか」確認の上で保存（rawは人間がキュレートする層なので原則は人間に促す）。
- **メモ**: `raw/memos/*.md` を読む。メモは「自分の思考」なので、要約より **構造化**（どの課題・どのアイデアに関係するか）を重視する。

## 3. citekey を決める

`CLAUDE.md` §5の規則で `citekey` を生成（例 `vaswani2017attention`）。人間に確認・調整を促す。
論文なら `raw/refs.bib` に対応BibTeXエントリがあるか確認。**無ければ ingest の最後に追記**する（§8）。

## 4. 要点を人間と確認（対話モード時）

以下を提示し、「この理解で合っているか / 強調・省略したい点はあるか」を尋ねる:
- 中心の課題（Problem）
- 鍵となる手法（Method）
- 主要な結果・主張（Results）
- 注目すべき限界（Limitations）
- 既存Wikiとの関係（似た source、関連 concept/problem）

> バッチ取り込み（多数を一気に）を指示された場合はこの対話を省略し、最後にまとめて報告する。

## 5. ソースページを書く

`wiki/sources/<citekey>.md` を `CLAUDE.md` §3.1 のスキーマで作成。
- frontmatter を完全に埋める。`type`（OKF必須）・`title`・`description`（日本語一行）・`generated: { by: claude-code/<model>, at: <ISO 8601 + offset> }`・`root: research` を必ず入れる。`root` は**本 skill が作る全ページ共通で常にこの値**（§6・§7 の concept/method/problem ページも同じ。`CLAUDE.md` §3.0）。`stage`（`to-read`/`skimmed`/`read`/`deep-read`）と `status`（OKF lifecycle。既定 `stable`、骨組みだけなら `draft`）を取り違えない（`CLAUDE.md` §3.0）。
- **provenance は frontmatter の `sources`**（`CLAUDE.md` §4.1）。ソースページ自身は一次資料を指す: `- { id: <citekey>, resource: ../../raw/papers/<citekey>.pdf, title: "..." }`。
- `concepts`/`methods`/`problems`/`entities` は**横の関係**なので **Concept ID** の素スカラ（例 `concepts/self-attention`）で記す。
- 本文の相互参照は**相対 markdown リンク**（例 `[title](../concepts/self-attention.md)`）。**`## 引用 (Citations)` 節は作らない**（v0.2 で廃止）。Wiki にページが無い外部資料を引くときは `sources` にエントリを足し `[^id]` 脚注で紐付ける（§4.2）。
- 本文 `## 自分の研究との接続` で、**この論文が我々に突きつける課題**を言語化する。これが課題抽出の起点。

## 6. concept / method ページを更新・作成

このソースが導入・使用・拡張する主要な概念/手法ごとに:
- 既存ページがあれば、このソースの貢献を1段落追記し、`sources` に `- { id: <citekey>, resource: ../sources/<citekey>.md, title: "...", relation: key-source }` を追加。`generated.at` を更新する。
- 無ければ `wiki/concepts/<slug>.md` または `wiki/methods/<slug>.md` を新規作成（`title`/`description`/`generated` を必ず付与）。骨組みだけの stub なら `status: draft` を付ける。

## 7. problem ページを更新・作成（研究の核）

- このソースが扱う既存課題があれば `addressed_by` に追加し、「これまでのアプローチと限界」表に1行追加。
- ソースの限界・未解決点から **新しい課題が見えたら** `wiki/problems/<slug>.md` を作成し、`sources` に `- { id: <citekey>, resource: ../sources/<citekey>.md, relation: arising-from }` を入れる。`severity` と `stage`（`open` 等）を付ける。

## 8. topic / overview / refs.bib を更新

- 関連する `wiki/topics/<slug>.md` の thesis・timeline を更新（無く、かつ系譜を成すテーマなら新規作成を提案）。
- 領域の高レベル像が変わる重要ソースなら `wiki/overview.md` の該当節を改訂。
- 論文の場合、`raw/refs.bib` に BibTeX エントリが無ければ追記（citekey一致）。

## 9. 矛盾チェック

このソースの主張が既存ページと矛盾しないか確認。矛盾があれば**消さずに両論併記**し、該当ページに `> **警告:** 矛盾: ...（[title](相対パス.md)）` を追記する。

## 10. wiki/index.md と wiki/log.md を更新

- `wiki/index.md`（OKF §8）: 該当カテゴリの箇条書きに `* [title](sources/<citekey>.md) - description （kind / stage: read）` を追加、新規 concept/problem/idea も該当節に追加、冒頭の集計行と日付を更新。frontmatter は `okf_version: "0.2"` のみ。
- `wiki/log.md`（OKF §9）: **新しい順**。当日の `## YYYY-MM-DD` 見出しが無ければ先頭に作り、その下に追記:
  ```markdown
  ## YYYY-MM-DD
  * **Ingest**: <タイトル>（`raw/<path>`）。Touched: [x](sources/x.md), [y](concepts/y.md)（作成・更新した全ページ）。Takeaways: (2-3点)。Notes: 矛盾・フォローアップ。
  ```

## 11. 報告

作成・更新した全ファイルを一覧で報告。抽出した課題があれば「`/idea` で展開しますか？」と提案。

## Args
`$ARGUMENTS` — 任意。`raw/` 内のファイル名/パス。空なら未取り込みファイルを提案する。
