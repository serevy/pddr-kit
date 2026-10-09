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

| 路径 | 说明 |
| --- | --- |
| `docs/specification.md` | PDDR 通用规范 |
| `docs/roadmap.md` | 初版与未来扩展的边界 |
| `docs/adoption.md` | 导入、验证与 CI 步骤 |
| `docs/skill-evaluation.md` | Skill 评估方法与当前状态 |
| `docs/records/` | 本项目自身的 PDDR |
| `evals/pddr-recorder/` | Skill 评估用例 |
| `templates/pddr.md` | 新建 PDDR 模板 |
| `skills/pddr-recorder/` | 面向 AI 的记录 Skill |
| `scripts/pddr.py` | 导入、升级与验证 CLI |
| `tests/` | CLI 与评估定义的自动化测试 |

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

使用 GitHub Actions 的项目还可以采用 **optional checkpoint CI**，用于补充 Agent Skill 无法持续观察的变更路径。它只会针对高信号变更留下复盘 marker，并不会强制创建 PDDR。设置方法请参阅 [`docs/adoption.md`](docs/adoption.md#optional-checkpoint-ci)。

### AI 工具集成与 Skill 更新（v0.3.0）

请将 PDDR 的操作规则放在所用 AI 编程工具**实际会读取**的指令文件中。例如，Claude Code 可使用 `CLAUDE.md`（在支持的版本和配置下也可读取 `AGENTS.md`），Codex 使用 `AGENTS.md`。PDDR Kit 不会擅自修改项目自有的指令文件。详情参见[导入指南](docs/adoption.md)。

v0.3.0 支持通过独立的 manifest 跟踪已明确登记的 `pddr-recorder` Skill，并以非破坏方式更新。从**新版 PDDR Kit 的目录**中，先预览再登记目标路径：

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project --include-skill --skill-path .claude/skills/pddr-recorder/SKILL.md
```

后续只需指定 `--include-skill`，无需重复传入已登记的路径。若 Skill 已被项目自行修改，更新将因冲突而停止，**不会静默覆盖**。**此功能自 v0.3.0 起提供。** 普通的 `upgrade` 仍只更新 Kit 管理的核心文件。

记录决策时，可以复用已有且可核实的人工批准证据。事实记录有误时，可保留修改理由和差异后进行更正；AI 发起的改动必须对人工可见。CI 成功或 PR 自动合并并不等同于人工批准决策。多个 PR 并行分配 PDDR 编号时，请参阅[编号冲突指南](docs/concurrent-record-ids.md)。

## 最小示例

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example) 保留了在新 Project 中最初导入 `v0.1.0` 的历史，并提供了一个将观察、备选方案、决策、产出物和验证 Evidence 连接起来的完整 PDDR 示例。其 managed core 现已更新到 `v0.2.1`，并对拆分为只读 signal workflow 与可信 marker writer 的 hardened optional checkpoint CI 进行了 dogfood。

题材与 Evidence 均为虚构内容，仅作为理解结构与运作方式的最小参考，与实验记录和实际使用记录相互分离。

## 当前阶段

当前稳定版是 **v0.3.0**。本版保留 v0.2.1 的最小权限 checkpoint CI 设计，并新增 AI 工具规则文件指南、显式登记的 Skill 更新、可追踪的记录更正以及并行 PR 的编号冲突处理。新增 Skill 评估用例已通过定义验证，但仍需独立的模型前向测试。

有关稳定版的验证范围，请参阅 [`docs/releases/v0.3.0.md`](docs/releases/v0.3.0.md)；有关变更历史，请参阅 [`CHANGELOG.md`](CHANGELOG.md)。

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
