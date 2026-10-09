# PDDR Kit

**English** | [日本語](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md) | [Français](README.fr.md)

**Project Design Decision Record** — A lightweight kit for connecting project decisions, context, implementation, and verification.

PDDR makes it possible to trace not only final decisions, but the full flow in which proposals emerge from observations and discussions, are adopted, implemented and verified, and are revised when necessary. It aims to help people and AI carry forward not only “what was decided,” but also “why the project took its current form.”

> PDDR (Project Design Decision Record) is a lightweight framework for preserving not only what a project decided, but how and why it evolved.

## What PDDR covers

- **Project** — Purpose, scope, priorities, publication Policy, and more.
- **Product** — Requirements, user experience, features, quality standards, and more.
- **Process** — Development procedures, reviews, AI usage, verification methods, and more.

PDDR does not replace ADR or DDR. It is a layer that links observations made before a decision to the implementation, verification, and review that follow it, while referring to the existing Decision Record.

## Important principles

1. **Do not fill in reasons that are not present in the conversation.** Leave unclear circumstances as `unknown` and unconfirmed decisions as `needs-confirmation`.
2. **Do not turn AI suggestions into human agreement.** Distinguish between proposals, adopted decisions, rejected decisions, and replaced decisions.
3. **Separate decisions from implementation.** Even an adopted decision may still be unimplemented or unverified.
4. **Do not delete old records.** When a Policy changes, reference the old record from the successor PDDR.
5. **Make the Evidence traceable.** Refer to conversations, Issue, PR, test results, and other supporting material.
6. **Do not turn records into unconditional rules.** PDDR provides decision context; it must not be executed as Policy while ignoring its scope or status.

## Repository structure

| Path | Description |
| --- | --- |
| `docs/specification.md` | Common PDDR specification |
| `docs/roadmap.md` | Boundary between the initial release and future extensions |
| `docs/adoption.md` | Adoption, verification, and CI procedures |
| `docs/skill-evaluation.md` | Skill evaluation method and current status |
| `docs/records/` | PDDR records for this project |
| `evals/pddr-recorder/` | Skill evaluation cases |
| `templates/pddr.md` | Template for a new PDDR |
| `skills/pddr-recorder/` | Recording Skill for AI |
| `scripts/pddr.py` | Adoption, upgrade, and validation CLI |
| `tests/` | Automated tests for the CLI and evaluation definitions |

## Getting started

Use Python 3.10 or later. From the directory containing PDDR Kit, specify the target project and initialize it.

```bash
python scripts/pddr.py init --target /path/to/your-project
```

Initialization does not overwrite existing files. The target project receives configuration, specifications, templates, a validation CLI, and `docs/records/`.

```bash
cd /path/to/your-project
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
python .pddr/pddr.py validate
```

Enter the facts and supporting grounds related to the decision, update `decision_status` and `delivery_status` separately, and have a person review them in a PR.

For a project where PDDR Kit is already installed, you can first preview the planned differences and then update it from the directory containing the new version of PDDR Kit.

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project
```

Only Kit-managed files tracked by the manifest are updated. Records, settings, and custom rules in the target project are not changed.

For detailed adoption instructions and CI examples, see [`docs/adoption.md`](docs/adoption.md). For record-keeping rules, see [`docs/specification.md`](docs/specification.md). In the initial release, Markdown-based operation is the source of truth, and no specific AI or service is required.

Projects using GitHub Actions can also use the **optional checkpoint CI** to cover change paths that an Agent Skill may not continuously observe. It only leaves a review marker for high-signal changes and does not require creating a PDDR. See [`docs/adoption.md`](docs/adoption.md#optional-checkpoint-ci) for setup.

### AI tool integration and Skill updates (v0.3.0)

Connect PDDR operating rules to the instruction files **actually loaded** by your AI coding tool. For example, Claude Code can use `CLAUDE.md` (or, under supported versions and configurations, `AGENTS.md`), while Codex uses `AGENTS.md`. PDDR Kit does not overwrite consumer-owned instruction files. See the [adoption guide](docs/adoption.md).

Version `0.3.0` supports an explicit, non-destructive update path for an enrolled `pddr-recorder` Skill, tracked by a separate manifest. From the **new PDDR Kit checkout**, enroll a Skill destination after previewing the changes:

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md
```

For subsequent updates, specify `--include-skill` without repeating the saved destination. Modified Skills are not silently overwritten: conflicts stop the update. **This option was introduced in v0.3.0.** Plain `upgrade` still updates only the managed core.

Verified prior human approval can be reused when recording a decision. Factual transcription errors can be corrected with a traceable rationale and diff; AI-initiated changes must be visible to a human. CI success or unattended PR merge is not human decision approval. See the [concurrent ID guidance](docs/concurrent-record-ids.md) when multiple PRs allocate PDDR IDs.

## Minimal example

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example) preserves the history of initially adopting `v0.1.0` in a new Project and provides a complete PDDR example linking observations, options, decisions, artifacts, and verification Evidence. Its managed core is now updated to `v0.3.0`, and it dogfoods the hardened optional checkpoint CI split into a read-only signal workflow and a trusted marker writer.

The scenario and Evidence are entirely fictional and serve as a minimal reference for understanding the structure and operation. They are separate from records of experiments or real-world use.

## Current stage

The current stable release is **v0.3.0**. It retains the least-privilege checkpoint CI design of v0.2.1 while adding AI-tool instruction guidance, opt-in Skill upgrades, transparent record corrections, and concurrent PR ID-allocation guidance. The new Skill evaluation case definitions have been validated; independent model forward-tests remain pending.

See [`docs/releases/v0.3.0.md`](docs/releases/v0.3.0.md) for the stable release’s verification scope, and [`CHANGELOG.md`](CHANGELOG.md) for the change history.

Paid and external services such as Jev are optional extensions. They can strengthen classification, missing-information detection, context selection for related PDDR records, and typed handoff integration, but they are not required for basic PDDR operation.

## References and acknowledgments

The following sources informed the concept behind this project and the design of its record-keeping flow.

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日。
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

In particular, this project draws on the practices of preserving not only deliverables but also the context behind decisions, having AI draft records while the context is still fresh, and combining human review with checks for missing records. This project is an independent initiative and does not imply official provision, partnership, or endorsement by the authors or organizations cited above.

## Contributing

Because the project is still at an early stage, please first share use cases and problems in an Issue. For change proposals, see [`CONTRIBUTING.md`](CONTRIBUTING.md).

## License

[MIT License](LICENSE)
