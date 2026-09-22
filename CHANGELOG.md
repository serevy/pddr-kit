# Changelog

PDDR Kitの主な変更をこのファイルに記録します。

## [Unreleased]

- 導入先の大きなフェーズ境界、Issue / roadmap棚卸し、複数Evidence-bearing Issue / PRのclose時に、recent workをPDDR thresholdで再点検するmilestone audit guidanceを追加しました。
- checkpointは記録作成のquotaではなく、durable decisionがなければPDDRを追加しないことをSkillと導入ガイドへ明記しました。
- milestone auditのno-opとdurable decision昇格を評価するSkillケースを2件追加しました。

## [0.1.0] - 2026-09-18

最初の安定版です。リリース候補の機能に加え、二つ目の異なる既存プロジェクト、新規プロジェクト、既存導入先の安全な更新で導入経路を検証しました。Issueを実験・作業の記録、PDDRを重要な判断の記録とする責務境界も導入ガイドへ追加しています。

詳細な検証結果と既知の制約は[`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)を参照してください。

## [0.1.0-rc.1] - 2026-09-18

最初のリリース候補です。PDDRの仕様、テンプレート、AI向けSkill、導入・更新・検証CLI、CI、評価ケースと実モデル評価結果を含みます。

詳細な検証結果と既知の制約は[`docs/releases/v0.1.0-rc.1.md`](docs/releases/v0.1.0-rc.1.md)を参照してください。
