# 日本語文書の推敲（任意・試験運用）

日本語のREADMEや導入・評価ガイドを読みやすくする際は、外部Agent Skill [yomiyasu](https://github.com/nanaism/yomiyasu) を任意で利用できます。**PDDR Kitの動作・検証・リリースに必須の依存ではありません。** 試験導入であり、全リポジトリ・全PRへの自動適用は行いません。

## 利用する版と既存運用との関係

- 参照する上流: `nanaism/yomiyasu` **v1.1.0**、commit `c2ffae670994fec96daef92e0bc219f5c1923113`（MIT License）。
- [security-twin-adapter-lab PR #8](https://github.com/serevy/security-twin-adapter-lab/pull/8) では、同じ版を個別の日本語レビューに利用しました。この運用を変更したり、他リポジトリへ設定を展開したりしません。
- [semantic-decision-lab PR #120](https://github.com/serevy/semantic-decision-lab/pull/120) はCodeRabbit設定のPRであり、yomiyasuの永続的な導入ではありません。CodeRabbitによるPRレビューとyomiyasuの文章推敲は別の役割として扱います。
- Kitでは`.github/workflows/yomiyasu-review.yml`を**手動実行（`workflow_dispatch`）専用**にします。`push`・`pull_request`・`workflow_run`では起動せず、required checkにもせず、PRコメントや文書へ自動で書き込みません。
- Workflowは上流commitを固定して読み取り専用でチェックアウトし、Python標準ライブラリだけで静的lintを実行します。Skill本文そのもののモデルによる推敲は、自動化されていません。

## 任意のSkill利用とCLI検査

上流が案内するAgent Skillの導入方法の一例は次のとおりです。**既存のSkillやAI向け規則ファイルを確認してから**利用し、ツールが既存の`.agents/skills/`や`.claude/skills/`を上書きしないか、提示される変更先を確かめてください。プロジェクト全体へインストールすることを必須とはしません。

```bash
npx skills add nanaism/yomiyasu
```

このコマンドは実行時の配布版を使うため、**v1.1.0を固定するコマンドではありません**。再現可能な比較が必要な場合は、別ディレクトリにタグ`v1.1.0`を取得し、取得先のcommitが上記SHAであることを確認してから付属スクリプトを実行します。GitHub Actionsの手動Workflowは既に上流commitを固定しています。

```bash
# 以下は v1.1.0 を別ディレクトリへ取得した場合の例
python /path/to/yomiyasu/skills/yomiyasu/scripts/yomiyasu_lint.py README.md
python /path/to/yomiyasu/skills/yomiyasu/scripts/yomiyasu_lint.py docs/adoption.md
python /path/to/yomiyasu/skills/yomiyasu/scripts/yomiyasu_diff.py /tmp/before.md /tmp/after.md --stance=説明
```

lintは表現やMarkdownの警告候補、diffは語・文末・構造の変化候補を示します。**警告ゼロ・スコア上昇は合格条件ではなく、意味の一致を証明しません。** 技術的な列挙や重要な否定は、自然な文章でも残ることがあります。

手動Actions: [Japanese prose review (yomiyasu, optional)](https://github.com/serevy/pddr-kit/actions/workflows/yomiyasu-review.yml)。対象は `README.md`・`docs/adoption.md`・`docs/skill-evaluation.md` から選択します。実行結果はJob LogとJob Summaryへ**助言**として出力され、ファイル・PR・Issueは変更しません。

## 推敲の対象と守る情報

対象は人が読む日本語の説明文のみです。原文の全文と差分を人が比較し、修正の理由をPRで報告します。

- **保持する**: 主張、判断の重要度、承認の有無、否定、条件、例外、義務・推奨の強さ、不確実性、時制、Scope、Evidenceの範囲。
- **書き換えない**: `decision_status` / `delivery_status` の値、PDDR ID、Issue・PR参照、数値・閾値、コード・CLI、front matter、JSON/YAML、評価fixture、スナップショット、ログ、既存のPDDR本文を丸ごと自動変更する処理。
- **承認と区別する**: 文書の推敲は新しい意思決定の承認ではありません。PRの自動マージも承認の代用品にはしません。
- **変更は見える形に**: AIが日本語を修正するときは、変更箇所・理由・証拠・差分をレビュアーに提示します。分からない意図を推測して確定しません。
- **安全性が必要な場面**: 身体的危険や不可逆の影響を伴う運用では、そのプロジェクトの承認済みPolicyと安全上のレビュー手順を優先します。yomiyasuは安全性の検証ツールではありません。

## 最初の試験範囲と確認方法

初回は `README.md`、`docs/adoption.md`、`docs/skill-evaluation.md` の小さな文章修正だけを対象とします。Before / After は導入PRの差分を正本とし、次を確認します。

1. README: PDDRの対象（決定だけでなくその前後）と**必要に応じた見直し**の条件が変わっていないか。
2. adoption: milestone checkpointを推奨する理由と、記録作成が義務ではないことが変わっていないか。
3. skill-evaluation: 記録・consumption・milestone・revisionの各ケースを混同せず、**評価定義の検証と実モデルforward-testを区別**できるか。
4. GitHubのdiffとCIを確認し、意味・ファイル識別子・リンク・評価結果への変更がないか点検します。

今回はPDDR本文や既存のCodeRabbit設定を変更しません。後日、利用効果と副作用が確認できて初めて、標準運用へ広げるかを判断します。
