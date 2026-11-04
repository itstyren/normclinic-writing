"""Framework figure v8: the original layout, compacted; flat icons; no formula;
one meaning per dash style; Nature text sizes. Reads the original draw.io and
writes a new file."""
import re, sys, os
import xml.etree.ElementTree as ET
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dio import Doc, LINE
import palette as P
import pix

SRC, OUT = sys.argv[1], sys.argv[2]
tree = ET.parse(SRC); root = tree.getroot()
model = root.find('.//mxGraphModel'); mroot = model.find('root')
cells = {c.get('id'): c for c in mroot}

def geo(cid):
    return cells[cid].find('mxGeometry')

def move(cid, dx, dy):
    g = geo(cid)
    g.set('x', str(float(g.get('x', 0)) + dx)); g.set('y', str(float(g.get('y', 0)) + dy))

def place(cid, x=None, y=None, w=None, h=None):
    g = geo(cid)
    for k, v in (('x', x), ('y', y), ('width', w), ('height', h)):
        if v is not None: g.set(k, str(v))

def edge_points(cid, pts):
    """Rewrite an unconnected edge's source point, waypoints and target point."""
    g = geo(cid)
    for p in list(g):
        g.remove(p)
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    ET.SubElement(g, 'mxPoint', {'x': str(x0), 'y': str(y0), 'as': 'sourcePoint'})
    ET.SubElement(g, 'mxPoint', {'x': str(x1), 'y': str(y1), 'as': 'targetPoint'})
    if len(pts) > 2:
        arr = ET.SubElement(g, 'Array', {'as': 'points'})
        for x, y in pts[1:-1]:
            ET.SubElement(arr, 'mxPoint', {'x': str(x), 'y': str(y)})

def shift_edge(cid, dx, dy):
    g = geo(cid)
    for p in g.iter('mxPoint'):
        p.set('x', str(float(p.get('x', 0)) + dx)); p.set('y', str(float(p.get('y', 0)) + dy))

def set_style(cid, **kv):
    st = cells[cid].get('style') or ''
    for k, v in kv.items():
        if re.search(rf'(^|;){k}=', st):
            st = re.sub(rf'(^|;){k}=[^;]*', rf'\g<1>{k}={v}', st)
        else:
            st += f'{k}={v};'
    cells[cid].set('style', st)

# ---- 1. remove smooth icons, the formula and the embedded R(a) chart ----------
for cid in ['u56', 'c82', 'c84', 'c86', 'c93', 'c95', 'c97', 'u409', 'c425', 'c54', 'c55', 'c68', 'c69', 'e70', 'e71', 'visible_note', 'u410', 'u411']:
    mroot.remove(cells[cid])
cells['c429'].set('value', '')
place('c72', 1540, 196, 220, 50); place('c75', 1653, 300, 120, 44)
edge_points('e30', [(522, 160), (522, 226)]); edge_points('e32', [(522, 226), (551, 226)])
edge_points('e34', [(536, 226), (536, 292)]); edge_points('e35', [(536, 226), (551, 226)])
edge_points('e66', [(1590, 174), (1590, 196)]); edge_points('e67', [(1700, 174), (1700, 196)])
cells['c373'].set('value', 'Active norm f'); place('c373', 440, 640, 230, 56)
edge_points('e376', [(740, 688), (671, 688)]); place('c377', 672, 692, 72, 20)
edge_points('e423', [(520, 696), (520, 767)])
cells['v6_observer_caption'].set('value', '')
# the policy-input icon's white grid lines and dot outlines were under 0.25 pt at print size
import base64
st = cells['u399'].get('style')
m = re.search(r'image=data:image/svg\+xml[,;]([A-Za-z0-9+/=]+)', st)
svg = base64.b64decode(m.group(1)).decode('utf-8')
svg = svg.replace('stroke-width="1.1"', 'stroke-width="1.3"').replace('stroke-width="1"', 'stroke-width="1.3"')
cells['u399'].set('style', st.replace(m.group(1), base64.b64encode(svg.encode('utf-8')).decode('ascii')))

