---
id: PDDR-0008
title: Add milestone audits to complement opportunistic decision capture
decision_date: 2026-09-22
recorded_date: 2026-09-22
decision_status: accepted
delivery_status: validated
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "Maintainer approval to feed the dogfooding finding back into PDDR Kit, 2026-09-22 (private)"
  - "https://github.com/serevy/semantic-decision-lab/pull/66"
  - "https://github.com/serevy/semantic-decision-lab/actions/runs/35732721814"
  - "https://github.com/serevy/pddr-kit/pull/29"
  - "https://github.com/serevy/pddr-kit/actions/runs/35735441734"
related:
  - PDDR-0003
  - PDDR-0004
  - PDDR-0007
supersedes: []
superseded_by: null
---

# PDDR-0008: Add milestone audits to complement opportunistic decision capture

## Summary

PDDR候補を個々の作業中に発見するopportunistic captureだけに依存せず、大きなフェーズ境界、Issue / roadmap棚卸し、複数Evidence-bearing Issue / PRのclose・統合時に、recent workを通常のPDDR thresholdで再点検するmilestone auditを標準運用として案内する。

checkpointは記録作成のquotaではなく、durable decisionがなければPDDRを追加しない。

## Context and observations

- PDDR KitのSkillは、読み込まれた作業コンテキストでは重要判断を記録する境界を持つが、Skillを通らないChat、GitHub UI操作、別Agent、手動作業まで常時監視する仕組みではない。
- semantic-decision-labでは、Issue棚卸しと実験の進展により複数のdurable decisionが形成されていたが、通常作業の都度ではPDDR-0001以降の追加記録が作られていなかった。
- 2026-09-22にrecent Issues / PRsをPDDR thresholdで棚卸しした結果、backend expansion freeze、provider-neutral evaluation contract、versioned dataset evolutionの3判断をPDDRへ昇格し、既存PDDRにもEvidenceを追記した。
- 同repositoryのAGENTS.mdへ、major experiment phase boundary、Issue / roadmap audit、複数Evidence-bearing Issueのclose時に再点検するcheckpointを追加した。
- PR #66のmerge後、main上のPDDR validationが成功した。
- 一方、checkpointの存在だけで毎回PDDRを作る運用にすると、PDDRを作業ログ化してしまい、PDDR-0003で確認したIssueとdurable decisionの責務境界を壊す。

## Options considered

### 個々の作業中のSkill判断だけに依存する

- Benefits: 追加の運用イベントが不要で、判断直後に記録できる。
- Costs / constraints: Skillを通らない経路や、複数Issueに分散して後からdurableになる判断を取りこぼせる。
- Status: rejected as the only mechanism

### CIでPDDR不足を自動判定し、節目ごとに必ず記録を要求する

- Benefits: 記録漏れを強く抑制できる。
- Costs / constraints: 文章意味と承認状態の判定を形式validatorへ持ち込み、false positiveやPDDR量産を招く。現在のvalidator責務を超える。
- Status: rejected

### opportunistic captureにmilestone auditを追加する

- Benefits: 日常作業での即時記録を維持しつつ、節目で取りこぼしを再点検できる。audit結果がno-opでも正常とできる。
- Costs / constraints: checkpointの起動は導入先の運用規則や人・Agentの実行に依存し、常時自動監視ではない。
- Status: accepted

## Decision

- PDDR Recorder Skillにmilestone auditの明示的な手順を追加する。
- 推奨checkpointは、major experiment / release / delivery phase boundary、Issue / roadmap audit、複数Evidence-bearing Issue / PRのcloseまたは統合とする。
- audit対象はrecent workなど必要な範囲へ限定し、通常のPDDR thresholdを変更しない。
- routine implementation、途中観測、実験完了そのものはPDDRへ昇格しない。
- durable decisionが見つからなければ新規PDDRを作成しない。
- 既存PDDRが同じ判断を表している場合は、新規記録より更新を優先する。
- 導入ガイドで、AGENTS.md等のプロジェクト固有規則へcheckpointを接続することを推奨する。
- PDDR-0003とPDDR-0007の非破壊方針を維持し、init / upgradeは導入先のAGENTS.mdやCIを自動上書きしない。
- milestone auditがno-opを許容することと、複数Evidenceからdurable decisionだけを昇格することをSkill evalで明示的に評価する。
- 現段階では自動semantic scannerや定期botを標準機能に含めない。

## Delivery and validation

semantic-decision-labでは、2026-09-22のcheckpoint auditで未記録だったdurable decisionを3件抽出し、既存PDDRのEvidence更新と合わせてPR #66へまとめた。同PRでは再発防止としてAGENTS.mdへcheckpointを追加し、merge後のmainでPDDR validationが成功した。これにより、導入先でmilestone auditが記録漏れの再点検として機能することを確認した。

PDDR Kit側では、本判断をSkill、導入ガイド、独立したmilestone audit Skill評価suite、Changelogへ反映した。PR #29をmainへmergeし、merge commit上のValidate PDDR Kitが成功した。これにより、Kit本体への実装とrepository-level validationが完了したため、delivery statusを`validated`とする。

追加したmilestone audit 2ケースはschema・repository validationまで完了しているが、Sol / Luna等による独立forward-testはまだ実施していない。このため、`validated`はmilestone audit運用とKit統合が検証済みであることを示し、新評価ケースのモデル品質まで証明するものではない。

## Consequences

- PDDR Skillを毎回読み込まない開発経路があっても、節目で重要判断の取りこぼしを発見しやすくなる。
- 「毎作業でPDDR」と「半年後にまとめて記憶から再構成」の中間となる運用ポイントを持てる。
- checkpoint自体はPDDR作成義務ではないため、IssueとPDDRの責務境界を維持できる。
- 導入先は、自分の開発フローに合うcheckpointをAGENTS.md等へ明示する必要がある。
- validatorは引き続き既存PDDRの形式・整合を検証し、未記録の判断を意味的に検出する責務を持たない。
- 将来、自動audit支援を追加する場合も、false positive、権限、承認推論、対象範囲を別途設計する必要がある。

## Revisit when

- 複数導入先でcheckpointの手動実行漏れが繰り返し観測された場合。
- GitHub Issue / PR metadataから安全にaudit候補だけを提示する仕組みを設計できた場合。
- semantic decision backendによるPDDR候補検出のprecision / recallを実測できた場合。
- milestone audit自体がPDDR量産や過剰なcontext loadingを引き起こす場合。

## Evidence

- Maintainer approval to feed the dogfooding finding back into PDDR Kit, 2026-09-22 (private).
- [semantic-decision-lab PR #66](https://github.com/serevy/semantic-decision-lab/pull/66)
- [semantic-decision-lab main PDDR validation after PR #66](https://github.com/serevy/semantic-decision-lab/actions/runs/35732721814)
- [PDDR Kit PR #29: milestone audit checkpoint](https://github.com/serevy/pddr-kit/pull/29)
- [PDDR Kit main validation after PR #29](https://github.com/serevy/pddr-kit/actions/runs/35735441734)

## Related records

- PDDR-0003: First external adoption findings
- PDDR-0004: Skill evaluation contract
- PDDR-0007: Safe upgrades for adopted projects
