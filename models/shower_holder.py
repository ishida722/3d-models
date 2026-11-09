"""シャワーポール (縦向き) に固定するシャワーホルダー。

ポールをはさむクランプは前後に割った 2 部品で、ポールの端から通さなくても
横から当てて取り付けられる。前側の半割りには腕とカップが付いている。
左右の耳を M4 ボルトとナット 2 組で締めて固定する。前後の半割りのあいだには
SPLIT_GAP のすき間があり、締めるとこのすき間が詰まってポールを締め付ける。

カップは前 (ポールから離れる向き、+Y) に開いた C 字形で、ホースはこの切り欠きから
横に入れる。持ち手は切り欠きより太いので抜けず、上から落とし込むとヘッドの根元の
太い部分がカップの上に乗って止まる。カップの軸は上端が前へ倒れるように傾けてあり、
ヘッドが斜め下の手前を向く。

印刷向き: ポールの軸を Z にして、底面 (z = 0) を造形面に置く。カップの穴は
CUP_TILT_DEG だけ傾くが、この程度の傾きならサポートは要らない。
後ろ側の半割りも同じ向きで印刷する。
ボルト穴は水平向きの小径穴なのでブリッジで印刷できる。

部品: M4 ボルト (長さ 16 mm) と M4 六角ナット各 2 個。浴室で使うのでステンレス製を推奨。
ボルトは後ろ側の半割りの座ぐりから差し、前側の耳に埋めたナットで受ける。

実行: uv run models/shower_holder.py
  - out/shower_holder_front.{stl,step} (腕・カップ付きの前側) と
    out/shower_holder_back.{stl,step} (後ろ側の押さえ) を出力
  - OCP CAD Viewer が起動していればプレビュー表示
"""

from math import radians, tan
from pathlib import Path

from build123d import *

# パラメータ (mm)
POLE_D = 22  # シャワーポールの直径
POLE_CLEARANCE = 0.2  # ポール穴のすき間 (直径)。ボルトで締めるので小さめでよい
CLAMP_WALL = 4  # クランプの肉厚
HEIGHT = 40  # 全体の高さ (クランプ・腕・カップ共通)。高いほどポール上で傾きにくい
SPLIT_GAP = 1  # 前後の半割りのあいだのすき間 (締め代)。締めてもゆるければ大きくする
EAR_T = 7  # 締め付け耳 1 枚の厚み (Y 方向)
EAR_W = 11  # 締め付け耳がクランプ外周から横へ出る長さ
BOLT_HOLE_D = 4.5  # M4 ボルトの通し穴
BOLT_HEAD_D = 8.5  # ボルト頭の座ぐり径
BOLT_HEAD_DEPTH = 2  # ボルト頭の座ぐり深さ
NUT_AF = 7.3  # M4 ナットの対辺 + すき間
NUT_DEPTH = 3.5  # ナット埋め込み穴の深さ
HANDLE_D = 25  # シャワーの持ち手の太さ (ホルダーに差し込む部分)
HANDLE_CLEARANCE = 1  # 持ち手とカップ穴のすき間 (直径)
CUP_WALL = 4  # カップの肉厚
CUP_TILT_DEG = 15  # カップの軸の傾き (上端が前へ倒れる)
HOSE_SLOT_W = 18  # ホースを通す切り欠きの幅。持ち手より細く、ホース (と口金) より太くする
ARM_L = 45  # ポール中心からカップ中心 (底面での位置) までの距離。ヘッドがポールに当たるなら大きくする
ARM_W = 16  # 腕の幅 (X 方向)
TOP_CHAMFER = 1.5  # カップ穴の上端の面取り (持ち手を落とし込みやすくする)

pole_r = (POLE_D + POLE_CLEARANCE) / 2
clamp_r = pole_r + CLAMP_WALL
cup_r = (HANDLE_D + HANDLE_CLEARANCE) / 2
cup_outer_r = cup_r + CUP_WALL
tilt = radians(CUP_TILT_DEG)

# カップの軸。底面中心 (0, ARM_L, 0) を通り、上へ行くほど +Y へ倒れる
cup_plane = Plane(origin=(0, ARM_L, 0), x_dir=(1, 0, 0), z_dir=(0, tan(tilt), 1))


def tilted_cylinder(r):
    """カップの軸に沿った円柱。上下を z = 0 と z = HEIGHT で切りそろえる前の長めの形。"""
    return cup_plane * Pos(0, 0, -HEIGHT) * Cylinder(r, 3 * HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))


