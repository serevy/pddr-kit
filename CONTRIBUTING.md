# Contributing to PDDR Kit

PDDR Kit is in an early design-validation stage. Issues describing real use cases, failure modes, and confusing distinctions are especially useful.

## Before proposing a change

- Check whether the proposal belongs in the common kit or in one project's local records.
- State the problem and an observable example before prescribing a format change.
- Keep Markdown as the portable source of truth unless a change explicitly revises that decision.
- Do not include private conversations, credentials, personal information, or proprietary project details.

## Pull requests

- Keep changes focused and explain whether they affect the specification, template, Skill, or tooling.
- When behavior changes, add or update a PDDR in `docs/records/`.
- Do not mark a proposal as accepted or validated without evidence.
- By contributing, you agree that your contribution is licensed under the repository's MIT License.

## Protected main branch

The default branch `main` is protected by a repository ruleset.

- Changes to `main` must go through a pull request.
- The required `validate` status check must pass before merge.
- Force pushes and branch deletion are blocked.
- Linear history is required.
- Approving reviews are currently not required for this single-maintainer repository.

Use focused branches and the normal pull-request workflow instead of pushing directly to `main`.

## Versioning and releases

PDDR Kitのversionはproduct release全体を表します。変更内容をpatch / minor / breakingのどれとして扱うか、development versionとstable tagの同期方法は[`docs/versioning.md`](docs/versioning.md)に従ってください。

managed core以外のSkill、guidance、optional CI / integrationの後方互換なcapability追加もminor updateとして扱います。

## Commit style

Use a short imperative summary. Japanese or English is acceptable; keep one language consistent within a pull request.
