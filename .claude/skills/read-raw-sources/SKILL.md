---
name: read-raw-sources
description: raw/ 配下の一次資料（PDF論文・Web記事・メモ・進捗）を正確に読むための正準手順。PDFの2パス抽出、Readツール（ページ画像）を使う判断、PDF検証、JATS全文の補助的利用を定める。/ingest・/query・/fetch-papers から参照される全skill共通の手順。
---

# raw ソースの読み方（PDF・全文アクセス）

`raw/` の一次資料をどう読むかは **全 skill で共通**とする。以下が正準の手順であり、`/ingest`・`/query`・`/fetch-papers` はここを参照する。

## 1. 原則

- **テキスト層を第一とする**。塩基配列・変異位置・MIC などは **1文字違えば無価値**であり、ページ画像からの読み取りは転記誤りのリスクが原理的に残る。`pdftotext` は文字を正確に取り出す。
- **`raw/` は読み取り専用**（`CLAUDE.md` §0 不変ルール1。唯一の例外は `/ingest` 時の PDF の citekey 名へのリネームで、`ingest` skill §3.1 が扱う）。抽出したテキストは**必ずスクラッチパッドに出力**し、`raw/` にファイルを増やさない。
- 環境依存の道具は devcontainer でビルド時に導入済み（`poppler-utils` / `python3` / `jq` / `curl` / `perl`）。無ければ `microdnf install -y <pkg>` で補う。

## 2. PDF の2パス抽出（必須）

**単一の方式では本文か表のどちらかが必ず壊れる。** 2段組の学術PDFで実測した挙動:

| 方式 | 2段組の本文 | 表 |
|------|------------|-----|
| `pdftotext`（素） | ✅ 正しい読み順に段組を解決 | ❌ セルが1行ずつに分解され崩壊 |
| `pdftotext -layout` | ❌ 左右カラムが同一行に混線 | ✅ 列が整列し数値を回収できる |

したがって**両方を出力してから読む**。

```bash
SP=<スクラッチパッド>
pdftotext          raw/papers/<citekey>.pdf "$SP/<citekey>.txt"         # 1. 本文の通読用
pdftotext -layout  raw/papers/<citekey>.pdf "$SP/<citekey>.layout.txt"  # 2. 表・数値の回収用
```

- **本文の通読は `.txt`**（素）を使う。`-layout` で本文を読むと左右カラムが混ざり、**文を読み落とす／取り違える**。
- **表の数値は `.layout.txt`** から取る。`.txt` 側の表は信用しない。
- 20ページ超なら abstract → intro → conclusion を先に読み、全体像を掴んでから method / results に入る。

## 3. Read ツール（ページ画像）を使う場面

`pdftoppm` によるページ描画はコストが高い（150 dpi で約450 KB/ページ）ので、**次の場合に限り該当ページだけ**を開く。

- **図（figure）**が要点を握るとき。
- §2 の**両方で崩れる複雑な表**（結合セル・多段ヘッダ等）。
- テキスト層を持たないスキャンPDF。

`raw/assets/` に切り出された図があれば、そちらを優先して併読する。

## 4. 検証と補助

- **PDF 検証**（ダウンロード直後は必須）: `head -c 4 <file>` が `%PDF` であること。ページ数は `pdfinfo <file>`。HTML エラーページを掴んでいたら削除して「失敗」に分類する。
- **JATS 全文（補助）**: OA なら Europe PMC の構造化全文が使える。
  ```bash
  curl -s "https://www.ebi.ac.uk/europepmc/webservices/rest/<PMCID>/fullTextXML"
  ```
  ただし **404 になる論文があり（free-to-read でも OA ライセンスでなければ返らない）、返っても表が欠落することがある**。JATS は本文の補助と位置づけ、**数値は必ず §2 の `.layout.txt` で裏を取る**。
- **JSON のパース**は `jq` を使う（`curl ... | jq -r '...'`）。

## 5. PDF 以外

- **Web記事**: `raw/web/*.md` をそのまま読む。インライン画像は本文を読んだ後、必要なものだけ確認。
- **メモ・進捗**: `raw/memos/*.md`・`raw/progress/**` をそのまま読む。メモは「自分の思考」なので要約より**構造化**（どの課題・どのアイデアに関係するか）を重視する。
