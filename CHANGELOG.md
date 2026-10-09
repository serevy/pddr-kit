# Changelog

PDDR Kitの主な変更をこのファイルに記録します。

## [Unreleased]

## [0.3.0] - 2026-10-09

外部利用の具体的なフィードバックを反映したminor releaseです。承認の権限境界を維持しながら、運用の継続性・訂正の透明性・Skill更新の利便性を改善しました。

- AIツールが読み込む規則ファイルの違いを説明し、Claude Codeの`CLAUDE.md` / `AGENTS.md`やCodexの`AGENTS.md`向け導入例を追加しました（Issue #50 / PR #55）。
- 人間が既に明示した判断のEvidenceを再利用し、事実誤認の訂正は履歴と報告を残して行う原則を仕様とRecorder Skillへ反映しました。CIやBotの自動マージを人間の承認とはみなしません（Issue #52 / PR #56）。
- 並行PRによるPDDR採番衝突のガイドを追加し、別ブランチでは個別にvalidateが通っても統合時に重複が検出されるケースをテストで再現しました（Issue #53 / PR #57）。
- Agent Skillの明示的な更新と独立manifestによる追跡を導入し、既定のcore-only upgradeと導入先の独自変更を保護しました（Issue #51 / PR #58）。
- PDDR-0013とPDDR-0014へ承認された改善原則・Skill配布の判断を記録しました（PR #54 / #58）。
- READMEを日本語・英語・中国語・韓国語・フランス語で更新し、実際のCLI起動と各言語のコマンド整合性をテストしました（PR #59 / #60）。

- `upgrade --include-skill`を明示した場合に限り、任意の配置先へ導入した`pddr-recorder` Skillを独立manifestで追跡・更新できるようにしました。既存ファイルのハッシュが合わない場合はcore更新前に停止し、通常の`upgrade`は従来どおりcoreのみ更新します。

- CI導入ガイドに既存のread-only jobへPDDR検証を追加する方法を先に示し、独立サンプルへPR限定の旧実行取消しと5分上限を追加しました。
- optional checkpointのsignal / trusted marker templateに5分上限を設定しました。イベント検査、正確なbase/head比較、権限分離は維持し、consumerごとの明示的な採用・検証手順を追加しました。
- Kit自身のread-only validationにも5分上限とPR限定の旧実行取消しを適用しました。

- maintainer向けに、version metadata・release note・CHANGELOG・repository validation・既存tagをguardする手動dispatchのGitHub Release workflowを常設しました。
- v0.2.1後に開発版`0.3.0-dev`で追加機能を検証し、安定版`0.3.0`としてまとめました。

詳細な移行方法、検証の範囲と未検証事項は[`docs/releases/v0.3.0.md`](docs/releases/v0.3.0.md)を参照してください。

## [0.2.1] - 2026-09-24

v0.2.0のoptional checkpoint CIをleast-privilege構成へhardeningするpatch releaseです。

- PR headを観測する `PDDR checkpoint` workflowをread-only化しました。
- PR本文 / commentへのwriteをdefault branchのtrusted `workflow_run` writerへ分離しました。
- privileged writerはPR headのcode / artifactを実行せず、GitHub APIからPR metadata / changed filesを取得してtrusted detectorでsignalを再計算します。
- workflow security boundaryをunit testで固定しました。
- greenfield exampleでpending marker自動追記、completed回収、再実行時のmarker重複なしをE2E確認しました。

詳細な検証結果は[`docs/releases/v0.2.1.md`](docs/releases/v0.2.1.md)を参照してください。

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
