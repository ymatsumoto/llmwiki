# Research Wiki — スキーマ & 運用ガイド

このファイルは **LLMが維持する学術研究Wiki** の唯一かつ正準のスキーマです。
**セッション開始時に必ず読み**、以下の規約を厳密に守ること。規約はWikiが成長しても一貫性とナビゲーション性を保つために存在します。

> 目的: 先行研究の調査・類似研究の整理を行い、そこから **課題（problems）を抽出**し、**それを解くアイデア（ideas）を蓄積・育成**していく。Wikiは問いを投げるたびに作り直すものではなく、**読むたび・問うたびに豊かになる永続的な成果物**である。

> **本Wikiは Open Knowledge Format (OKF) v0.2 準拠のバンドルである。** `wiki/` ディレクトリが OKF の Knowledge Bundle（バンドル root）に相当する。本スキーマは OKF の必須事項（本書 §11 および `okf-conformance` skill に内包）を満たしつつ、研究運用に必要な追加規約（ドメイン分類・frontmatter 拡張フィールド等）を OKF の「拡張」として重ねたものである。
>
> 正準の仕様は **https://github.com/GoogleCloudPlatform/open-knowledge-format**（`SPEC.md`）。旧 `GoogleCloudPlatform/knowledge-catalog/okf/` は凍結スナップショットなので参照しない。

---

## 0. 役割分担（最重要）

- **人間（あなた）の仕事**: ソースの収集・キュレーション、探索の方向づけ、良い問いを立てること、意味を考えること。
- **LLM（Claude）の仕事**: それ以外すべて — 要約、横断参照、ページ作成・更新、矛盾の検出、索引・ログの保守という「退屈だが価値を生む雑務」。
- **不変ルール**:
  1. `raw/` 配下は **読むだけ。絶対に書き換えない**（source of truth）。**唯一の例外**は、`/ingest` で PDF を取り込むときに `raw/papers/` の PDF を `<citekey>.pdf` へ**リネームすること**（内容の編集・変換・削除はしない。手順は `ingest` skill §3）。
  2. `wiki/` 配下は **LLMが全面的に所有**する。人間は基本的に読むだけ。
  3. ページを作成・更新したら **必ず `wiki/index.md` と `wiki/log.md` を更新**する。
  4. 新しいソースが既存ページの主張と矛盾したら、**消さずに両論を併記し `> **警告:**` blockquote で明示**する（§9 参照）。
  5. 破壊的・不可逆な操作（ページ削除、大規模リネーム）は **人間に確認**してから行う。消す代わりに `status: deprecated`（§3.0）でマークして残すのが既定の作法。
  6. **OKF v0.2 準拠を維持**する: 全ページに非空の `type` を持つ parseable な YAML frontmatter を置き、Wiki内リンクは **相対 markdown リンク** で張る（`[[wikilink]]` は使わない、§5 参照）。
  7. **`verified` は人間が明示的に確認したときだけ書く**（§3.0）。LLM が自分自身を verifier にすると trust tier の意味が消えるので、**LLM は絶対に `verified` に自分を書かない**。

---

## 1. 3層アーキテクチャ

| 層 | 場所 | 性質 | OKF上の位置づけ |
|----|------|------|----------------|
| **Raw sources** | `raw/` | 不変の一次資料（PDF論文・Web記事・メモ・進捗・`refs.bib`）。LLMは読むのみ。 | バンドル**外**（source 層） |
| **The Wiki** | `wiki/` | LLM生成のmarkdown群。要約・概念・課題・アイデア・総説。LLMが所有。 | **OKF Knowledge Bundle（バンドル root）** |
| **The Schema** | `CLAUDE.md`（本ファイル） | 構造・規約・ワークフローの定義。人間とLLMが共進化させる。 | バンドル**外**（schema） |

> `wiki/` が OKF バンドル root。バンドル内の各 markdown ファイルが OKF の **Concept**（1 md = 1 knowledge）に相当し、その **Concept ID** は「`wiki/` からの相対パスから `.md` を除いたもの」（例 `wiki/sources/vaswani2017attention.md` → `sources/vaswani2017attention`）。

---

## 2. ディレクトリ構造

```
research-wiki/
├── CLAUDE.md                 ← 本ファイル（スキーマ / バンドル外）
├── raw/                      ← 一次資料（不変 / バンドル外）
│   ├── papers/               ← PDF論文（<citekey>.pdf。/ingest 時にリネームして揃える）
│   ├── web/                  ← Web記事のmarkdown（Markdownクリッパ等で取り込み）
│   ├── memos/                ← 自分の生メモ・実験ログ・思いつき
│   ├── progress/             ← メンバー別の作業進捗（研究進捗発表・週報等）
│   │   └── <氏名>/           ← background.pdf / overview.pdf / <YYYY>/ の日付別PDF 等
│   ├── refs.bib              ← BibTeX。引用の単一の真実（source of truth）
│   └── assets/               ← 図表・画像
└── wiki/                     ← ★OKF Knowledge Bundle（バンドル root）
    ├── index.md              ← 全ページのカタログ（OKF §8。変更のたび更新）
    ├── log.md                ← 操作の履歴ログ（OKF §9。新しい順）
    ├── overview.md           ← 研究領域全体のトップ総説
    ├── sources/              ← ソース1件 = 1ページ（論文/Web/メモ/進捗の要約）
    ├── concepts/             ← 概念・理論・問題設定（抽象）
    ├── methods/              ← 手法・アルゴリズム・モデル（具体的技術）
    ├── entities/             ← 著者・研究グループ・データセット・ツール・ベンチマーク
    ├── topics/               ← サブ領域ごとの総説（進化する thesis）
    ├── problems/             ← ★研究課題・未解決問題（研究の核）
    ├── ideas/                ← ★解決アイデア・仮説（研究の核）
    └── computations/         ← 任意: 再現可能な解析（type: Attested Computation, §3.8）
```

