# Figure sources

Scripts that produced the current `figures/framework/normclinic_framework.drawio`
and the previews used to check it. They need Python 3 (standard library only,
PyMuPDF for the PDF check) and Node with Playwright for rendering.

| File | Role |
|---|---|
| `restyle_framework.py` | Transformed the v6 draw.io file (in git history before this commit) into the current one: pixel-style icons, compact memory band, flat actor-critic, no formula, Nature text sizes. Kept for the record; edit the current `.drawio` directly from here on. |
| `dio.py` | Small writer for draw.io XML with explicit coordinates (rects, text, edges, polygons, extruded bars, pixel sprites). |
| `palette.py`, `pix.py`, `sprites.json` | Colours (Wong palette plus tints) and the pixel sprites (robot, RL agent, environments). |
| `drawio2svg.py` | Approximate renderer of an uncompressed `.drawio` to SVG, for previews. Group containers draw nothing, as in draw.io. Text wrapping is approximate. |
| `rast.js`, `svg2pdf.js` | Rasterise an SVG (Playwright/Chromium) and print it to a PDF page of a given width in mm. |

```bash
python3 figures/src/drawio2svg.py figures/framework/normclinic_framework.drawio /tmp/fw.svg
node figures/src/svg2pdf.js /tmp/fw.svg figures/framework/normclinic_framework.pdf 183
python3 .claude/skills/nature-check/scripts/check.py figure figures/framework/normclinic_framework.pdf
```

The PDF printed here embeds whatever font the machine maps Helvetica to. For
submission, export the PDF from draw.io on a machine with Arial or Helvetica
(File, Export as, PDF, crop, no page) so the font check passes.

Canvas scale: 1800 px = 183 mm, so 1 px = 0.288 pt. Text 18 px = 5.2 pt,
21 px = 6.0 pt, panel labels 27.8 px = 8.0 pt. Strokes at least 0.875 px.

Working rules kept from the review rounds:

- Group containers have no frame; every new element sets fill and stroke explicitly.
- No gradients or 3D effects; the extruded pilot bars are the one agreed exception.
- Dashed lines mean "reads"; reference lines are dotted.
- Three text sizes, all text black; line widths at least 0.25 pt, including inside embedded SVG icons.
- Size text boxes from the text; check text overlap and page clipping before delivery.
- Arrows into one card meet at one attachment point; panel-b edits move every `editable_layer` together.
- Run the nature-check figure check and inspect the 300 dpi preview block by block before delivering.
