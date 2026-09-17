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

## 更新方針

現在の初期化処理は非破壊性を優先し、導入済みファイルを自動更新しません。PDDR Kit更新時の差分確認・移行方法は今後の導入検証を踏まえて設計します。
