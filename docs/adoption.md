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

## 節目でPDDRを棚卸しする

個々の作業中にPDDR候補へ気づく運用だけでは、AI Skillを読み込まない経路や、複数Issueへ判断根拠が分散した場合に重要な判断を取りこぼすことがあります。導入先の`AGENTS.md`や開発者向け規則に、節目でrecent Issues / PRsを再点検するcheckpointを置くことを推奨します。

代表的なcheckpointは次です。

- 大きな実験・リリース・開発フェーズの境界
- Issueまたはroadmapの棚卸し
- Evidenceを持つ複数Issue / PRをまとめてclose・統合するタイミング

checkpointでは、対象期間のIssue、PR、既存PDDR、検証Evidenceを通常のPDDR thresholdで再評価します。将来も理由を参照すべきProject / Product / Process判断だけを作成・更新し、通常実装、途中観測、実験完了そのものは昇格させません。

**checkpointを実施したからといってPDDRを作る必要はありません。** durable decisionが見つからなければ「追加記録なし」が正常な結果です。

例えばAI・開発者向け規則には、次のようなプロジェクト固有ルールを追加できます。

```text
## PDDR checkpoints

At a major phase boundary, Issue/roadmap audit, or consolidation of
multiple Evidence-bearing Issues/PRs, review recent work against the
normal PDDR threshold.

Create or update a PDDR only for a durable Project, Product, or Process
decision. Do not create a PDDR merely because the checkpoint occurred.
```

PDDR Kitの`init`と`upgrade`は、引き続き導入先の`AGENTS.md`などを自動変更しません。既存規則との重複や上書きを避けるため、checkpointの追加は導入先ごとにレビューして接続します。


### Optional checkpoint CI

GitHub Actionsを利用するconsumerでは、Agent Skillが常時repoを観測していない作業経路を補完するため、optionalなcheckpoint CIを導入できます。これは**推奨オプション**であり、PDDR Kit利用の必須条件ではありません。

PDDR Kit checkoutから、detectorと2つのworkflow templateを明示的にコピーします。

```bash
mkdir -p /path/to/your-project/.pddr
mkdir -p /path/to/your-project/.github/workflows

cp scripts/pddr_checkpoint.py \
  /path/to/your-project/.pddr/pddr_checkpoint.py

cp templates/checkpoint-ci/pddr-checkpoint.yml \
  /path/to/your-project/.github/workflows/pddr-checkpoint.yml

cp templates/checkpoint-ci/pddr-checkpoint-marker.yml \
  /path/to/your-project/.github/workflows/pddr-checkpoint-marker.yml
```

このoptional integrationはmanaged coreの`upgrade`対象ではありません。導入先の既存CI・権限・branch運用を確認してから追加してください。

v1 detectorは、誤検知を抑えるため次のhigh-confidence signalだけを扱います。

- `AGENTS.md`の変更
- roadmap系surfaceの変更
- architecture系surfaceの変更
- PR label `pddr-checkpoint`
- PR本文の明示marker `[pddr-checkpoint]`

PR数やEvidence量だけを根拠に「PDDRが必要」と判定しません。

checkpoint CIは権限を分離した2段構成です。

- `PDDR checkpoint`: `pull_request`上でPR headを検査するread-only signal workflow。Check / Job Summaryへsignal結果を残します。
- `PDDR checkpoint marker`: signal workflow完了後の`workflow_run`で動くtrusted writer。default branch上のdetectorだけを実行し、PRの現在のchanged files / body / labelsからsignalを再計算してからmarkerを書き込みます。

write権限を持つmarker workflowはPR headのコードをcheckout・実行しません。PR側でsignal workflowやdetectorを変更しても、その変更コードがwrite-capable jobで実行されない境界を維持します。

checkpoint reviewを推奨するsignalがあり、PR本文に既存の`## PDDR checkpoint`がなければ、trusted marker workflowが次のpending markerをPR本文末尾へ追加します。

```md
## PDDR checkpoint

- Signal: recommended
- Review: pending
- Reason: <deterministic signal>

Checkpoint Signal ≠ PDDR required.
```

PR本文を更新できない場合はcheckpoint commentをfallbackとして使用します。repository policy等でtrusted marker workflowからもwriteできない場合は、read-only signal workflowのCheck / Job Summaryが最低限のtraceとして残ります。

