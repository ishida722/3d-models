"""ピルシート 2 錠分を入れる小さなケース。

片方の短辺側が開いた直方体のスリーブ。開口部からシートを差し込み、
開口部の上下にある半円の切り欠きでシートをつまみ出す。

実行: uv run models/pill_case.py
  - out/pill_case.stl と out/pill_case.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from pathlib import Path

from build123d import *

# パラメータ (mm)
SHEET_L = 33  # ピルシート 2 錠分の長さ
SHEET_W = 18  # ピルシートの幅
SHEET_T = 6  # ピルシートの厚み (錠剤のふくらみ込み)
CLEARANCE = 0.3  # シートと内壁のすき間 (片側)
WALL = 1.2  # 肉厚
NOTCH_R = 6  # 指かけ切り欠きの半径

inner_l = SHEET_L + CLEARANCE  # 開口側にはすき間不要なので片側分だけ
inner_w = SHEET_W + 2 * CLEARANCE
inner_t = SHEET_T + 2 * CLEARANCE
outer_l = inner_l + WALL  # 開口側には壁がない
outer_w = inner_w + 2 * WALL
outer_t = inner_t + 2 * WALL

with BuildPart() as case:
    Box(outer_l, outer_w, outer_t, align=(Align.MIN, Align.CENTER, Align.MIN))
    # +X 側の端面まで突き抜けるようにくり抜いて開口部にする
    with Locations((WALL, 0, WALL)):
        Box(inner_l, inner_w, inner_t, align=(Align.MIN, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    # 底の外周エッジを丸める (造形時の象の足対策にもなる)
    fillet(case.edges().group_by(Axis.Z)[0], radius=0.5)
    # 開口部の天井と底を半円に切り欠いて、シートを指でつまみ出せるようにする
    with BuildSketch():
        with Locations((outer_l, 0)):
            Circle(NOTCH_R)
    extrude(amount=outer_t, mode=Mode.SUBTRACT)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(case.part, out_dir / "pill_case.stl")
export_step(case.part, out_dir / "pill_case.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(case)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
