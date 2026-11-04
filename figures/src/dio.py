"""Tiny draw.io (mxGraph XML) writer with explicit coordinates for every element.

Canvas unit: 1 px. The figure is designed on an 1800 px wide canvas that prints at
183 mm, so 1 px = 0.1017 mm = 0.288 pt. Text sizes: 18 px = 5.2 pt, 21 px = 6.0 pt,
24 px = 6.9 pt, 28 px = 8.1 pt. Strokes: 1.25 px = 0.36 pt, 1.75 px = 0.5 pt.
"""
from xml.sax.saxutils import escape

FONT = 'Helvetica'
INK = '#000000'        # all text black (Nature)
LINE = '#262A31'       # workflow lines
PX_PER_PT = 1 / 0.288


def pt(points):
    """Pixels for a size in printed points."""
    return round(points * PX_PER_PT, 2)


class Doc:
    def __init__(self, width, height, name='Figure'):
        self.width, self.height, self.name = width, height, name
        self.cells = []  # xml strings
        self.n = 0

    def _id(self, prefix):
        self.n += 1
        return f'{prefix}{self.n}'

    # -- vertices ---------------------------------------------------------
    def rect(self, x, y, w, h, fill='#FFFFFF', stroke=LINE, sw=1.25, rounded=0, arc=10,
             dashed=False, label='', fs=21, fc=INK, bold=False, align='center',
             valign='middle', spacing=2, spacing_left=0, spacing_top=0, opacity=100,
             parent='1', prefix='r', extra=''):
        style = (f'rounded={1 if rounded else 0};absoluteArcSize=1;arcSize={arc};whiteSpace=wrap;html=1;'
                 f'fillColor={fill};strokeColor={stroke};strokeWidth={sw};fontFamily={FONT};'
                 f'fontSize={fs};fontColor={fc};fontStyle={1 if bold else 0};align={align};'
                 f'verticalAlign={valign};spacing={spacing};spacingLeft={spacing_left};'
                 f'spacingTop={spacing_top};')
        if dashed:
            style += 'dashed=1;dashPattern=5 4;'
        if opacity != 100:
            style += f'opacity={opacity};'
        style += extra
        cid = self._id(prefix)
        self.cells.append(
            f'<mxCell id="{cid}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" '
            f'vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
            f'as="geometry"/></mxCell>')
        return cid

    def text(self, x, y, w, h, label, fs=21, fc=INK, bold=False, align='left',
             valign='middle', parent='1', prefix='t'):
        style = (f'text;html=1;strokeColor=none;fillColor=none;align={align};verticalAlign={valign};'
                 f'whiteSpace=wrap;fontFamily={FONT};fontSize={fs};fontColor={fc};'
                 f'fontStyle={1 if bold else 0};spacing=0;spacingLeft=0;spacingTop=0;')
        cid = self._id(prefix)
        self.cells.append(
            f'<mxCell id="{cid}" value="{escape(label, {chr(34): "&quot;"})}" style="{style}" '
            f'vertex="1" parent="{parent}"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" '
            f'as="geometry"/></mxCell>')
        return cid

    def ellipse(self, x, y, w, h, fill='#FFFFFF', stroke=LINE, sw=1.25, label='', fs=21,
                bold=False, parent='1'):
        style = (f'ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor={fill};strokeColor={stroke};'
                 f'strokeWidth={sw};fontFamily={FONT};fontSize={fs};fontColor={INK};'
                 f'fontStyle={1 if bold else 0};')
        cid = self._id('e')
        self.cells.append(
            f'<mxCell id="{cid}" value="{escape(label)}" style="{style}" vertex="1" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def polygon(self, pts, fill='#FFFFFF', stroke=LINE, sw=1, parent='1'):
        """A flat polygon through absolute points (draw.io basic polygon with polyCoords)."""
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, y0, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
        coords = ','.join(f'[{(x - x0) / w:.4f},{(y - y0) / h:.4f}]' for x, y in pts)
        style = (f'shape=mxgraph.basic.polygon;polyCoords=[{coords}];polyline=0;fillColor={fill};'
                 f'strokeColor={stroke};strokeWidth={sw};html=1;')
        cid = self._id('y')
        self.cells.append(f'<mxCell id="{cid}" value="" style="{style}" vertex="1" parent="{parent}">'
                          f'<mxGeometry x="{x0}" y="{y0}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    def bar3d(self, x, y, w, h, fill, top, side, stroke=LINE, sw=1, d=5, parent='1'):
        """An extruded bar: front face plus top and right faces offset by d."""
        self.polygon([(x, y), (x + d, y - d), (x + w + d, y - d), (x + w, y)], fill=top, stroke=stroke, sw=sw, parent=parent)
        self.polygon([(x + w, y), (x + w + d, y - d), (x + w + d, y + h - d), (x + w, y + h)], fill=side, stroke=stroke, sw=sw, parent=parent)
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, parent=parent)

    def group(self, x, y, w, h, parent='1'):
        cid = self._id('g')
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="group" vertex="1" connectable="0" parent="{parent}">'
            f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
        return cid

    # -- edges ------------------------------------------------------------
    def edge(self, points, stroke=LINE, sw=1.75, dashed=False, arrow='block', start_arrow=None,
             parent='1', opacity=100):
        """Polyline through points; first and last are the end points."""
        style = (f'edgeStyle=none;html=1;rounded=0;strokeColor={stroke};strokeWidth={sw};'
                 f'endArrow={arrow};endFill={1 if arrow in ("block", "classic") else 0};'
                 f'startArrow={start_arrow or "none"};startFill={1 if start_arrow in ("block", "classic") else 0};'
                 f'endSize=5;startSize=5;')
        if dashed:
            style += 'dashed=1;dashPattern=5 4;'
        if opacity != 100:
            style += f'opacity={opacity};'
        cid = self._id('a')
        (x0, y0), (x1, y1) = points[0], points[-1]
        mids = ''.join(f'<mxPoint x="{x}" y="{y}"/>' for x, y in points[1:-1])
        arr = f'<Array as="points">{mids}</Array>' if mids else ''
        self.cells.append(
            f'<mxCell id="{cid}" value="" style="{style}" edge="1" parent="{parent}">'
            f'<mxGeometry relative="1" as="geometry"><mxPoint x="{x0}" y="{y0}" as="sourcePoint"/>'
            f'<mxPoint x="{x1}" y="{y1}" as="targetPoint"/>{arr}</mxGeometry></mxCell>')
        return cid

    def line(self, points, **kw):
        kw.setdefault('arrow', 'none')
        return self.edge(points, **kw)

    # -- pixel sprites ----------------------------------------------------
    def sprite(self, grid, palette, x, y, px, parent='1', overlap=0.15):
        """A grid of characters -> one group of merged pixel runs. '.' is transparent."""
        h = len(grid); w = max(len(r) for r in grid)
        gid = self.group(x, y, w * px, h * px, parent=parent)
        for r, row in enumerate(grid):
            c = 0
            while c < len(row):
                ch = row[c]
                if ch == '.' or ch == ' ':
                    c += 1; continue
                run = 1
                while c + run < len(row) and row[c + run] == ch:
                    run += 1
                fill = palette[ch]
                self.cells.append(
                    f'<mxCell id="{self._id("p")}" value="" style="rounded=0;whiteSpace=wrap;html=1;'
                    f'fillColor={fill};strokeColor=none;" vertex="1" parent="{gid}">'
                    f'<mxGeometry x="{c * px}" y="{r * px}" width="{run * px + overlap}" '
                    f'height="{px + overlap}" as="geometry"/></mxCell>')
                c += run
        return gid

    # -- output -----------------------------------------------------------
    def save(self, path):
        body = '\n'.join(self.cells)
        xml = (f'<?xml version="1.0" encoding="utf-8"?>\n'
               f'<mxfile host="normclinic-figures" agent="generated by figures/src">\n'
               f'<diagram id="{self.name.lower()}" name="{self.name}">\n'
               f'<mxGraphModel dx="0" dy="0" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" '
               f'arrows="1" fold="0" page="1" pageScale="1" pageWidth="{self.width}" '
               f'pageHeight="{self.height}" math="0" shadow="0">\n<root>\n'
               f'<mxCell id="0"/>\n<mxCell id="1" parent="0"/>\n{body}\n'
               f'</root>\n</mxGraphModel>\n</diagram>\n</mxfile>\n')
        open(path, 'w', encoding='utf-8').write(xml)
        return path