> `index.md` / `log.md` は **バンドル内（`wiki/` 配下）** に置く（OKF の予約ファイル）。

> `concepts` と `methods` の境界が曖昧なら `concepts` に寄せてよい。`methods` は「実装・追試できる具体的技術」に限定する目安。

> `computations/` は**必要になってから作る**（数値を伴う解析を再現可能な形で残したいとき、§3.8）。使わない研究では存在しなくてよい。

> **内容の置き場所ルール（編集方針）**:
> - `wiki/methods/` は**先行研究の情報を主体**にする — 文献で確立された汎用的・追試可能な技術のリファレンス。**特定研究のための実行計画・解析パイプライン・プロトコルは methods に書かない**（method ページの純度を保つ）。
> - **自分のデータ・考え・実行計画**を残す場所は **`raw/memos/`（生メモ）/ `wiki/ideas/`（仮説と、その検証パイプライン等の実行計画）/ `wiki/problems/`（自分にとっての課題）**。プロジェクト固有の解析パイプラインは対応する idea ページ内（例: `## 解析パイプライン` 節）に格納する。数値の再現性まで担保したいなら `wiki/computations/` に切り出す（§3.8）。
> - ソース要約（`wiki/sources/`）の客観/主観の分離は §9 を参照。

---

## 3. ページ種別と frontmatter スキーマ

全ページはYAML frontmatterで始める。**`type` は OKF 必須フィールド**（非空であること）。frontmatter は素の markdown として `grep` / `/lint` / Foam のバックリンク・グラフ・タグエクスプローラが読む（動的集計エンジンは使わない — カタログは `wiki/index.md` が正準）。

### 3.0 全ページ共通フィールド（OKF v0.2 コア）

以下は**ページ種別によらず共通**。種別固有の拡張フィールドは §3.1 以降で足す。

```yaml
---
type: source                 # OKF必須。非空。本Wikiの値: source|concept|method|entity|topic|problem|idea|Attested Computation
title: "表示名"               # OKF推奨（本運用で必須）
description: "日本語の一行要約"  # OKF推奨（本運用で必須）。index.md の説明文にそのまま使う
tags: [tag1, tag2]           # OKF推奨
generated: { by: claude-code/claude-opus-5, at: 2026-08-26T10:00:00Z }  # OKF推奨（本運用で必須）
verified: { by: human:ymatsumoto, at: 2026-08-27T09:00:00Z }            # 任意。人間が確認したときだけ
status: stable               # 任意。OKF lifecycle: draft | stable | deprecated（省略時 stable）
stale_after: 2027-02-26T00:00:00Z  # 任意。この瞬間以降は陳腐化扱い
sources:                     # OKF provenance。このページが依拠した資料（§4）
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: key-source }
resource: "https://arxiv.org/abs/1706.03762"  # 任意。原資産のURI。source ページのみ（抽象概念には付けない）
root: <project-root>         # OKF外・ツール用。CLAUDE.md を置いたディレクトリの名前（後述）
---
```

**`generated` / `verified`（trust, OKF §5.2）**
- `generated.by` は**必須**（`generated` を書くなら）。`generated.at` はそのページの内容が最後に実質的に変わった瞬間。**ページを書き換えたら必ず `at` を更新**する。
- **actor 表記（OKF §7）**: LLM は `claude-code/<model>`（例 `claude-code/claude-opus-5`）、人間は `human:ymatsumoto`、自動処理は `process:<id>`。
- `verified` は「内容がソースと合っているか誰が確認したか」。**人間が明示的に確認したときのみ** `{ by: human:<id>, at: ... }` を追記する（§0 不変ルール7）。複数回の確認はリストで並べる。
- OKF の **trust tier** はこれで決まる: `verified` なし = *unverified* / 非 `human:` のみ = *machine-confirmed* / `human:` あり = *human-reviewed*。本Wikiの LLM 生成ページは既定で unverified であり、それが正しい状態。

**`status`（lifecycle, OKF §5.4）** — **文書そのものの状態**であって、記述対象の状態ではない（対象の段階は `stage`、後述）。
- `draft`: 書きかけ・stub（`/ingest` が作った骨組みだけの concept など）。
- `stable`: 既定。省略時もこれ。
- `deprecated`: 別ページに統合された、または棄却された。**削除の代わりにこれを付けて残す**（§0 不変ルール5）。

**`stale_after`（freshness, OKF §5.5）** — 任意。`topics/` と `overview.md` には付けることを推奨（総説は古くなる。目安は半年後）。`/lint` が `now >= stale_after` のページを陳腐化候補として挙げる。

**`stage`（OKF拡張・本Wiki固有）** — **記述対象がどの段階にあるか**。`status`（文書のライフサイクル）とは直交する別軸。値は種別ごとに定まり、4種の値集合は互いに素なので `grep '^stage: open'` だけで曖昧なく引ける。

