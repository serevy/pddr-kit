# Changelog

PDDR Kitの主な変更をこのファイルに記録します。

## [Unreleased]

- maintainer向けに、version metadata・release note・CHANGELOG・repository validation・既存tagをguardする手動dispatchのGitHub Release workflowを常設しました。
- v0.2.0後の最初のminor capabilityとしてmainのdevelopment versionを`0.3.0-dev`へ進めました。

## [0.2.0] - 2026-09-23

v0.1.0のportableなmanaged coreを維持しながら、PDDR候補の取りこぼしを節目で再点検するmilestone auditと、その実行漏れを補完するoptional checkpoint CIを追加したminor releaseです。product release全体とconsumer managed coreのprovenanceを分けるversion contractも明文化しました。

- Agent Skillが常時観測しない変更経路を補完するoptional checkpoint CI、deterministic signal detector、PR checkpoint marker運用を追加しました。
- greenfield exampleでhigh-signal changeのpending marker自動追記、bounded auditによる既存PDDR更新、completed state再実行時の重複防止、routine UI changeのno-signalをdogfoodしました。
- PDDR Kitのversionをproduct release全体のversionとして定義し、managed coreのprovenanceとoptional integrationの導入状態を分離しました。
- patch / minor / pre-1.0 breaking changeの基準とrelease checklistを`docs/versioning.md`へ追加しました。
- 多言語READMEのリポジトリ構成説明が日本語のまま残らないよう、翻訳対象外のfenced code blockから翻訳可能なMarkdown表へ変更しました。
- 導入先の大きなフェーズ境界、Issue / roadmap棚卸し、複数Evidence-bearing Issue / PRのclose時に、recent workをPDDR thresholdで再点検するmilestone audit guidanceを追加しました。
- checkpointは記録作成のquotaではなく、durable decisionがなければPDDRを追加しないことをSkillと導入ガイドへ明記しました。
- milestone auditのno-opとdurable decision昇格を評価するSkillケースを2件追加しました。

詳細な検証結果と既知の制約は[`docs/releases/v0.2.0.md`](docs/releases/v0.2.0.md)を参照してください。

## [0.1.0] - 2026-09-18

最初の安定版です。リリース候補の機能に加え、二つ目の異なる既存プロジェクト、新規プロジェクト、既存導入先の安全な更新で導入経路を検証しました。Issueを実験・作業の記録、PDDRを重要な判断の記録とする責務境界も導入ガイドへ追加しています。

詳細な検証結果と既知の制約は[`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)を参照してください。

## [0.1.0-rc.1] - 2026-09-18

最初のリリース候補です。PDDRの仕様、テンプレート、AI向けSkill、導入・更新・検証CLI、CI、評価ケースと実モデル評価結果を含みます。

詳細な検証結果と既知の制約は[`docs/releases/v0.1.0-rc.1.md`](docs/releases/v0.1.0-rc.1.md)を参照してください。
