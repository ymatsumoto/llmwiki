---
name: okf-conformance
description: 本Wiki（wiki/ 配下）と Open Knowledge Format (OKF) v0.2 の正準対応表。バンドルroot・Concept ID・リンク・予約ファイル・provenance/trust/lifecycle の構造対応と、frontmatterフィールドのOKF必須/推奨/拡張の区分を定める。/lint での適合検査や、スキーマ改訂でドリフトを防ぎたいときに参照する。
---

# OKF 準拠マッピング（正準の対応表）

将来のドリフト防止のための正準参照。`CLAUDE.md` §11（OKF 準拠とバージョニング）と対で用いる。

- **対象バージョン**: OKF **v0.2**
- **仕様の正準の在処**: https://github.com/GoogleCloudPlatform/open-knowledge-format （`SPEC.md`）
  - 旧 `GoogleCloudPlatform/knowledge-catalog/okf/` は**凍結スナップショット**。参照しない。
  - 版が上がったら `curl -sSL https://raw.githubusercontent.com/GoogleCloudPlatform/open-knowledge-format/main/SPEC.md` で取得し、本表と `CLAUDE.md` に差分を当てる。

## 構造の対応

| OKF 概念 | 本Wiki |
|----------|--------|
| Knowledge Bundle（バンドル root） | `wiki/` |
| Concept（1 md = 1 knowledge） | `sources/` `concepts/` `methods/` `entities/` `topics/` `problems/` `ideas/` `computations/` 各ページ |
| Concept ID（path − `.md`） | `wiki/` からの相対パス（例 `sources/vaswani2017attention`） |
| Link（標準 md リンク, 仕様 §6.1） | **相対** markdown リンク（`../concepts/x.md`）。仕様が推奨する絶対形 `/concepts/x.md` は Foam 互換のため使わない（どちらも許容される） |
| Provenance（`sources`, 仕様 §5.1） | frontmatter `sources`。`resource` は Wiki内相対パス / `raw/` 相対パス / 外部URL / 範囲記述。`id` = citekey |
| Per-claim attribution（脚注, 仕様 §5.1） | Wiki内 source があれば相対リンク `([citekey](../sources/<citekey>.md))`、無い外部資料は `[^id]` 脚注（`CLAUDE.md` §4.2） |
| Trust（`generated` / `verified`, 仕様 §5.2） | `generated: { by, at }`（本運用で必須）／ `verified: { by: human:<id>, at }`（人間確認時のみ） |
| Actor 表記（仕様 §7） | LLM `claude-code/<model>` ／ 人間 `human:ymatsumoto` ／ 自動処理 `process:<id>` |
| Lifecycle（`status`, 仕様 §5.4） | `draft` \| `stable` \| `deprecated`。削除の代わりに `deprecated` を付けて残す |
| Freshness（`stale_after`, 仕様 §5.5） | `topics/` と `overview.md` に推奨（半年目安） |
| Attested Computation（仕様 §10） | `wiki/computations/<slug>.md`（任意。`CLAUDE.md` §3.8） |
| `references/` 規約（仕様 §6.3） | 本Wikiでは使わない。外部資産は `raw/` が担う（バンドル外・人間キュレート層） |
| Reserved `index.md` / `log.md` | `wiki/index.md`（`CLAUDE.md` §6）／ `wiki/log.md`（§7） |

## frontmatter フィールドの対応

