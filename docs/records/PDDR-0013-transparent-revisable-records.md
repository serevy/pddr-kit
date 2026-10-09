---
id: PDDR-0013
title: Keep decision records revisable, visible and authority-safe
decision_date: 2026-10-09
recorded_date: 2026-10-09
decision_status: accepted
delivery_status: not-started
scope:
  - product
  - process
owners:
  - serevy
evidence:
  - "https://github.com/serevy/pddr-kit/issues/52"
  - "https://github.com/serevy/pddr-kit/issues/50"
  - "https://github.com/serevy/pddr-kit/issues/51"
  - "https://github.com/serevy/pddr-kit/issues/53"
  - "Maintainer explicitly endorsed the principles and requested that the decision be recorded, 2026-10-09 (private summary; no conversation transcript published)"
  - "docs/specification.md"
  - "skills/pddr-recorder/SKILL.md"
related:
  - PDDR-0003
  - PDDR-0006
  - PDDR-0007
  - PDDR-0008
  - PDDR-0009
supersedes: []
superseded_by: null
---

# PDDR-0013: Keep decision records revisable, visible and authority-safe

## Summary

PDDRの判断承認は厳密に保ちつつ、記録の作成・事実誤認の訂正は必要以上に重くしない。既に確認できる人間の合意は重ねて確認せず再利用し、AIや仕組みによる記録の変更は差分・理由・通知または作業報告から人間が把握できるようにする。

**記録しなくなること**と、**人間に知らせず記録が書き換わること**の両方を避ける。PDDRを軽量な作業ログへ変える判断ではない。

## Context and observations

- Kitの外部導入から、AI向け規則の配置、任意Skillの更新、PRベースの承認運用、並行PRでの採番について具体的な改善要望が寄せられた。個別課題はIssue #50〜#53で追跡する。
- 会話内で意思決定を明示した後、PDDRへの転記確認、PRレビュー、マージ後の`proposed`→`accepted`修正PRを繰り返すと、同じ判断の確認が重複し、記録作業を先送りする動機になる。
- 一方、PDDRはAIも判断材料として読むため、AIによる曖昧な合意の捏造や、気付かないうちの記録書換えは実装判断への影響を生む。
- PDDRの正本はGit管理されたMarkdownであり、誤字・誤解釈・事実誤認を訂正可能である。訂正の経緯を残すことと、過去の意思決定を消すことは同義ではない。
- 既存のConsumption Contractは`proposed`や`needs-confirmation`を承認済みの判断として扱わず、古い判断を無条件のPolicyへ昇格しない。

## Options considered

### 記録の作成・訂正と判断の承認を毎回同じ手順で求める

- Benefits: 人間の明示レビューを多く挟める。
- Costs / constraints: 同じ判断の確認や状態変更だけの追加PRが重なり、重要な経緯が記録されずに終わるリスクが高まる。
- Status: not selected as the universal default

### AIが通知なしで記録を修正・承認する

- Benefits: 目先の操作回数は減る。
- Costs / constraints: 誤った合意の確定や静かな履歴改変を発見しづらく、AIが後続判断に利用する文脈の信頼性を下げる。
- Status: rejected

### 承認権限・記録訂正・変更可視性を分離する

- Benefits: 重要な判断の権限境界を維持しながら、記録の継続と訂正のしやすさを両立できる。
- Costs / constraints: 合意のEvidence、訂正と方針変更の区別、通知・レビュー経路を導入先の運用に合わせて定義する必要がある。
- Status: accepted

## Decision

Maintainerは2026-10-09に、以下をPDDR Kitの運用改善の基本方針として採用し、この判断を記録するよう明示した。