後続Agent / maintainerがmarkerを回収したら、PR本文のcurrent stateを`Review: completed`へ更新します。過去のCheck Summaryはsignal発生時点の履歴なので同期更新しません。

PR headを観測するworkflowは通常の`pull_request` eventをread-onlyで使用し、PR本文への書き込みはdefault branchのtrusted `workflow_run`へ分離します。`pull_request_target`は使用しません。CIはPDDRの自動作成・自動承認を行いません。

初回導入PRでは、trusted marker workflowがまだdefault branchに存在しないため、signal workflowだけが動く場合があります。2つのworkflowがmainへ入った次のPRからmarker write pathが有効になります。

#### 実行上限・イベント・履歴の扱い

signalとmarkerのtemplateには、それぞれ5分のjob timeoutを設定しています。signalの既存PR単位concurrencyは維持し、状態を書き込むmarkerには新しい取消し設定を追加しません。

`opened / synchronize / reopened / edited / labeled`の対象イベントを維持します。titleだけの編集や無関係なlabelをjob-level `if`でskipすると、[GitHubがskipをSuccessとして報告する](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-jobs-with-conditions)ため、同じSHAの実検証失敗を新しいskipped-successで覆う可能性があります。また、workflow-level concurrencyで有用な実行を取り消した後にjobだけをskipすると、検証結果やSummaryを残せません。この互換性が解消されるまではイベントを省略せず、本文marker、base変更、label、通常のcode更新を従来どおり検査します。

`fetch-depth: 0`も維持します。現在のsignal workflowはbase/headの厳密なSHAで`git diff`するため、履歴を減らす場合は両commitの取得、forkやbase変更、取得失敗の扱いを別途検証します。単純にdepthを1へ変える修正は含めません。

