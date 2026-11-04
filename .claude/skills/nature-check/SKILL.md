---
name: nature-check
description: Check the NormClinic manuscript and its figures against Nature journal rules. The text check counts the words of the abstract, main text (introduction, Results, Discussion), Methods and each figure legend in main.tex against the target journal's limits, and counts display items, Extended Data items and references. The figure check reads figure PDFs and reports width, height, fonts, text sizes, panel labels, text colour and line widths against Nature's figure guide, with a PNG preview. Use it after editing text in main.tex, before reporting a writing task as done, whenever a figure is added to or replaced in figures/, before submission, and whenever someone asks how long the paper is, whether it fits the word limit, or whether a figure meets Nature's requirements, even if they do not name this check.
---

# Nature check

One script, `scripts/check.py` in this skill's folder, does both checks. Run it from the repository root with the `normclinic-writing` conda environment, which has PyMuPDF for the figure check:

```bash
PY=/home/tyren/miniconda3/envs/normclinic-writing/bin/python
$PY .claude/skills/nature-check/scripts/check.py text                    # Nature Machine Intelligence
$PY .claude/skills/nature-check/scripts/check.py text --journal ncomms   # or nhb
$PY .claude/skills/nature-check/scripts/check.py figure figures/<name>.pdf
$PY .claude/skills/nature-check/scripts/check.py figure --width 183 figures/<name>.pdf
```

Both exit with status 1 when something is outside the limits.

## Text check

The script splits `main.tex` at its `\section*` headings. Text between the abstract and the first heading is the introduction, because Nature Machine Intelligence and Nature Human Behaviour print it without a heading; a `\section*{Introduction}` is counted the same way. The main text that the journals limit is the introduction, Results and Discussion. Counts leave out math, citations, labels, cross-references and figure and table environments. Subheadings are counted, so the totals err slightly high. Each legend is counted on its own. References are counted from `build/main.bbl`, so build with `latexmk` first.

The target journal has not been chosen, so the default is Nature Machine Intelligence, whose limits are the tightest of the candidates. The limits and their sources are in `docs/nature_style.md`. Once the journal is chosen, change `DEFAULT_JOURNAL` in `check.py`.

When a count is over its limit, report the section and by how much. Cutting text is the author's decision, so suggest where to cut only if asked.

## Figure check

Every page of a figure PDF is checked at its final printed size: width 89, 120, 136 or 183 mm; height at most 170 mm; Arial or Helvetica, embedded, no Type 3 fonts; text 5-7 pt and panel labels 8 pt bold lowercase; black text; strokes at least 0.25 pt. A 300 dpi PNG preview goes to `build/previews/<name>.png`.

Pass `--width <mm>` for a PDF whose page is not the printed size, such as a draw.io export of a larger canvas. The script then scales every size to that width before checking. Without it, a figure drawn at 260 mm is reported as too wide with text too large, which says nothing about how it will print.

Some of Nature's rules need eyes. After the script runs, open the preview with Read and check that:

- the palette is colour-blind safe and colour is never the only cue (markers, line styles or direct labels carry it too);
- panel labels sit at the top left of their panels, in order;
- each condition has the colour it has in every other figure (`COLORS` in the code repo's `analysis/style.py`);
- there are no gridlines, shadows, gradients or 3D effects.

Then read the figure's legend in `main.tex`. It should say what the centre values and error bars show, give n and what it counts, and name the tests.

## Reporting

Give the counts or the issues found, then what you saw in the preview. Data figures are drawn in the code repo, which stays read-only unless the user asks for a change there, so report a figure problem without fixing it at the source.
