#!/usr/bin/env python
"""Check the manuscript and its figures against Nature journal rules.

  check.py text [--journal nmi|nhb|ncomms]    word counts, display items, references
  check.py figure [--width MM] PDF [PDF ...]   size, fonts, text, lines; PNG preview

Exit status 1 means something is outside the limits. The figure check needs
PyMuPDF, installed in the normclinic-writing conda environment.
"""
import argparse
from collections import defaultdict
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # .claude/skills/nature-check/scripts/
DEFAULT_JOURNAL = 'nmi'  # target not chosen yet; NMI's limits are the tightest

# Article limits, checked 2026-11-04 (docs/nature_style.md). None: no stated limit.
LIMITS = {
    'nmi': dict(name='Nature Machine Intelligence', abstract=150, main=3500,
                display=6, extended=10, legend=None, methods=None, refs=50),
    'nhb': dict(name='Nature Human Behaviour', abstract=150, main=5000,
                display=8, extended=None, legend=None, methods=None, refs=None),
    'ncomms': dict(name='Nature Communications', abstract=200, main=5000,
                   display=10, extended=None, legend=350, methods=3000, refs=70),
}
MAIN = ('Introduction', 'Results', 'Discussion')
MAIN_FLOATS = ('figure', 'figure*', 'table', 'table*')
EXT_FLOATS = ('extfigure', 'exttable')
# Commands whose first argument is not prose.
DROP = ('cite', 'citep', 'citet', 'nocite', 'ref', 'eqref', 'label', 'includegraphics',
        'natfig', 'url', 'input', 'include', 'bibliography', 'bibliographystyle',
        'begin', 'end', 'vspace', 'hspace', 'href')

# Nature's figure guide.
PT_PER_MM = 72 / 25.4
WIDTHS = (89, 120, 136, 183)  # mm
MAX_HEIGHT = 170  # mm
TEXT_SIZES = (5, 7)  # pt
PANEL_LABEL_SIZE = 8  # pt
MIN_LINE_WIDTH = 0.25  # pt
FONTS = ('arial', 'helvetica')
TOLERANCE = 0.05  # pt, for rounding in exported sizes


# Text ------------------------------------------------------------------------

def strip_comments(text):
    return re.sub(r'(?<!\\)%.*', '', text)


