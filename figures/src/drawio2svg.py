"""Minimal draw.io (uncompressed mxGraphModel) -> SVG renderer, for viewing layout."""
import re, html, sys, math
import xml.etree.ElementTree as ET

src = sys.argv[1]; out = sys.argv[2]
tree = ET.parse(src); root = tree.getroot()
model = root.find('.//mxGraphModel')
pw = float(model.get('pageWidth', 1800)); ph = float(model.get('pageHeight', 975))
cells = {c.get('id'): c for c in model.iter('mxCell')}

def style_of(c):
    st = c.get('style') or ''
    d = {}
    for part in st.split(';'):
        if not part: continue
        if '=' in part:
            k, v = part.split('=', 1); d[k] = v
        else:
            d[part] = '1'
    return d

def geom(c):
    g = c.find('mxGeometry')
    if g is None: return None
    return dict(x=float(g.get('x', 0)), y=float(g.get('y', 0)), w=float(g.get('width', 0)), h=float(g.get('height', 0)), el=g)

def abs_pos(c):
    """Absolute x,y of a vertex, following parent chain."""
    g = geom(c)
    if g is None: return 0, 0, 0, 0
    x, y = g['x'], g['y']
    p = cells.get(c.get('parent'))
    while p is not None and p.get('vertex') == '1':
        pg = geom(p)
        if pg: x += pg['x']; y += pg['y']
        p = cells.get(p.get('parent'))
    return x, y, g['w'], g['h']

def esc(s): return html.escape(s, quote=True)

def label_lines(v):
    v = html.unescape(v or '')
    v = re.sub(r'<br\s*/?>', '\n', v, flags=re.I)
    v = re.sub(r'</div>|</p>', '\n', v, flags=re.I)
    v = re.sub(r'<[^>]+>', '', v)
    v = html.unescape(v)
    lines = [re.sub(r'\s+', ' ', l).strip() for l in v.split('\n')]
    return [l for l in lines if l]

svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {pw} {ph}" width="{pw}" height="{ph}" font-family="Helvetica, Arial, sans-serif">']
svg.append(f'<rect width="{pw}" height="{ph}" fill="#fff"/>')

# order: document order
order = [c for c in model.iter('mxCell') if c.get('id') not in ('0', '1')]

_FONTS = {}
def _measure(size, bold=False):
    """Text width in px at a font size, with Liberation Sans (Arial metrics) when PIL is available."""
    try:
        from PIL import ImageFont
        key = (round(size, 2), bold)
        if key not in _FONTS:
            path = '/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf' % ('Bold' if bold else 'Regular')
            _FONTS[key] = ImageFont.truetype(path, size)
        f = _FONTS[key]
        return lambda t: f.getlength(t)
    except Exception:
        return lambda t: len(t) * size * 0.5

