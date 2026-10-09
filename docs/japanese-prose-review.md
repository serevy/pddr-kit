# 日本語文書の推敲（任意・試験運用）

日本語のREADMEや導入・評価ガイドを読みやすくする際は、外部Agent Skill [yomiyasu](https://github.com/nanaism/yomiyasu) を任意で利用できます。**PDDR Kitの動作・検証・リリースに必須の依存ではありません。** 試験導入であり、全リポジトリ・全PRへの自動適用は行いません。

## 利用する版と既存運用との関係

- 参照する上流: `nanaism/yomiyasu` **v1.1.0**、commit `c2ffae670994fec96daef92e0bc219f5c1923113`（MIT License）。
- [security-twin-adapter-lab PR #8](https://github.com/serevy/security-twin-adapter-lab/pull/8) では、同じ版を個別の日本語レビューに利用しました。この運用を変更したり、他リポジトリへ設定を展開したりしません。
- [semantic-decision-lab PR #120](https://github.com/serevy/semantic-decision-lab/pull/120) はCodeRabbit設定のPRであり、yomiyasuの永続的な導入ではありません。CodeRabbitによるPRレビューとyomiyasuの文章推敲は別の役割として扱います。
- Kitでは`.github/workflows/yomiyasu-review.yml`を**手動実行（`workflow_dispatch`）専用**にします。`push`・`pull_request`・`workflow_run`では起動せず、required checkにもせず、PRコメントや文書へ自動で書き込みません。
- Workflowは上流commitを固定して読み取り専用でチェックアウトし、Python標準ライブラリだけで静的lintを実行します。Skill本文そのもののモデルによる推敲は、自動化されていません。

## 既存の日本語Skillがある場合（最初に確認）

**新規インストールより既存の運用を優先**します。確認対象は同名のyomiyasuだけではありません。たとえば`natural-japanese`や`japanese-tech-writing`など、別名でも日本語文章の校正・推敲を担当するSkillがあり得ます。名称だけで互換性や競合を断定しないでください。

最初に次の3つを区別します。

1. **存在**：プロジェクト、ユーザー共通のSkill、プラグイン、独自ディレクトリやエージェント規則に設定があるか。
2. **有効性**：いま利用するエージェントが、どの階層のどのSkill/ルールを実際に読み込むか。
3. **役割の重なり**：日本語を直接**書き換える**Skillなのか、翻訳・用語検査・静的lintなどの補助なのか。競合するのは主に同じ文章への異なる推敲指示です。

導入先のプロジェクトを対象に、PDDR Kit側から次の**読み取り専用・任意**の候補確認ができます。`--include-user`を付けると実行者のホームディレクトリにある通常のSkill配置先も確認します（結果はローカル端末に表示され、どのSkillも実行・変更しません）。

```bash
python /path/to/pddr-kit/scripts/report_japanese_skill_candidates.py --target /path/to/your-project
# 必要な場合だけユーザー領域も確認する
python /path/to/pddr-kit/scripts/report_japanese_skill_candidates.py --target /path/to/your-project --include-user
```

このチェックは`.agents/skills/`、`.claude/skills/`、`.codex/skills/`、`.cursor/skills/`、`skills/`直下にあるSkillの**名前とfront matterの一部**を限定的に調べ、日本語推敲と用途が重なる**可能性がある候補**を報告します。Skill本文を実行・解釈しません。symlink先は追跡せず、読み取り範囲を制限します。

候補が見つからなくても、**ほかの日本語Skillがないとは証明できません**。プラグイン管理、独自パス、祖先ディレクトリの`AGENTS.md` / `CLAUDE.md`、CodeRabbitの指示、Skills以外の日本語スタイル規則は対象外です。ツール自身が表示する読み込み済みSkillと既存ルールを最終的に確認してください。候補検出だけでインストール済みの版や優先順位、競合の有無を推定しません。

| 確認できた状況 | 対応 |
| --- | --- |
| 同名yomiyasuが有効 | 既存版・カスタマイズを**そのまま再利用**。新規インストールや無断アップグレードをしない |
| 別名の日本語推敲Skillが有効 | **既存Skillを優先**。同じ文章にyomiyasuの書換え指示を並行適用しない。乗り換える場合は、使用者が明示的に対象の作業・有効化方法を選ぶ |
| 翻訳・用語検査など役割が異なる | 明示的に役割と実行順を決められる場合に限り併用可能。独立lintも助言として併用できるが、意味保持を検証したことにはならない |
| 別名のSkillが複数、または内容・優先順位が不明 | **保留して人が判断**。勝手に削除・無効化・入替え・設定ファイルの書換えをしない |
| 該当する日本語推敲Skillが確認できず、利用者が採用を選択 | 追加先と差分を確認してからyomiyasuを任意導入 |
| 固定版の機械的lintだけを比較したい | 現存するSkillとは独立に、下記のread-only Workflowまたは隔離したv1.1.0 checkoutから実行 |

**優先順位**：既存のProject / Organization Policy、人間の承認・指示、PDDRの権限・Evidence・Scopeは、どの文章推敲Skillよりも優先します。文章の自然さを理由に、否定・条件・義務・承認状態などを書き換えることはできません。
PDDR Kitの`pddr-recorder`は**判断・承認・Evidenceの解釈**を担当し、yomiyasuは**人間向け日本語の推敲**を担当します。複数Skillを使う際も、文章表現の改善を理由にPDDRの承認や提供状態を変えないでください。 PDDR Kit v0.3.0の`upgrade --include-skill`が追跡・更新できるのは**`pddr-recorder`のみ**で、既存のyomiyasuは管理・更新しません。

## 任意のSkill利用とCLI検査

上記の事前確認で**yomiyasuに限らず、用途の重なる日本語推敲Skillが有効でないこと**を確かめ、利用者が明示的に選んだ場合だけ新規インストールを検討してください。上流が案内するインストールコマンドの例は次のとおりです。すでにSkillがある環境では実行せず、インストールツールが提示する追加・上書き・同期先（`.agents/skills/`、`.claude/skills/`、`AGENTS.md`など）を確認してください。プロジェクト全体へのインストールは必須ではありません。

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

手動Actions: [Japanese prose review (yomiyasu, optional)](https://github.com/serevy/pddr-kit/actions/workflows/yomiyasu-review.yml)。対象は `README.md`・`docs/adoption.md`・`docs/skill-evaluation.md` から選択します。WorkflowはSkillを導入先へインストールせず、上流の固定版を隔離した一時パスに取得してlintします。既に一時パスが存在する場合は**上書きせず失敗**します。プロジェクト内の一般的なSkill配置先を限定的に確認し、**同名yomiyasuと別名の日本語推敲Skillの候補**をJob Logに表示します。候補の有無は実際の有効化や衝突を証明せず、どのSkillも変更・起動しません。ユーザーレベルやプラグイン、独自の日本語規則はWorkflowでは検出しません。結果はJob LogとJob Summaryへ**助言**として出力され、ファイル・PR・Issueは変更しません。

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
