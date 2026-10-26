"""タンブラーを逆さにして乾かす水切りスタンド。

台座に棒 (ペグ) を 6 本、2-1-2-1 の千鳥配置で立てる。タンブラーは口を下にして
ペグにかぶせる。口の縁は放射状のリブに乗るので、台座との間にすき間ができて
水が抜け、空気も通る。

台座の上面はシンク側の長辺 (+X) に向かって下り勾配になっていて、垂れた水は
シンク側へ流れ落ちる。シンク側以外の 3 辺には低い壁を立てて、水がキッチン台へ
こぼれないようにする。シンクが逆側にあるときはスライサーで 180° 回転させる。

シンク側の辺はドリップエッジとして LIP_L だけ張り出させ、シンクの縁の上に
かぶせて置く。張り出しの先端の裏には水切り溝を彫り、水が裏側を伝って
キッチン台へ回り込まないようにする。

実行: uv run models/tumbler_rack.py
  - out/tumbler_rack.stl と out/tumbler_rack.step を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from math import cos, radians, sin, tan
from pathlib import Path

from build123d import *

# パラメータ (mm)
WIDTH = 215  # 横幅 (X)。キッチンの空きスペースに合わせる
DEPTH = 256  # 奥行き (Y)。Bambu Lab A1 の造形範囲いっぱい
BASE_T = 4  # 台座の厚み (ドリップエッジ先端の最も薄いところ)
SLOPE_DEG = 2  # 台座上面の勾配 (シンク側へ下る)
CORNER_R = 10  # 台座の角の丸め半径
LIP_L = 15  # ドリップエッジの張り出し長さ (WIDTH の外側、シンクの上に出る分)
DRIP_GROOVE_W = 2  # 水切り溝の幅
DRIP_GROOVE_D = 1.5  # 水切り溝の深さ
DRIP_GROOVE_INSET = 4  # 水切り溝の中心から先端までの距離
WALL_T = 2.5  # 水よけ壁の厚み
WALL_H = 2  # 水よけ壁の高さ (上面から)。リブより低くしてタンブラーの縁に当たらないようにする
TUMBLER_D = 78  # タンブラーの外径
PEG_H = 120  # ペグの高さ (台座上面から)
PEG_BOTTOM_D = 16  # ペグ根元の直径
PEG_TOP_D = 12  # ペグ先端の直径
PEG_FLARE_D = 26  # ペグ根元の補強 (すそ広がり) の直径
PEG_FLARE_H = 8  # ペグ根元の補強の高さ
RIB_COUNT = 6  # タンブラー 1 個あたりのリブ本数
RIB_INNER_R = 26  # リブの内側端 (ペグ中心から)
RIB_OUTER_R = TUMBLER_D / 2  # リブの外側端 (ペグ中心から)。口の縁まで (これ以上だと台座からはみ出す)
RIB_W = 3  # リブの幅
RIB_H = 3  # リブの高さ (= 口の縁と台座のすき間の最小値)

slope = tan(radians(SLOPE_DEG))
x_min = -WIDTH / 2
x_max = WIDTH / 2 + LIP_L  # ドリップエッジの先端


def top_z(x):
    """位置 x における台座上面の高さ。"""
    return BASE_T + (x_max - x) * slope


def slab(extra):
    """台座上面の勾配に沿った、上面を extra だけ持ち上げた板 (平面形は四角のまま)。"""
    pts = [(x_min, 0), (x_max, 0), (x_max, top_z(x_max) + extra), (x_min, top_z(x_min) + extra)]
    return extrude(Plane.XZ * Polygon(*pts, align=None), amount=DEPTH / 2, both=True)


# ペグ中心の配置。タンブラーが台座からはみ出さないよう、中心は縁から外径の半分だけ内側に置く
margin = TUMBLER_D / 2
x_span = WIDTH - 2 * margin
row_pitch = (DEPTH - 2 * margin) / 3  # 4 列 (2-1-2-1) を奥行き方向に均等配置
peg_xy = []
for row, count in enumerate([2, 1, 2, 1]):
    y = -DEPTH / 2 + margin + row * row_pitch
    xs = [-x_span / 2, x_span / 2] if count == 2 else [0]
    peg_xy += [(x, y) for x in xs]

# 平面形はドリップエッジ込みの角丸長方形
outer_w = WIDTH + LIP_L
outline = extrude(Pos(LIP_L / 2, 0) * RectangleRounded(outer_w, DEPTH, CORNER_R), amount=top_z(x_min) + WALL_H)
# シンク側の辺を除いた外周 3 辺のリング (前後の壁はドリップエッジの先端まで延ばす)
ring = outline - extrude(Pos(LIP_L / 2, 0) * RectangleRounded(outer_w - 2 * WALL_T, DEPTH - 2 * WALL_T, CORNER_R - WALL_T), amount=outline.bounding_box().max.Z)
ring -= Pos(x_max, 0, 0) * Box(2 * WALL_T, DEPTH - 2 * WALL_T, 2 * outline.bounding_box().max.Z)
base = slab(0) & outline
walls = slab(WALL_H) & ring

with BuildPart() as rack:
    add(base)
    # 底の外周エッジを丸める (造形時の象の足対策にもなる)
    fillet(rack.edges().group_by(Axis.Z)[0], radius=0.8)
    add(walls)
    # ドリップエッジ先端の裏に水切り溝を彫る。水は溝を越えて裏へ回り込めず、先端から落ちる
    with Locations((x_max - DRIP_GROOVE_INSET, 0, 0)):
        Box(DRIP_GROOVE_W, DEPTH, DRIP_GROOVE_D, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

    # リブは上面を水平にそろえ、タンブラーがまっすぐ立つようにする。
    # 高さは勾配の上側の端で RIB_H になるように決める (下側ほどすき間が広がる)
    for x, y in peg_xy:
        with BuildSketch():
            for i in range(RIB_COUNT):
                a = 360 / RIB_COUNT * i + 90
                r = (RIB_INNER_R + RIB_OUTER_R) / 2
                with Locations(Location((x + r * cos(radians(a)), y + r * sin(radians(a))), a)):
                    Rectangle(RIB_OUTER_R - RIB_INNER_R, RIB_W)
        extrude(amount=top_z(x - RIB_OUTER_R) + RIB_H)

    # ペグは垂直に立てる。根元は上面より 1 mm 下から始めて、勾配の上でも台座と確実につなげる
    with Locations(*[(x, y, top_z(x) - 1) for x, y in peg_xy]):
        Cone(PEG_FLARE_D / 2, PEG_BOTTOM_D / 2, PEG_FLARE_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Cone(PEG_BOTTOM_D / 2, PEG_TOP_D / 2, PEG_H + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # 先端を半球にして、タンブラーの内底を傷つけないようにする
    with Locations(*[(x, y, top_z(x) + PEG_H) for x, y in peg_xy]):
        Sphere(PEG_TOP_D / 2)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(rack.part, out_dir / "tumbler_rack.stl")
export_step(rack.part, out_dir / "tumbler_rack.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    show(rack)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
