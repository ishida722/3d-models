"""サンプル: 角を丸めた小物入れ。

実行: uv run models/sample_box.py
  - out/sample_box.stl と out/sample_box.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from pathlib import Path

from build123d import *

# パラメータ (mm)
WIDTH = 60
DEPTH = 40
HEIGHT = 25
WALL = 2
CORNER_R = 5

with BuildPart() as box:
    with BuildSketch():
        RectangleRounded(WIDTH, DEPTH, CORNER_R)
    extrude(amount=HEIGHT)
    # 上面をくり抜いて肉厚 WALL のシェルにする
    offset(amount=-WALL, openings=box.faces().sort_by(Axis.Z)[-1])
    # 底の外周エッジを丸める (造形時の象の足対策にもなる)
    fillet(box.edges().group_by(Axis.Z)[0], radius=1)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(box.part, out_dir / "sample_box.stl")
export_step(box.part, out_dir / "sample_box.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(box)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