| ページ種別 | `stage` の値 | 意味 |
|-----------|-------------|------|
| `source` | `to-read` \| `skimmed` \| `read` \| `deep-read` | 自分がどこまで読んだか |
| `topic` | `active` \| `mature` \| `dormant` | その総説の活性度 |
| `problem` | `open` \| `partially-addressed` \| `solved` | 課題の解決状況 |
| `idea` | `seed` \| `developing` \| `promising` \| `validated` \| `parked` \| `discarded` | アイデアの育成段階 |
| `concept` / `method` / `entity` | （なし） | — |

> **注記:** `stage` と `status` は混同しやすいので対比で覚える。`stage: solved` な problem ページは依然として `status: stable` な良い文書である。逆に `stage: seed` のまま別アイデアに吸収されたページは `status: deprecated` になる。

**日付・時刻の書き方**
- **OKF が時刻値として定めるキー**（`generated.at` / `verified[].at` / `stale_after` / `sources[].last_modified` / `usage_window.from`/`to`）は、**UTC オフセットを明示した ISO 8601 datetime** で書く（`2026-08-26T10:00:00Z`）。日付だけの `2026-08-26` はタイムゾーンごとに別の瞬間を指すため OKF v0.2 では不正。
- 本Wiki拡張の暦日フィールド（`created` / `ingested`）は意味的に「日」なので `YYYY-MM-DD` のままでよい。

**リンク系フィールドの二層構造（重要）**
- **provenance（このページが何に依拠したか）** → OKF の `sources`（§4）。`resource` は相対パス、`id` は citekey。
- **横の関係（概念どうしの関連・課題とアイデアの接続など）** → **Concept ID の素スカラリスト**（`concepts: [concepts/self-attention]`）。`[[ ]]` やダブルクオートは使わない。
- **本文中の相互参照** → 相対 markdown リンク（§5）。

**`## 参考文献 (Bibliography)` 節（任意）** — **まだ Wiki にページ化していない外部文献**の一覧を本文末尾に置く節。番号付きリストで書誌を素の文で書く（「取り込み候補」の待ち行列）。
- v0.1 の `## 引用 (Citations)` 節とは目的が違う。あちらは**主張ごとの帰属**を担っていて `sources` ＋ `[^id]` 脚注に移った（§4.2、§11）。こちらは**ページ化の待ち行列**なので節として残す。
- ページ化したら該当項目をこの節から外し、`sources` と本文の相対リンクに移す。

**`root`（OKF外・ツール用）** — このページが属する**プロジェクト root** をページ自身が申告するフィールド。**値はプロジェクト root（`CLAUDE.md`・`raw/`・`wiki/` を直下に持つディレクトリ）の basename** で、種別・階層によらず全ページ同一（迷ったら既存ページの `root` と一致させる）。

- **OKF のバンドル root（`wiki/`）とは別物。** バンドル root は Concept ID の基準（§5）であり `wiki/` のまま。一方 `root` はツールが「このページ群と、それが参照する資産がどこまでか」を知るためのもので、`sources[].resource` が `../../raw/` を指すとおり `raw/` はバンドルの外にある。したがって `wiki/` では狭すぎ、プロジェクト root が正しい単位になる。
- **ディレクトリ名として解釈される**（「その名前を持つ最も近い祖先ディレクトリ」）。したがって `wiki/concepts/x.md` でも `wiki/computations/deep/y.md` でも同じ値が正しく、階層が深くなっても書き換え不要。
- **ディレクトリ名を変えたら全ページの `root` を一括で置換する。** 値がディレクトリ名で決まるため、リネームや別名での clone（`git clone <repo> <別名>`）をすると全ページの値が一斉に不正になる。`/lint` が「この名前の祖先ディレクトリが無い」として検出する。
- **相対パス（`..`, `../..`）で書いてはいけない。** 正しい値がページの深さに依存するため、ページを移動すると**エラーにならずに別の場所を指す**ようになる。
- **絶対パス（`/root/work/<project-root>`）で書いてはいけない。** clone・移動・devcontainer のホスト/コンテナ間でパスが変わるため、いずれかの環境で必ず壊れる。マシン固有の状態をコンテンツに埋めない。
- 本Wikiは `[[wikilink]]` を使わない（§0 不変ルール6）ので、この値は現時点では**メタデータであり本Wiki内のリンク解決には影響しない**。同名ディレクトリを持つ別プロジェクトと同一ワークスペースに置いたとき、ツールがどのプロジェクトの一員かを判別するために書いておく。`/lint` は「パスでないこと」と「その名前の祖先が実在すること」を検査する。

### 3.1 ソースページ `wiki/sources/<citekey>.md`

論文・Web記事・メモ・進捗を問わず1ソース1ページ。ファイル名 = `citekey`（§5参照）。

```yaml
---
type: source                             # OKF必須
kind: paper                              # paper | web | memo | progress | exp
title: "Attention Is All You Need"       # OKF推奨: 表示名
description: "self-attention のみで系列変換を実現し、RNN/CNNを排したTransformerを提案。"  # OKF推奨: 一行要約（日本語）
citekey: vaswani2017attention
authors: [Vaswani, Shazeer, Parmar]      # メモ/進捗なら [self] 等
year: 2017
venue: "NeurIPS"                         # 会議/雑誌略称。Webなら媒体名、メモ/進捗は空でも可
resource: "https://arxiv.org/abs/1706.03762"   # OKF推奨: 原資産のURI（DOI/URL）。無ければ raw/ への相対パス
stage: read                              # to-read | skimmed | read | deep-read（自分の読解段階）
status: stable                           # OKF lifecycle
rating: 4                                # 1-5（自分にとっての重要度。任意）
tags: [transformer, attention, nlp]
concepts: [concepts/self-attention]              # 関連conceptのConcept ID
methods: [methods/scaled-dot-product-attention]
problems: [problems/long-range-dependency]       # このソースが扱う課題
entities: [entities/wmt14]
sources:                                 # OKF provenance: この要約が依拠した一次資料そのもの
  - { id: vaswani2017attention, resource: ../../raw/papers/vaswani2017attention.pdf, title: "Attention Is All You Need (PDF)", last_modified: 2017-06-12T00:00:00Z }
ingested: 2026-06-04                     # 取り込み日（暦日。拡張）
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```

