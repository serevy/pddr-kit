---
id: PDDR-0012
title: Bound CI execution and make efficient adoption explicit
decision_date: 2026-10-04
recorded_date: 2026-10-04
decision_status: accepted
delivery_status: in-progress
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "https://github.com/serevy/pddr-kit/issues/47"
  - "Maintainer authorized source defaults, greenfield validation and explicit consumer adoption, 2026-10-04 (private summary)"
  - "docs/adoption.md"
  - "templates/checkpoint-ci/pddr-checkpoint.yml"
  - "templates/checkpoint-ci/pddr-checkpoint-marker.yml"
  - ".github/workflows/validate.yml"
related:
  - PDDR-0009
  - PDDR-0010
supersedes: []
superseded_by: null
---

# PDDR-0012: Bound CI execution and make efficient adoption explicit

## Summary

PDDRのCI導入時に、既存のread-only検証jobへのstep追加を最初の選択肢として案内する。独立validatorとoptional checkpointには実行上限を持たせ、読み取り専用検証の旧実行取消しは同一PRへ限定する。

PDDR-0010のadvisory signal / trusted writer分離と既存の検出範囲を維持し、source更新とconsumerへの明示的な採用を別々に追跡する。

## Context and observations

- Issue #47では、PDDRの標準ライブラリ検証が短時間で終わる一方、独立サンプルとoptional templateに明示timeoutがないことを確認した。
- 導入サンプルは、既存の検証jobを利用できる場合にも新しいrunnerを起動する構成だけを示していた。
- `init` / `upgrade`はCI、AGENTS、optional checkpoint integrationを管理しない。sourceだけの変更では既存consumerへ反映されない。
- GitHubはjob単位で実行分数を切り上げるため、短い独立jobを増やすと実行秒数以外の重複も生じる。
- job-level条件でskipしたcheckはSuccess扱いになる。titleだけの変更等でsignal jobを省略する案には、同じSHAの失敗済みcheckや共有concurrencyへの影響を解消する必要がある。
- 現在のsignalは正確なbase/head SHAのdiffを使い、markerはtrusted default branchから現在のPR metadata/filesを再取得する。

## Options considered

### 現行の独立jobと明示timeoutのないtemplateをそのまま案内する

- Benefits: sourceとconsumerの追加変更が不要。
- Costs / constraints: 既存jobの再利用が案内されず、異常長時間実行の上限も明示されない。
- Status: not selected for the updated defaults

### 軽量な既定値と明示的なconsumer採用を提供する

- Benefits: runner起動数を増やす前に既存jobを検討でき、PRの旧実行と異常長時間実行を抑えられる。
- Costs / constraints: consumerのcheck依存やcold実行予算を個別に確認し、各PRで採用する必要がある。
- Status: accepted

### title / label条件だけでjobをskipし、checkoutを直ちにshallow化する

- Benefits: 一部イベントや履歴取得の仕事量を減らせる可能性がある。
- Costs / constraints: skipped-success、進行中・pending runの置換、markerの後続起動、base/head取得の正当性を単純な置換では保証できない。
- Status: deferred pending a separate compatibility design

## Decision

2026-10-04にmaintainerがIssue #47のsource改善、greenfieldでの確認、必要なconsumer採用を依頼したことを根拠として、この範囲の既定値を採用する。

- Python 3.10以降がある既存read-only jobへPDDR検証stepを追加する選択肢を先に示す。
- 独立validatorの例は5分上限とworkflow / PR単位の旧実行取消しを持つ。non-PRはref / run IDを含む固有groupで独立させる。
- optional signalとtrusted markerは各5分上限を持つ。signalの既存PR groupを維持し、markerへ取消し設定を追加しない。
- 既存jobへの統合では、job全体のcold実行に応じてtimeoutを決め、trigger/path、required check、権限、失敗の伝播を維持する。
- checkpointのイベント検査と`fetch-depth: 0`は維持する。省略する場合は別途、チェック結果と正確なcommit取得の互換性を検証する。
- Kit自身の通常read-only validationにも5分上限と同一PR限定の取消しを適用する。required `validate`名と検証コマンドは変えない。
- sourceとconsumer採用は別管理とし、source ref、変更ファイル、PR/head、通常CI、merge/main状態を記録する。
- PDDRの自動作成・自動承認、optional integrationの自動導入・自動更新を追加しない。

## Delivery and validation

sourceの実装対象は導入ガイド、2つのcheckpoint template、Kit自身のvalidation設定、Unreleased CHANGELOGである。managed core、detector、Skill、release / translation workflowは変更しない。現在のdevelopment version `0.3.0-dev`で追跡し、stable releaseの公開とは分ける。

repositoryの既存unit tests、Skill eval検証、PDDR検証を実施する。templateは追加したtimeout以外が従来と同じであること、独立サンプルとKit validationの取消し範囲、公開文書のリンクと導入境界を確認する。

greenfieldでは通常のPR更新を使い、routine変更のno-signal、AGENTS変更のrecommended signal、trusted default-branch writer、completed回収と重複防止を確認する。その後に対象consumerへ必要な差分だけを提案する。

具体的なPR / CI結果、sourceとconsumerのmerge状態はIssue #47で追跡する。各採用先の検証・反映が完了するまで、この記録のdeliveryは `in-progress` とする。

## Consequences

- 今後の導入時からrunner起動数と実行上限を検討できる。
- タイムアウトと取消しは通常の検証処理そのものを高速化する変更ではない。
- 同一PR以外のmain / manual実行は独立して完了できる。markerにはconcurrencyによる旧実行取消しを追加しない。
- イベント検査範囲と全履歴取得を維持するため、それらによる起動数・転送量の削減は今回の効果へ計上しない。
- 公開standard runnerの検証結果をprivate無料枠の直接削減量として扱わず、単発時間から月間請求額を推計しない。
- consumer固有のcheck名や権限を無条件に置き換える根拠にはしない。

## Revisit when

- cold実行が5分へ近づき、実行上限の調整が必要になった場合。
- skipped-successや有用な実行の取消しを起こさないmetadata-event除外方法が検証できた場合。
- fork / base変更を含む正確なbase/head取得を保った履歴削減の根拠が得られた場合。
- consumerのcheck依存が変わり、独立jobの統合を再検討できる場合。
- 継続運用のjob数・使用量で、より優先度の高い費用要因が見つかった場合。

## Evidence

- [Issue #47](https://github.com/serevy/pddr-kit/issues/47)
- Maintainer authorization for the scoped source and consumer work, 2026-10-04 (private summary).
- [GitHub job conditions](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)
- [GitHub concurrency](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [GitHub required checks](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
- [GitHub per-job minute rounding](https://docs.github.com/en/billing/reference/actions-runner-pricing)
- `docs/adoption.md`
- `templates/checkpoint-ci/pddr-checkpoint.yml`
- `templates/checkpoint-ci/pddr-checkpoint-marker.yml`
- `.github/workflows/validate.yml`
- Existing `tests/test_pddr_checkpoint.py` and repository validation.

## Related records

- PDDR-0009: Product-level versioning and optional integration boundaries
- PDDR-0010: Advisory checkpoint CI and trusted writer separation