slab = Box(400, 400, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))

bolt_x = clamp_r + EAR_W / 2  # 締め付けボルトの X 位置 (左右対称)
ear_face_y = SPLIT_GAP / 2 + EAR_T  # 耳の外側の面の Y 位置 (前側は +, 後ろ側は -)


def clamp_half():
    """前側 (y > 0) のクランプの半割り。リングの半分と左右の耳。"""
    ring = Cylinder(clamp_r, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ears = Box(2 * (clamp_r + EAR_W), EAR_T, HEIGHT, align=(Align.CENTER, Align.MIN, Align.MIN))
    half = (ring + ears) & Box(400, 200, HEIGHT, align=(Align.CENTER, Align.MIN, Align.MIN))
    half -= Cylinder(pole_r, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return Pos(0, SPLIT_GAP / 2, 0) * half


def bolt_holes(y, depth, pocket):
    """左右の耳を Y 方向に貫くボルト穴。y の面から depth だけ pocket (座ぐりかナット穴) を掘る。"""
    holes = Part()
    for x in (-bolt_x, bolt_x):
        holes += Pos(x, 0, HEIGHT / 2) * (Plane.XZ * Cylinder(BOLT_HOLE_D / 2, 2 * ear_face_y + 2))
        holes += Pos(x, y, HEIGHT / 2) * (Plane.XZ * extrude(pocket, amount=depth, both=True))
    return holes


# 前側: クランプの半割り + 腕 + カップ。耳の前面に M4 ナットを埋める
arm = Box(ARM_W, ARM_L, HEIGHT, align=(Align.CENTER, Align.MIN, Align.MIN))
cup = tilted_cylinder(cup_outer_r) & slab
holder = clamp_half() + arm + cup
holder -= Cylinder(pole_r, HEIGHT, align=(Align.CENTER, Align.CENTER, Align.MIN))
# 六角穴は頂点を上下に向け、上側の傾斜面がブリッジにならずに印刷できるようにする
holder -= bolt_holes(ear_face_y, NUT_DEPTH, RegularPolygon(NUT_AF / 2, 6, major_radius=False, rotation=30))

# 後ろ側: 前側の半割りを鏡写しにしたもの。耳の背面にボルト頭の座ぐりを掘る
back = mirror(clamp_half(), Plane.XZ)
back -= bolt_holes(-ear_face_y, BOLT_HEAD_DEPTH, Circle(BOLT_HEAD_D / 2))

# カップの穴と、ホースを通す前向きの切り欠き (カップの軸に沿って傾ける)
holder -= tilted_cylinder(cup_r)
holder -= cup_plane * Pos(0, 0, -HEIGHT) * Box(HOSE_SLOT_W, cup_outer_r + 5, 3 * HEIGHT, align=(Align.CENTER, Align.MIN, Align.MIN))

with BuildPart() as shower_holder:
    add(holder)
    # カップ穴の上端を面取りする。穴が傾いているので縁は楕円になる。
    # 穴の内面上にある (カップの軸からの距離が cup_r の) エッジを選ぶ
    def dist_from_cup_axis(p):
        v = p - cup_plane.origin
        return (v - cup_plane.z_dir * v.dot(cup_plane.z_dir)).length

    cup_top = [e for e in shower_holder.edges().group_by(Axis.Z)[-1] if abs(dist_from_cup_axis(e @ 0.5) - cup_r) < 0.1]
    chamfer(cup_top, length=TOP_CHAMFER)

out_dir = Path(__file__).resolve().parent.parent / "out"
out_dir.mkdir(exist_ok=True)
export_stl(shower_holder.part, out_dir / "shower_holder_front.stl")
export_step(shower_holder.part, out_dir / "shower_holder_front.step")
export_stl(back, out_dir / "shower_holder_back.stl")
export_step(back, out_dir / "shower_holder_back.step")
print(f"exported to {out_dir}")

from ocp_vscode import get_port, show

# ビューアが起動していなければ表示はスキップ (未起動時の show はエラーを大量に出力する)
if get_port() is not None:
    # 組み立て状態で表示し、参考用にポールも並べる
    pole = Pos(0, 0, -50) * Cylinder(POLE_D / 2, HEIGHT + 100, align=(Align.CENTER, Align.CENTER, Align.MIN))
    show(shower_holder, back, pole, colors=[None, "orange", "silver"], alphas=[1, 1, 0.3])
else:
    print("OCP CAD Viewer が起動していないためプレビューをスキップ")
