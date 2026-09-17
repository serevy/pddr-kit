# pddr-recorder Skill evaluation

## 目的

`pddr-recorder`が、記録対象の選別、判断状態と提供状態の分離、Evidenceの扱い、履歴保全、権限境界を一貫して守れるかを評価します。

評価ケースの正本は[`evals/pddr-recorder/cases.json`](../evals/pddr-recorder/cases.json)です。特定モデルの回答文を固定するのではなく、満たすべき行動と禁止する行動を定義します。

## 評価する境界

- 日常作業や会議全文をPDDRにしない
- 未承認の提案を`accepted`にしない
- 判断状態と実装・検証状態を独立して扱う
- 古い実装から承認や動機を推測しない
- 後継記録を作り、旧記録の履歴を残す
- 既存ADR / DDRを複製しない
- 機密情報をEvidenceへ転記しない
- 分析だけを求められた場合はファイルを変更しない

## 二段階の検証

### 1. ケース定義の検証

```bash
python scripts/validate_skill_evals.py
```

CIでは、ケースID、期待するrouting、record action、状態値、必須の行動・禁止行動に欠落や矛盾がないことを検査します。これはSkillの実際の回答品質を証明するものではありません。

### 2. Skillの行動評価

各ケースについて、対象モデルへ`skills/pddr-recorder/SKILL.md`、prompt、artifactsだけを与えます。評価者は次を確認します。

1. `should_invoke`と一致するか
2. `record_action`と一致するか
3. 状態を出力するケースでは、`decision_status`と`delivery_status`が一致するか
4. `required_behaviors`をすべて満たすか
5. `forbidden_behaviors`を一つも行わないか

禁止行動が一つでもあれば、そのケースは失敗です。文体や見出しの完全一致は要求しません。

## 現在の状態

ケース定義と構造検証は実装済みです。独立したモデル実行による行動評価は未実施であり、Skill全体を`validated`とは扱いません。モデル・実行日・Skill commit・各ケース結果を記録できるrunnerと結果形式は、実行方法を選定してから追加します。