def draw_vertex(c):
    st = style_of(c)
    if (c.get('style') or '').strip() == 'group' or st.get('group') == '1':
        return []   # a group container has no visible frame in draw.io
    x, y, w, h = abs_pos(c)
    fill = st.get('fillColor', '#ffffff'); stroke = st.get('strokeColor', '#000000')
    if fill == 'none': fill = 'none'
    sw = st.get('strokeWidth', '1')
    op = float(st.get('opacity', 100)) / 100
    dash = ' stroke-dasharray="6 4"' if st.get('dashed') == '1' else ''
    g = []
    img = st.get('image')
    shape = st.get('shape', '')
    if img and img.startswith('data:'):
        href = img.replace('data:image/svg+xml,', 'data:image/svg+xml;base64,') if not ';base64,' in img and img.startswith('data:image/svg+xml,') else img
        g.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="{esc(href)}" style="image-rendering:pixelated" preserveAspectRatio="xMidYMid meet"/>')
    elif shape == 'image' or 'text' in st and 'strokeColor' not in st and 'fillColor' not in st:
        pass
    elif shape == 'mxgraph.basic.polygon' and 'polyCoords' in st:
        import json as _json
        coords = _json.loads(st['polyCoords'])
        pts = ' '.join(f'{x + cx * w},{y + cy * h}' for cx, cy in coords)
        g.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"/>')
    elif 'ellipse' in st or shape == 'ellipse':
        g.append(f'<ellipse cx="{x+w/2}" cy="{y+h/2}" rx="{w/2}" ry="{h/2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{dash}/>')
    elif shape in ('rhombus',):
        pts = f"{x+w/2},{y} {x+w},{y+h/2} {x+w/2},{y+h} {x},{y+h/2}"
        g.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{dash}/>')
    elif shape in ('line',) or st.get('line') == '1':
        g.append(f'<line x1="{x}" y1="{y+h/2}" x2="{x+w}" y2="{y+h/2}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
    elif shape.startswith('mxgraph.') or shape in ('triangle','hexagon','process','cylinder3','document','note','card','parallelogram','step','callout','or','xor','cloud','trapezoid','tape','umlActor','datastore','mxgraph.basic.diag_round_rect'):
        g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}" rx="3"{dash}/>')
        g.append(f'<text x="{x+2}" y="{y+8}" font-size="7" fill="#c00">{esc(shape)}</text>')
    elif 'text' in st and fill in ('none', '#ffffff') and st.get('strokeColor','none') == 'none' and 'fillColor' not in st:
        pass
    else:
        rx = 0
        if st.get('rounded') == '1':
            arc = float(st.get('arcSize', 15))
            rx = arc if st.get('absoluteArcSize') == '1' else min(w, h) * arc / 100 / 2
        if fill != 'none' or stroke != 'none':
            g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{dash}/>')
    # label
    lines = label_lines(c.get('value'))
    if lines and st.get('whiteSpace') == 'wrap':
        fs0 = float(st.get('fontSize', 12))
        avail = max(w - 2 * float(st.get('spacing', 2)) - float(st.get('spacingLeft', 0)), 10)
        bold = int(st.get('fontStyle', 0)) & 1
        measure = _measure(fs0, bold)
        wrapped = []
        for l in lines:
            words = l.split(' '); cur = ''
            for wd in words:
                trial = (cur + ' ' + wd).strip()
                if cur and measure(trial) > avail:
                    wrapped.append(cur); cur = wd
                else:
                    cur = trial
            if cur: wrapped.append(cur)
        lines = wrapped
    if lines:
        fs = float(st.get('fontSize', 12)); fc = st.get('fontColor', '#000000')
        fst = int(st.get('fontStyle', 0)); bold = ' font-weight="bold"' if fst & 1 else ''; ital = ' font-style="italic"' if fst & 2 else ''
        align = st.get('align', 'center'); valign = st.get('verticalAlign', 'middle')
        lp = float(st.get('labelPosition' , 'center') == 'left' and -1 or 0)
        spacing = float(st.get('spacing', 2)); sl = float(st.get('spacingLeft', 0)); sr = float(st.get('spacingRight', 0)); stp = float(st.get('spacingTop', 0)); sb = float(st.get('spacingBottom', 0))
        lx = {'left': x + spacing + sl, 'right': x + w - spacing - sr}.get(align, x + w / 2)
        anchor = {'left': 'start', 'right': 'end'}.get(align, 'middle')
        labpos = st.get('labelPosition'); vlabpos = st.get('verticalLabelPosition')
        if labpos == 'right': lx = x + w + spacing; anchor = 'start'
        if labpos == 'left': lx = x - spacing; anchor = 'end'
        n = len(lines); lh = fs * 1.2
        if vlabpos == 'bottom': y0 = y + h + fs
        elif vlabpos == 'top': y0 = y - (n - 1) * lh - 4
        elif valign == 'top': y0 = y + stp + spacing + fs
        elif valign == 'bottom': y0 = y + h - sb - spacing - (n - 1) * lh - fs * 0.25
        else: y0 = y + h / 2 - (n - 1) * lh / 2 + fs * 0.35
        bg = st.get('labelBackgroundColor')
        for i, l in enumerate(lines):
            if bg and bg != 'none':
                tw = len(l) * fs * 0.52
                bx = lx - (tw / 2 if anchor == 'middle' else (tw if anchor == 'end' else 0))
                g.append(f'<rect x="{bx-2}" y="{y0 + i*lh - fs}" width="{tw+4}" height="{fs*1.25}" fill="{bg}"/>')
            g.append(f'<text x="{lx}" y="{y0 + i*lh}" font-size="{fs}" fill="{fc}" text-anchor="{anchor}"{bold}{ital}>{esc(l)}</text>')
    return g

def port(c, X, Y):
    """Point on vertex c at relative (X,Y) in [0,1]."""
    x, y, w, h = abs_pos(c)
    return x + w * X, y + h * Y