# ---- 2. text: three sizes (18, 21, 28), one ink; no hairlines -----------------
def fix_style(st):
    st = re.sub(r'fontSize=(11|14|16|17|19|20|22)(;|$)', r'fontSize=18\2', st)
    st = re.sub(r'fontSize=18;', 'fontSize=18;', st)
    st = re.sub(r'fontColor=#(5A606A|8D5729|95682F|262A31)', 'fontColor=#000000', st)
    st = re.sub(r'strokeWidth=0\.[0-8][0-9]*(?=;|$)', lambda m: 'strokeWidth=0.875' if float(m.group(0).split('=')[1]) < 0.875 else m.group(0), st)
    return st
for c in mroot.iter('mxCell'):
    st = c.get('style')
    if st: c.set('style', fix_style(st))
for cid in ('c8', 'c11', 'c14', 'c17', 'c20', 'c52', 'c5', 'c119', 'c83', 'c94', 'c396', 'c434', 'u410', 'u411'):
    set_style(cid, fontSize=21)   # role names, panel titles, plus signs, pi and V
place('v6_rep_value_0', 93, 21, 32, 23); place('v6_rep_value_1', 93, 60, 32, 23)
for cid in ('c4', 'c118'):
    set_style(cid, fontSize=27.8)   # 8.0 pt panel labels

# ---- 3. compact panel a: the two memories side by side -----------------------
# band and label
place('c3', 262, 330, 1238, 118); place('c76', 272, 332, 90, 22)
# Trial memory block: shift (-300, +10)
for cid in ('c77', 'c78', 'c83', 'c85', 'c89', 'c90', 'c91', 'c92'):
    move(cid, -310, 10)
for cid in ('e87', 'e88'):
    shift_edge(cid, -310, 10)
place('c77', h=88)
edge_points('e105', [(600, 354), (600, 319)])                 # Advisor reads the trial memory
# Norm history block: new box (670, 354, 560, 92) with a two-line flow
place('c79', 660, 354, 680, 88); place('c80', 674, 360, 150, 22); place('c81', 674, 382, 150, 44)
cells['c81'].set('value', 'norms that trained')
place('c94', 942, 364, 16, 26)
place('c96', 1131, 363, 28, 28)
edge_points('e98', [(1030, 377), (1127, 377)]); edge_points('e99', [(1163, 377), (1260, 377)])
for cid, x, label in (('c100', 820, 'previous<br>summary'), ('c101', 950, 'retired norm'),
                      ('c102', 1080, 'Reviewer'), ('c103', 1210, 'updated<br>summary')):
    place(cid, x, 396, 130, 44); cells[cid].set('value', label)
    set_style(cid, align='center', verticalAlign='top')
edge_points('e104', [(770, 354), (770, 319)])                 # Advisor reads the norm history
edge_points('e106', [(1100, 354), (1100, 319)])               # Designer reads it
# inputs to the memories
edge_points('e107', [(1400, 316), (1400, 460), (450, 460), (450, 442)])   # pilots not adopted
place('c108', 900, 462, 180, 22)
edge_points('e73', [(1553, 160), (1525, 160), (1525, 398), (1341, 398)]) # retired norm
place('c74', 1414, 402, 100, 44); cells['c74'].set('value', 'retired<br>norm'); set_style('c74', align='center')
# panel a box and the lines that leave it
place('c2', 20, 20, 1760, 476)
DY = -50
edge_points('e442', [(1645, 246), (1645, 554 + DY), (555, 554 + DY), (555, 640 + DY)])
edge_points('e23', [(130, 110), (130, 561 + DY)])
edge_points('e24', [(30, 561 + DY), (30, 84), (39, 84)])

