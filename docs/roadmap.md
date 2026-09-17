# Roadmap

ロードマップは方向性であり、記載項目の採用や実装完了を意味しません。

## v0.1 — Markdown first

- PDDR仕様とテンプレート
- PDDR Kit自身の記録によるdogfooding
- AIが安全に下書きを作るためのSkill
- 状態・必須項目・参照の最小検証

## v0.2 — Reusable adoption

- 既存プロジェクトへ非破壊で導入する方法
- 新規プロジェクト向け初期化
- 二つ以上の異なるプロジェクトで運用検証
- 実利用に基づくテンプレートとSkillの評価ケース

## Research track — optional integrations

以下は研究候補であり、初版の依存関係や採用決定ではありません。

- 会話からObservation / Proposal / Decision / Evidenceを分類する
- 状態や根拠の不足をスコア化・指摘する
- 現在のタスクに関連するPDDRだけをcontext selectionする
- PDDRを長期記録、typed handoffを短期のエージェント間プロトコルとして接続する
- Organization Policy → Project Decision → Task / Agent Handoff → Implementation → Test / Evidence → Review → Resultを追跡する
- Baselineと最適化構成を比較し、コスト、トークン、時間、強いモデルの利用率、初回受入率、手戻り、制約保持、人間のレビュー時間を測定する

Jevなどの有償サービスは、上記を強化する任意アダプターとしてのみ扱います。未契約・未接続でもPDDR Kitの基本機能とデータ可搬性を損なわないことを要件とします。研究・調査・PoC・比較実験はPDDR Kit本体から分離し、本体には有効性を確認した仕様だけを取り込みます。
