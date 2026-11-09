# 3d-models

[build123d](https://github.com/gumyr/build123d) で作る 3D プリンタ用モデル集です。
モデルはすべて Python コードで定義しており、パラメータを書き換えるだけで寸法を調整できます。

## 必要なもの

- [uv](https://docs.astral.sh/uv/)
- Python 3.12〜3.14 (`cadquery-ocp` のホイールが cp312〜cp314 のみのため。`.python-version` では 3.14 を指定)
- (任意) VS Code + [OCP CAD Viewer](https://marketplace.visualstudio.com/items?itemName=bernhard-42.ocp-cad-viewer) 拡張 — モデルのプレビュー用

## セットアップ

```sh
git clone https://github.com/ishida722/3d-models.git
cd 3d-models
uv sync
```

VS Code で開くと推奨拡張 (Python / OCP CAD Viewer) の導入を案内されます。インタプリタは `.venv` が自動で選ばれます。

## 使い方

各モデルは `models/` 以下の単体スクリプトです。実行すると `out/` に STL と STEP を出力します。

```sh
uv run models/sample_box.py
# -> out/sample_box.stl, out/sample_box.step
```

OCP CAD Viewer が起動していれば、同時にビューアへプレビューが表示されます (未起動ならスキップ)。

`out/` は `.gitignore` 対象なので、生成物はコミットされません。

## モデル一覧

| ファイル | 内容 |
| --- | --- |
| [models/sample_box.py](models/sample_box.py) | 角を丸めた小物入れ (60×40×25 mm, 肉厚 2 mm) |
| [models/b6_card_holder.py](models/b6_card_holder.py) | B6 情報カード用の下敷き兼ケース (191×137×7 mm, 深さ 5 mm のくぼみ) |
| [models/pill_case.py](models/pill_case.py) | ピルシート 2 錠用の片側開口ケース (内寸 33×18×6 mm + すき間, 肉厚 1.2 mm, 開口部に指かけ切り欠き) |
| [models/tumbler_rack.py](models/tumbler_rack.py) | タンブラー (外径 78 mm) を逆さにして乾かす水切りスタンド (215×256 mm, ペグ 6 本を 2-1-2-1 の千鳥配置, 上面はシンク側の長辺へ 2° の水切り勾配, シンク側に 15 mm 張り出す水切り溝つきドリップエッジ)。ペグは別部品で、寝かせて印刷して台座の八角穴に差し込む (`tumbler_rack_base` ×1, `tumbler_rack_peg` ×6) |
| [models/drain_cover.py](models/drain_cover.py) | 洗面台の排水口 (上端 φ80 mm → 深さ 30 mm で φ55 mm、壁は内側へ丸く膨らむ) にはめ込むゴミ受けカバー。上端に止水ゴムを貼る φ96 の縁つき (壁の膨らみは `MID_D` で調整, すき間 0.5 mm, 肉厚 2 mm, 側面スリット 24 本 + 底の水抜き穴, 中央につまみ) |
| [models/spice_box.py](models/spice_box.py) | 調味料入れを収める上面開口の箱 (外寸 183×160×200 mm, 肉厚 2.4 mm, 縦の角 R6) |
| [models/rice_frame.py](models/rice_frame.py) | 冷凍ご飯を成形する底なしのガイド枠 (内寸 100×82 mm, 高さ 33 mm, 肉厚 2 mm, 短辺に抜き取り用のつまみ) |

## その他

- [ocp_vscode_demo.py](ocp_vscode_demo.py) — build123d の Builder / Algebra モードと OCP CAD Viewer の表示オプションを試すデモ。`# %%` 区切りのセル単位で実行できます。

## モデルの追加

1. `models/<name>.py` を作成し、ファイル先頭にパラメータ (mm) を定数として並べる
2. `out/<name>.stl` / `out/<name>.step` を出力する (既存の [sample_box.py](models/sample_box.py) を参考に)
3. 上のモデル一覧に追記する

## ライセンス

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — クレジット表記をすれば、改変・再配布・商用利用が可能です。詳細は [LICENSE](LICENSE) を参照してください。
