---
id: PDDR-0003
title: First external adoption findings
decision_date: 2026-09-17
recorded_date: 2026-09-17
decision_status: accepted
delivery_status: validated
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "Maintainer-approved adoption into a separate existing project, 2026-09-17 (private)"
  - "PDDR validation CI and the adopter project's existing CI succeeded"
related:
  - PDDR-0001
  - PDDR-0002
supersedes: []
superseded_by: null
---

# PDDR-0003: First external adoption findings

## Summary

最初の既存プロジェクト導入により、非破壊なファイル配置と自動検証だけでなく、READMEの導線、AI・開発者向け規則、CIへの接続がPDDRを実運用へ組み込むために必要だと確認した。

## Context and observations

- PDDR Kitとは別の、既存CIと固有の開発規則を持つプロジェクトへ初めて導入した。
- `init`は既存ファイルを変更せず、共通の設定・仕様・テンプレート・CLI・記録ディレクトリを配置できた。
- 過去の判断を、根拠が確認できる事実とEvidenceだけからPDDRとして再構成できた。
- 導入ファイルを配置しただけでは、READMEやAI向け指示からPDDRへ到達できず、日常の変更フローにも検証が接続されない。
- 導入先の規則やCI構成はプロジェクト固有であり、共通CLIが一律に書き換えるべきではない。

## Options considered

### 共通ファイルの配置だけを導入完了とする

- Benefits: 変更量が最小で、どのリポジトリにも同じ処理を適用できる。
- Costs / constraints: 開発者やAIがPDDRを発見・更新せず、CIでも記録漏れを検出できない可能性がある。
- Status: rejected

### README・開発規則・CIも一律に自動変更する

- Benefits: 一回のコマンドで運用まで接続できる。
- Costs / constraints: 既存の文書構造、AI向け指示、CI方針を誤って上書きまたは重複させる可能性がある。
- Status: rejected for v0.1

### 共通ファイルは非破壊で配置し、プロジェクト固有の接続は確認項目として案内する

- Benefits: 可搬性と既存プロジェクトの規則を両立できる。
- Costs / constraints: 導入時に人またはAIがプロジェクト固有の編集を行う必要がある。
- Status: accepted

## Decision

- `init`の非破壊な共通ファイル配置は維持する。
- 導入手順に、READMEなどからの導線、AI・開発者向け規則、CI接続の確認項目を追加する。
- プロジェクト固有ファイルはv0.1の`init`で自動変更しない。
- 非公開プロジェクトの名称、URL、内部判断は、公開PDDR Kitへ転記しない。検証結果は必要最小限に要約する。

## Delivery and validation

既存のWindows-first C++/QtプロジェクトへPDDR Kitを導入した。共通仕様を変更せず最初のPDDRを作成でき、導入先のPDDR検証CIと既存のビルド・テストCIがともに成功した。メンテナーによるPR確認とマージも完了した。

得られた導入チェック項目を`docs/adoption.md`とREADMEの現在段階へ反映した。

## Consequences

- 初期化は引き続き安全で予測可能な範囲に限定される。
- 導入者は、配置後にプロジェクト固有の運用接続を行う必要がある。
- 将来、複数プロジェクトで同じ接続パターンが確認できれば、安全な自動化候補を識別できる。
- 公開キットから非公開プロジェクトの機密情報を辿れない状態を維持する。

## Revisit when

- 二つ以上の導入先で同一のREADME・AI指示・CI変更が必要になった場合。
- 手動の運用接続が導入漏れや誤設定の主要因になった場合。
- `init`が既存ファイルを安全に解析・提案できる方式を設計できた場合。

## Evidence

- 2026-09-17、別の既存プロジェクトへの導入PRをメンテナーが確認し、マージした。
- 導入先でPDDR検証CIが成功した。
- 導入先の既存ビルド・テストCIも変更後に成功した。
- 非公開プロジェクトのURLと内部情報は公開記録へ含めない。

## Related records

- PDDR-0001: Why PDDR Kit exists
- PDDR-0002: Portable initialization and validation
