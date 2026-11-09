"""洗面台の排水口にはめ込むカバー (ゴミ受け)。

排水口のくぼみ (上端 φ80 mm → 30 mm 下で φ55 mm、壁は内側へ丸く膨らむ) に沿う
カップ。側面のスリットと底の穴から水を流し、髪の毛などを受け止める。
中央のつまみを持って取り出す。

上端に外径 φ96 の縁があり、排水口のまわりの面に引っかかる。
縁の下面は平らなので、止水用のゴムを貼って排水口との間のすき間をふさぐ。

印刷向き: 小径側 (底) を下にして印刷する。縁の下面は張り出しになるので、
縁の下だけサポートを付ける (ゴムを貼る面なので、サポート跡は軽く整える)。

実行: uv run models/drain_cover.py
  - out/drain_cover.stl と out/drain_cover.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

import math
from pathlib import Path

from build123d import *

# パラメータ (mm)
TOP_D = 80  # 排水口くぼみの上端の直径
BOTTOM_D = 55  # 排水口くぼみの下端の直径
DEPTH = 30  # くぼみの深さ (上端から下端まで)
# くぼみの深さ半分 (上端から DEPTH/2 下) での直径。壁は円弧でこの点を通る。
# 直線なら (TOP_D + BOTTOM_D) / 2 = 67.5。壁が内側へ丸く膨らんでいるほど小さくなる。
MID_D = 63
CLEARANCE = 0.5  # くぼみの内面とカバー外面のすき間 (半径方向)
WALL = 2.0  # 側面と底の肉厚

SLOT_W = 2.5  # 側面スリットの幅
SLOT_COUNT = 24  # 側面スリットの本数
SLOT_MARGIN_BOTTOM = 4  # 底面からスリット下端までの高さ
SLOT_MARGIN_TOP = 4  # 上端からスリット上端までの高さ

HOLE_D = 3.0  # 底の水抜き穴の直径
HOLE_PITCH = 5.5  # 底の水抜き穴の間隔

FLANGE_D = 96  # 縁 (フランジ) の外径。排水口のまわりの面に引っかける
FLANGE_T = 2.0  # 縁の厚み。下面は平らで、止水用のゴムを貼る
FLANGE_FILLET = 1.0  # 縁の上面外周の丸め

KNOB_D = 8  # 中央つまみの直径
KNOB_H = 18  # 中央つまみの高さ (底の上面から)

top_r = TOP_D / 2 - CLEARANCE
mid_r = MID_D / 2 - CLEARANCE
bottom_r = BOTTOM_D / 2 - CLEARANCE
height = DEPTH  # 上端をくぼみの縁と面一にする

with BuildPart() as cover:
    # 外形: 側面が円弧になった回転体 (XZ 平面の断面を Z 軸まわりに回す)
    with BuildSketch(Plane.XZ):
        with BuildLine():
            ThreePointArc((bottom_r, 0), (mid_r, height / 2), (top_r, height))
            Polyline((top_r, height), (0, height), (0, 0), (bottom_r, 0))
        make_face()
    revolve(axis=Axis.Z)
    # 上面を開口にして内側へ肉厚 WALL でくり抜く (側面も底も同じ厚みになる)
    offset(amount=-WALL, openings=cover.faces().sort_by(Axis.Z)[-1])

    # 縁: カップ上端から外へ張り出すリング。下面がくぼみの縁の高さ (z = height) に来る
    with Locations((0, 0, height)):
        Cylinder(FLANGE_D / 2, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cylinder(top_r - WALL, FLANGE_T, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)
    flange_top = [
        e for e in cover.edges().filter_by(GeomType.CIRCLE)
        if abs(e.radius - FLANGE_D / 2) < 1e-3 and abs(e.center().Z - (height + FLANGE_T)) < 1e-3
    ]
    fillet(flange_top, radius=FLANGE_FILLET)

    # 側面スリット: 壁を半径方向に貫く細長い箱を放射状に並べる
    # 壁は曲面なので、スリットの高さ全体で壁を貫けるよう箱を半径方向に長くとる
    slot_h = height - SLOT_MARGIN_BOTTOM - SLOT_MARGIN_TOP
    slot_r_in = bottom_r - WALL - 3
    slot_r_out = top_r + 2
    for i in range(SLOT_COUNT):
        slot = Box(slot_r_out - slot_r_in, SLOT_W, slot_h, mode=Mode.PRIVATE)  # PRIVATE: その場ではパートに足さない
        slot = Rot(0, 0, 360 / SLOT_COUNT * i) * Pos((slot_r_in + slot_r_out) / 2, 0, SLOT_MARGIN_BOTTOM + slot_h / 2) * slot
        add(slot, mode=Mode.SUBTRACT)

    # 底の水抜き穴: 格子状に並べ、外周とつまみに近いものは除く
    floor_r = bottom_r - WALL - HOLE_D / 2 - 1.0
    n = int(floor_r // HOLE_PITCH)
    hole_pts = [
        (x * HOLE_PITCH, y * HOLE_PITCH)
        for x in range(-n, n + 1)
        for y in range(-n, n + 1)
        if KNOB_D / 2 + HOLE_D / 2 + 1.0 < math.hypot(x * HOLE_PITCH, y * HOLE_PITCH) < floor_r
    ]
    with BuildSketch():
        with Locations(*hole_pts):
            Circle(HOLE_D / 2)
    extrude(amount=WALL, mode=Mode.SUBTRACT)

    # 中央つまみ
    with Locations((0, 0, WALL)):
        Cylinder(KNOB_D / 2, KNOB_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    knob_top = [
        e for e in cover.edges().filter_by(GeomType.CIRCLE)
        if abs(e.radius - KNOB_D / 2) < 1e-3 and abs(e.center().Z - (WALL + KNOB_H)) < 1e-3
    ]
    fillet(knob_top, radius=KNOB_D / 2 - 0.5)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(cover.part, out_dir / "drain_cover.stl")
export_step(cover.part, out_dir / "drain_cover.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(cover)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
