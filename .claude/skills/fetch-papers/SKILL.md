---
name: fetch-papers
description: 参考文献リスト（DOI/URL を含むテキスト/markdown）から open-access PDF を curl で raw/papers/ に自動ダウンロードし、続けて /ingest で Wiki に取り込む。Gemini Deep Research 等の出力の文献リストを一括取り込みたいときに使う。
---

# 参考文献リストから PDF を取得して取り込む (Fetch & Ingest)

与えられたテキスト/markdown（例: `Gemini_DeepResearch_Result.md`）の参考文献リストから **DOI / URL を抽出**し、**open-access の PDF だけ**を `curl` で `raw/papers/` にダウンロードして、**`/ingest` で Wiki に統合**する。

> 専用 Python スクリプトは作らない。取得は `curl` + 公開 API（Unpaywall / Europe PMC / Crossref / doi.org の `citation_pdf_url`）で行う。依存は `curl`・`jq`（JSON パース）・`poppler-utils`（PDF 検証の `pdfinfo`）のみで、いずれも devcontainer にビルド時導入済み。取り込んだ PDF の**読み方**は `read-raw-sources` skill に従う。

## 原則（守ること）
- **open-access のみ**。paywall を回避しない（sci-hub 等は使わない）。取得不可は「要手動入手」として正直に報告する。
- **raw/ は人間がキュレートする層**（`CLAUDE.md` §0）。**ダウンロード前**に抽出 DOI 一覧を提示して人間に確認、**/ingest 前**に取得マニフェストを提示して確認する。
- 礼儀: User-Agent を付け、`--max-time` を設定し、リクエスト間に `sleep 1`。失敗を連打しない。
- Unpaywall は有効な email 必須。既定は `ymatsumoto@mats.ist.osaka-u.ac.jp`（引数で上書き可）。

## 手順

### 1. 入力の特定と DOI/URL 抽出
- 引数のファイルパスを使う。無ければ作業ディレクトリ直下や `raw/memos/` の最近の `.md` を提示して選ばせる。
- ファイルを Read し、**DOI と直リンク URL を抽出**:
  - DOI 正規表現: `10\.\d{4,9}/[^\s"'<>)\]}]+`（末尾の `. , ; ) ]` は除去）。`doi.org/…`・`dx.doi.org/…` も剥がして DOI 本体に正規化。重複除去。
  - URL: `.pdf` 直リンク、`biorxiv.org`/`ncbi.nlm.nih.gov/pmc`/`europepmc.org` などの記事 URL も拾う。
  - 補助: `grep -oE '10\.[0-9]{4,9}/[^ "'\''<>)\]}]+' <file> | sed 's/[.,;]\+$//' | sort -u`
- 抽出結果（DOI/URL のリスト）を**件数つきで提示**。

### 2. 重複除外（既存 Wiki と照合）
- 既に取り込み済み/取得済みを除く:
  - `raw/refs.bib` の DOI（`grep -i doi raw/refs.bib`）と照合。
  - `wiki/sources/*.md` frontmatter の `resource:`（DOI/URL）と照合。
  - `raw/papers/` の既存ファイル。
- 「新規 N 件 / 既存 M 件（スキップ）」を提示。**ここで人間に「この新規 N 件を取得してよいか」確認**（raw 層のキュレーション）。

### 3. 各 DOI → OA PDF を解決してダウンロード
新規 DOI ごとに、以下の**優先チェーン**で PDF URL を1つ得る。得られたら `curl` で `raw/papers/<name>.pdf` に保存。

1. **Unpaywall**（最優先・横断的）:
   ```bash
   curl -s "https://api.unpaywall.org/v2/<DOI>?email=<EMAIL>" \
     | jq -r '.best_oa_location.url_for_pdf // (.oa_locations[]?.url_for_pdf) // empty' | head -1
   ```
2. **Europe PMC**（生物医学。本 Wiki の多くがここで OA）:
   ```bash
   PMCID=$(curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:<DOI>&format=json" \
     | jq -r '.resultList.result[0].pmcid // empty')
   # → PDF（検証済みの正しい形式）: https://europepmc.org/articles/<PMCID>?pdf=render
   #   ※ REST の .../<PMCID>/fullTextPDF は 404 になるので使わない。
   ```
