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

ペグは台座と別部品にして、横に寝かせて印刷する。縦向きに印刷すると積層の境目が
曲げに弱いため。断面は八角形で、寝かせたときに平らな面が下になりサポートが要らない。
台座のボスに彫った八角形の穴に差し込む (八角形なので回り止めにもなる)。

実行: uv run models/tumbler_rack.py
  - out/tumbler_rack_base.{stl,step} (台座, 1 個) と
    out/tumbler_rack_peg.{stl,step} (ペグ, 寝かせた向き, 6 本印刷する) を出力
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
PEG_AF = 16  # ペグの八角形断面の対辺距離
PEG_EXPOSED = 110  # ペグがボスの上に出ている長さ
PEG_TIP_CHAMFER = 2.5  # ペグ先端の面取り (タンブラーの内底を傷つけないように)
PEG_END_CHAMFER = 1  # ペグ差し込み側の面取り (差し込みやすくし、象の足も逃がす)
FIT_CLEARANCE = 0.15  # ペグと穴のすき間 (片側)。ゆるければ小さく、入らなければ大きくする
SOCKET_D = 12  # 差し込み穴の深さ
SOCKET_FLOOR = 1.5  # 差し込み穴の底の最小厚み
BOSS_D = 30  # 差し込み穴まわりのボスの直径
BOSS_H = 8  # ボスの高さ (台座上面から、最小値)
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


def boss_top(x):
    """位置 x のボス上面の高さ。差し込み穴の底に SOCKET_FLOOR 以上の厚みが残るようにする。"""
    return max(top_z(x) + BOSS_H, SOCKET_FLOOR + SOCKET_D)


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

    # ペグを差すボス。下端は上面より 1 mm 下から始めて、勾配の上でも台座と確実につなげる
    for x, y in peg_xy:
        with Locations((x, y, top_z(x) - 1)):
            Cylinder(BOSS_D / 2, boss_top(x) - top_z(x) + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for x, y in peg_xy:
        with BuildSketch(Plane.XY.offset(boss_top(x))):
            with Locations((x, y)):
                RegularPolygon(PEG_AF / 2 + FIT_CLEARANCE, 8, major_radius=False, rotation=22.5)
        extrude(amount=-SOCKET_D, mode=Mode.SUBTRACT)

peg_l = SOCKET_D + PEG_EXPOSED
with BuildPart() as peg:
    with BuildSketch():
        # 平らな面が X・Y 軸に向くように回す (寝かせたときに面が下になる)
        RegularPolygon(PEG_AF / 2, 8, major_radius=False, rotation=22.5)
    extrude(amount=peg_l)
    chamfer(peg.edges().group_by(Axis.Z)[-1], length=PEG_TIP_CHAMFER)
    chamfer(peg.edges().group_by(Axis.Z)[0], length=PEG_END_CHAMFER)

# 印刷向き: 長手方向を X にして寝かせ、平らな面を造形面に置く
peg_print = Rot(0, 90, 0) * peg.part
peg_print = Pos(-peg_print.bounding_box().min) * peg_print

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(rack.part, out_dir / "tumbler_rack_base.stl")
export_step(rack.part, out_dir / "tumbler_rack_base.step")
export_stl(peg_print, out_dir / "tumbler_rack_peg.stl")
export_step(peg_print, out_dir / "tumbler_rack_peg.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    # 台座にペグを差し込んだ組み立て状態で表示する
    pegs = [Pos(x, y, boss_top(x) - SOCKET_D) * peg.part for x, y in peg_xy]
    show(rack, *pegs)
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