本文構成:
```markdown
## TL;DR
2〜3文。最大の signal density で。何を主張し、何を達成したか。

## 背景・課題 (Problem)
このソースが埋めようとしたギャップ。

## 手法 (Method)
どう解いたか。鍵となる architectural / algorithmic 選択。

## 結果 (Results)
主要な数値。何を、どのベンチで上回ったか。

## 限界・批判的検討 (Limitations)
著者が認める弱点 + 自分から見た疑問・反証可能性。

## 自分の研究との接続 (My notes)
我々の研究にどう効くか。ここで引き出された課題は [problems/...](../problems/....md) へ昇格させる。

## 関連ページ (Related)
Wiki内の関連ページへの相対 markdown リンク群。
```

> **注記:** v0.1 の `## 引用 (Citations)` 節は**廃止**。外部出典は frontmatter の `sources` に移し、個別の主張への紐付けは `[^id]` 脚注で行う（§4）。

### 3.2 概念ページ `wiki/concepts/<slug>.md`

```yaml
---
type: concept
title: "Self-Attention"
description: "系列内の各要素が他の全要素へ注意を張り、文脈依存の表現を得る機構。"
aliases: ["セルフアテンション", "自己注意"]   # 表示ゆらぎ・検索補助用メタデータ
tags: [attention]
related: [concepts/positional-encoding]
sources:
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: key-source }
status: stable
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```
本文: `## 定義` / `## なぜ重要か` / `## バリエーション・発展` / `## 関連ソース`。

### 3.3 手法ページ `wiki/methods/<slug>.md`

```yaml
---
type: method
title: "Scaled Dot-Product Attention"
description: "QK^T をスケールし softmax して V を重み付き和する注意計算。"
aliases: []
tags: [attention]
solves: [problems/long-range-dependency]     # この手法が対処する課題
related_methods: [methods/multi-head-attention]
sources:
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: key-source }
status: stable
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```
本文: `## 概要` / `## 仕組み（手続き/数式）` / `## 計算量・前提` / `## 長所と短所` / `## 使用例（ソース）`。

### 3.4 エンティティページ `wiki/entities/<slug>.md`

著者・研究グループ・データセット・ベンチマーク・ツール。
```yaml
---
type: entity
entity_kind: dataset        # author | group | dataset | benchmark | tool
title: "WMT14 En-De"
description: "英独機械翻訳の標準ベンチマーク（約450万文対）。"
aliases: []
tags: [mt, benchmark]
resource: "https://www.statmt.org/wmt14/translation-task.html"   # 任意。実在資産があれば
sources:
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: adjacent }
status: stable
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```

### 3.5 トピック総説ページ `wiki/topics/<slug>.md`

サブ領域の「進化する thesis」。新ソースを取り込むたびに更新。
```yaml
---
type: topic
title: "効率的なTransformerの系譜"
description: "計算量O(n^2)の緩和を狙う各種効率化Transformerの流れを俯瞰する総説。"
tags: [transformer, efficiency]
stage: active             # active | mature | dormant（総説の活性度）
status: stable            # OKF lifecycle
stale_after: 2027-02-04T00:00:00Z   # 総説は古くなる。半年後を目安に
open_problems: [problems/long-range-dependency]
sources:
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: key-source }
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```
本文: `## 現状の理解（thesis）` / `## 主要な系譜・流派` / `## 未解決の論点` / `## タイムライン`。

### 3.6 課題ページ `wiki/problems/<slug>.md` ★

```yaml
---
type: problem
title: "長距離依存の効率的なモデリング"
description: "系列長に対し二次コストを避けつつ遠距離の依存を捉える手法が未確立。"
tags: [transformer, efficiency]
severity: high            # high | medium | low（自分の研究にとっての重要度）
stage: open               # open | partially-addressed | solved（課題の解決状況）
status: stable            # OKF lifecycle
maturity: well-defined    # vague | well-defined | formalized（定式化の度合い）
addressed_by: []          # 部分的にでも対処するソース/手法のConcept ID
ideas: []                 # この課題に挑むアイデアのConcept ID
related_problems: []
sources:                  # この課題を浮かび上がらせたソース（旧 arising_from）
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: arising-from }
created: 2026-06-04
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```
本文:
```markdown
## 課題の記述
何が、なぜ難しいのか。理想と現状のギャップ。

## なぜ重要か
解けると何が変わるか。誰が困っているか。

## これまでのアプローチと限界
| アプローチ | 出典 | どこまで解けた | 残る限界 |
|-----------|------|--------------|---------|
| ... | [citekey](../sources/citekey.md) | ... | ... |

## 未解決の核心
結局まだ解けていない一点は何か。

## 関連アイデア
[idea-...](../ideas/idea-....md) 群（ここに集約される）。
```

