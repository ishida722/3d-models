"""調味料入れを並べて収める上面開口の箱。

実行: uv run models/spice_box.py
  - out/spice_box.stl と out/spice_box.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from pathlib import Path

from build123d import *

# パラメータ (mm)
OUTER_L = 183  # 外寸の長さ
OUTER_W = 160  # 外寸の奥行き
OUTER_H = 200  # 外寸の高さ
WALL = 2.4  # 側面の肉厚
FLOOR = 2.4  # 底の厚み
CORNER_R = 6  # 外側の縦の角の丸め
BOTTOM_FILLET = 1.0  # 底の外周エッジの丸め (象の足対策)

with BuildPart() as box:
    with BuildSketch():
        RectangleRounded(OUTER_L, OUTER_W, CORNER_R)
    extrude(amount=OUTER_H)
    # 上面を開口にして内側へくり抜く
    offset(amount=-WALL, openings=box.faces().sort_by(Axis.Z)[-1])
    fillet(box.edges().group_by(Axis.Z)[0], radius=BOTTOM_FILLET)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(box.part, out_dir / "spice_box.stl")
export_step(box.part, out_dir / "spice_box.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(box)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
