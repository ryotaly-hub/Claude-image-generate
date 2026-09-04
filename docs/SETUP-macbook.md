# Claude Code × Gemini「Nano Banana Pro」連携セットアップ手順（MacBook 向け）

新しい Mac で、Claude Code から Gemini の画像生成モデル
**Nano Banana Pro（Gemini 3 Pro Image）** を呼び出せるようにするための手順。

---

## 0. 仕組み（先に全体像）

**MCP サーバーは使っていない。** Claude Code は「Python スクリプトを実行する」
という形で Gemini API を叩いているだけ。構成要素は次の 5 つ:

| # | 要素 | 役割 |
|---|------|------|
| 1 | Gemini API キー | Google AI Studio で発行。課金アカウントが必要 |
| 2 | Python 3.10+ | スクリプトの実行環境 |
| 3 | ライブラリ | `google-genai`（SDK 版）/ `Pillow`（サイズ調整用）|
| 4 | 呼び出しスクリプト | ① このリポジトリ `generate.py` か ② `generate-illustration` スキル |
| 5 | Claude Code | `python` をBashツールでたたけるようにしておくだけでOK |

呼び出し口は 2 系統あり、どちらか（または両方）を用意する:

- **A. スキル方式** … `generate-illustration` スキルを `~/.claude/skills/` に置く。
  「イラスト作って」と言うと Claude が自動で使う。汎用。
- **B. リポジトリ方式** … この `Claude-image-generate` を clone。
  `jobs/*.py` にプロンプトを定義して `python generate.py jobs.xxx` で再現・再実行しやすい。

---

## 1. Claude Code を入れる

```bash
# Node.js が無ければ先に（Homebrew 経由）
brew install node

npm install -g @anthropic-ai/claude-code
claude            # 初回起動 → ブラウザでサインイン
```

---

## 2. Python とライブラリ

macOS には `python3` が入っているが、Homebrew 版が無難:

```bash
brew install python           # python3 / pip3 が入る
python3 --version             # 3.10 以上であること

pip3 install --user google-genai pillow
```

> `pip3 install` で「externally-managed-environment」エラーが出る場合は
> `pip3 install --user --break-system-packages google-genai pillow`
> もしくは venv を作る（後述の「補足」）。

インストール確認:

```bash
python3 -c "import google.genai, PIL; print('ok')"
```

---

## 3. Gemini API キーを取得

1. https://aistudio.google.com/ にログイン
2. 左メニュー **「Get API key」** → **Create API key**
3. **課金を有効化する**（重要）
   - Gemini 3 Pro Image（Nano Banana Pro）は無料枠では基本的に使えない。
   - AI Studio の課金画面、または Google Cloud プロジェクトで請求先を紐付ける。
4. 発行されたキー（`AIzaSy...` または `AQ.xxx` 形式）を控える。

モデル ID:

| 用途 | モデル ID |
|------|-----------|
| SDK（スキル）既定 | `gemini-3-pro-image-preview` |
| このリポジトリの `generate.py` 既定 | `gemini-3-pro-image` |

※ どちらも Nano Banana Pro。preview 付き/無しはSDK・エンドポイントの都合。
将来 ID が変わったら `generate.py` の `MODEL` かスキルの `--model` で上書き。

---

## 4. API キーを環境に置く

### 方式 A（スキル用）: シェルの環境変数

`~/.zshrc` に追記:

```bash
export GEMINI_API_KEY="ここにキー"
```

反映:

```bash
source ~/.zshrc
echo $GEMINI_API_KEY   # 出れば OK
```

### 方式 B（このリポジトリ用）: `.env` ファイル

リポジトリ直下に `.env` を作る（**Git 管理外**、`.gitignore` 済み）:

```
GEMINI_API_KEY=ここにキー
```

`generate.py` はこの `.env` を読む。環境変数と両方あっても問題ない。

> キーはコード・コミットに絶対に書かない。`.env` か環境変数のみ。

---

## 5. 呼び出し口を用意する

### 方式 A: スキルを配置