# ---- 4. move panel b up ------------------------------------------------------
LAYERS = {c.get('id') for c in mroot if c.get('parent') == '0'}
PANEL_B_IDS = set()
for c in mroot:
    g = c.find('mxGeometry')
    if g is None or c.get('parent') not in LAYERS: continue
    if c.get('vertex') == '1':
        if float(g.get('y', 0)) >= 556: PANEL_B_IDS.add(c.get('id'))
    elif c.get('edge') == '1':
        ys = [float(p.get('y', 0)) for p in g.iter('mxPoint')]
        if ys and min(ys) >= 556: PANEL_B_IDS.add(c.get('id'))
PANEL_B_IDS -= {'e442', 'e23', 'e24', 'c1', 'c2'}
for cid in PANEL_B_IDS:
    c = cells[cid]
    if c.get('vertex') == '1': move(cid, 0, DY)
    else: shift_edge(cid, 0, DY)
place('c1', 0, 0, 1800, 975 + DY); model.set('pageHeight', str(975 + DY))

# ---- 5. dash styles: dashed = reads; everything else solid or dotted ---------
# (the pilot lanes and reference lines are drawn below)

# ---- 6. new flat elements --------------------------------------------------------
d = Doc(1800, 975 + DY, 'tmp')
d._id = lambda prefix, _n=[0]: (_n.__setitem__(0, _n[0] + 1) or f'v8_{prefix}{_n[0]}')

DOC = ['.oooooooo....', '.owwwwwwoo...', '.owwwwwwowo..', '.owwwwwwoooo.', '.owwwwwwwwwo.', '.owllllllwwo.',
       '.owwwwwwwwwo.', '.owlllllllwo.', '.owwwwwwwwwo.', '.owlllllwwwo.', '.owwwwwwwwwo.', '.owwwwwwwwwo.',
       '.owwwwwwwwwo.', '.ooooooooooo.', '.............']
def doc_variant(kind):
    g = [list(r) for r in DOC]
    if kind == 'pilots':
        for r in (5, 7): g[r] = list('.owgg.gg.ggo.')
        g[9] = list('.owgg.gg.wwo.')
    elif kind == 'updated':
        for r in (10, 11, 12): g[r] = list('.owbbbbbbbwo.')
    elif kind == 'norm':
        for r in (5, 7, 9): g[r] = list('.owwwwwwwwwo.')
        for (r, c) in [(11, 3), (10, 4), (10, 5), (9, 6), (8, 7), (8, 8), (7, 9)]: g[r][c] = 'k'
        g[6][3] = 'k'; g[6][4] = 'k'
    return [''.join(r) for r in g]
DOC_PAL = {'o': P.OUTLINE, 'w': '#FFFFFF', 'l': '#A0A6AE', 'g': '#8DCBB7', 'k': '#262A31'}
def doc(x, y, kind='plain', colour=None, px=2):
    pal = dict(DOC_PAL)
    if colour: pal['b'] = colour
    return d.sprite(doc_variant(kind), pal, x, y, px)

# memory documents (Trial memory shifted by (-300, +10); Norm history in its new slots)
doc(327, 384, 'plain'); doc(407, 384, 'pilots'); doc(567, 384, 'updated', '#F4D35E')
doc(872, 362, 'plain'); doc(1002, 362, 'norm'); doc(1262, 362, 'updated', '#8FA3E8')

# pilot trial lanes: solid train, pale solid frozen evaluation, flat bars, dotted reference
GREY, GREEN = '#8A9099', '#8DCBB7'
FACES = {GREY: ('#B4B9C0', '#6E747D'), GREEN: ('#B9E0D3', '#6FB39C')}
AX, DEPTH = 1300, 5
d.line([(AX, 126), (AX, 274)], stroke=LINE, sw=1)
for y, col, length in ((150, GREY, 60), (200, GREEN, 76), (250, GREEN, 96)):
    top, side = FACES[col]
    d.bar3d(AX, y - 8, length, 16, col, top, side, d=DEPTH)
    if col == GREEN:   # the candidate's difference from the control
        d.line([(AX + 60, y - 17), (AX + length + DEPTH, y - 17)], stroke=LINE, sw=1, arrow='block')
