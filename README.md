# Claude-image-generate

Gemini 3 Pro Image (`gemini-3-pro-image`) を使った画像生成・編集用リポジトリ。

## セットアップ

```
pip install Pillow
```

`.env` に API キーを置く（gitignore 済み）:

```
GEMINI_API_KEY=xxxxx
```

## 使い方

ジョブを `jobs/` にモジュールとして定義し、実行:

```
python generate.py jobs.sniper
```

各ジョブモジュールで定義する変数:

| 変数 | 必須 | 内容 |
|------|------|------|
| `PROMPT` | ○ | 生成/編集の指示文 |
| `REF_IMAGES` | | 参照画像パスのリスト（省略可） |
| `OUT_NAME` | ○ | 出力ファイルのベース名 |
| `ASPECT` | | アスペクト比（既定 `"5:4"`） |
| `SIZE` | | 出力ピクセル（既定 `(2000, 1600)`） |

出力: `<OUT_NAME>_raw.png`（API 生出力・gitignore）と
`<OUT_NAME>_2000x1600.png`（指定サイズにセンタークロップ）。

## ジョブ一覧

- `jobs/sniper.py` — 松田さんをスナイパー装備・ニヒルな笑みで downtown 実写背景に合成
