# PDDR Kit versioning

PDDR Kitのversionは、managed filesだけではなく、Skill、導入ガイダンス、optional integrationを含む **PDDR Kit product release全体** を表します。

## Version surface

### Product release version

repository rootの`VERSION`と`scripts/pddr.py`の`KIT_VERSION`は同じ値を持ちます。

stable releaseではSemVer形式のversionとGit tagを対応させます。

- `VERSION: 0.1.0` ↔ tag `v0.1.0`
- `VERSION: 0.2.0` ↔ tag `v0.2.0`

stable release間の`main`では、次のrelease候補を明示するpre-release versionを使用します。

例:

- stable: `0.1.0`
- development: `0.2.0-dev`
- next stable: `0.2.0`

これにより、未リリースの`main`からconsumerへ導入した場合に、stable releaseと誤認しないようにします。

## Consumer manifest

consumerの`.pddr/manifest.json`に記録される`kit_version`は、**managed coreを最後に導入または更新したPDDR Kit source versionのprovenance**です。

`kit_version`は、次を保証しません。

- Agent Skillが導入済みであること
- `AGENTS.md`等のproject guidanceが最新であること
- validation CI / checkpoint CI等のoptional integrationが導入済みであること
- consumer固有の運用surfaceがrelease時点の推奨状態と一致すること

managed coreの実体は、manifestの`managed_files` hashesで追跡します。

## Managed core and optional integrations

`upgrade`が自動更新するmanaged coreは、PDDR-0007で定義した次のファイルです。

- `.pddr/pddr.py`
- `.pddr/specification.md`
- `.pddr/template.md`

次はPDDR Kit releaseの一部としてversioning / changelog対象に含めますが、consumerへ自動上書きしません。

- Agent Skill
- `AGENTS.md`等へ接続する運用ガイダンス
- validation CI template
- checkpoint CI等のoptional integration
- examples / adoption guidance

optional integrationは、各consumerの既存構成と権限を尊重して明示的に導入・更新します。

## Version bump policy

### Patch

新しい利用能力を追加しない、後方互換な修正です。

例:

- bug fix
- typo / broken link修正
- 挙動を変えないmaintenance
- 既存契約の意味を変えない説明明確化

### Minor

後方互換なcapability追加です。managed core以外の追加機能も含みます。

例:

- 新しいCLI command / option
- Skill capabilityの追加
- 新しい推奨運用surface
- optional validation / checkpoint CI
- 新しいintegrationやadoption workflow

### Breaking changes

PDDR Kitが`0.x`の間は、breaking changeもminor versionを上げて扱えます。ただし、CHANGELOGとrelease noteでbreakingであることを明示し、migration guidanceを用意します。

`1.0.0`以降はSemVerに従いmajor versionを上げます。

## Release checklist

stable releaseを作るときは最低限、次を確認します。

1. 変更内容からpatch / minor / majorを決定する
2. `VERSION`と`KIT_VERSION`をrelease versionへ揃える
3. unit testでversion一致を確認する
4. `CHANGELOG.md`のUnreleasedをrelease sectionへ整理する
5. `docs/releases/vX.Y.Z.md`へ検証範囲と既知の制約を記録する
6. repository validationを成功させる
7. `vX.Y.Z` tag / GitHub Releaseを作成する

PDDR Kit repositoryでは、release metadataをmainへmergeした後、default branch上の恒久workflow `.github/workflows/release.yml` を手動dispatchしてtag / GitHub Releaseを公開します。

workflowでは次を再確認します。

- dispatch元がdefault branchであること
- 指定versionがroot `VERSION` と `scripts/pddr.py` の `KIT_VERSION` に一致すること
- release kind（stable / prerelease）とversion表記が整合すること
- `docs/releases/vX.Y.Z.md` とCHANGELOG release sectionが存在すること
- repository unit tests / Skill eval validation / PDDR validationが成功すること
- 同名tag / GitHub Releaseがまだ存在しないこと

条件を満たした場合だけ、workflow実行時のmain commitをtargetとしてGit tagとGitHub Releaseを作成します。release publication自体は自動push連動にせず、人がversionとrelease kindを確認して明示的に開始します。

release後に次の開発を始める場合は、最初のunreleased changeの分類に応じて次の`-dev` versionへ進めます。

## Deferred

現段階では、remote latest releaseを問い合わせる`pddr upgrade --check`や、optional integrationの自動更新は導入しません。

consumerが最新版を自動発見する仕組みは、このversion contractと複数consumerの運用実績を踏まえて別途検討します。
