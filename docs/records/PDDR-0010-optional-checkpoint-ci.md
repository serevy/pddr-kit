---
id: PDDR-0010
title: Provide optional checkpoint CI as an advisory safety net
decision_date: 2026-09-23
recorded_date: 2026-09-23
decision_status: accepted
delivery_status: validated
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "https://github.com/serevy/pddr-kit/issues/32"
  - "Maintainer approved optional recommended checkpoint CI, 2026-09-23 (private)"
  - "scripts/pddr_checkpoint.py"
  - "templates/checkpoint-ci/pddr-checkpoint.yml"
  - "templates/checkpoint-ci/pddr-checkpoint-marker.yml"
  - "tests/test_pddr_checkpoint.py"
  - "https://github.com/serevy/pddr-greenfield-example/pull/18"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35860389299"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35860608772"
  - "https://github.com/serevy/pddr-greenfield-example/pull/19"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35860852749"
  - "https://github.com/serevy/pddr-kit/pull/39"
  - "https://github.com/serevy/pddr-kit/actions/runs/35885546317"
  - "https://github.com/serevy/pddr-greenfield-example/pull/21"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35886025597"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35886046614"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35886130669"
  - "https://github.com/serevy/pddr-greenfield-example/actions/runs/35886151266"
related:
  - PDDR-0008
  - PDDR-0009
supersedes: []
superseded_by: null
---

# PDDR-0010: Provide optional checkpoint CI as an advisory safety net

## Summary

PDDR milestone auditをAgent Skillやproject guidanceだけに依存させず、GitHub Actionsを利用するconsumer向けにoptional / recommendedなcheckpoint CIを提供する。

CIはPDDRの必要性を意味的に判定したり記録を自動作成したりせず、deterministicなhigh-signal changeを検出して「checkpoint review recommended」という留守番signalを残す。

## Context and observations

- PDDR-0008では、opportunistic captureを補完するmilestone auditを標準運用として採用した。
- その後のdogfoodで、ChatGPT経由のcloud development、GitHub上の直接変更、人手編集など、Agent Skillが常時観測しない開発経路ではcheckpoint自体の実行が漏れることが確認された。
- local AgentでもSkillやrepository contextの再読込は実行環境・session・cache状態に依存し、常に同じ運用知識がactiveとは限らない。
- Semantic Decision LabではPR本文末尾の `## PDDR checkpoint` が実運用上のreview surfaceとして定着したが、これはAgentがその場でrepository guidanceや過去PRを参照できている場合に成立していた。
- 全consumerがGitHub Actionsを利用するわけではないため、checkpoint CIをPDDR Kitの必須要件にすると可搬性を損なう。
- CIがPDDR作成義務を判定すると、PDDR-0008で避けた記録ノルマとfalse positiveを再導入する。

## Options considered

### Agent Skill / AGENTS guidanceだけに依存する

- Benefits: CI権限やplatform依存を追加しない。
- Costs / constraints: Agentが不在、contextを再読込していない、または手動変更経路ではcheckpoint signal自体が残らない。
- Status: rejected as the only mechanism

### checkpoint CIを必須にする

- Benefits: GitHub Actions環境では一貫してsignalを残せる。
- Costs / constraints: GitHub Actionsを使わないconsumerを不完全扱いし、PDDR Kitのplatform portabilityを損なう。
- Status: rejected

### optional / recommendedなadvisory CIを提供する

- Benefits: Skill中心の運用を維持しながら、監視外経路にrepo側のdurableな目印を残せる。
- Costs / constraints: signalはsemantic decisionではなく、後続Agent / maintainerによるbounded auditが必要。
- Status: accepted

## Decision

- checkpoint CIはoptional / recommended integrationとし、PDDR Kit利用の必須条件にしない。
- 通常の主経路はAgent Skillとproject guidanceによるmilestone auditのままとする。
- v1のdetectorはhigh-confidenceなdeterministic signalに限定する。
  - `AGENTS.md`変更
  - roadmap surface変更
  - architecture surface変更
  - `pddr-checkpoint` label
  - PR本文の明示marker `[pddr-checkpoint]`