### 3.7 アイデアページ `wiki/ideas/<slug>.md` ★

```yaml
---
type: idea
title: "グラフ構造への相対位置エンコーディング"
description: "グラフ上の相対距離を注意に組み込み長距離依存を効率化する仮説。"
hypothesis: "一行で核心の主張"
stage: seed               # seed | developing | promising | validated | parked | discarded
confidence: low           # low | medium | high
status: stable            # OKF lifecycle（棄却して残すときだけ deprecated）
addresses: [problems/long-range-dependency]    # 必ず1つ以上の課題にひも付ける
related_ideas: []
sources:                  # 着想元（旧 inspired_by）
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: inspired-by }
created: 2026-06-04
generated: { by: claude-code/claude-opus-5, at: 2026-06-04T09:00:00Z }
---
```
本文:
```markdown
## 仮説 (Hypothesis)
中心となる主張・メカニズムを明確に。

## 動機 (Motivation)
どの課題を解くか。既存手法が取りこぼしている点。なぜ今これか。

## スケッチ (Sketch)
どう動くか — おおまかなアルゴリズム/アーキテクチャ/実験設計。
「何を実装・証明すべきか」が分かる程度に具体的に。

## 強み / 弱み
- 効きそうな理由・支持する既存証拠
- 失敗しそうな理由・リスク

## 反証条件 (Falsification)
何が観測されたらこのアイデアは間違いだと分かるか。

## 関連研究との位置づけ
| 研究 | 関係 | メモ |
|------|------|------|
| [citekey](../sources/citekey.md) | builds-on / departs-from / contradicts / adjacent | ... |

## ネクストアクション
- [ ] 具体的な次の一手1
- [ ] 具体的な次の一手2
```

### 3.8 解析ページ `wiki/computations/<slug>.md`（任意, OKF §10）

**数値を伴う解析を再現可能な形で残したいときだけ**作る。OKF の `type: Attested Computation` は「その数字が、決めた手順どおりに出されたものか」を後から機械的に確かめるための型。統計処理・スクリプトで出した図表の値などが対象。

```yaml
---
type: Attested Computation
title: "MIC 分布の要約統計"
description: "臨床分離株の MIC を株ごとに集計し中央値と四分位を返す。"
runtime: python                      # この type の必須フィールド。bigquery | postgres | python | dbt | R 等
parameters:
  - { name: species, type: string, required: true }
computation: ../../raw/memos/mic-summary.py   # 省略時は本文の `# Computation` フェンスが計算本体
executor: { resource: ../../raw/memos/run-mic.md, receipt: [command, stdout, result] }
attester:  { resource: ../../raw/memos/check-mic.py }
tags: [amr, statistics]
status: stable
generated: { by: claude-code/claude-opus-5, at: 2026-08-26T10:00:00Z }
---

# Computation

（`computation` を書かない場合は、ここにフェンスで計算本体を置く）
```

- 使う側（`ideas/` や `topics/`）からは**相対リンクで参照**する: `[MIC 要約統計](../computations/mic-summary.md)`。
- LLM は `parameters` に**値を入れることしかできない**。計算本体を書き換えてよいのは人間だけ（そうでないと attestation の意味が消える）。
- 重い仕組みなので**既定では使わない**。`raw/memos/` や idea ページ内の `## 解析パイプライン` で足りるならそれでよい（§2）。

---

## 4. 引用規則（`sources` と BibTeX 連携）

OKF v0.2 では provenance は **frontmatter の `sources`** が担う（v0.1 の本文 `# Citations` 節は廃止された）。

### 4.1 `sources` の書き方

```yaml
sources:
  - { id: vaswani2017attention, resource: ../sources/vaswani2017attention.md, title: "Attention Is All You Need", relation: key-source }
  - { id: ga4-schema, resource: "https://developers.google.com/analytics/bigquery/export-schema", title: "GA4 Export schema", last_modified: 2026-05-30T00:00:00Z }
```

- `resource`（**エントリ内で必須**）: 追跡できる実体。次のいずれか — Wiki内 source ページへの**相対パス**（`../sources/<citekey>.md`）／ `raw/` 資産への**相対パス**（`../../raw/papers/<citekey>.pdf`）／ 外部 URL・DOI ／ 追跡不能な範囲記述（例 `PubMed の <検索式> の検索結果 120 件`）。
- `id`: **citekey と一致させる**。本文の脚注 `[^citekey]` の join key になるので、本文で引くなら必須。
- `title`: 人間可読なラベル。
- `relation`（本Wiki拡張）: `key-source`（主要な出典）／ `arising-from`（この課題を生んだ）／ `inspired-by`（着想元）／ `contradicts`（対立・反証）／ `adjacent`（隣接）。v0.1 の `key_sources` / `arising_from` / `inspired_by` / `related_sources` はこの1フィールドに統合された。
- 任意の信頼度シグナル: `author`（actor 表記）／ `last_modified`（原資料の更新時刻）／ `usage_count` + `usage_window`（被引用数を残したいときに使ってよい。`usage_window: { from: <出版日時>, to: <確認日時> }`）。

### 4.2 本文中の attribution

**Wiki内に source ページがある主張** → 従来どおり文末に相対リンクを置く。これがグラフのエッジ（Foam のバックリンク）になるため、脚注では代替しない。

```markdown
self-attention は再帰を排して並列化を可能にした（[vaswani2017attention](../sources/vaswani2017attention.md)）。
```