1. **記録の継続を重視する。** PDDRの対象を通常の実装ログへ広げるのではなく、将来参照すべき重要なProject / Product / Process判断の取りこぼしを減らす。
2. **判断の承認と記録の編集を分ける。** 人間の明示的な判断が根拠として確認できれば、同じ判断をPDDRへの転記時に改めて承認させる必要はない。曖昧な発言・AIの提案から承認を推測しない。
3. **記録の訂正を許容する。** 誤字、事実誤認、意図の取り違えは既存Markdownを修正できる。変更理由と根拠、旧記述への追跡可能性を残す。斜線や訂正履歴は使えるが、現在有効な本文と訂正された過去の記述は区別する。
4. **実際の意思決定の変更は別扱いにする。** 承認済み判断そのものの変更や適用範囲の拡大を単なる訂正として扱わない。必要な権限を確認し、既存のsupersession contractに従って経緯を残す。
5. **AI・自動処理による無通知の書換えを避ける。** 変更した場合は少なくとも変更内容、理由、根拠、差分を追跡可能にし、人間が認知できる通知または作業報告の経路へ接続する。毎回の事前承認を一律に要求する意味ではない。
6. **自動マージは人間の合意の代用品ではない。** PRのマージ、CI成功、エージェントによる自己申告だけで`decision_status: accepted`へ昇格させない。承認を確認できなければ`proposed`または`needs-confirmation`を維持する。事前委任の可否や証拠の形式は別途設計する。
7. **誤記録の影響を追えるようにする。** 既にAIや実装作業で参照されたPDDRを訂正した場合、必要に応じてその下流への影響を確認する。`decision_status`と`delivery_status`の区別を維持する。

このPDDRは運用改善の**原則**を採用するものであり、具体的な通知手段、承認証拠の形式、Skill実装・CI構成を承認したものではない。設計と実装はIssue #52等で別途レビューする。

## Delivery and validation

判断原則を本記録とIssue #52へ整理した段階。`docs/specification.md`、`docs/adoption.md`、`skills/pddr-recorder/SKILL.md`の仕様・手順・評価ケースへの反映は未着手であるため`delivery_status: not-started`とする。本記録をPRとしてレビューに出すことと、機能変更・運用検証の完了は区別する。

Issue #50、#51、#53はそれぞれAIツールへの導入、Agent Skill配布更新、並行PRでの採番に関する改善候補であり、本記録から具体的な解決手段まで自動採用されたとはみなさない。

## Consequences

- 明示済みの人間判断をEvidenceに基づいて転記でき、同じ判断の重複承認を減らせる。
- 訂正履歴と現在有効な記録を分けることで、AIが古い文面を現行方針と誤認するリスクを抑える。
- 小さな訂正にも変更の可視性は必要だが、独立した新規PDDRや専用の追加PRを毎回要求しない。
- 認証や秘密情報、非公開の会話全文を公開記録へ転載しない。
- PDDR自身を実行可能なPolicyにはしない。承認済みPolicyとの優先順位はPDDR-0006のまま。
- 通知がどの程度確実に届くか、証拠の取り回し、代理承認の境界については追加の設計・検証が必要となる。

## Revisit when

- 明示的な意思決定の転記でも重複確認が実際に残る場合。
- 人間が変更に気付かない、理由を追跡できないなどの事例が生じた場合。
- 事実訂正を装って承認済み判断や`scope`が変更される危険が確認された場合。
- auto-mergeや複数Agentの運用において、人間の承認証拠を安全に追跡する仕組みが検証された場合。
- PDDRに基づくAIの判断・実装へ誤記録の影響が波及した場合。

## Evidence

- [Issue #52: duplicate confirmations and transparent corrections](https://github.com/serevy/pddr-kit/issues/52)
- [Issue #50: instruction file integration](https://github.com/serevy/pddr-kit/issues/50)
- [Issue #51: optional Skill upgrade](https://github.com/serevy/pddr-kit/issues/51)
- [Issue #53: concurrent ID collisions](https://github.com/serevy/pddr-kit/issues/53)
- Maintainerの2026-10-09の原則承認と記録依頼（非公開の要約。会話全文や利用者の内部情報は公開しない）。
- 現行仕様の`docs/specification.md`、`skills/pddr-recorder/SKILL.md`、`docs/adoption.md`。

## Related records

- PDDR-0003: First external adoption findings
- PDDR-0006: Safe context consumption and policy separation
- PDDR-0007: Safe adoption upgrades
- PDDR-0008: Milestone audits complement in-task recording
- PDDR-0009: Product-level versioning and optional integration boundaries
