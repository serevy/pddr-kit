# Releasing PDDR Kit

リリース作業では、バージョン変更と検証結果を先にPRでレビューし、マージ後の同一コミットへタグを付けます。

## リリース手順

1. `VERSION`と`scripts/pddr.py`の`KIT_VERSION`を同じSemVerへ更新する。
2. `CHANGELOG.md`と`docs/releases/`へ変更内容、検証範囲、既知の制約を記録する。
3. 次の検証をすべて実行する。

   ```bash
   python -m unittest discover -s tests -v
   python scripts/validate_skill_evals.py
   python scripts/validate_skill_evals.py evals/pddr-recorder/consumption-cases.json
   python scripts/validate_skill_eval_results.py
   python scripts/pddr.py validate
   git diff --check
   ```

4. リリース準備PRをレビューし、CI成功後にマージする。
5. マージコミットへ`v`付きのannotated tagを付ける。
6. `docs/releases/`の本文を使ってGitHub Releaseを作る。RCだけをPre-releaseとして公開する。

## stable版の確認項目

自動検証の成功に加えて、少なくとも次をstable版の判断材料とします。

- 新規プロジェクトへの導入と運用
- Audio Guardian以外の、性質が異なるプロジェクトへの導入と運用
- RC利用中に見つかった互換性・更新・記録負債の問題への対応

チェック項目を満たした事実は既存のPDDRやリリースノートへEvidenceとして追記します。リリース作業そのものについて、既存の判断を変えない限り新しいPDDRは作成しません。