**Wiki内にページを持たない外部資料**（まだ ingest していない論文、規格書、Webページ）→ `sources` にエントリを足し、`[^id]` 脚注で紐付ける（OKF §5.1 の per-claim attribution）。

```markdown
GA4 の `events_` テーブルは日次シャーディングされる。[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

**すべての主張を attributable に**すること。どちらの形式でも、根拠のない断定は書かない。

### 4.3 BibTeX 連携

- **`raw/refs.bib` が引用の単一の真実**。ソースを取り込んだら、対応するBibTeXエントリが `refs.bib` にあることを確認し、無ければ作成する。
- BibTeX の `citekey` と、ソースページの**ファイル名**・`citekey` フィールド・他ページの `sources[].id` を**完全一致**させる。
- これにより `\cite{vaswani2017attention}`（LaTeX原稿）と、Wiki内のファイル `sources/vaswani2017attention.md`・そこへの相対リンク `[title](../sources/vaswani2017attention.md)`・frontmatter の `sources[].id` が一本の鎖で繋がり、Wikiから論文執筆へシームレスに接続する。

---

## 5. 命名規則・リンク規則

- **ソース**: ファイル名 = `citekey` = `<筆頭著者姓><年><キーワード>`（小文字、記号なし）。例 `vaswani2017attention`。Web記事は `<媒体or著者><年><キーワード>`、メモは `memo<YYYYMMDD><キーワード>`、進捗は `<氏名><年><キーワード>`。
- **概念・手法・課題・アイデア・エンティティ・トピック**: `kebab-case` の slug。例 `self-attention`、`long-range-dependency`、`idea-relative-pos-graph`。アイデアは衝突回避のため `idea-` 接頭辞を付ける。

### OKF Concept ID
各ページの **Concept ID** = 「`wiki/`（バンドル root）からの相対パス − `.md`」。例: `wiki/concepts/self-attention.md` → `concepts/self-attention`。frontmatter の**横の関係**フィールド（`concepts` / `methods` / `problems` / `entities` / `related` / `solves` / `addresses` / `addressed_by` / `ideas` / `open_problems` / `related_*`）はこの Concept ID を素スカラで格納する。

### リンク規則（相対 markdown リンクのみ）
- **Wiki内リンクは必ず相対 markdown リンク**。`[[wikilink]]` は使わない。
  - 同一ディレクトリ内: `[表示](./other-slug.md)`
  - 別ディレクトリ: `[表示](../concepts/self-attention.md)`（例: source から concept へ）
- **OKF §6.1 が推奨する絶対リンク（`/concepts/...`）は使わない**。Foam/VS Code はワークスペース root 相対で解決するため、絶対リンクは環境依存で壊れうる。相対リンクは位置に依存せず解決する。この逸脱は OKF の適合条件（§11）に触れない（両形式とも許容される）。
- **パス値フィールド**（`sources[].resource` / `computation` / `executor.resource` / `attester.resource` / `resource`）も同じ理由で**相対パス**を使う（外部 URL はそのまま）。
- **表示テキスト**は原則リンク先ページの `title`（または citekey/slug）を用いる。
- 別名は frontmatter の `aliases` に登録（表示ゆらぎ・検索補助のメタデータ。Foam では frontmatter エイリアスによる自動リンク解決は前提にしない）。
- **双方向性**: ページAからBへリンクを張ったら、Bの該当セクション（例: `## 関連ソース`）からもAへ張れないか確認する。
- **最小リンク要件**:
  - 各ソースページ → 最低1つの concept/method と、関連する problem にリンク。
  - 各 idea ページ → **必ず1つ以上の problem** にリンク（frontmatter `addresses` ＋本文リンク。孤立アイデア禁止）。
  - 各 problem ページ → それを生んだ source（`sources` の `relation: arising-from`）と、挑む idea にリンク。

---

## 6. wiki/index.md の構造（OKF §8）

`wiki/index.md` は全ページのカタログ（OKF の progressive disclosure）。**ページの追加・重要な変更のたびに更新**する。クエリ時はまずこれを読んで関連ページを特定し、そこから drill down する。

- frontmatter は **`okf_version: "0.2"` のみ許される**（OKF で index に frontmatter を置ける唯一の箇所）。それ以外の index には frontmatter を置かない。
- 本文は見出しでグループ化し、各項目を **`* [Title](相対パス.md) - description`** の箇条書きで列挙する（`wiki/index.md` は `wiki/` 直下なので相対パスは `sources/x.md`・`concepts/x.md` の形）。各項目の説明は対象ページの `description` を用いる。
- 括弧内の補足には `stage` と種別固有の軸を出す。`status: deprecated` のページは末尾に `(deprecated)` を付ける。
- 冒頭に集計行を置く。比較テーブルは補助ビューとして併用してよいが、**正準カタログは箇条書き**（OKF §8 形式）とし、grep 可能な素の markdown を必ず維持する。
- サブディレクトリごとの `index.md` も OKF は許すが、**本Wikiは `wiki/index.md` 一枚を正準**とする（同期コストを増やさない）。

