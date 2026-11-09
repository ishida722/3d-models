"""冷凍ご飯を一定の大きさに成形するためのガイド枠 (底なしの四角い枠)。

ラップの上に枠を置いてご飯を詰め、上面をならしてから枠を真上に抜く。
両端のつまみを持って抜く。

印刷向き: つまみの付いた側を下にすると、サポートなしで印刷できる。

実行: uv run models/rice_frame.py
  - out/rice_frame.stl と out/rice_frame.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from pathlib import Path

from build123d import *

# パラメータ (mm)
INNER_L = 100  # 内寸の長さ (ご飯の大きさ)
INNER_W = 82  # 内寸の幅
HEIGHT = 33  # 枠の高さ (ご飯の厚み)
WALL = 2.0  # 肉厚
INNER_R = 4  # 内側の角の丸め (ご飯が角に残りにくくする)

TAB_L = 12  # つまみの張り出し
TAB_W = 30  # つまみの幅
TAB_T = 3  # つまみの厚み (枠の上端に付ける)

outer_l = INNER_L + 2 * WALL
outer_w = INNER_W + 2 * WALL

with BuildPart() as frame:
    with BuildSketch():
        RectangleRounded(outer_l, outer_w, INNER_R + WALL)
        RectangleRounded(INNER_L, INNER_W, INNER_R, mode=Mode.SUBTRACT)
    extrude(amount=HEIGHT)
    # 短辺の両側に、上端と面一のつまみを付ける
    with BuildSketch(Plane.XY.offset(HEIGHT - TAB_T)):
        # 壁の厚み分だけ重ねて外側へ張り出す (内側には出さない)
        tab_x = outer_l / 2 + TAB_L / 2 - WALL / 2
        with Locations((tab_x, 0), (-tab_x, 0)):
            RectangleRounded(TAB_L + WALL, TAB_W, 3)
    extrude(amount=TAB_T)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(frame.part, out_dir / "rice_frame.stl")
export_step(frame.part, out_dir / "rice_frame.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(frame)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