Windows 機での置き場所は:
`Desktop\photo by claude\.claude\skills\generate-illustration\`

Mac では **ユーザー全体で使える** `~/.claude/skills/` に置くのが楽:

```bash
mkdir -p ~/.claude/skills
# 旧マシンからコピー、または git などで持ってくる
cp -R "/path/to/generate-illustration" ~/.claude/skills/
```

中身:

```
generate-illustration/
├── SKILL.md                    # スキル定義（説明・使い方）
└── scripts/generate_image.py   # google-genai SDK を叩く本体
```

`claude` を起動して `/` を打つと `generate-illustration` が候補に出れば認識OK。

### 方式 B: このリポジトリを clone

```bash
cd ~/dev   # 好きな場所
git clone https://github.com/ryotaly-hub/Claude-image-generate.git
cd Claude-image-generate
printf 'GEMINI_API_KEY=%s\n' "ここにキー" > .env
pip3 install --user pillow
```

構成:

```
Claude-image-generate/
├── generate.py          # 汎用ランナー（urllib で REST 直叩き、SDK 不要）
├── jobs/
│   ├── __init__.py
│   └── sniper.py        # ジョブ定義の例（PROMPT / REF_IMAGES / OUT_NAME ...）
├── .env                 # ← 自分で作る（gitignore済）
└── docs/SETUP-macbook.md
```

---

## 6. 動作テスト

### スキル方式

```bash
cd ~/.claude/skills/generate-illustration
python3 scripts/generate_image.py \
  --prompt "A friendly robot mascot waving, flat vector, mint palette, white background" \
  --output out/test.png --aspect-ratio 1:1 --image-size 2K
```

`out/test.png` の絶対パスが表示されれば成功。
Claude Code 上では「ロボットのマスコットを描いて」等と言えば自動で呼ばれる。

### リポジトリ方式

```bash
cd ~/dev/Claude-image-generate
python3 generate.py jobs.sniper
# → sniper_downtown_2000x1600.png が出力される
```

新しい絵は `jobs/` に `myjob.py` を作って:

```python
REF_IMAGES = ["松田.jpg"]      # 参照画像（任意・複数可）
OUT_NAME   = "myjob"
ASPECT     = "5:4"
SIZE       = (2000, 1600)      # PIL で最終センタークロップ
PROMPT     = "ここに詳しい指示文（被写体＋構図＋光＋スタイル＋背景）"
```

→ `python3 generate.py jobs.myjob`

---

## 7. Claude Code の権限（任意・快適化）

毎回 `python` 実行の確認を出したくなければ、プロジェクトの
`.claude/settings.json`（またはユーザー全体 `~/.claude/settings.json`）に:

```json
{
  "permissions": {
    "allow": ["Bash(python3:*)", "Bash(python:*)"]
  }
}
```

`git push` を Claude にやらせたい場合は `Bash(git push:*)` も追加
（今回 Windows 側ではこれが無くて push がブロックされた）。

---

## 8. パラメータ早見

**アスペクト比**: `1:1 2:3 3:2 3:4 4:3 4:5 5:4 9:16 16:9 21:9`
**解像度**: `1K` / `2K` / `4K`（通常 `2K`、印刷用途のみ `4K`）

実ピクセルは指定比率で近い値が返る（例: 5:4 2K → 2304×1856）。
厳密なサイズが必要なら Pillow でセンタークロップ（`generate.py` は実装済み）。

**プロンプトのコツ**:
- 単語の羅列でなく情景で書く: 被写体＋動作＋場所＋構図＋光＋画風＋色＋背景
- 画像内の文字は指示文で "" で囲って正確に（例: `看板に "OPEN" と書かれている`）
- 編集時は「変える所」と「保つ所」を両方書く（顔・ポーズは維持、など）
- 合成の透過背景が要るなら明示的に頼む

---

## 補足: venv を使う場合

システム Python を汚したくないとき:

```bash
cd ~/dev/Claude-image-generate
python3 -m venv .venv
source .venv/bin/activate
pip install google-genai pillow
```

この場合、Claude Code に実行させるコマンドは
`.venv/bin/python generate.py jobs.xxx` のようにフルパス指定にする
（あるいは `direnv` で自動 activate）。

---

## トラブルシュート

| 症状 | 対処 |
|------|------|
| `google-genai is not installed` | `pip3 install --user google-genai` |
| `set GEMINI_API_KEY ...` エラー | `.env` か `export` を確認、`echo $GEMINI_API_KEY` |
| 403 / PERMISSION_DENIED | AI Studio で課金有効化、キーの権限、モデル ID を確認 |
| `no image returned` + 安全性メッセージ | プロンプトを穏当に言い換える。stderr の `[model text]` を読む |
| 画像が指定サイズでない | 仕様。`generate.py` の Pillow クロップを使うか手動リサイズ |
| 日本語フォルダ名で `cp` が失敗（Win） | Mac では基本問題なし。PowerShell 特有の現象 |
