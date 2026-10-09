---
id: PDDR-0014
title: Optional hash-tracked Agent Skill upgrades
decision_date: 2026-10-09
recorded_date: 2026-10-09
decision_status: accepted
delivery_status: validated
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "https://github.com/serevy/pddr-kit/issues/51"
  - "https://github.com/serevy/pddr-kit/pull/58"
  - "https://github.com/serevy/pddr-kit/pull/60"
  - "https://github.com/serevy/pddr-kit/actions/runs/37894401566"
  - "https://github.com/serevy/pddr-kit/actions/runs/37894850729"
  - "tests/test_v030_integration.py"
  - "https://github.com/serevy/pddr-kit/blob/main/docs/records/PDDR-0007-safe-adoption-upgrades.md"
  - "https://github.com/serevy/pddr-kit/blob/main/docs/records/PDDR-0009-product-versioning.md"
  - "Maintainer approved optional non-destructive Skill update work, 2026-10-09 (private summary)"
  - "scripts/pddr.py"
  - "tests/test_pddr_cli.py"
related:
  - PDDR-0007
  - PDDR-0009
supersedes: []
superseded_by: null
---

# PDDR-0014: Optional hash-tracked Agent Skill upgrades

## Summary

PDDR Kit本体のmanaged coreと導入先が所有するoptional integrationの境界を維持しながら、利用者が明示的に登録した`pddr-recorder` Skillだけを、ハッシュ追跡と競合検出のもとで更新可能にする。

## Context and observations

- 現行`upgrade`は`.pddr/`の管理ファイルのみを更新し、Skillは製品版の対象であっても導入先へ自動反映しない。これはPDDR-0007とPDDR-0009で意図的に定義した境界だった。
- 外部導入時に、手動コピーしたSkillがKitの更新から取り残されることが具体的な運用課題として確認された。内部資料・導入先の固有情報は公開しない。
- 逆に、任意の場所へ配置されたSkillや利用者が編集したSkillを強制上書きすると、利用者の運用規則が失われる。
- `.pddr/manifest.json`の`kit_version`はmanaged coreの導入source provenanceであり、optional Skillの更新証明として扱うべきではない。

## Options considered

### Skillを引き続きすべて手動コピーする

- Benefits: 導入先の操作が明示的で、CLI実装は不要。
- Costs / constraints: 更新漏れや版の不整合を人手で調べ続ける必要がある。
- Status: rejected as the only supported method

### 全optional integrationを通常upgradeへ追加する

- Benefits: 一度に更新できる。
- Costs / constraints: consumer-ownedな規則・Skill・CIを予告なく書き換え得るため、既存の非破壊契約に反する。
- Status: rejected

### Skillのみ別manifestでオプトイン管理する

- Benefits: 明示的に導入したSkillを安全に追随させつつ、既存coreのmanifestや通常upgradeの意味を維持できる。
- Costs / constraints: 初回登録と既存の異なるSkillの移行には人のレビューが残る。通知なしの自動更新は行わない。
- Status: accepted

## Decision

Maintainerが2026-10-09に、実利用の要望に基づき以下の方針での対応を承認した。

- 通常の`upgrade`はmanaged coreのみ更新し、Skillはデフォルトで触らない。
- `upgrade --include-skill`で明示的に要求した場合だけ`pddr-recorder` Skillを対象にする。
- 初回は`--skill-path`で導入先相対パスを指定し、独立した`.pddr/skill-manifest.json`へ配置先、Kit source version、SHA-256を記録する。
- 未追跡ファイルが存在する場合、現行Skill sourceとバイト単位で同一の場合に限り登録し、そうでなければ差分をレビューするまで停止する。
- 以降は記録済みハッシュで利用側変更・欠落・パス変更を検知し、変更があればcore更新も含めて事前に停止する。不正パスとsymlinkも拒否する。
- Skillの更新を行う場合にも`--dry-run`で予定を確認できることとする。
- CI、Agent固有の規則、ほかのoptional integration、Skillの自律書換えはこの判断の対象外とする。

この判断はPDDR-0007の**既定の非破壊性**を置き換えず、明示的なオプションを追加するもの。

## Delivery and validation

PR #58でCLI、Skill manifest、競合時の事前停止、単体テスト、導入・versioningガイドをmainへ反映した。PR #60では一時consumerへ**実際にCLIをsubprocessで起動**し、`init` → Skill登録の`--dry-run` → 初回更新 → 保存先による再実行 → `validate --allow-empty`を通す統合テストを追加した。PR #58のmain CI（run 37894401566）とPR #60のmain CI（run 37894850729）で既存テスト・新テスト・PDDR検証が成功した。

これをもって、**Kitの指定したオプトイン更新経路**は`delivery_status: validated`とする。検証対象には、初回登録、クリーンな旧Skillからの更新、dry-run、保存済み配置先、利用側変更・削除・未追跡ファイル、危険なパス・symlink、不正manifest、および競合時のcore更新停止が含まれる。実際の第三者consumerの全設定や別OSの互換性を網羅した証拠ではない。複数ファイル間のディスク障害に対するトランザクション性も保証しない。

## Consequences

- Skillの更新漏れを、導入先の運用規則やcoreを無断上書きせずに減らせる。
- 既存の独自Skillには人による移行が必要であり、無条件に最新版へ置き換えられるわけではない。
- core manifestとSkill manifestは別々のversion provenanceを持つ。
- 安全なオプトイン更新は、Skillの自律改善や変更の自動承認を意味しない。

## Revisit when

- 別形式のSkill、複数Skill、登録済み配置先の移動をサポートする需要がある場合。
- consumer独自変更の安全な三方マージや、単一transactionとしての障害復旧が必要になった場合。
- Skillの配布元の検証方法や署名・パッケージング方針を変更する場合。
- 他のoptional integrationにも同等の更新ニーズが実運用で確認された場合。

## Evidence

- [Issue #51](https://github.com/serevy/pddr-kit/issues/51)
- [PDDR-0007](PDDR-0007-safe-adoption-upgrades.md)
- [PDDR-0009](PDDR-0009-product-versioning.md)
- Maintainer承認（2026-10-09、非公開の要約。会話全文は公開しない）
- `scripts/pddr.py`、`tests/test_pddr_cli.py`、`docs/adoption.md`、`docs/versioning.md`

## Related records

- PDDR-0007: Safe upgrades for adopted projects
- PDDR-0009: Product-level versioning and optional integration boundaries
