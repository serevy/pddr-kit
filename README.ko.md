# PDDR Kit

[English](README.en.md) | [日本語](README.md) | [简体中文](README.zh-CN.md) | **한국어** | [Français](README.fr.md)

**Project Design Decision Record** — 프로젝트의 판단, 배경, 구현 및 검증을 연결하기 위한 경량 키트입니다.

PDDR은 최종 결정뿐만 아니라 관찰과 논의에서 제안이 나오고, 채택되고, 구현·검증되며, 필요할 경우 재검토될 때까지의 흐름을 추적할 수 있게 합니다. 사람과 AI가 “무엇을 결정했는가”뿐만 아니라 “왜 현재의 형태가 되었는가”까지 이어받을 수 있도록 하는 것을 목표로 합니다.

> PDDR (Project Design Decision Record)는 Project가 무엇을 결정했는지뿐만 아니라 어떻게, 그리고 왜 변화해 왔는지도 보존하기 위한 경량 프레임워크입니다.

## PDDR이 다루는 범위

- **Project** — 목적, 범위, 우선순위, 공개 방침 등.
- **Product** — 요구사항, 사용자 경험, 기능, 품질 기준 등.
- **Process** — 개발 절차, 리뷰, AI 활용, 검증 방법 등.

PDDR은 ADR이나 DDR을 대체하지 않습니다. 기존 Decision Record를 참조하면서, 판단에 이르기 전의 관찰과 판단 후의 구현·검증·재검토를 연결하는 레이어입니다.

## 중요한 원칙

1. **대화에 없는 이유를 보완하지 않습니다.** 불분명한 경위는 `unknown`, 확인되지 않은 판단은 `needs-confirmation`으로 남깁니다.
2. **AI의 제안을 인간의 합의로 바꾸지 않습니다.** 제안, 채택, 미채택, 대체됨을 구분합니다.
3. **결정과 구현을 분리합니다.** 채택되었더라도 아직 구현되지 않았거나 검증되지 않은 경우가 있습니다.
4. **오래된 기록을 삭제하지 않습니다.** 방침이 변경되면 후속 PDDR에서 이전 기록을 참조합니다.
5. **Evidence를 추적 가능하게 합니다.** 대화, Issue, PR, 테스트 결과 등을 참조합니다.
6. **기록을 무조건적인 규칙으로 만들지 않습니다.** PDDR은 판단 자료이며, 적용 범위나 상태를 무시한 채 Policy로 실행하지 않습니다.

## 저장소 구성

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

## 사용 시작하기

Python 3.10 이상을 사용합니다. PDDR Kit가 있는 디렉터리에서 대상 프로젝트를 지정해 초기화합니다.

```bash
python scripts/pddr.py init --target /path/to/your-project
```

초기화는 기존 파일을 덮어쓰지 않습니다. 대상 프로젝트에는 설정, 사양, 템플릿, 검증 CLI와 `docs/records/`가 추가됩니다.

```bash
cd /path/to/your-project
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
python .pddr/pddr.py validate
```

판단과 관련된 사실과 근거를 작성하고, `decision_status`와 `delivery_status`를 각각 업데이트한 뒤 PR에서 사람이 확인합니다.

PDDR Kit가 이미 도입된 프로젝트는 새 버전의 PDDR Kit가 있는 디렉터리에서 먼저 변경 예정 사항을 확인한 뒤 업데이트할 수 있습니다.

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project
```

업데이트되는 것은 매니페스트에서 추적되는 Kit 관리 파일뿐입니다. 도입 대상의 기록, 설정, 사용자 지정 규칙은 변경하지 않습니다.

자세한 도입 방법과 CI 예시는 [`docs/adoption.md`](docs/adoption.md), 기록 규칙은 [`docs/specification.md`](docs/specification.md)를 참조하세요. 초판에서는 Markdown 기반 운영을 정본으로 하며, 특정 AI나 서비스를 필수로 요구하지 않습니다.

## 최소 예시

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example)에서는 신규 Project에 `v0.1.0`을 도입한 결과와 관찰·선택지·판단·산출물·검증 Evidence를 연결한 완성된 PDDR 예시를 확인할 수 있습니다.

주제와 Evidence는 모두 허구이며, 구성과 운영을 이해하기 위한 최소 참조 자료입니다. 실험이나 실제 사용 기록과는 분리되어 있습니다.

## 현재 단계

현재 안정 버전은 **v0.1.0**입니다. PDDR Kit 자체의 dogfooding, 서로 다른 두 기존 프로젝트에 대한 도입 및 CI 검증, 기존 도입처의 안전한 업데이트, 신규 프로젝트의 초기 도입, 그리고 Sol과 Luna를 이용한 기록 작성 및 안전 해석에 대한 독립 forward-test를 거쳐 공개되었습니다.

안정 버전의 검증 범위와 알려진 제약 사항은 [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md)를, 변경 이력은 [`CHANGELOG.md`](CHANGELOG.md)를 참조하세요.

Jev 등의 유료·외부 서비스는 선택적 확장 기능입니다. 분류, 누락 판정, 관련 PDDR의 context selection, typed handoff 연계를 강화할 수 있지만 PDDR의 기본 운영에는 필요하지 않습니다.

## 참고문헌 및 감사의 말

본 프로젝트의 착안과 기록 흐름을 검토하는 데 다음 자료를 참고했습니다.

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日。
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

특히 결과물뿐만 아니라 판단의 배경을 남기는 것, 맥락이 남아 있는 동안 AI가 초안을 작성하도록 하는 것, 사람의 검토와 기록 누락 검사를 결합하는 방식을 참고했습니다. 본 프로젝트는 독립적인 이니셔티브이며, 위 참고문헌의 저자나 소속 기관이 공식적으로 제공하거나 제휴하거나 승인한 것임을 의미하지 않습니다.

## 기여하기

아직 초기 단계이므로 먼저 Issue에서 사용 사례와 과제를 공유해 주세요. 변경 제안은 [`CONTRIBUTING.md`](CONTRIBUTING.md)를 참조해 주세요.

## 라이선스

[MIT 라이선스](LICENSE)
