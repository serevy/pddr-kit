# PDDR Kitの導入

## 前提

- Python 3.10以降
- 導入対象のプロジェクトがローカルに存在すること

PDDR KitはMarkdownとPython標準ライブラリだけで動作します。特定のAI、SaaS、パッケージマネージャーは必要ありません。

## 初期化

PDDR Kitを取得したディレクトリで実行します。

```bash
python scripts/pddr.py init --target /path/to/your-project
```

記録先を変更する場合は、対象プロジェクト内の相対パスを指定します。

```bash
python scripts/pddr.py init \
  --target /path/to/your-project \
  --records-dir docs/decisions
```

変更予定だけを確認するには`--dry-run`を付けます。

初期化で追加されるファイルは次のとおりです。

```text
.pddr/
  config.json        記録先などの設定
  manifest.json      Kit管理ファイルの版とハッシュ
  pddr.py            導入先で使う検証CLI
  specification.md   導入時点の仕様
  template.md        導入時点のテンプレート
docs/records/
  README.md           記録ディレクトリの案内
```

既存ファイルと内容が異なる場合、初期化は処理開始前に停止し、何も変更しません。同じ内容で再実行した場合は成功します。

## プロジェクトの運用へ接続する

初期化は、既存プロジェクト固有の文書やCIを自動変更しません。配置後に次を確認します。

- READMEや開発ドキュメントから`docs/records/`へ辿れるようにする
- `AGENTS.md`などのAI・開発者向け規則に、PDDRを作成・更新する条件を記載する
- `decision_status`と`delivery_status`を分けて扱うよう明記する
- PRまたはmainへのpushで`python .pddr/pddr.py validate`を実行する
- 最初の記録を、根拠が追跡できる実際の判断から作成する

これらはプロジェクトごとに既存の構成や規則が異なるため、v0.1では確認項目として扱います。一律の追記や上書きは行いません。

## 作業記録と重要な判断を分ける

Issue、タスク、実験ログなど既存の作業管理を、すべてPDDRへ移す必要はありません。例えば次のように責務を分けます。

- Issue：仮説、作業計画、途中経過、生の結果、フォローアップ
- PDDR：結果を根拠に採用・不採用・保留した、将来も理由を参照すべき重要なProject / Product / Process判断

作業や実験の開始・変更・完了だけを理由にPDDRを作成しません。重要な判断が生じた場合は、PDDRから根拠となるIssueを参照し、Issue側からもPDDRへリンクします。詳細な時系列はIssueに残し、PDDRには判断に必要な要約とEvidenceだけを記録します。

## 記録を作る

```bash
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
```

テンプレートのID・タイトル・日付・状態を更新し、仕様に従って各セクションを記入します。PDDR番号は導入先リポジトリ内で一意にします。

## 検証する

```bash
python .pddr/pddr.py validate
```

検証器は次を確認します。

- ファイル名とIDの形式・一致
- 必須metadataと必須セクション
- 判断状態・提供状態・scopeの許可値
- 日付形式とID重複
- `superseded`と`superseded_by`の整合
- `validated`にEvidenceと検証内容があること
- `supersedes`と`superseded_by`が存在するPDDRを参照すること

文章の正しさ、判断の妥当性、Evidenceが主張を本当に裏付けるかは自動判定しません。これらは人のレビュー対象です。

記録がまだない導入直後だけ成功させたい場合は、次を使用できます。

```bash
python .pddr/pddr.py validate --allow-empty
```

## GitHub Actions

導入先に`.github/workflows/pddr.yml`を作成します。

```yaml
name: Validate PDDR

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: python .pddr/pddr.py validate --allow-empty
```

最初のPDDRを追加した後は、記録の消失を見逃さないよう`--allow-empty`を外すことを推奨します。

## 導入済みプロジェクトを更新する

PDDR Kitの新しい版を取得したディレクトリから、まず更新予定を確認します。

```bash
python scripts/pddr.py upgrade \
  --target /path/to/your-project \
  --dry-run
```

内容を確認した後、`--dry-run`を外して更新します。

```bash
python scripts/pddr.py upgrade --target /path/to/your-project
```

`upgrade`が更新するのは、`.pddr/manifest.json`でハッシュを追跡する次のKit管理ファイルだけです。

- `.pddr/pddr.py`
- `.pddr/specification.md`
- `.pddr/template.md`

`.pddr/config.json`、PDDR記録、導入先のREADME・AI向け規則・CIなどは更新しません。管理ファイルが導入後に編集されている、削除されている、または追跡外の同名ファイルがある場合は、すべての書き込み前に競合として停止します。

導入先の`.pddr/pddr.py`自身からは更新せず、新しいPDDR Kit側の`scripts/pddr.py`を使います。

### マニフェスト導入前のプロジェクト

古い導入先には`.pddr/manifest.json`がありません。まず三つのKit管理ファイルが、導入時のコピーから意図せず変更されていないことを人が確認します。その後、現在の内容を初期基準として記録します。

```bash
python scripts/pddr.py upgrade \
  --target /path/to/your-project \
  --bootstrap-manifest \
  --dry-run

python scripts/pddr.py upgrade \
  --target /path/to/your-project \
  --bootstrap-manifest
```

`--bootstrap-manifest`はマニフェストだけを作り、管理ファイルを更新しません。作成後に通常の`upgrade --dry-run`、`upgrade`を順に実行します。導入先で意図的に管理ファイルを変更している場合は、その変更を別ファイルへ移すか、新版との差分を手動で統合してください。