- PR数だけの閾値やEvidence量だけの推測はv1に含めない。
- CIはPDDRを自動作成・更新・承認しない。
- **Checkpoint Signal ≠ PDDR required** を明示し、audit結果がno-opでも正常とする。
- Check / Job Summaryには実行時点のsignalを常に残し、後から同期更新する必要のないexecution traceとする。
- recommended signalがあり、PR本文に既存の `## PDDR checkpoint` がなければ、PR本文末尾へpending markerを追加する。
- PR本文を更新できない場合は既存checkpoint commentの更新または新規commentをfallbackとする。
- PR本文・commentへのwriteができない場合もCI自体は失敗させず、Check / Job Summaryを最低限のtraceとして残す。
- pending markerを後続Agent / maintainerが確認した場合、通常のPDDR thresholdでbounded auditし、PR本文のcurrent review stateを更新する。過去のCheck Summaryは書き換えない。
- PR headをcheckout・実行するsignal workflowは通常の `pull_request` eventを使用し、`contents: read` / `pull-requests: read` のread-only権限に限定する。
- PR本文・commentへのwriteは、signal workflow完了後にdefault branchのtrusted codeだけを実行する `workflow_run` writerへ分離する。
- privileged writerはPR headのコード・artifactをcheckoutまたは実行せず、GitHub APIからPR metadata / changed filesを取得してtrusted detectorでsignalを再計算する。
- security上、`pull_request_target`は使用しない。
- optional integrationはPDDR-0009どおりproduct releaseのversioning対象だが、managed-core `upgrade`では自動導入・更新しない。

## Delivery and validation

deterministic signal detectorを `scripts/pddr_checkpoint.py` として実装し、high-signal path、明示label / marker、routine changeのno-op、既存checkpoint surface、advisory markerをunit testで検証する。

consumer向けtemplateをread-only signal workflow `templates/checkpoint-ci/pddr-checkpoint.yml` とtrusted marker writer `templates/checkpoint-ci/pddr-checkpoint-marker.yml` に分離して提供する。導入時はdetectorをconsumerの `.pddr/pddr_checkpoint.py` へ明示的にコピーし、2つのworkflowと合わせてreviewする。

PDDR Recorder Skillにはpending markerを「PDDR required」ではなくmilestone audit requestとして扱う指針を追加する。

repository-level unit testsとPDDR validationに加え、`pddr-greenfield-example`で実consumer dogfoodを行った。

PR #18ではcheckpoint sectionを事前記載せずに`AGENTS.md`を変更し、checkpoint run `35860389299` がhigh-signal changeを検出してPR本文末尾へ `Signal: recommended / Review: pending` を自動追記した。後続のbounded auditでは新規PDDRを量産せず、既存PDDR-0002のrevisit conditionに該当すると判断して同記録を更新し、PR本文を `Review: completed` / `existing PDDR-0002 updated` へ回収した。更新後のcheckpoint run `35860608772` も成功し、checkpoint headingは1件のままで重複しなかった。

PR #19では`app.js` / `styles.css`だけのroutine UI変更に対してcheckpoint run `35860852749` が成功し、PR本文へcheckpoint markerを追加しなかった。これによりhigh-signal positive pathとroutine no-signal pathの両方を実consumerで確認した。

v0.2.0で同一repository内PRのprimary flowをE2E確認した後、横展開前のsecurity reviewで、`pull_request` workflowがPR headのdetectorを実行しながらPR write permissionも持つ構成はsame-repository branch PRに対するleast-privilege境界として不十分だと判断した。

このため、PR headを観測するread-only signal workflowと、default branchのtrusted detectorだけを実行するprivileged `workflow_run` marker writerへ分離した。unit testでsignal workflowにwrite permissionがないこと、writerがdefault branchをcheckoutしPR headをcheckoutしないことを固定する。