| フィールド | 区分 | 備考 |
|-----------|------|------|
| `type` | OKF 必須 | 現行の小文字語（`source` 等）を値として維持。`Attested Computation` のみ仕様の型名をそのまま使う |
| `title` / `description` | OKF 推奨（本運用で必須） | `description` は日本語一行 |
| `resource` | OKF 推奨 | source / entity など実在資産を持つページのみ。抽象概念には付与しない |
| `tags` | OKF 推奨 | — |
| `generated` (`by`/`at`) | OKF 推奨（本運用で必須） | `at` は UTC オフセット明示の ISO 8601 datetime。v0.1 の `timestamp` の後継 |
| `verified` (`by`/`at`) | OKF 推奨 | 人間確認時のみ。LLM は自分を書かない（`CLAUDE.md` §0 ルール7） |
| `status` | OKF 推奨 | **lifecycle 専用**（`draft`/`stable`/`deprecated`）。領域別の段階は `stage` |
| `stale_after` | OKF 推奨 | ISO 8601 datetime |
| `sources` (`id`/`resource`/`title`/`relation`/`author`/`usage_count`/`last_modified`) | OKF 推奨（`relation` は拡張） | `relation`: `key-source` \| `arising-from` \| `inspired-by` \| `contradicts` \| `adjacent` |
| `usage_window` | OKF 推奨 | 被引用数を `usage_count` に残す場合の集計期間 |
| `runtime` / `parameters` / `computation` / `executor` / `attester` | OKF（Attested Computation で `runtime` は必須） | `computations/` のページのみ |
| `stage` | OKF 拡張 | source: `to-read`/`skimmed`/`read`/`deep-read`、topic: `active`/`mature`/`dormant`、problem: `open`/`partially-addressed`/`solved`、idea: `seed`/`developing`/`promising`/`validated`/`parked`/`discarded` |
| `root` | OKF外（ツール） | **プロジェクト root の**ディレクトリ名。値は `CLAUDE.md` を直下に置いたディレクトリの名前（全ページ同一値）。**バンドル root（`wiki/`）とは別物** — `sources[].resource` が `../../raw/` を指すとおり参照資産はバンドル外にあるので、ツールが見る単位はプロジェクト root。「その名前を持つ最も近い祖先ディレクトリ」と解釈されるので階層に依らず同一値。相対パス（深さ依存）・絶対パス（環境依存）で書かない。`[[wikilink]]` を使わない本Wikiでは現状メタデータのみ（`CLAUDE.md` §3.0） |
| `provenance` | OKF外（v0.1 由来） | 全ページに `literature` が入っている。v0.2 のどの規約にも対応が無く、意味が定まっていない。新規ページでは書かない。既存分の扱いは未決 |
| `kind` / `citekey` / `authors` / `year` / `venue` / `created` / `ingested` / `rating` / `severity` / `maturity` / `confidence` / `hypothesis` / `aliases` / `entity_kind` | OKF 拡張 | ドメイン運用のための追加キー。OKF は未知キーを許容 |
| 横の関係リスト（`concepts` / `methods` / `problems` / `entities` / `related` / `solves` / `addresses` / `addressed_by` / `ideas` / `open_problems` / `related_problems` / `related_ideas` / `related_methods`） | OKF 拡張 | 値は **Concept ID 素スカラ**（`dir/slug`）。`[[ ]]`・引用符は使わない |

> **注記:** provenance は `sources`、横の関係は Concept ID リスト、本文の参照は相対リンク — この三層を混ぜない。

## v0.1 → v0.2 で退役したフィールド

`/lint` は以下を検出したら移行を促す（`CLAUDE.md` §11 と同一）。

| 旧 (v0.1) | 新 (v0.2) |
|----------|-----------|
| `timestamp` | `generated: { by, at }` |
| `updated` | `generated.at` に一本化 |
| 本文 `## 引用 (Citations)` 節 | `sources` ＋ `[^id]` 脚注 |
| `key_sources` / `arising_from` / `inspired_by` / `related_sources` | `sources` に `relation:` を添えて統合 |
| `status: read`/`open`/`seed`/`active` | `stage:`（`status` は lifecycle 専用） |
| `url` | `resource` |

## 適合条件（`/lint` が検査する）

仕様 §11 の必須3条件:

1. 全非予約 md に parseable な YAML frontmatter があること
2. frontmatter に**非空の `type`** があること
3. 予約ファイル（`index.md` / `log.md`）が仕様 §8 / §9 の形式であること（`index.md` の frontmatter は bundle root の `okf_version: "0.2"` のみ）

加えて本運用のローカル必須:

- `title` / `description`（日本語一行）
- `generated.by` と `generated.at`（`at` は UTC オフセット付き ISO 8601 datetime）

consumer 側の緩さ（仕様 §11）も守る: 未知の `type`・未知のキー・欠けた任意フィールド・壊れたリンク・`index.md` の不在を**理由にページを拒否しない**（`/lint` は報告するが、ページを壊さない）。