3. **bioRxiv/medRxiv**（DOI が `10.1101/…`）: `https://www.biorxiv.org/content/<DOI>v1.full.pdf`（v1→v2 と試す）。
4. **doi.org → citation_pdf_url**（出版社ページの meta タグ）:
   ```bash
   HTML=$(curl -sL -A "Mozilla/5.0 (research-wiki fetch-papers)" "https://doi.org/<DOI>")
   echo "$HTML" | grep -oiE '<meta[^>]+citation_pdf_url[^>]+>' | grep -oE 'https?://[^"'\'' ]+\.pdf' | head -1
   ```
- ダウンロード: `curl -sL -A "Mozilla/5.0 (research-wiki fetch-papers)" --max-time 60 -o "raw/papers/<name>.pdf" "<PDF_URL>"`、その後 `sleep 1`。
- **ファイル名**: Crossref で著者姓・年・キーワードを取り `<著者姓><年><kw>.pdf`（citekey 風, §5）にすると `raw/papers/` が読みやすい。判らなければ DOI のサフィックスを sanitize して使う。最終 citekey は /ingest が再決定し、ずれていれば /ingest がファイル名を citekey に揃える（`ingest` skill §3.1）ので厳密でなくてよい。
   ```bash
   curl -s "https://api.crossref.org/works/<DOI>" | jq -r '.message | (.author[0].family), (.published."date-parts"[0][0]), .title[0]'
   ```
- **検証**（必須、`read-raw-sources` skill §4）: 取得物が本当に PDF か確認。HTML エラーページを掴んでいないか:
  ```bash
  head -c 4 raw/papers/<name>.pdf          # → %PDF であること
  pdfinfo   raw/papers/<name>.pdf | head -8  # → ページ数・生成元が読めること
  ```
  PDF でなければ削除し「失敗」に分類。

### 4. 取得マニフェストを提示
表で報告: `参照 | DOI | 取得状況(OK/paywalled/失敗) | 保存ファイル | venue/年(Crossref)`。
- **OK** = `raw/papers/` に検証済み PDF。
- **paywalled/失敗** = OA が見つからない or PDF 検証に失敗 → 「人間が手動で `raw/papers/` に入れてください」と促す（raw は人間キュレート層）。
- バッチ件数・成功率を要約。

### 5. /ingest へ受け渡し（確認後）
- 人間に「取得した OK の PDF を `/ingest` で取り込んでよいか」確認。
- 承認されたら、`/ingest` の手順で**1本ずつ順次**取り込む（共有ファイル `wiki/index.md`・`wiki/log.md`・`raw/refs.bib`・`wiki/overview.md` への書き込み競合を避けるため**並列にしない**）。多数あればサブエージェントに1本ずつ割り当てて逐次実行してよい（既存の運用パターン）。
- 各 ingest で `raw/refs.bib` の DOI と citekey を一致させる（§4）。

### 6. wiki/log.md に追記（OKF §9, 新しい順）
```markdown
## YYYY-MM-DD
* **Fetch-papers**: <ソースリスト名> — Input: <file>（抽出 DOI N 件）。Downloaded: OK K 件（citekey候補 …）/ paywalled・失敗 L 件。Ingested: /ingest 済み J 件（または「人間確認待ち」）。Notes: 手動入手が必要な文献、重複スキップ等。
```

## 注意・限界
- OA でない論文は取得できない（設計通り）。著者最終稿が PMC/Europe PMC にあることが多いので、まず Unpaywall→Europe PMC を試す。
- **`is_oa: true` でも `url_for_pdf` が返らない**ことがある（Unpaywall が PMC のランディングページだけを返すケース）。その場合は PMCID を解決して `https://europepmc.org/articles/<PMCID>?pdf=render` を直接叩くと取れる。
- **free-to-read だが OA ライセンスでない論文**（PMC で読めるが `isOpenAccess: N`）は、Europe PMC の `fullTextXML` が **404** を返す。PDF は上記 `?pdf=render` で取得できるので、全文が要るならそちらから `read-raw-sources` skill §2 の2パス抽出に回す。
- 出版社サイトは bot 対策・robots があるため、`citation_pdf_url` 経由でも失敗しうる。失敗は握りつぶさず報告。
- ダウンロードした PDF を `raw/papers/` に置くこと自体が raw 層への書き込みなので、**スコープ確認（手順2）とマニフェスト確認（手順4）の2つの人間チェックポイント**を必ず通す。

## Args
`<file>` — 参考文献リストを含むテキスト/markdown のパス（例 `raw/memos/Gemini_DeepResearch_Result.md`）。省略時は候補を提示。任意で `email=<addr>`（Unpaywall 用）、`--no-ingest`（ダウンロードのみで /ingest しない）を受け付ける。
