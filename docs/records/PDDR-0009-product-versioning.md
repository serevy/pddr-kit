---
id: PDDR-0009
title: Define product-level versioning and optional integration boundaries
decision_date: 2026-09-23
recorded_date: 2026-09-23
decision_status: accepted
delivery_status: validated
scope:
  - project
  - product
  - process
owners:
  - serevy
evidence:
  - "https://github.com/serevy/pddr-kit/issues/33"
  - "Maintainer approved the product-level versioning contract, 2026-09-23 (private)"
  - "docs/versioning.md"
  - "tests/test_pddr_cli.py"
  - "https://github.com/serevy/pddr-kit/pull/34"
  - "https://github.com/serevy/pddr-kit/actions/runs/35854662290"
related:
  - PDDR-0007
  - PDDR-0008
supersedes: []
superseded_by: null
---

# PDDR-0009: Define product-level versioning and optional integration boundaries

## Summary

PDDR Kitのversionをmanaged coreだけのversionではなく、Skill、guidance、optional integrationを含むproduct release全体のversionとして扱う。

consumer manifestの`kit_version`はmanaged coreを最後に導入・更新したKit source versionのprovenanceを示すが、optional integrationの導入済み・最新状態までは保証しない。

## Context and observations

- stable `v0.1.0`公開後も、milestone audit guidance、Skill評価ケース、多言語README改善などPDDR Kit全体のcapabilityが進化した。
- 一方、root `VERSION`とCLIの`KIT_VERSION`は`0.1.0`のままで、mainからconsumerへ導入してもstable `0.1.0`と同じ`kit_version`が記録される状態だった。
- PDDR-0007では、consumerを安全に更新するため、自動管理対象を`.pddr/pddr.py`、specification、templateへ限定した。
- Skill、AGENTS guidance、validation CI等はconsumer固有の構成や権限と衝突し得るため、PDDR-0007では自動上書き対象から除外している。
- PDDR-0008以降のdogfoodでは、managed core以外の運用surfaceもPDDR Kitの実用能力として重要になっている。
- Issue #33で、product version、manifest provenance、release/tag、optional integrationの境界を明示する必要が確認された。

## Options considered

### Versionをmanaged core三ファイルだけの識別子として扱う

- Benefits: manifestの管理対象とversionの意味が一致しやすい。
- Costs / constraints: Skillやoptional CI等のproduct capability追加がrelease versionに反映されず、consumerがKit全体の世代を判断しづらい。
- Status: rejected

### Product versionに含まれる全surfaceをupgradeで自動更新する

- Benefits: versionとconsumer状態を一対一に近づけられる。
- Costs / constraints: consumer所有のCI、AI規則、既存運用を上書きする危険があり、PDDR-0007の非破壊方針を壊す。
- Status: rejected

### Product-level versionとmanaged-core provenanceを分離する

- Benefits: releaseとしての機能進化をversionへ反映しつつ、安全なmanaged core upgrade境界を維持できる。
- Costs / constraints: `kit_version`だけではoptional integrationの導入状態を判定できず、README / adoption guidance / changelogの確認が必要になる。
- Status: accepted

## Decision

- PDDR Kitのversionはproduct release全体を表す。
- root `VERSION`と`scripts/pddr.py`の`KIT_VERSION`は一致させる。
- stable releaseのversionとGit tag `vX.Y.Z`を対応させる。
- stable release間のmainは次release候補の`-dev` versionを使用する。
- v0.1.0後のdevelopment lineは、後方互換なcapability追加を反映して`0.2.0-dev`とし、v0.2.0 release時に`0.2.0`へ確定する。
- manifestの`kit_version`はmanaged coreを最後に導入・更新したsource versionのprovenanceとする。
- manifestのmanaged hashesをmanaged core実体の追跡に使用する。
- Skill、AGENTS guidance、validation / checkpoint CI等はproduct releaseのversioning対象だが、自動upgrade対象には含めない。
- 新しい利用能力を追加しない後方互換修正はpatch、後方互換なcapability追加はminorとする。optional integrationの追加もminorに含む。
- `0.x`期間のbreaking changeはminorを上げ、CHANGELOG / release noteでbreakingとmigrationを明示する。`1.0.0`以降はmajorを上げる。
- remote latest discoveryやoptional integration自動更新は今回の判断に含めない。

## Delivery and validation

version contractを`docs/versioning.md`へ明文化し、consumer向けadoption guidanceとcontributor向けrelease guidanceから参照する。

root `VERSION`とCLIの`KIT_VERSION`を`0.2.0-dev`へ更新する。既存unit testは両者の一致を検証しており、PR上のrepository validationで確認する。

version contractはPR #34でmainへmergeされ、merge commit `5beb746dfccac81d172fa4a431f644f6ce75ec76` を対象としたValidate PDDR Kit run `35854662290` が成功した。root `VERSION` とCLIの `KIT_VERSION` の一致を含むunit testとrepository validationが完了したため、deliveryを `validated` とする。

## Consequences

- product capabilityがmanaged core外で追加されても、release versionへ反映できる。
- mainから導入したconsumerはstable releaseとdevelopment sourceを区別できる。
- `kit_version`はoptional integrationの完全なinventoryではないため、その意味を誤解しないためのguidanceが必要になる。
- optional integrationは引き続きconsumerごとに明示的に導入・更新する。
- checkpoint CIのような後方互換なoptional capabilityはminor release対象として整理できる。
- remote update discoveryを急いで実装せず、まずversion semanticsを安定させられる。

## Revisit when

- optional integrationの導入状態をmachine-readableに追跡する必要が複数consumerで生じた場合。
- remote latest release discoveryをCLIへ追加する場合。
- manifest schemaを拡張する場合。
- PDDR Kitを1.0.0としてstable API contractへ移行する場合。
- package managerや署名付きdistributionを提供する場合。

## Evidence

- [Issue #33: version / upgrade運用の棚卸し](https://github.com/serevy/pddr-kit/issues/33)
- Maintainer approval of the product-level versioning contract, 2026-09-23 (private).
- `docs/versioning.md`
- `tests/test_pddr_cli.py`
- [PR #34: PDDR Kitのversion contractを定義](https://github.com/serevy/pddr-kit/pull/34)
- [main validation after PR #34](https://github.com/serevy/pddr-kit/actions/runs/35854662290)
- PDDR-0007: Safe upgrades for adopted projects
- PDDR-0008: Add milestone audits to complement opportunistic decision capture

## Related records

- PDDR-0007: Safe upgrades for adopted projects
- PDDR-0008: Add milestone audits to complement opportunistic decision capture
