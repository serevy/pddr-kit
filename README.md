# PDDR Kit

[English](README.en.md) | **日本語** | [简体中文](README.zh-CN.md) | [한국어](README.ko.md) | [Français](README.fr.md)

**Project Design Decision Record** — プロジェクトの判断・背景・実装・検証をつなぐための軽量キットです。

PDDRは、最終的な決定だけでなく、観測や議論から提案が生まれ、採用され、実装・検証され、必要なら見直されるまでの流れを追跡可能にします。人とAIが「何を決めたか」だけでなく「なぜ現在の形になったか」を引き継げることを目指します。

> PDDR (Project Design Decision Record) is a lightweight framework for preserving not only what a project decided, but how and why it evolved.

## PDDRが扱うもの

- **Project** — 目的、範囲、優先順位、公開方針など
- **Product** — 要件、ユーザー体験、機能、品質基準など
- **Process** — 開発手順、レビュー、AI活用、検証方法など

PDDRはADRやDDRを置き換えません。既存のDecision Recordを参照しながら、判断に至る前の観測と、判断後の実装・検証・見直しをつなぐレイヤーです。

## 重要な原則

1. **会話にない理由を補完しない。** 不明な経緯は`unknown`、未確認の判断は`needs-confirmation`として残します。
2. **AIの提案を人間の合意に変換しない。** 提案、採用、不採用、置換済みを区別します。
3. **決定と実装を分ける。** 採用済みでも、未実装・未検証の場合があります。
4. **古い記録を消さない。** 方針変更時は後継PDDRから旧記録を参照します。
5. **根拠を追跡可能にする。** 会話、Issue、PR、テスト結果などを参照します。
6. **記録を無条件のルールにしない。** PDDRは判断材料であり、適用範囲や状態を無視してPolicyとして実行しません。

## リポジトリ構成

| パス | 説明 |
| --- | --- |
| `docs/specification.md` | PDDRの共通仕様 |
| `docs/roadmap.md` | 初版と将来拡張の境界 |
| `docs/adoption.md` | 導入・検証・CIの手順 |
| `docs/skill-evaluation.md` | Skill評価の方法と現在状態 |
| `docs/records/` | このプロジェクト自身のPDDR |
| `evals/pddr-recorder/` | Skill評価ケース |
| `templates/pddr.md` | 新規PDDRテンプレート |
| `skills/pddr-recorder/` | AI向け記録Skill |
| `scripts/pddr.py` | 導入・更新・検証CLI |
| `tests/` | CLI・評価定義の自動テスト |

## 使い始める

Python 3.10以降を使用します。PDDR Kitを取得したディレクトリから、対象プロジェクトを指定して初期化します。

```bash
python scripts/pddr.py init --target /path/to/your-project
```

初期化は既存ファイルを上書きしません。対象プロジェクトには、設定・仕様・テンプレート・検証CLIと`docs/records/`が追加されます。

```bash
cd /path/to/your-project
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
python .pddr/pddr.py validate
```

判断に関係する事実と根拠を記入し、`decision_status`と`delivery_status`を別々に更新したうえで、PRで人が確認します。

導入済みプロジェクトは、PDDR Kitの新しい版を取得したディレクトリから、先に差分予定を確認して更新できます。

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project
```

更新するのはマニフェストで追跡されたKit管理ファイルだけです。導入先の記録・設定・独自ルールは変更しません。

詳しい導入方法とCI例は[`docs/adoption.md`](docs/adoption.md)、記録ルールは[`docs/specification.md`](docs/specification.md)を参照してください。初版ではMarkdownによる運用を正本とし、特定のAIやサービスを必須にしません。

## 最小サンプル

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example)では、新規プロジェクトへの`v0.1.0`導入結果と、観測・選択肢・判断・成果物・検証Evidenceを結んだPDDRの完成例を確認できます。

題材とEvidenceはすべて架空であり、構成と運用を理解するための最小リファレンスです。実験や実利用の記録とは分離しています。

## 現在の段階

現在の安定版は**v0.1.0**です。PDDR Kit自身でのdogfooding、二つの異なる既存プロジェクトへの導入・CI検証、既存導入先の安全な更新、新規プロジェクトへの初期導入、SolとLunaを使った記録作成および安全解釈の独立forward-testを経て公開しました。

安定版の検証範囲と既知の制約は[`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)、変更履歴は[`CHANGELOG.md`](CHANGELOG.md)を参照してください。

Jevなどの有償・外部サービスは任意の拡張です。分類・不足判定・関連PDDRのcontext selection・typed handoff連携を強化できますが、PDDRの基本運用には不要です。

## 参考文献・謝辞

本プロジェクトの着想と記録フローの検討にあたり、以下を参考にしています。

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

特に、成果物だけでなく判断の背景を残すこと、文脈が残っているうちにAIが下書きを作ること、人による確認と記録漏れの検査を組み合わせることを参考にしています。本プロジェクトは独立した取り組みであり、参考文献の著者・所属組織による公式提供、提携、承認を示すものではありません。

## Contributing

初期段階のため、まずはIssueでユースケースや課題を共有してください。変更提案は[`CONTRIBUTING.md`](CONTRIBUTING.md)を参照してください。

## License

[MIT License](LICENSE)
