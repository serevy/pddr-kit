---
id: PDDR-0011
title: Protect main branch history with repository rules
decision_date: 2026-09-24
recorded_date: 2026-09-24
decision_status: accepted
delivery_status: validated
scope:
  - project
  - process
owners:
  - serevy
evidence:
  - "Maintainer approved protecting main with repository rules, 2026-09-24 (private)"
  - "https://github.com/serevy/pddr-kit/rules/23887444"
  - "https://github.com/serevy/pddr-kit/actions/runs/35879480089"
related:
  - PDDR-0009
supersedes: []
superseded_by: null
---

# PDDR-0011: Protect main branch history with repository rules

## Summary

PDDR Kit repositoryのdefault branch `main` をGitHub repository rulesetで保護し、履歴改変や誤操作からrelease / validationの信頼性を守る。

`main`への変更はPull Request経由とし、required status check `validate` の成功をmerge条件にする。force pushとbranch deletionを禁止し、linear historyを要求する。

## Context and observations

- PDDR-0009で、stable releaseは特定のmain commitへGit tag / GitHub Releaseを対応させるversion contractを採用した。
- v0.2.0ではrelease commitを明示してtag / GitHub Releaseを作成し、その後PDDR Kit repositoryへguarded release workflowを常設した。
- release automationがmain commitをrelease targetとして信頼する以上、mainの履歴を後からforce pushで書き換えられる状態はrelease provenanceと相性が悪い。
- repository settingsはGit commitだけでは追跡できず、後から「なぜこの保護があるのか」が分かりにくい。
- 2026-09-24にrepository ruleset `protect-main` を作成し、GitHub APIでactive状態と適用内容を確認した。
- rulesetはdefault branchを対象とし、bypass actorを持たない。

## Options considered

### mainを保護しない

- Description: repository ownerの裁量でdirect push / force push / deletionを許容する。
- Benefits: 緊急時を含め、最も自由に履歴を操作できる。
- Costs / constraints: release targetとなるmain履歴を誤操作で書き換えられ、tag / validation / PDDR Evidenceとの対応を損なえる。
- Status: rejected

### force pushと削除だけ禁止する

- Description: 履歴破壊操作だけを禁止し、direct pushは許可する。
- Benefits: 最低限の履歴保護をしつつ、個人開発の操作自由度を残せる。
- Costs / constraints: PR review surfaceとrequired validationを迂回した変更がmainへ入る余地が残る。
- Status: rejected

### PR + validation + immutable historyをrulesetで要求する

- Description: Pull Request経由、required status check、linear history、force push / deletion禁止をdefault branchへ適用する。
- Benefits: release provenanceとCI Evidenceを守りつつ、review approval数を0にすることで個人OSS運用を過度に重くしない。
- Costs / constraints: emergency direct pushもできず、required check障害時はmergeが止まる。repository settings変更にはGitHub側の管理操作が必要。
- Status: accepted

## Decision

- repository ruleset `protect-main` をdefault branchへactive適用する。
- branch deletionを禁止する。
- non-fast-forward update、すなわちforce pushを禁止する。
- mainへの変更はPull Request経由を必須とする。
- required approving review countは0とし、個人OSSで自己承認を必須化しない。
- required status checkとしてGitHub Actionsの `validate` を要求する。
- required status checkはstrict policyとし、merge前に最新mainとの整合を要求する。
- linear historyを要求する。
- bypass actorは設定しない。
- repositoryの通常merge方法は引き続きsquash mergeを標準運用とする。
- このrulesetはPDDR Kit productのconsumer-facing機能ではなく、PDDR Kit repository自身のProject / Process governanceとして扱う。

## Delivery and validation

2026-09-24にGitHub repository ruleset ID `23887444`、名称 `protect-main` を作成した。

GitHub APIで次を確認した。

- `enforcement: active`
- target: default branch
- deletion rule: enabled
- non-fast-forward rule: enabled
- Pull Request rule: enabled
- required approving review count: 0
- required status check: `validate`
- strict required status check policy: enabled
- required linear history: enabled
- bypass actors: none
- current user bypass: never

また、ruleset導入直前のmain commit `7a1e642fd6edfc73e3b362659754638f68a18fc2` に対するValidate PDDR Kit run `35879480089` が成功しており、required checkとして指定した `validate` がmainで正常動作することを確認した。

以上より、設定のactive適用とrequired checkの実在・成功を確認できたため、delivery statusを `validated` とする。

## Consequences

- mainの履歴をforce pushで書き換えたりbranch自体を削除したりできなくなる。
- mainへの変更はPRと `validate` 成功を通るため、release targetとvalidation Evidenceの対応を維持しやすくなる。
- review approval数は0のため、個人OSSで毎回自己承認する運用負荷は増えない。
- bypassを設定していないため、repository owner自身も通常経路を迂回できない。
- required checkの障害時はmainへのmergeも止まるため、CI障害とコード障害を切り分けて復旧する必要がある。
- GitHub repository settingsはGit history外の状態なので、ruleset変更時は本PDDRのDecision / Delivery / Evidenceも再評価する必要がある。
- このProject / Process判断をconsumer repositoryへ自動的に一般化しない。導入先ごとの権限、CI、運用事情に応じて別途判断する。

## Revisit when

- repository maintainerが複数人になり、required approval数やCODEOWNERSが必要になった場合。
- `validate` workflowの名称・job context・責務が変更された場合。
- merge queueや別のrequired checkを導入する場合。
- emergency bypassが必要な運用要件が実際に発生した場合。
- GitHub以外へrepository hostingを移行する場合。
- rulesetが通常の保守作業を過度に妨げるEvidenceが蓄積した場合。

## Evidence

- Maintainer approval to protect main with repository rules, 2026-09-24 (private).
- [GitHub ruleset: protect-main](https://github.com/serevy/pddr-kit/rules/23887444)
- Ruleset ID: `23887444`
- [Validate PDDR Kit on main before ruleset recording](https://github.com/serevy/pddr-kit/actions/runs/35879480089)
- PDDR-0009: Define product-level versioning and optional integration boundaries

## Related records

- PDDR-0009: Define product-level versioning and optional integration boundaries
