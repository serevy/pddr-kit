# PDDR Kit

[English](README.en.md) | [日本語](README.md) | [简体中文](README.zh-CN.md) | [한국어](README.ko.md) | **Français**

**Project Design Decision Record** — Un kit léger pour relier les décisions d’un projet, leur contexte, leur implémentation et leur vérification.

PDDR permet de retracer non seulement les décisions finales, mais aussi tout le processus par lequel des propositions émergent d’observations et de discussions, sont adoptées, mises en œuvre et vérifiées, puis réexaminées si nécessaire. L’objectif est de permettre aux humains et à l’IA de transmettre non seulement « ce qui a été décidé », mais aussi « pourquoi le projet a pris sa forme actuelle ».

> PDDR (Project Design Decision Record) est un framework léger qui préserve non seulement les décisions prises par un Project, mais aussi la manière dont il a évolué et les raisons de cette évolution.

## Ce que couvre PDDR

- **Project** — Objectifs, portée, priorités, Policy de publication, etc.
- **Product** — Exigences, expérience utilisateur, fonctionnalités, critères de qualité, etc.
- **Process** — Procédures de développement, revues, utilisation de l’IA, méthodes de vérification, etc.

PDDR ne remplace ni ADR ni DDR. Il constitue une couche qui, en se référant au Decision Record existant, relie les observations antérieures à la décision à l’implémentation, la vérification et le réexamen qui la suivent.

## Principes importants

1. **Ne complétez pas les raisons absentes de la conversation.** Laissez les circonstances inconnues sous `unknown` et les décisions non confirmées sous `needs-confirmation`.
2. **Ne transformez pas les propositions de l’IA en accord humain.** Distinguez les propositions, les décisions adoptées, rejetées et remplacées.
3. **Séparez les décisions de l’implémentation.** Même une décision adoptée peut ne pas encore être implémentée ou vérifiée.
4. **Ne supprimez pas les anciens enregistrements.** Lorsqu’une Policy change, référencez l’ancien enregistrement depuis le PDDR qui lui succède.
5. **Assurez la traçabilité des Evidence.** Référencez les conversations, Issue, PR, résultats de tests et autres éléments d’appui.
6. **Ne transformez pas les enregistrements en règles absolues.** PDDR fournit du contexte pour la décision ; il ne doit pas être exécuté comme une Policy sans tenir compte de son champ d’application ni de son état.

## Structure du dépôt

| Chemin | Description |
| --- | --- |
| `docs/specification.md` | Spécification commune de PDDR |
| `docs/roadmap.md` | Limites entre la version initiale et les extensions futures |
| `docs/adoption.md` | Procédures d’adoption, de vérification et de CI |
| `docs/skill-evaluation.md` | Méthode d’évaluation du Skill et état actuel |
| `docs/records/` | PDDR de ce projet |
| `evals/pddr-recorder/` | Cas d’évaluation du Skill |
| `templates/pddr.md` | Modèle pour un nouveau PDDR |
| `skills/pddr-recorder/` | Skill d’enregistrement destiné à l’IA |
| `scripts/pddr.py` | CLI d’adoption, de mise à jour et de validation |
| `tests/` | Tests automatisés de la CLI et des définitions d’évaluation |

## Prise en main

Utilisez Python 3.10 ou une version ultérieure. Depuis le répertoire contenant PDDR Kit, indiquez le projet cible et lancez l’initialisation.

```bash
python scripts/pddr.py init --target /path/to/your-project
```

L’initialisation n’écrase pas les fichiers existants. Le projet cible reçoit la configuration, les spécifications, les modèles, une CLI de validation et `docs/records/`.

```bash
cd /path/to/your-project
cp .pddr/template.md docs/records/PDDR-0001-short-title.md
python .pddr/pddr.py validate
```

Renseignez les faits et les justifications liés à la décision, mettez à jour séparément `decision_status` et `delivery_status`, puis faites-les vérifier par une personne dans une PR.

Pour un projet où PDDR Kit est déjà installé, vous pouvez d’abord prévisualiser les différences prévues, puis effectuer la mise à jour depuis le répertoire contenant la nouvelle version de PDDR Kit.

```bash
python scripts/pddr.py upgrade --target /path/to/your-project --dry-run
python scripts/pddr.py upgrade --target /path/to/your-project
```

Seuls les fichiers gérés par le Kit et suivis dans le manifeste sont mis à jour. Les enregistrements, paramètres et règles personnalisées du projet cible ne sont pas modifiés.

Pour les instructions détaillées d’adoption et les exemples de CI, consultez [`docs/adoption.md`](docs/adoption.md). Pour les règles de consignation, consultez [`docs/specification.md`](docs/specification.md). Dans la première version, le fonctionnement fondé sur Markdown fait foi et aucun service ni aucune IA particulière n’est obligatoire.

## Exemple minimal

[`pddr-greenfield-example`](https://github.com/serevy/pddr-greenfield-example) fournit un exemple complet de PDDR reliant le résultat de l’adoption de `v0.1.0` dans un nouveau Project aux observations, options, décisions, livrables et Evidence de vérification.

Le scénario et les Evidence sont entièrement fictifs et servent de référence minimale pour comprendre la structure et le fonctionnement. Ils sont distincts des enregistrements d’expériences ou d’utilisations réelles.

## Étape actuelle

La version stable actuelle est **v0.1.0**. Elle a été publiée après le dogfooding de PDDR Kit lui-même, son adoption et sa vérification CI dans deux projets existants distincts, la mise à jour sûre des installations existantes, l’adoption initiale dans un nouveau projet, ainsi que des forward-tests indépendants de la création d’enregistrements et de l’interprétation sûre à l’aide de Sol et Luna.

Consultez [`docs/releases/v0.1.0.md`](docs/releases/v0.1.0.md) pour connaître le périmètre de vérification et les limites connues de la version stable, et [`CHANGELOG.md`](CHANGELOG.md) pour l’historique des modifications.

Les services payants et externes tels que Jev sont des extensions facultatives. Ils peuvent renforcer la classification, la détection des informations manquantes, la context selection des PDDR associés et l’intégration de typed handoff, mais ils ne sont pas nécessaires au fonctionnement de base de PDDR.

## Références et remerciements

Les sources suivantes ont contribué à la conception de ce projet et de son flux de consignation.

- 窪内 彩佳「[AIとの対話履歴を資産にする。DDR（Design Decision Record）自動記録の仕組み](https://zenn.dev/softbank/articles/ee93e87a9d5dac)」ソフトバンク テックブログ / Zenn、2026年8月21日。
- Michael Nygard, “[Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions),” 2011.
- [Markdown Architectural Decision Records (MADR)](https://adr.github.io/madr/)

Ce projet s’inspire notamment des pratiques consistant à conserver non seulement les livrables, mais aussi le contexte des décisions, à faire rédiger un brouillon par l’IA tant que le contexte est encore frais, et à combiner la revue humaine avec des contrôles visant à repérer les enregistrements manquants. Il s’agit d’une initiative indépendante qui n’implique aucune fourniture officielle, aucun partenariat ni aucune approbation de la part des auteurs ou organisations cités ci-dessus.

## Contribuer

Le projet étant encore à un stade initial, commencez par partager vos cas d’utilisation et vos difficultés dans une Issue. Pour les propositions de modification, consultez [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licence

[Licence MIT](LICENSE)
