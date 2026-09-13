# CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) への指針を提供する。

## プロジェクト概要

Gemini 3 Pro Image (`gemini-3-pro-image`) を使った画像生成・編集用のジョブ実行リポジトリ。`jobs/` 配下に Python モジュールとしてジョブを定義し、`generate.py` から実行する。

`build-app` という個人ワークスペース内の1プロジェクトとして管理されているが、それ自体は独立した git リポジトリ。

**新規の画像生成作業はこのリポジトリではなく、PC全体で共有されている `generate-illustration` スキル（`~/.claude/skills/generate-illustration/`）を使うこと。** このリポジトリはそのスキルより前に作られた旧実装（REST APIを直接叩く方式）で、既存ジョブの参照・保守用に残っている。

## セットアップ

```bash
pip install Pillow
```

`.env` に `GEMINI_API_KEY=xxxxx` を置く（`.gitignore` 済み）。

## コマンド

- **ジョブ実行**: `python generate.py jobs.<ジョブ名>`（例: `python generate.py jobs.sniper`）
- **ビルド／lint／テスト**: 該当コマンド無し。

## ディレクトリ構造・仕組み

```
generate.py              REST APIを直接叩いてジョブを実行する本体
jobs/                     ジョブ定義（各モジュールが PROMPT / REF_IMAGES / OUT_NAME / ASPECT / SIZE を定義）
docs/SETUP-macbook.md     セットアップ手順
```

- 各ジョブモジュールの必須変数は `PROMPT`（生成/編集の指示文）と `OUT_NAME`（出力ファイルのベース名）。任意で `REF_IMAGES`（参照画像パスのリスト）、`ASPECT`（既定 `"5:4"`）、`SIZE`（既定 `(2000, 1600)`）を指定できる。
- 出力は `<OUT_NAME>_raw.png`（API生出力・gitignore対象）と `<OUT_NAME>_<幅>x<高さ>.png`（指定サイズにセンタークロップ）の2つ。

## 注意事項

- `GEMINI_API_KEY` は `.env`（gitignore済み）のみに置き、コードやコミットに含めないこと。
- 新しいジョブを追加するより先に、その画像生成が `generate-illustration` スキルで代替できないか検討する。
