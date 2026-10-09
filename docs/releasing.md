# Releasing PDDR Kit

リリース作業では、バージョンと検証結果を**release準備PR**でレビューし、mainへマージした後、そのコミットへ既存の手動GitHub ActionsからタグとReleaseを公開します。PRのマージやpushだけでは公開しません。

## リリース手順

1. 今回リリースする機能PR・PDDR・ドキュメントをmainへ反映し、mainの通常CIが成功していることを確認する。
2. `VERSION`と`scripts/pddr.py`の`KIT_VERSION`を同じSemVerへ更新する。安定版では`-dev`を外す。
3. `CHANGELOG.md`へ当該バージョンの節を作り、`docs/releases/vX.Y.Z.md`へ変更内容、導入・更新方法、検証の範囲、既知の制約、Evidenceを記録する。
4. 日本語を正本とするREADMEの変更を他の公開言語にも同期し、リンク・コマンド・意味・バージョン表記を確認する。README i18nの手動Workflowを利用した場合は、その実行結果と最終diffをレビューする。
5. 次のコマンドと通常CIを実行し、問題があればrelease準備PR上で解決する。

   ```bash
   python -m unittest discover -s tests -v
   python scripts/validate_skill_evals.py
   python scripts/validate_skill_evals.py evals/pddr-recorder/consumption-cases.json
   python scripts/validate_skill_evals.py evals/pddr-recorder/revision-cases.json
   python scripts/validate_skill_eval_results.py
   python scripts/pddr.py validate
   python scripts/release_guard.py --expected-version X.Y.Z --kind stable
   git diff --check
   ```

6. PRをレビューしてマージし、mainへ反映したコミットのCI成功を確認する。
7. [Publish PDDR Kit release](https://github.com/serevy/pddr-kit/actions/workflows/release.yml)を**default branch上で手動実行**する。`version`へ`X.Y.Z`（`v`なし）を入力し、正式版は`kind=stable`、RCなら`kind=prerelease`とする。
8. Workflowがdefault branch、バージョン整合、リリースノート、既存tag/Releaseの不存在、テスト成功を確認し、実行時のmain SHAを対象に`vX.Y.Z`のGitHub Releaseとtagを作成する。**別途手動でtagを作らない。**
9. 公開後はGitHub ReleaseのURL、tagの指すコミット、必要なconsumerへの明示的な採用・検証を確認する。README上の最新安定版とReleaseの実体に食い違いがないかを確認する。

## 安定版の確認事項

- 権限境界、既存ファイルの非破壊性、必須状態と評価ケースの後方互換性が維持されている。
- 初期化・更新・記録の検証を、単体テストだけでなく対象機能に応じた実際のconsumer構成または一時consumerで確認できている。
- Skillの新しい振る舞いをモデル実行で評価していない場合、**既存の保存済み評価結果を新Skillのモデル評価成功と説明しない**。別途forward-testが必要な範囲をリリースノートに残す。
- 複数言語のREADMEで機能境界・コマンドが矛盾していない。自動翻訳を実行していない場合、その旨を記録する。
- 既存のRC / stable releaseからの更新時に必要な明示操作、衝突時の停止条件、未サポート事項を案内している。

チェック項目を満たした証拠は既存PDDRやリリースノートに追記します。リリース作業そのものについて、既存の判断を変えない限り新しいPDDRは作成しません。