def group_end(text, start):
    """Index just past the brace group opening at text[start] == '{'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == '{' and text[i - 1] != '\\':
            depth += 1
        elif text[i] == '}' and text[i - 1] != '\\':
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def command_args(text, name):
    """(start, end, argument) for each \\name[...]{argument} in text."""
    for match in re.finditer(r'\\' + re.escape(name) + r'\*?\s*(\[[^\]]*\])?\s*(?=\{)', text):
        end = group_end(text, match.end())
        yield match.start(), end, text[match.end() + 1:end - 1]


def environments(text, names):
    pattern = r'\\begin\{(%s)\}(.*?)\\end\{\1\}' % '|'.join(re.escape(n) for n in names)
    return list(re.finditer(pattern, text, flags=re.S))


def without_floats(text):
    for env in reversed(environments(text, MAIN_FLOATS + EXT_FLOATS)):
        text = text[:env.start()] + ' ' + text[env.end():]
    return text


def words(text):
    """Words of prose in a LaTeX fragment, after removing math and non-prose commands."""
    text = re.sub(r'\\\[.*?\\\]|\$\$.*?\$\$|\\\(.*?\\\)|(?<!\\)\$.*?(?<!\\)\$', ' ', text, flags=re.S)
    text = re.sub(r'\\begin\{(equation|align|gather|multline)(\*?)\}.*?\\end\{\1\2\}', ' ',
                  text, flags=re.S)
    for name in DROP:
        for start, end, _ in reversed(list(command_args(text, name))):
            text = text[:start] + ' ' + text[end:]
    text = re.sub(r'\\[A-Za-z@]+\*?(\[[^\]]*\])?', ' ', text)  # keeps a command's text argument
    text = text.replace('~', ' ')
    return len(re.findall(r"[A-Za-z0-9]+(?:['\-.][A-Za-z0-9]+)*", text))


def split_manuscript(tex):
    """The abstract and {heading: text} of main.tex. Text between the abstract and the
    first heading is the introduction, which NMI and NHB print without a heading."""
    body = strip_comments(tex).split(r'\begin{document}', 1)[-1].split(r'\end{document}', 1)[0]
    abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', body, flags=re.S)
    rest = body[abstract.end():] if abstract else body
    parts = re.split(r'\\section\*?\{([^}]*)\}', rest)
    sections = defaultdict(str, Introduction=parts[0])
    for name, text in zip(parts[1::2], parts[2::2]):
        sections[name.strip()] += text
    return (abstract.group(1) if abstract else ''), sections


def row(label, count, limit, approx=False):
    bound = '' if limit is None else f" / {'~' if approx else ''}{limit}"
    over = limit is not None and count > limit
    note = f'   OVER by {count - limit}' if over else ''
    print(f'  {label:<18}{count:>6}{bound}{note}')
    return over


def check_text(journal):
    limit = LIMITS[journal]
    abstract, sections = split_manuscript((ROOT / 'main.tex').read_text(encoding='utf-8'))
    main_counts = {name: words(without_floats(sections[name])) for name in MAIN}
    floats_text = ''.join(text for name, text in sections.items() if name != 'Extended Data')
    everything = ''.join(sections.values())

    print(f"{limit['name']} limits (docs/nature_style.md)")
    over = row('abstract', words(abstract), limit['abstract'])
    over |= row('main text', sum(main_counts.values()), limit['main'])
    print('    ' + ', '.join(f'{name} {count}' for name, count in main_counts.items()))
    over |= row('Methods', words(without_floats(sections['Methods'])), limit['methods'],
                approx=True)
    over |= row('display items', len(environments(floats_text, MAIN_FLOATS)), limit['display'])
    over |= row('Extended Data', len(environments(everything, EXT_FLOATS)), limit['extended'])

    bbl = ROOT / 'build' / 'main.bbl'
    if bbl.exists():
        refs = bbl.read_text(encoding='utf-8').count(r'\bibitem')
        over |= row('references', refs, limit['refs'], approx=True)
        print('    from build/main.bbl; rebuild for a current count')
    else:
        print('  references        build main.tex first (no build/main.bbl)')

    captions = []
    for env in environments(everything, MAIN_FLOATS + EXT_FLOATS):
        label = next((arg for _, _, arg in command_args(env.group(2), 'label')), env.group(1))
        captions += [(label, words(text)) for _, _, text in command_args(env.group(2), 'caption')]
    if captions:
        print('legends (words)')
        for label, count in captions:
            over |= row(label, count, limit['legend'])
    return over


# Figures ---------------------------------------------------------------------

def examples(texts, limit=3):
    unique = list(dict.fromkeys(texts))
    return ', '.join(repr(text[:25]) for text in unique[:limit]) + (', ...' if len(unique) > limit else '')


def check_page(page, width_mm=None):
    """Issues on one page at its final size (scaled to width_mm when given)."""
    issues = []
    width, height = page.rect.width / PT_PER_MM, page.rect.height / PT_PER_MM
    scale = width_mm / width if width_mm else 1.0
    note = f' (checked at {width * scale:.0f} x {height * scale:.0f} mm, scale {scale:.3f})' \
        if width_mm else ''
    print(f'  size {width:.1f} x {height:.1f} mm{note}')
    width, height = width * scale, height * scale
    if not any(abs(width - allowed) <= 1 for allowed in WIDTHS):
        issues.append(f'width {width:.1f} mm is not one of {WIDTHS} mm')
    if height > MAX_HEIGHT + 1:
        issues.append(f'height {height:.1f} mm exceeds {MAX_HEIGHT} mm')

    for _, ext, kind, basefont, *_ in page.get_fonts(full=True):
        name = basefont.split('+')[-1]
        if kind == 'Type3':
            issues.append(f'font {name} is Type 3: its text is not editable')
        if ext == 'n/a':
            issues.append(f'font {name} is not embedded')
        if not any(font in name.lower() for font in FONTS):
            issues.append(f'font {name} is not Arial or Helvetica')

    bad_size, coloured, plain_labels = defaultdict(list), defaultdict(list), []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                text, size = span['text'].strip(), round(span['size'] * scale, 2)
                if not text:
                    continue
                bold = span['flags'] & 16 or 'bold' in span['font'].lower()
                if len(text) == 1 and text.islower() and abs(size - PANEL_LABEL_SIZE) <= TOLERANCE:
                    if not bold:
                        plain_labels.append(text)
                elif not TEXT_SIZES[0] - TOLERANCE <= size <= TEXT_SIZES[1] + TOLERANCE:
                    bad_size[size].append(text)
                if span['color'] not in (0x000000, 0xFFFFFF):
                    coloured[f'#{span["color"]:06x}'].append(text)
    for size, texts in sorted(bad_size.items()):
        issues.append(f'{len(texts)} text span(s) at {size:g} pt, outside '
                      f'{TEXT_SIZES[0]}-{TEXT_SIZES[1]} pt: {examples(texts)}')
    for colour, texts in coloured.items():
        issues.append(f'{len(texts)} text span(s) coloured {colour}; use black: {examples(texts)}')
    if plain_labels:
        issues.append(f'panel label(s) not bold: {examples(plain_labels)}')

    widths = [path['width'] * scale for path in page.get_drawings()
              if path['type'] in ('s', 'fs') and path.get('width') is not None]
    thin = [w for w in widths if w < MIN_LINE_WIDTH - 0.01]
    if thin:
        issues.append(f'{len(thin)} stroke(s) thinner than {MIN_LINE_WIDTH} pt '
                      f'(thinnest {min(thin):.2f} pt; 0 is a hairline)')
    return list(dict.fromkeys(issues))


def check_figures(pdfs, width_mm, out):
    import pymupdf  # only the figure check needs it

    out.mkdir(parents=True, exist_ok=True)
    failed = False
    for pdf in pdfs:
        print(pdf)
        with pymupdf.open(pdf) as doc:
            for number, page in enumerate(doc):
                issues = check_page(page, width_mm)
                for issue in issues:
                    print(f'  ISSUE {issue}')
                if not issues:
                    print('  no issues')
                failed |= bool(issues)
                suffix = f'-p{number + 1}' if len(doc) > 1 else ''
                preview = out / f'{pdf.stem}{suffix}.png'
                page.get_pixmap(dpi=300).save(preview)
                print(f'  preview {preview}')
    return failed


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    text = commands.add_parser('text', help='word counts and display items of main.tex')
    text.add_argument('--journal', choices=LIMITS, default=DEFAULT_JOURNAL)
    figure = commands.add_parser('figure', help='figure PDFs against the figure guide')
    figure.add_argument('pdfs', nargs='+', type=Path)
    figure.add_argument('--width', type=float, metavar='MM',
                        help='check as if the figure were scaled to this final width')
    figure.add_argument('--out', type=Path, default=ROOT / 'build' / 'previews',
                        help='directory for PNG previews (default: build/previews)')
    args = parser.parse_args()
    if args.command == 'text':
        failed = check_text(args.journal)
    else:
        failed = check_figures(args.pdfs, args.width, args.out)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
