# llmwiki

**LLM が維持する学術研究 Wiki** のスキーマと Claude Code skill 一式。

先行研究を取り込んで要約・横断参照し、そこから**課題（problems）を抽出**し、
**それを解くアイデア（ideas）を育てる**ためのフレームワーク。
Wiki は問いを投げるたびに作り直すものではなく、読むたび・問うたびに豊かになる永続的な成果物として設計されている。

生成物は **[Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format)**
準拠のバンドル。仕様の必須事項を満たしつつ、研究運用に必要な追加規約
（ドメイン分類・`stage` 等の frontmatter 拡張）を OKF の「拡張」として重ねている。

## このリポジトリに含まれるもの

| パス | 内容 |
|------|------|
| `CLAUDE.md` | **スキーマの正準定義**。ディレクトリ構造・ページ種別・frontmatter・引用規則・命名規則・文体規則・OKF 対応 |
| `.claude/skills/` | 上記スキーマを実行する Claude Code skill 群 |

生成される `wiki/` と一次資料 `raw/` は**含まない**（研究内容そのもののため）。
このリポジトリはあくまで「器」であり、中身は各自の研究データで満たす。

## Skills

| Skill | 用途 |
|-------|------|
| `/ingest [file]` | `raw/` のソース（論文 PDF / Web / メモ / 進捗）を読み、要約ページを作り、concept / method / problem / topic / index / log へ波及させる（1回で5〜15ページ） |
| `/query <質問>` | index → 関連ページを辿り、引用付きで合成回答。良い回答は新ページとして filing |
| `/idea [説明]` | アイデアを課題にひも付け、関連研究で位置づけて idea ページを作成・育成 |
| `/web-survey <トピック>` | WebSearch/WebFetch で先行研究を網羅探索し、既存知識と照合してギャップを発見 |
| `/fetch-papers` | 参考文献リストから open-access PDF を `raw/papers/` へ一括取得し、続けて ingest |
| `/lint [--fix]` | 健康診断。矛盾・陳腐化・孤立ページ・壊れリンク・不備 frontmatter・KaTeX エラー・OKF 非準拠を検出 |
| `read-raw-sources` | 一次資料を正確に読むための正準手順（PDF 2パス抽出等）。他 skill から参照される |
| `okf-conformance` | 本 Wiki と OKF v0.2 の正準対応表。スキーマ改訂時のドリフト防止 |

## 3層アーキテクチャ

| 層 | 場所 | 性質 |
|----|------|------|
| Raw sources | `raw/` | 不変の一次資料。LLM は**読むのみ、絶対に書き換えない** |
| The Wiki | `wiki/` | LLM 生成の markdown 群。**OKF Knowledge Bundle の root**。LLM が全面的に所有 |
| The Schema | `CLAUDE.md` | 構造・規約・ワークフローの定義。人間と LLM が共進化させる |

**役割分担**: 人間はソースのキュレーション・探索の方向づけ・良い問いを立てること・意味を考えること。
LLM はそれ以外すべて（要約・横断参照・ページ作成・矛盾検出・索引とログの保守）。

## 導入

```bash
# 研究プロジェクトの root で
git clone <this-repo> .
mkdir -p raw/{papers,web,memos,progress,assets} wiki
touch raw/refs.bib
```

`raw/` と `wiki/` は各プロジェクトの `.gitignore` で除外するか、別の非公開リポジトリで管理する
（このリポジトリの `.gitignore` がその前提で書かれている）。

Claude Code をそのディレクトリで起動すると `CLAUDE.md` が自動で読まれ、`.claude/skills/` の
skill が `/ingest` 等として使えるようになる。

## 想定環境

- **Claude Code**（skill と `CLAUDE.md` の自動読み込みに依存）
- **Foam / VS Code** でのブラウズを想定。リンクは相対 markdown リンクのみを使い、
  `[[wikilink]]` は使わない。数式は KaTeX 記法（VS Code 組み込みプレビューが描画する範囲）
- `/lint` の `lint.py` に **Python 3**、PDF 読み取りに **poppler-utils**、`/fetch-papers` に **curl** と **jq**
  （いずれも devcontainer 側で導入済みの想定）

## スキーマは固定ではない

運用して詰まったら人間と LLM で `CLAUDE.md` を改訂する。
OKF 側が版を上げたら正準リポジトリの `SPEC.md` を取得して差分を当てる。
