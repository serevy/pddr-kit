# PDDR Kit

[English](README.en.md) | [日本語](README.md) | **简体中文** | [한국어](README.ko.md) | [Français](README.fr.md)

**Project Design Decision Record** — 用于连接项目决策、背景、实现与验证的轻量级工具包。

PDDR 不仅追踪最终决定，还追踪提案如何从观察和讨论中产生、被采纳、实施与验证，并在必要时被重新审视的全过程。它的目标是让人类与 AI 不仅能够传承“决定了什么”，还能够传承“为什么会形成当前的形态”。

> PDDR（Project Design Decision Record）是一个轻量级框架，不仅用于保留 Project 做出了什么决策，也用于保留它如何演变以及为何如此演变。

## PDDR 覆盖的内容

- **Project** — 目的、范围、优先级、发布方针等。
- **Product** — 需求、用户体验、功能、质量标准等。
- **Process** — 开发流程、评审、AI 应用、验证方法等。

PDDR 不会取代 ADR 或 DDR。它是在参照现有 Decision Record 的同时，将作出决策前的观察与决策后的实现、验证和复盘连接起来的一层。

## 重要原则

1. **不要补充对话中不存在的理由。** 不明的经过保留为 `unknown`，未经确认的判断保留为 `needs-confirmation`。
2. **不要把 AI 的提案转化为人类共识。** 区分提案、已采纳、未采纳和已替换。
3. **将决策与实现分离。** 即使已经采纳，也可能尚未实现或验证。
4. **不要删除旧记录。** 方针变更时，从后续 PDDR 中引用旧记录。
5. **让依据可追溯。** 引用对话、Issue、PR、测试结果等 Evidence。
6. **不要把记录变成无条件规则。** PDDR 是判断材料，不应无视适用范围或状态而作为 Policy 执行。

## 仓库结构

```text
docs/
  specification.md          PDDRの共通仕様
  roadmap.md                初版と将来拡張の境界
  adoption.md               導入・検証・CIの手順
  skill-evaluation.md       Skill評価の方法と現在状態
  records/                  このプロジェクト自身のPDDR
evals/
  pddr-recorder/             Skill評価ケース
templates/
  pddr.md                    新規PDDRテンプレート
skills/
  pddr-recorder/             AI向け記録Skill
scripts/
  pddr.py                    導入・更新・検証CLI
tests/                       CLI・評価定義の自動テスト
```

## 开始使用

使用 Python 3.10 或更高版本。在 PDDR Kit 所在目录中指定目标项目并进行初始化。

```bash
python scripts/pddr.py init --target /path/to/your-project
```

初始化不会覆盖现有文件。目标项目中会新增配置、规范、模板、验证 CLI 以及 `docs/records/`。

```bash
cd /path/to/your-project
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
python .pddr/pddr.py validate
```

填写与决策相关的事实和依据，分别更新 `decision_status` 和 `delivery_status`，然后由人工在 PR 中审核。

对于已经导入 PDDR Kit 的项目，可以先在包含新版 PDDR Kit 的目录中预览计划差异，再执行更新。

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project
```

只更新清单中跟踪的 Kit 管理文件。目标项目中的记录、设置和自定义规则不会被修改。

有关详细的导入方法和 CI 示例，请参阅 [`docs/adoption.md`](docs/adoption.md)；有关记录规则，请参阅 [`docs/specification.md`](docs/specification.md)。初版以基于 Markdown 的运作为准，不要求使用特定的 AI 或服务。

## 最小示例

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example) 提供了一个完整的 PDDR 示例，将在新 Project 中导入 `v0.1.0` 的结果与观察、备选方案、决策、产出物和验证 Evidence 连接起来。

题材与 Evidence 均为虚构内容，仅作为理解结构与运作方式的最小参考，与实验记录和实际使用记录相互分离。

## 当前阶段

当前稳定版是 **v0.1.0**。该版本是在 PDDR Kit 自身完成 dogfooding、在两个不同的现有项目中完成导入与 CI 验证、验证现有导入环境的安全更新、完成新项目的初始导入，以及使用 Sol 和 Luna 对记录创建和安全解释进行独立 forward-test 之后发布的。

有关稳定版的验证范围和已知限制，请参阅 [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)；有关变更历史，请参阅 [`CHANGELOG.md`](CHANGELOG.md)。

Jev 等付费或外部服务属于可选扩展。它们可以增强分类、缺失判定、相关 PDDR 的 context selection 以及 typed handoff 集成，但并非 PDDR 基本运作所必需。

## 参考文献与致谢

本项目的构想和记录流程设计参考了以下资料。

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日。
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

尤其参考了以下做法：不仅保留成果物，还保留决策背景；在上下文仍然鲜明时由 AI 起草记录；并将人工审核与记录遗漏检查结合起来。本项目是独立开展的工作，不表示上述参考资料的作者或其所属组织提供官方支持、建立合作关系或予以认可。

## 贡献

由于项目仍处于初期阶段，请先在 Issue 中分享用例和问题。有关变更提案，请参阅 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 许可证

[MIT 许可证](LICENSE)
