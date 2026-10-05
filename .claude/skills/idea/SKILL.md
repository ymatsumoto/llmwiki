---
name: idea
description: 研究アイデア・仮説を捕捉し、課題（problem）にひも付け、関連研究で位置づけて idea ページを作成・育成する。思いついた解決策・仮説を蓄積したいときに使う。
---

# アイデアの捕捉・育成 (Idea)

研究アイデアを記録し、**必ず課題（problem）に接地**させ、先行研究の中に位置づけて、発展可能な形に構造化する。孤立したアイデアは作らない。

## 手順

1. **アイデアを引き出す**: `$ARGUMENTS` にあればそれを使う。無ければ尋ねる —「核となる仮説は？ どの課題を解く？」

2. **slug を決める**: `idea-<短いkebab>`（例 `idea-relative-pos-graph`）。人間に確認。

3. **課題に接地（必須）**: `wiki/problems/` を見て、このアイデアが挑む課題ページを特定する。
   - 該当する problem が無ければ、**先に `wiki/problems/<slug>.md` を作る**ことを提案・実行（`CLAUDE.md` §3.6、`title`/`description`/`generated`/`root`（§3.0 のプロジェクト root 名）を付与）。
   - `addresses` に最低1つの Concept ID `problems/<slug>` を入れる（本文では相対リンク `[title](../problems/<slug>.md)`）。

4. **関連研究で位置づける**: concept/method/source ページと（必要なら `/web-survey`）から探す:
   - 同じ課題を部分的に解く研究
   - このアイデアが **builds-on / departs-from** する研究
   - このアイデアと **contradicts** しうる研究（反証リスク）

5. **`wiki/ideas/<slug>.md` を書く**: `CLAUDE.md` §3.7 のスキーマで（`type`/`title`/`description`/`generated`/`root`（§3.0 のプロジェクト root 名）必須。`addresses` は Concept ID、着想元は `sources` に `relation: inspired-by`、本文は相対リンク）。特に:
   - `## 仮説` — 一行で核心。
   - `## スケッチ` — 「何を実装・証明すべきか」が分かる程度に具体的に。
   - `## 反証条件` — 何が観測されたら間違いと分かるか（ここを必ず埋める。アイデアを科学にする）。
   - `## 関連研究との位置づけ` 表。
   - `## ネクストアクション` — 具体的な次の一手のチェックリスト。
   - 初期 `stage: seed` / `confidence` を正直に設定（`status` は OKF lifecycle 用なので `stable`。書きかけなら `draft`）。

6. **problem ページを更新**: 接地先の problem の `ideas` フィールドに Concept ID `ideas/<idea-slug>` を、「## 関連アイデア」節に相対リンク `[idea-slug](../ideas/<idea-slug>.md)` を追加（双方向リンク）。

7. **wiki/index.md / wiki/log.md を更新**:
   - `wiki/index.md`（OKF §8）: Ideas 節に `* [title](ideas/<idea-slug>.md) - description （stage: seed / confidence: ...）` を追加、集計行を更新。
   - `wiki/log.md`（OKF §9, 新しい順）:
   ```markdown
   ## YYYY-MM-DD
   * **Idea**: <タイトル> — [idea-slug](ideas/<idea-slug>.md) を新規作成。Addresses: [problem-slug](problems/<slug>.md) / Inspired by: [citekey](sources/<citekey>.md)。Stage: seed。
   ```

8. **次の一手を相談**: 以下を提案 —
   - 関連研究の深掘り（`/web-survey`）
   - 実験プロトコルの起草
   - 競合手法に対する位置づけ表（`/query` で比較を filing）
   - `stage` を `developing` に上げる条件の明確化

## アイデアの育成（既存アイデアの更新）

既存 idea の発展を指示されたら: 新たな証拠・反証を `強み/弱み`・`関連研究` に反映し、`stage`/`confidence`/`generated.at` を更新。検証されたら `stage: validated`、棚上げは `parked`、否定されたら `discarded`（**消さず `stage` で記録**し、なぜダメだったかを残す — 失敗の記録も資産）。別アイデアに完全に吸収された場合のみ `status: deprecated` も併記する。

## Args
`$ARGUMENTS` — 任意。アイデアの短い説明。空なら尋ねる。