```markdown
---
okf_version: "0.2"
---

# Research Wiki Index
_最終更新: 2026-06-04 — sources: N / concepts: N / methods: N / problems: N / ideas: N_

# 🔭 Topics（総説）
* [効率的なTransformerの系譜](topics/transformer-efficiency.md) - 各種効率化Transformerの俯瞰（stage: active）

# 📄 Sources
* [Attention Is All You Need](sources/vaswani2017attention.md) - self-attentionのみでTransformerを提案（paper / stage: read）

# 🧩 Concepts / Methods
* [Self-Attention](concepts/self-attention.md) - 文脈依存表現を得る注意機構

# ❓ Problems
* [長距離依存の効率的なモデリング](problems/long-range-dependency.md) - 二次コストを避け遠距離依存を捉える（severity: high / stage: open）

# 💡 Ideas
* [グラフ構造への相対位置エンコーディング](ideas/idea-relative-pos-graph.md) - 相対距離を注意に組込む仮説（stage: seed / confidence: low）

# 🏷 Entities
* [WMT14 En-De](entities/wmt14.md) - 英独MTベンチマーク（dataset）
```

---

## 7. wiki/log.md の形式（OKF §9）

すべての主要操作（ingest / query / idea / lint / web-survey）でエントリを記録。**日付見出し `## YYYY-MM-DD` を新しい順（newest first）** に並べ、同一日付の操作はその下にまとめる。各エントリは太字ラベル（`**Ingest**` / `**Query**` / `**Idea**` / `**Update**` / `**Creation**` / `**Verify**` / `**Deprecation**` 等）＋散文で書く。frontmatter は置かない。

履歴は `grep "^## " wiki/log.md | head` で新しい順に辿れる。

```markdown
# Operation Log

## 2026-06-04
* **Idea**: [グラフ構造への相対位置エンコーディング](ideas/idea-relative-pos-graph.md) を新規作成。Addresses: [長距離依存](problems/long-range-dependency.md) / Inspired by: [vaswani2017attention](sources/vaswani2017attention.md)。
* **Query**: 「Transformerはどう位置情報を扱うか？」— Consulted: [positional-encoding](concepts/positional-encoding.md), [vaswani2017attention](sources/vaswani2017attention.md)。Filed: no（会話のみ）。

## 2026-06-03
* **Ingest**: [Attention Is All You Need](sources/vaswani2017attention.md)（`raw/papers/vaswani2017attention.pdf`）。Touched: [self-attention](concepts/self-attention.md), [scaled-dot-product-attention](methods/scaled-dot-product-attention.md), [long-range-dependency](problems/long-range-dependency.md)。Takeaways: (2-3点)。Notes: 矛盾/フォローアップがあれば。
```

---

## 8. ワークフロー（skillsで実行）

各操作は `/skill` として実装済み。skillが詳細手順を持つので、ここでは要点のみ。**各 skill は OKF v0.2 準拠（相対 markdown リンク・Concept ID frontmatter・`description`/`generated` 付与・provenance は `sources`・`wiki/index.md`/`wiki/log.md` の OKF 形式）で生成物を作る。**

| Skill | 用途 | 概要 |
|-------|------|------|
| `/ingest [file]` | ソース取り込み | `raw/` のソース（papers/web/memos/progress）を読み、要約ページを作り、concept/method/problem/topic/index/log を更新（1回で5〜15ページに波及）。 |
| `/query <質問>` | Wikiへの問い合わせ | index→関連ページを読み、引用付きで合成回答。良い回答は新ページとして filing。 |
| `/idea [説明]` | アイデアの捕捉・育成 | 課題にひも付け、関連研究で位置づけ、idea ページを作成・発展。 |
| `/web-survey <トピック>` | 先行研究の網羅探索 | WebSearch/WebFetch で関連研究を探索し、ギャップを発見、取り込み候補を提示。 |
| `/lint [--fix]` | 健康診断 | 矛盾・陳腐化・孤立ページ・欠落ページ・壊れリンク・不備frontmatter・OKF非準拠を検出し、次に読むべき文献・問うべき問いを提案。 |

**ingest と idea の関係（研究サイクルの核）**: ソースを取り込むたび「## 自分の研究との接続」で課題を意識し、価値ある課題は `problems/` に昇格。課題が溜まったら `/idea` でアイデアに展開し、`/web-survey` で関連研究を確認、`/ingest` で裏取り — このループを回す。

---

## 9. 文体・スタイル規則

- **言語**: **本Wikiの基本言語は日本語**。本文・見出し・要約（`description` を含む）は日本語で書く。ただし専門用語・固有名詞・モデル名・データセット名・引用は **英語の原語のまま**（例: 「self-attention により long-range dependency を捉える」）。無理な訳語を作らない。
- **精度**: 「言語モデルを改善」ではなく「PTBで perplexity を 3.2 改善」のように **具体的な数値・条件** を書く。
- **attribution**: 主張には出典を付ける（§4.2）。Wiki内 source があれば相対リンク、無ければ `sources` ＋ `[^id]` 脚注。
- **客観と主観の分離**: ソース要約の `Problem/Method/Results` には著者の主張のみ。自分の意見・批判は `限界・批判的検討` と `自分の研究との接続`、および idea ページに書く。
- **TL;DR は2〜3文**。hedging（「〜かもしれない」の乱用）を削る。
- **形式の使い分け**: 比較は表、列挙は箇条書き、統合・論証は散文。
- **注意喚起**: Foam/VS Code は Obsidian の `> [!note]` callout を専用スタイルで描画しない（GitHub 風 `> [!NOTE]` も素の blockquote に退化する）。そこで **blockquote＋太字ラベル** を用いる:
  - `> **注記:** …` / `> **警告:** …` / `> **疑問:** …`
  - 矛盾の併記（不変ルール4）は `> **警告:** 出典Aは〜と主張するが、出典Bは〜。両論を併記する。` の形で明示。