新しい2段構成はPR #39でmainへmergeし、main validation run `35885546317` が成功した。

その後、greenfield example PR #21でread-only signal workflowとtrusted marker writerを導入した。既存PR #20へ明示markerを追加してdogfoodし、signal run `35886025597` が成功した後、trusted `workflow_run` marker writer `35886046614` がPR本文へ `Review: pending` markerを自動追記した。

markerを `Review: completed` / `no new PDDR` へ回収した後もsignal run `35886130669` とwriter run `35886151266` が成功し、PR本文の `## PDDR checkpoint` headingは1件のままで重複しなかった。

read-only signal、trusted writer、pending marker write、completed state、重複防止をconsumer E2Eで確認できたため、deliveryを再び `validated` とする。

## Consequences

- Agentが一時的にPDDR運用contextを失っても、repository側にcheckpoint候補の目印を残せる。
- GitHub Actionsを使わないconsumerは従来どおりSkill / guidanceだけで運用できる。
- PR本文のcheckpoint sectionをcurrent review surfaceとして再利用でき、Semantic Decision Labで自然発生した運用と揃う。
- Check Summaryは履歴、PR本文はcurrent stateという役割分担になり、過去Checkの同期更新は不要になる。
- false positiveを完全には避けられないが、v1はhigh-signal surfaceに限定し、signal自体にPDDR作成義務を持たせない。
- untrusted PR codeを観測するsignal workflowはread-onlyになり、PR write権限はtrusted default-branch writerだけが持つ。
- marker writeがrepository policy等で拒否されても、read-only signal workflowのSummaryは残る。
- optional integrationはmanaged-core upgradeの対象外なので、consumerごとに明示的な導入・更新が必要になる。

## Revisit when

- 複数consumerでfalse positive / false negativeが蓄積した場合。
- Evidence-bearing PR / Issue consolidationを安全にdeterministic signal化できる場合。
- GitHub以外のCI向けadapter需要が生じた場合。
- markerのmachine-readable schemaやoptional integration inventoryが必要になった場合。
- consumer dogfoodでPR本文更新・comment fallback・fork権限の扱いに問題が見つかった場合。

## Evidence

- [Issue #32: OptionalなPDDR checkpoint CIを提供する](https://github.com/serevy/pddr-kit/issues/32)
- Maintainer approval of optional recommended checkpoint CI, 2026-09-23 (private).
- `scripts/pddr_checkpoint.py`
- `templates/checkpoint-ci/pddr-checkpoint.yml`
- `templates/checkpoint-ci/pddr-checkpoint-marker.yml`
- `tests/test_pddr_checkpoint.py`
- [greenfield dogfood PR #18](https://github.com/serevy/pddr-greenfield-example/pull/18)
- [first high-signal checkpoint run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35860389299)
- [completed-marker checkpoint run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35860608772)
- [routine UI PR #19](https://github.com/serevy/pddr-greenfield-example/pull/19)
- [routine no-signal checkpoint run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35860852749)
- [PDDR Kit PR #39: checkpoint CI privilege hardening](https://github.com/serevy/pddr-kit/pull/39)
- [main validation after PR #39](https://github.com/serevy/pddr-kit/actions/runs/35885546317)
- [greenfield hardening PR #21](https://github.com/serevy/pddr-greenfield-example/pull/21)
- [read-only signal dogfood run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35886025597)
- [trusted marker writer dogfood run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35886046614)
- [completed-state signal run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35886130669)
- [completed-state writer run](https://github.com/serevy/pddr-greenfield-example/actions/runs/35886151266)
- PDDR-0008: Add milestone audits to complement opportunistic decision capture
- PDDR-0009: Define product-level versioning and optional integration boundaries

## Related records

- PDDR-0008: Add milestone audits to complement opportunistic decision capture
- PDDR-0009: Define product-level versioning and optional integration boundaries
