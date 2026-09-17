---
id: PDDR-0004
title: Skill evaluation contract
decision_date: 2026-09-17
recorded_date: 2026-09-17
decision_status: accepted
delivery_status: implemented
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "evals/pddr-recorder/cases.json"
  - "python scripts/validate_skill_evals.py"
  - "python -m unittest discover -s tests -v"
related:
  - PDDR-0002
  - PDDR-0003
supersedes: []
superseded_by: null
---

# PDDR-0004: Skill evaluation contract

## Summary

`pddr-recorder`の評価を、回答文の完全一致ではなく、routing、record action、状態、必須行動、禁止行動からなる可搬なケース契約として定義する。

## Context and observations

- Skillのfront matterと形式検証だけでは、実際に提案を採用済みと誤認しないか、実装と検証を分けられるかを確認できない。
- モデルの自然言語出力は複数の正解表現があり、文章の完全一致は有効な品質指標にならない。
- PDDRの重大な失敗は、誤った状態、履歴の破壊、機密情報の転記、権限を越えた変更として観測できる。
- 特定のモデルや有償サービスをPDDR Kit本体の評価ケース形式へ必須化する必要はない。

## Options considered

### 期待回答の全文をgolden fileにする

- Benefits: 単純な文字列比較で自動化できる。
- Costs / constraints: 正しい言い換えまで失敗になり、表面的な一致が意味上の正しさを保証しない。
- Status: rejected

### 状態値だけを比較する

- Benefits: 小さく決定論的に評価できる。
- Costs / constraints: 機密情報の漏洩、履歴の書き換え、無断変更などを見逃す。
- Status: rejected

### 行動契約としてケースを定義する

- Benefits: モデル非依存で、PDDR固有の重大な成功・失敗条件を評価できる。
- Costs / constraints: 実モデルの出力を判定するrunnerまたは人による評価が別途必要になる。
- Status: accepted

## Decision

- JSONでSkill評価ケースを管理する。
- 各ケースはprompt、最小限のartifacts、routing期待、record action、必要な状態、必須行動、禁止行動を持つ。
- CIはケース定義の構造と内部整合性を検証する。
- 実モデル評価では禁止行動を一つでも行ったケースを失敗とする。
- 文体や見出しの完全一致は評価条件にしない。
- 実モデルでケースを実行するまでは、Skillの提供状態を`validated`と主張しない。

## Delivery and validation

11件の評価ケース、標準ライブラリだけで動くケース検証器、unit test、評価手順を追加した。ケース定義の構造と内部整合性はローカルテストおよびCIで検証する。

独立したモデル実行による行動評価は未実施のため、提供状態は`implemented`とする。

## Consequences

- 異なるモデルや将来のrunnerで同じ意味上の期待を再利用できる。
- Skillの重大な誤動作を、単なる文言差より優先して評価できる。
- ケース定義が妥当でもSkillの実際の挙動は保証されず、別途実行結果が必要になる。
- モデル名、実行日、Skill commit、結果を保存する形式は今後決める必要がある。

## Revisit when

- 同じケースへの人の判定が一致しない場合。
- 実モデル出力から期待項目を安定して抽出できない場合。
- 追加のPDDR状態やrecord actionが仕様へ導入された場合。
- 複数モデルの比較に、コストや再現性を含む結果形式が必要になった場合。

## Evidence

- `evals/pddr-recorder/cases.json`
- `python scripts/validate_skill_evals.py`
- `python -m unittest discover -s tests -v`

## Related records

- PDDR-0002: Portable initialization and validation
- PDDR-0003: First external adoption findings
