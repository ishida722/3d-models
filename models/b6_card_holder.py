"""B6 情報カード用の下敷き兼ケース。

B6 サイズのくぼみにカードをはめて持ち歩き、そのまま書ける板。

実行: uv run models/b6_card_holder.py
  - out/b6_card_holder.stl と out/b6_card_holder.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from pathlib import Path

from build123d import *

# パラメータ (mm)
CARD_W = 182  # B6 長辺
CARD_H = 128  # B6 短辺
CLEARANCE = 0.5  # カードと溝のすき間 (片側)
POCKET_DEPTH = 5  # 溝の深さ
FLOOR = 2  # 底板の厚み
RIM = 4  # 外周の壁の幅
CORNER_R = 5  # 外形の角の丸み
NOTCH_R = 12  # 指かけ切り欠きの半径

pocket_w = CARD_W + 2 * CLEARANCE
pocket_h = CARD_H + 2 * CLEARANCE
outer_w = pocket_w + 2 * RIM
outer_h = pocket_h + 2 * RIM

with BuildPart() as holder:
    with BuildSketch():
        RectangleRounded(outer_w, outer_h, CORNER_R)
    extrude(amount=FLOOR + POCKET_DEPTH)
    # カードを収めるくぼみ
    with BuildSketch(Plane.XY.offset(FLOOR)):
        Rectangle(pocket_w, pocket_h)
    extrude(amount=POCKET_DEPTH, mode=Mode.SUBTRACT)
    # 両長辺中央の壁を切り欠いて、カードを指でつまみ出せるようにする
    with BuildSketch(Plane.XY.offset(FLOOR)):
        with Locations((0, -pocket_h / 2), (0, pocket_h / 2)):
            Circle(NOTCH_R)
    extrude(amount=POCKET_DEPTH, mode=Mode.SUBTRACT)
    # 底の外周エッジを丸める (造形時の象の足対策にもなる)
    fillet(holder.edges().group_by(Axis.Z)[0], radius=1)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(holder.part, out_dir / "b6_card_holder.stl")
export_step(holder.part, out_dir / "b6_card_holder.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(holder)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
