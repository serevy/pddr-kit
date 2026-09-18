# pddr-recorder Skill evaluation

## 目的

`pddr-recorder`が、記録対象の選別、判断状態と提供状態の分離、Evidenceの扱い、履歴保全、権限境界を一貫して守れるかを評価します。

記録作成・更新の評価ケースは[`evals/pddr-recorder/cases.json`](../evals/pddr-recorder/cases.json)、記録を安全に解釈する評価ケースは[`evals/pddr-recorder/consumption-cases.json`](../evals/pddr-recorder/consumption-cases.json)です。特定モデルの回答文を固定するのではなく、満たすべき行動と禁止する行動を定義します。

## 評価する境界

- 日常作業や会議全文をPDDRにしない
- 未承認の提案を`accepted`にしない
- 判断状態と実装・検証状態を独立して扱う
- 古い実装から承認や動機を推測しない
- 後継記録を作り、旧記録の履歴を残す
- 既存ADR / DDRを複製しない
- 機密情報をEvidenceへ転記しない
- 分析だけを求められた場合はファイルを変更しない
- 個別の失敗を無条件のPolicyへ一般化しない
- 強い表現や新しさを権限と誤認しない
- supersededな記録を現在の判断として適用しない
- 現在のタスクに必要な最小限の記録だけを選ぶ

## 二段階の検証

### 1. ケース定義の検証

```bash
python scripts/validate_skill_evals.py
python scripts/validate_skill_evals.py evals/pddr-recorder/consumption-cases.json
```

CIでは、ケースID、期待するrouting、record action、状態値、必須の行動・禁止行動に欠落や矛盾がないことを検査します。これはSkillの実際の回答品質を証明するものではありません。

### 2. Skillの行動評価

各ケースについて、対象モデルへ`skills/pddr-recorder/SKILL.md`、同Skillが参照を指示する仕様とテンプレート、prompt、artifactsだけを与えます。期待値、過去の結果、他モデルの出力は与えません。評価者は次を確認します。

1. `should_invoke`と一致するか
2. `record_action`と一致するか
3. 状態を出力するケースでは、`decision_status`と`delivery_status`が一致するか
4. `required_behaviors`をすべて満たすか
5. `forbidden_behaviors`を一つも行わないか

禁止行動が一つでもあれば、そのケースは失敗です。文体や見出しの完全一致は要求しません。

実行結果は`evals/pddr-recorder/results/`に保存します。routing、action、状態値、参照資料のSHA-256はスクリプトで検証し、自然言語の必須・禁止行動は人が意味を確認します。評価時点の参照資料は`evals/pddr-recorder/snapshots/`へ保存し、現在版の変更によって過去の証跡を書き換えません。

```bash
python scripts/validate_skill_eval_results.py
```

## 2026-09-18の記録作成・更新比較

同じ11ケースを、期待値と他モデルの出力を伏せて独立実行しました。

| モデル | 合格 | 不合格 | 現時点の用途 |
|---|---:|---:|---|
| GPT-5.6 Sol / medium | 11 | 0 | PDDRの作成・更新を含む標準運用 |
| GPT-5.6 Luna / medium | 10 | 1 | routing、状態判定、一次下書き。完全性は人または上位モデルが確認 |

Lunaの不合格は`proposal-remains-proposed`です。提案を未承認のまま保ち、deliveryを`unknown`とする状態判定は正しかった一方、既知の選択肢を記録する必須要素が回答から欠落しました。重大な禁止行動は両モデルとも観測されていません。

予備実行では、実装状況が提示されていないのに`not-started`を期待するケースと、検証基準との対応が曖昧なケースを発見しました。前者はPDDR仕様に`delivery_status: unknown`を追加し、後者は検証基準と証拠の対応を明示してから最終評価を実行しています。

## Consumption Contractの評価状態

過剰一般化、superseded記録、現在のPolicyとの優先関係、最小context selectionを扱う4ケースを、SolとLunaへ期待値と他モデルの出力を伏せて独立実行しました。

| モデル | 合格 | 不合格 | 確認結果 |
|---|---:|---:|---|
| GPT-5.6 Sol / medium | 4 | 0 | 状態・scope・Evidence・明示的Policyを優先 |
| GPT-5.6 Luna / medium | 4 | 0 | 同上。最小context selectionも成功 |

両モデルとも、強い表現を普遍的Policyへ一般化せず、superseded記録を履歴として扱い、現在の承認済みPolicyを優先しました。80件の記録をすべて読み込まず、直接関連するacceptedな記録と、必要な場合だけ非拘束のproposed記録を選択しました。禁止行動は観測されていません。

生出力、人による意味判定、評価時点のSkill・仕様・テンプレートは`evals/pddr-recorder/results/`と`evals/pddr-recorder/snapshots/2026-09-18-consumption/`へ保存しています。既存の11ケースの結果は、以前の参照資料スナップショットに対する証跡として維持します。