d.cells.append(f'<mxCell id="v8_ref1" value="" style="edgeStyle=none;html=1;endArrow=none;strokeColor={GREY};strokeWidth=1;dashed=1;dashPattern=1 3;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="{AX + 60}" y="126" as="sourcePoint"/><mxPoint x="{AX + 60}" y="274" as="targetPoint"/></mxGeometry></mxCell>')
d.rect(AX - 3, 250 - 13, 96 + DEPTH + 7, 26, fill='none', stroke=LINE, sw=1.25)   # the candidate the Arbiter adopts

by = DY

# actor-critic, flat: two inputs, four hidden units, two heads
inp = [(1560, 636 + by, '#DADDE1'), (1560, 690 + by, '#F9B882')]
hid = [(1624, 630 + by), (1624, 654 + by), (1624, 678 + by), (1624, 702 + by)]
out = [(1680, 640 + by), (1680, 682 + by)]
R = 7
for (x, y, f) in inp:
    for (hx, hy) in hid:
        d.line([(x + 18, y + 9), (hx, hy + R)], stroke='#B4B9C0', sw=0.875)
for (hx, hy) in hid:
    for (ox, oy) in out:
        d.line([(hx + 2 * R, hy + R), (ox, oy + 8)], stroke='#B4B9C0', sw=0.875)
for (x, y, f) in inp:
    d.rect(x, y, 18, 18, fill=f, stroke=LINE, sw=1, rounded=1, arc=4)
for (hx, hy) in hid:
    d.ellipse(hx, hy, 2 * R, 2 * R, fill='#FFFFFF', stroke=LINE, sw=1)
for (ox, oy) in out:
    d.ellipse(ox, oy, 16, 16, fill='#FFFFFF', stroke=LINE, sw=1)

# R(a) for every action: the agent, one bar per action, the chosen one dark
g, pal = pix.agent_sprite()
d.sprite(g, pal, 443, 786 + by, 3)
d.rect(470, 772 + by, 40, 12, fill='#FCDCC2', stroke=LINE, sw=0.875)
d.rect(470, 790 + by, 78, 12, fill='#F9B882', stroke=LINE, sw=1.6)
d.rect(470, 808 + by, 30, 12, fill='#FCDCC2', stroke=LINE, sw=0.875)
d.cells.append(f'<mxCell id="v8_ref2" value="" style="edgeStyle=none;html=1;endArrow=none;strokeColor={LINE};strokeWidth=1;dashed=1;dashPattern=1 3;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="520" y="{768 + by}" as="sourcePoint"/><mxPoint x="520" y="{826 + by}" as="targetPoint"/></mxGeometry></mxCell>')

# reputation advantage: the chosen action's R above the mean under the policy
for i, hgt in enumerate([18, 26, 40, 14]):
    d.rect(700 + i * 22, 842 + by - hgt, 16, hgt, fill='#E58A3A' if i == 2 else '#FBD1AE', stroke='none')
d.line([(694, 842 + by), (796, 842 + by)], stroke=LINE, sw=1)
d.cells.append(f'<mxCell id="v8_ref3" value="" style="edgeStyle=none;html=1;endArrow=none;strokeColor={LINE};strokeWidth=1;dashed=1;dashPattern=1 3;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="694" y="{823 + by}" as="sourcePoint"/><mxPoint x="850" y="{823 + by}" as="targetPoint"/></mxGeometry></mxCell>')
d.line([(792, 802 + by), (792, 823 + by)], stroke=LINE, sw=1.25, start_arrow='block', arrow='block')
d.text(798, 798 + by, 50, 20, 'A<sub>rep</sub>', fs=18)
d.text(856, 812 + by, 136, 22, 'mean under π', fs=18)

for xml in d.cells:
    mroot.append(ET.fromstring(xml))
tree.write(OUT, encoding='utf-8', xml_declaration=True)
print('wrote', OUT, 'panel b cells moved', len(PANEL_B_IDS), 'added', len(d.cells))