[Issue #47](https://github.com/serevy/pddr-kit/issues/47)で、この既定値の採用とイベント・履歴最適化の検討結果を追跡します。

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

### 既存の軽量jobへ追加する

Python 3.10以降とcheckoutを既に用意しているread-onlyの検証jobがあれば、まずPDDR検証をstepとして追加できるか確認します。

```yaml
- name: Validate PDDR records
  run: python .pddr/pddr.py validate --allow-empty
```

既存のcheckoutとPython環境を再利用すると、PDDR検証のためだけのrunner起動を増やさずに済みます。PDDR検証は標準ライブラリだけで動くため、追加の依存インストールやcacheは不要です。

統合前に、既存jobのtrigger/path条件でPDDR関連の変更も検査されること、権限がread-onlyであること、失敗時の後続stepの扱いを確認します。PDDRの失敗はjobの失敗として伝え、`continue-on-error`で成功扱いにしません。既存jobのtimeoutは、そのjob全体のcold実行に必要な余裕から決めます。

既に独立したPDDR workflowを使っている場合は、workflow/job名を参照するrequired checkや他の処理を確認してから統合します。既存check名の削除・変更は明示的な移行として扱い、空の成功jobで代用しません。

### 独立workflowを使う

独立した検証結果が必要な場合や、既存jobとtrigger・権限・実行環境を共有できない場合は、`.github/workflows/pddr.yml`を作成します。

```yaml
name: Validate PDDR

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.event.pull_request.number || format('{0}-{1}', github.ref, github.run_id) }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.10"
      - run: python .pddr/pddr.py validate --allow-empty
```

この例ではworkflow名とPR番号で同一PRの旧実行を取り消します。non-PRはrefとrun IDを含む固有groupにして、別のmain実行が進行中・待機中のどちらでも置換しないようにしています。workflow名はrepository内で一意にし、default branch名が異なる場合は`main`を変更します。

5分は軽量なPDDR検証の異常長時間実行を止める上限です。通常jobの所要時間や、1回あたりの消費分数を示す値ではありません。追加のOS/matrixやcacheを導入する場合は、確認したい環境と実測効果を先に明らかにします。

最初のPDDRを追加した後は、記録の消失を見逃さないよう`--allow-empty`を外すことを推奨します。既存consumerへの適用では、現在のPython版、Action参照、`--allow-empty`の有無、検証コマンドを意図せず変更しないよう差分を確認します。

### Required checkと計測

required checkにするworkflowは、必要なPRで必ず結果が出る構成を保ちます。GitHubではworkflow全体がpath filter等で実行されないとcheckがPendingのままになるため、必須でないことを確認した検証だけにpath filteringを検討します。既存のworkflow/job/check名と参照元は、設定を変える前に確認してください。

ジョブを条件でskipした場合はSuccessとして報告されるため、必須検証の成功を空のjobや無条件のskipで代用しません。[GitHubのrequired-check仕様](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)も参照してください。

改善前後では、イベントごとのjob数と各jobの実行時間を記録し、workflow全体の経過時間とは分けて比較します。[GitHubはjobごとに分を切り上げる](https://docs.github.com/en/billing/reference/actions-runner-pricing)ため、短いjobの統合はrunner起動数と切り上げの重複を減らせます。実行時間の単発比較を月間使用量や請求額と同一視せず、publicの標準hosted runnerとprivateの使用量も分けて評価します。

### 導入先の作成ルールと更新記録

このページのCI設定は、`init` / `upgrade`では自動反映されません。各consumerでworkflow差分をレビューし、`AGENTS.md`等の既存ルールに次の確認事項を明示的に接続します。

- 新しいjobを増やす前に、既存のread-only検証へstepを追加できるか確認する。
- read-only検証jobの取消しは同一PRの旧実行に限定し、別PRや独立したmain/manual実行とはgroupを共有しない。状態を書き込むmarkerにはconcurrencyによる旧実行取消しを追加しない。
- cold実行に余裕を持つtimeoutを設定し、依存のない検証へcache用Actionを追加しない。
- required check、失敗の伝播、既存のpath条件と検証範囲を維持する。
- checkpointのread-only PR検証とtrusted default-branch writerを分離する。
- 通常CIのjob数・実行時間と、未検証の効果をPRに記録する。

公開consumerの更新対象を確認する例です。この一覧は適用完了を示すものではありません。

| Consumer | 確認するCI surface |
| --- | --- |
| [pddr-greenfield-example](https://github.com/serevy/pddr-greenfield-example) | validator、checkpoint、marker、ローカル作成ルール。最初の導入検証に使う |
| [agent-kpt](https://github.com/serevy/agent-kpt)、[office-hours](https://github.com/serevy/office-hours)、[tech-content](https://github.com/serevy/tech-content) | 独立PDDR validatorとローカル作成ルール |
| [semantic-decision-lab](https://github.com/serevy/semantic-decision-lab)、[readme-i18n-kit](https://github.com/serevy/readme-i18n-kit)、[ip-radar](https://github.com/serevy/ip-radar) | validator、checkpoint、marker、ローカル作成ルール |

source変更とconsumer採用を別々に追跡します。各導入PR / Issueには、次を記録してください。

| 記録項目 | 内容 |
| --- | --- |
| Source | 使用したKit tag / commit SHAと対象template |
| Consumer | 対象ファイル、既存の独自設定、PR / head SHA |
| Validation | 通常PR CI、signal/no-signal、trusted writerのコード由来、job数・実行時間 |
| Rollout | PR検証済みか、mergeとmain確認まで完了したか |
| Limits | markerが既存mainで動いた等、まだ確認していない範囲 |

まずgreenfield exampleでsignalあり・なしの両方を確認し、その後に他のconsumerへ必要な差分を個別PRで反映します。既に同じ上限や取消し範囲を持つconsumerには、重複した変更を加える必要はありません。非公開consumerの一覧・実行結果は、非公開の管理先で追跡します。

## Kit versionとmanifestの意味

PDDR Kitのversionは、managed filesだけでなくSkillやoptional integrationを含むproduct release全体を表します。

consumerの`.pddr/manifest.json`にある`kit_version`は、managed coreを最後に導入・更新したKit source versionのprovenanceです。`kit_version`が新しいからといって、Agent Skill、`AGENTS.md`の運用規則、validation CI、checkpoint CI等のoptional integrationまで導入済み・最新であることは保証しません。

stable releaseを利用する場合は対応する`vX.Y.Z` tag / Releaseを取得してください。`main`は開発版で、stable release間は`0.2.0-dev`のようなpre-release versionを使用します。

versionの詳細とpatch / minor / breakingの基準は[`docs/versioning.md`](versioning.md)を参照してください。

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
