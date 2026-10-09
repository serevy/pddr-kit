# 日本語文書の推敲（任意・試験運用）

日本語のREADMEや導入・評価ガイドを読みやすくする際は、外部Agent Skill [yomiyasu](https://github.com/nanaism/yomiyasu) を任意で利用できます。**PDDR Kitの動作・検証・リリースに必須の依存ではありません。** 試験導入であり、全リポジトリ・全PRへの自動適用は行いません。

## 利用する版と既存運用との関係

- 参照する上流: `nanaism/yomiyasu` **v1.1.0**、commit `c2ffae670994fec96daef92e0bc219f5c1923113`（MIT License）。
- [security-twin-adapter-lab PR #8](https://github.com/serevy/security-twin-adapter-lab/pull/8) では、同じ版を個別の日本語レビューに利用しました。この運用を変更したり、他リポジトリへ設定を展開したりしません。
- [semantic-decision-lab PR #120](https://github.com/serevy/semantic-decision-lab/pull/120) はCodeRabbit設定のPRであり、yomiyasuの永続的な導入ではありません。CodeRabbitによるPRレビューとyomiyasuの文章推敲は別の役割として扱います。
- Kitでは`.github/workflows/yomiyasu-review.yml`を**手動実行（`workflow_dispatch`）専用**にします。`push`・`pull_request`・`workflow_run`では起動せず、required checkにもせず、PRコメントや文書へ自動で書き込みません。
- Workflowは上流commitを固定して読み取り専用でチェックアウトし、Python標準ライブラリだけで静的lintを実行します。Skill本文そのもののモデルによる推敲は、自動化されていません。

## 既存のyomiyasuがある場合（最初に確認）

**新規インストールより再利用を優先**します。別のリポジトリにyomiyasuが導入済みでも、それが現在のプロジェクトのAIで有効とは限りません。作業前に、インストール方式、適用範囲（プロジェクト/ユーザー/プラグイン）、実際に読み込まれる配置先、カスタマイズの有無を確認してください。

導入対象の**プロジェクトルート**で次の読み取り専用チェックを実行できます。既存ファイルの内容を変更せず、一般的なSkill配置先が存在するかだけを表示します。

```bash
python - <<'PY'
from pathlib import Path

locations = (
    ".agents/skills/yomiyasu/SKILL.md",
    ".claude/skills/yomiyasu/SKILL.md",
    ".codex/skills/yomiyasu/SKILL.md",
    ".cursor/skills/yomiyasu/SKILL.md",
    "skills/yomiyasu/SKILL.md",
)
found = False
for scope, root in (("project", Path.cwd()), ("user", Path.home())):
    for relative in locations:
        path = root / relative
        if path.exists() or path.is_symlink():
            kind = "symlink" if path.is_symlink() else "file or directory"
            print(f"{scope}: {path} ({kind})")
            found = True
if not found:
    print("Common directories: no yomiyasu found. Check plugins/custom paths manually.")
PY
```

このチェックは**全インストール先の検出を保証しません**。Claude Codeプラグインのインストール状況、エージェント固有のSkill一覧、上位ディレクトリの規則ファイルやカスタムパスも、それぞれのツールで確認してください。存在を確認しただけで、実際に読み込まれている、あるいはv1.1.0だと推定しません。symlinkは参照先を変更・削除せず、どこを指すかも必要に応じて人が確認します。

| 確認結果 | 推奨する対応 |
| --- | --- |
| 既に利用するAIがyomiyasuを読み込む | **その既存版を再利用**し、新規インストール・重複したルールの追記はしない |
| 版や由来が不明、古い版、独自に修正されている | **そのまま保持**。実際の版・差分・更新方法を確認し、明示承認なしに置換しない |
| 複数の配置先・プラグインが見つかった | 有効な読み込み先と優先順位を確認し、同名Skillの二重実行・競合する日本語規則を避ける。既存のものを無断で無効化しない |
| まだ必要な環境にない | はじめてインストールを検討する。ツールが提案する追加・変更・同期先を確認する |
| 上流v1.1.0と結果を再現して比較したい | 既存のSkillを変更せず、別checkoutの**固定版スクリプト**か下記の手動Workflowを利用する |

PDDR Kitの`pddr-recorder`は**判断・承認・Evidenceの解釈**を担当し、yomiyasuは**人間向け日本語の推敲**を担当します。複数Skillを使う際も、文章表現の改善を理由にPDDRの承認や提供状態を変えないでください。 PDDR Kit v0.3.0の`upgrade --include-skill`が追跡・更新できるのは**`pddr-recorder`のみ**で、既存のyomiyasuは管理・更新しません。

## 任意のSkill利用とCLI検査

上記の事前確認を行い、**必要なAI環境にyomiyasuが存在しない場合だけ**新規インストールを検討してください。上流が案内するインストールコマンドの例は次のとおりです。すでにSkillがある環境では実行せず、インストールツールが提示する追加・上書き・同期先（`.agents/skills/`、`.claude/skills/`、`AGENTS.md`など）を確認してください。プロジェクト全体へのインストールは必須ではありません。

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

手動Actions: [Japanese prose review (yomiyasu, optional)](https://github.com/serevy/pddr-kit/actions/workflows/yomiyasu-review.yml)。対象は `README.md`・`docs/adoption.md`・`docs/skill-evaluation.md` から選択します。WorkflowはSkillを導入先へインストールせず、上流の固定版を隔離した一時パスに取得してlintします。既に一時パスが存在する場合は**上書きせず失敗**します。既存のSkill候補がプロジェクト内にある場合は参考情報として表示し、そちらは変更・起動しません。ユーザーレベルやプラグインのSkillはWorkflowで自動検出しません。結果はJob LogとJob Summaryへ**助言**として出力され、ファイル・PR・Issueは変更しません。

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
