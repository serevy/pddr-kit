# PDDR Kit

[English](README.en.md) | **日本語** | [简体中文](README.zh-CN.md) | [한국어](README.ko.md) | [Français](README.fr.md)

[![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/serevy/pddr-kit?utm_source=oss&utm_medium=github&utm_campaign=serevy%2Fpddr-kit&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)](https://coderabbit.ai)

**Project Design Decision Record** — プロジェクトの判断・背景・実装・検証をつなぐための軽量キットです。

PDDRは、最終的な決定だけでなく、観測や議論から提案が生まれ、採用・実装・検証を経て、必要に応じて見直されるまでの経緯を追跡できます。人とAIが「何を決めたか」だけでなく、「なぜ現在の形になったか」も引き継げるようにすることを目指します。

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

GitHub Actionsを利用するプロジェクトでは、Agent Skillが常時観測しない変更経路を補完する**optional checkpoint CI**も利用できます。high-signal changeに対して棚卸し用のmarkerを残すだけで、PDDRの作成を強制しません。セットアップは[`docs/adoption.md`](docs/adoption.md#optional-checkpoint-ci)を参照してください。

### AIツール連携とSkillの更新（v0.3.0）

PDDRをAIとの開発で利用する場合は、利用するツールが実際に読み込む規則ファイルへ運用ルールを接続してください。たとえばClaude Codeでは`CLAUDE.md`（設定・バージョンによっては`AGENTS.md`）、Codexでは`AGENTS.md`を利用できます。PDDR Kitはこれらのファイルを勝手に書き換えません。詳しくは[導入ガイド](docs/adoption.md)を参照してください。

v0.3.0では、明示的に登録した`pddr-recorder` Skillを、既存の管理ファイルとは別のmanifestで安全に追跡できます。以下は**新しいPDDR Kit側のディレクトリ**から実行する初回登録例です。

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md
```

以降は`--include-skill`のみ指定すれば同じ配置先を更新できます。独自変更したSkillは自動で上書きせず、競合として停止します。**このオプションはv0.3.0で追加されました。** 通常の`upgrade`は引き続きKit管理ファイルだけを更新します。

意思決定を記録するときは、既に確認できる人間の承認を再利用できます。事実誤認などは理由と差分を残して訂正でき、AIによる変更は人間に見える形で報告します。PRの自動マージやCI成功だけで新たな人間の承認があったとはみなしません。並行するPRでPDDR番号が衝突する場合は[採番ガイド](docs/concurrent-record-ids.md)を参照してください。

## 最小サンプル

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example)では、新規プロジェクトへ最初に`v0.1.0`を導入した履歴と、観測・選択肢・判断・成果物・検証Evidenceを結んだPDDRの完成例を確認できます。現在はmanaged coreを`v0.3.0`へ更新し、read-only signal workflowとtrusted marker writerへ分離したhardened optional checkpoint CIもdogfoodしています。

題材とEvidenceはすべて架空であり、構成と運用を理解するための最小リファレンスです。実験や実利用の記録とは分離しています。

## 現在の段階

現在の安定版は**v0.3.0**です。v0.2.1のleast-privilege checkpoint CIを維持しながら、AIツール別の規則配置、明示的なSkill更新、判断・訂正の透明性、並行PRの採番ガイドを追加しました。Skillの新しい評価ケースは定義検証済みですが、実モデルforward-testは別途必要です。

安定版の検証範囲は[`docs/releases/v0.3.0.md`](docs/releases/v0.3.0.md)、変更履歴は[`CHANGELOG.md`](CHANGELOG.md)を参照してください。

Jevなどの有償・外部サービスは任意の拡張です。分類・不足判定・関連PDDRのcontext selection・typed handoff連携を強化できますが、PDDRの基本運用には不要です。

## 参考文献・謝辞

本プロジェクトの着想と記録フローの検討にあたり、以下を参考にしています。

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

特に、成果物だけでなく判断の背景を残すこと、文脈が残っているうちにAIが下書きを作ること、人による確認と記録漏れの検査を組み合わせることを参考にしています。本プロジェクトは独立した取り組みであり、参考文献の著者・所属組織による公式提供、提携、承認を示すものではありません。

## Contributing

初期段階のため、まずはIssueでユースケースや課題を共有してください。変更提案は[`CONTRIBUTING.md`](CONTRIBUTING.md)を参照してください。

日本語のREADMEや導入ガイドの任意レビューには、[yomiyasuを用いた推敲手順](docs/japanese-prose-review.md)を利用できます。文章の修正はPRで差分を確認し、PDDRの判断やEvidenceの意味を変えないようにします。

## License

[MIT License](LICENSE)