def draw_edge(c):
    st = style_of(c)
    g = geom(c)
    pts = []
    sp = tp = None
    srcc = cells.get(c.get('source')); tgtc = cells.get(c.get('target'))
    if g is not None:
        for p in g['el'].findall('mxPoint'):
            if p.get('as') == 'sourcePoint': sp = (float(p.get('x', 0)), float(p.get('y', 0)))
            if p.get('as') == 'targetPoint': tp = (float(p.get('x', 0)), float(p.get('y', 0)))
        arr = g['el'].find('Array')
        if arr is not None:
            pts = [(float(p.get('x', 0)), float(p.get('y', 0))) for p in arr.findall('mxPoint')]
    # parent offset for edges inside groups
    ox = oy = 0
    p = cells.get(c.get('parent'))
    while p is not None and p.get('vertex') == '1':
        pg = geom(p)
        if pg: ox += pg['x']; oy += pg['y']
        p = cells.get(p.get('parent'))
    pts = [(px + ox, py + oy) for px, py in pts]
    if srcc is not None and srcc.get('vertex') == '1':
        X = float(st.get('exitX', 0.5)); Y = float(st.get('exitY', 0.5))
        if 'exitX' not in st:
            # aim at next point
            nxt = pts[0] if pts else (port(tgtc, 0.5, 0.5) if tgtc is not None and tgtc.get('vertex')=='1' else ((tp[0]+ox, tp[1]+oy) if tp else (0,0)))
            x, y, w, h = abs_pos(srcc); cx, cy = x+w/2, y+h/2
            dx, dy = nxt[0]-cx, nxt[1]-cy
            if abs(dx)*h > abs(dy)*w: X, Y = (1 if dx>0 else 0), 0.5
            else: X, Y = 0.5, (1 if dy>0 else 0)
        sp = port(srcc, X, Y)
    elif sp: sp = (sp[0]+ox, sp[1]+oy)
    if tgtc is not None and tgtc.get('vertex') == '1':
        X = float(st.get('entryX', 0.5)); Y = float(st.get('entryY', 0.5))
        if 'entryX' not in st:
            prv = pts[-1] if pts else (sp if sp else (0,0))
            x, y, w, h = abs_pos(tgtc); cx, cy = x+w/2, y+h/2
            dx, dy = prv[0]-cx, prv[1]-cy
            if abs(dx)*h > abs(dy)*w: X, Y = (1 if dx>0 else 0), 0.5
            else: X, Y = 0.5, (1 if dy>0 else 0)
        tp = port(tgtc, X, Y)
    elif tp: tp = (tp[0]+ox, tp[1]+oy)
    if sp is None or tp is None: return []
    allpts = [sp] + pts + [tp]
    # orthogonal edge style: insert elbows if no waypoints
    es = st.get('edgeStyle', '')
    if not pts and 'orthogonal' in es or (not pts and 'elbow' in es):
        (x1, y1), (x2, y2) = sp, tp
        if st.get('elbow') == 'vertical':
            my = (y1 + y2) / 2; allpts = [sp, (x1, my), (x2, my), tp]
        else:
            mx = (x1 + x2) / 2; allpts = [sp, (mx, y1), (mx, y2), tp]
    stroke = st.get('strokeColor', '#000000'); sw = st.get('strokeWidth', '1')
    dash = ' stroke-dasharray="6 4"' if st.get('dashed') == '1' else ''
    op = float(st.get('opacity', 100)) / 100
    d = 'M ' + ' L '.join(f'{px:.1f},{py:.1f}' for px, py in allpts)
    out = [f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" opacity="{op}"{dash}/>']
    if st.get('endArrow', 'classic') not in ('none', ''):
        (x1, y1), (x2, y2) = allpts[-2], allpts[-1]
        ang = math.atan2(y2 - y1, x2 - x1); L = 6 + 2*float(sw)
        a1 = (x2 - L*math.cos(ang - 0.4), y2 - L*math.sin(ang - 0.4)); a2 = (x2 - L*math.cos(ang + 0.4), y2 - L*math.sin(ang + 0.4))
        out.append(f'<polygon points="{x2},{y2} {a1[0]},{a1[1]} {a2[0]},{a2[1]}" fill="{stroke}" opacity="{op}"/>')
    if st.get('startArrow', 'none') not in ('none', ''):
        (x1, y1), (x2, y2) = allpts[1], allpts[0]
        ang = math.atan2(y2 - y1, x2 - x1); L = 6 + 2*float(sw)
        a1 = (x2 - L*math.cos(ang - 0.4), y2 - L*math.sin(ang - 0.4)); a2 = (x2 - L*math.cos(ang + 0.4), y2 - L*math.sin(ang + 0.4))
        out.append(f'<polygon points="{x2},{y2} {a1[0]},{a1[1]} {a2[0]},{a2[1]}" fill="{stroke}" opacity="{op}"/>')
    lines = label_lines(c.get('value'))
    if lines:
        fs = float(st.get('fontSize', 11)); fc = st.get('fontColor', '#000000')
        # midpoint of polyline
        tot = sum(math.dist(allpts[i], allpts[i+1]) for i in range(len(allpts)-1)); acc = 0; mid = allpts[0]
        for i in range(len(allpts)-1):
            seg = math.dist(allpts[i], allpts[i+1])
            if acc + seg >= tot/2:
                f = (tot/2 - acc)/seg if seg else 0
                mid = (allpts[i][0] + f*(allpts[i+1][0]-allpts[i][0]), allpts[i][1] + f*(allpts[i+1][1]-allpts[i][1])); break
            acc += seg
        for i, l in enumerate(lines):
            out.append(f'<text x="{mid[0]}" y="{mid[1] - 4 + i*fs*1.2}" font-size="{fs}" fill="{fc}" text-anchor="middle" paint-order="stroke" stroke="#fff" stroke-width="3">{esc(l)}</text>')
    return out

# edges that are children of vertices (labels of edges) -> edge labels: handle cells with vertex=1 and connectable=0 whose parent is an edge
for c in order:
    if c.get('vertex') == '1':
        par = cells.get(c.get('parent'))
        if par is not None and par.get('edge') == '1':
            continue  # skip edge-attached labels for simplicity
        svg.extend(draw_vertex(c))
    elif c.get('edge') == '1':
        svg.extend(draw_edge(c))
svg.append('</svg>')
open(out, 'w').write('\n'.join(svg))
print('vertices', sum(1 for c in order if c.get('vertex')=='1'), 'edges', sum(1 for c in order if c.get('edge')=='1'))