### 数式は KaTeX 記法で書く

数式は **KaTeX** 記法で書く（VS Code の組み込み Markdown プレビューと mdExplorer が同じ `markdown-it` + KaTeX で描画する）。区切りは4通りとも使える。

| 用途 | 書き方 |
|------|--------|
| 本文中（インライン） | `$O(n \log n)$` |
| 独立した式（display） | `$$` … `$$` を**それぞれ独立した行**に置き、前後に空行を入れる |
| 独立した式（フェンス形式） | ` ```math ` … ` ``` `（`$$` と機能的に等価。ソース上で「ここは散文でない」と一目で分かる方を選ぶ） |
| 環境をそのまま | `\begin{aligned}` … `\end{aligned}`（`$$` で囲まなくても描画される） |

- **KaTeX は LaTeX の全機能を持たない。** 未対応のコマンドは**黙って壊れず赤いエラー表示**になる（`\unsupportedmacro` → `ParseError: Undefined control sequence`）。迷ったら [KaTeX supported functions](https://katex.org/docs/supported.html) で確認する。TikZ・`\usepackage`・カスタムマクロは使えない。数式を書いたら `/lint` を回す（数式内の全 `\コマンド` を KaTeX サポート表と照合し、波括弧・`\left`/`\right`・二重添字も検査する）。
- **markdown のエスケープを数式内に持ち込まない。** `$...$` の内側は markdown として解釈されないので、`*` や `_` を `\*` `\_` とエスケープする必要はなく、**むしろ壊れる**（`\*` は KaTeX に存在せず `ParseError: Undefined control sequence` になる。LaTeX には `\*` があるが KaTeX は未実装。`_` も数式中では下付き添字そのもの）。正しくは `$C^{*}$`（`$C^*$` も可）、`$a_{ij}$`。
- **添字が2文字以上なら必ず波括弧**: `a_{ij}` / `x^{(t)}`。`a_b_c` は LaTeX として二重添字エラーになる（markdown の強調とは無関係）。
- **コード内の `$` はエスケープ不要**。インラインコード `` `$WORK/data` `` とコードフェンス内の `SP=$WORK` は数式として解釈されない（本Wikiはシェル片を多く含むので重要）。
- **散文中の裸の `$`** は、`$100 と $200` のように離れていれば数式にならないが、確実にしたいなら `\$100` とエスケープする。
- 数式は**主張の一部**なので、出典のある式には attribution を付ける（§4.2）。論文の式番号を引くときは `([citekey](../sources/<citekey>.md) 式(3))` のように節番号・式番号まで書く。

---

## 10. セッション開始チェックリスト

1. `wiki/log.md` の先頭（新しい順）を読み、直近の活動を把握（`grep "^## " wiki/log.md | head`）。
2. `wiki/index.md` を読み、Wikiの現在地を把握。
3. 今日やりたいこと（ingest / query / idea / web-survey / lint）を確認（未指定なら尋ねる）。

---

## 11. OKF 準拠とバージョニング

- 本Wikiは **OKF version 0.2** を対象とする。バンドル root は `wiki/`、`okf_version: "0.2"` を `wiki/index.md` の frontmatter で宣言する。
- **OKF 適合条件**（仕様 §11）: (1) 全非予約 md に parseable な YAML frontmatter、(2) frontmatter に非空 `type`、(3) 予約ファイル（`index.md`/`log.md`）が仕様 §8/§9 形式。`/lint` がこれを検査する。
- **ローカルで必須化した OKF 推奨フィールド**: `title` / `description`（一行要約）／ `generated`（`by` と `at`）。OKF 上は推奨だが本運用では必須。
- **v0.1 から退役したフィールド**（書かない・見つけたら移行する）:

  | 旧 (v0.1) | 新 (v0.2) |
  |----------|-----------|
  | `timestamp: <ISO>` | `generated: { by: <actor>, at: <ISO> }` |
  | `updated: <date>` | `generated.at` に一本化（重複させない） |
  | 本文 `## 引用 (Citations)` 節 | 主張の帰属は `sources` ＋ `[^id]` 脚注（§4）へ。未ページ化文献の一覧は `## 参考文献 (Bibliography)` に改名して残す（§3.0） |
  | `key_sources` / `arising_from` / `inspired_by` / `related_sources` | `sources` に `relation:` を添えて統合（§4.1） |
  | `status: read` / `open` / `seed` / `active` | `stage:`（`status` は OKF lifecycle 専用に明け渡した、§3.0） |
  | `url:`（`resource` と重複していた） | `resource:` に一本化 |

- **v0.1 → v0.2 の一括移行は 2026-09-02 に完了済み**（155ページ）。移行時に `type: progress`/`exp` は `source`（`kind: progress`/`exp`）、`plan` は `idea`、`overview` は `topic` へ畳んだ。
- 本スキーマは固定ではない。運用して詰まったら人間とLLMで `CLAUDE.md` を改訂する。OKF 側が版を上げたら正準リポジトリの `SPEC.md` を取得して差分を当てる。

---

## 12. OKF 準拠マッピング

OKF v0.2 との正準の対応表（構造の対応・frontmatter フィールドの必須/推奨/拡張の区分・適合条件）は **`okf-conformance` skill** に置いた。スキーマ改訂時や `/lint` での適合検査時に参照する。
