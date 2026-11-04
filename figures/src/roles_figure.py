"""Roles figure: role | abridged instruction | input and output keywords, tinted by who writes them.
Chip widths are measured from the text (Liberation Sans is metric-compatible with Arial/Helvetica).
1800 px = 183 mm."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import ImageFont
from dio import Doc, LINE
import palette as P
import pix

FONT = ImageFont.truetype('/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf', 18)
W = 1800
FSS, FSN = 18, 21
X_ROLE, X_P, X_P_END, X_K, X_K_END = 40, 236, 1160, 1200, 1760
LBL = 66
TOP, GAP = 60, 14
CHIP_H, CHIP_GAP, PAD = 26, 8, 10
d = Doc(W, 10, 'Roles')
ACCENT = {r: P.ROLE[r]['body'] for r in P.ROLE}
CHIP_STROKE = '#9AA0A8'
SRC = {'rl': '#EDE7DC', 'arbiter': P.ROLE['arbiter']['tint'], 'reviewer': P.ROLE['reviewer']['tint'],
       'advisor': P.ROLE['advisor']['tint'], 'designer': P.ROLE['designer']['tint'], 'env': '#FFFFFF'}
WRITER = {'goal measures': 'rl', 'latest interval': 'rl', 'course by norm': 'rl', 'pilot evaluation': 'rl',
          'difference from active': 'rl', 'environment': 'env', 'sandbox rules': 'env',
          'history summary': 'reviewer', 'diagnosis': 'reviewer', 'verdict': 'reviewer',
          'trial memory': 'advisor', 'advice': 'advisor',
          'active norm': 'designer', 'intent': 'designer', 'assess function': 'designer',
          'wait': 'arbiter', 'wake': 'arbiter', 'adopt': 'arbiter', 'keep': 'arbiter'}
DOC = ['.oooooooo....', '.owwwwwwoo...', '.owwwwwwowo..', '.owwwwwwoooo.', '.owwwwwwwwwo.', '.owllllllwwo.',
       '.owwwwwwwwwo.', '.owlllllllwo.', '.owwwwwwwwwo.', '.owlllllwwwo.', '.owwwwwwwwwo.', '.owllllllwwo.',
       '.owwwwwwwwwo.', '.ooooooooooo.', '.............']

def doc(x, y, colour, px=2):
    return d.sprite(DOC, {'o': P.OUTLINE, 'w': '#FFFFFF', 'l': colour}, x, y, px)

def robot(x, y, role, size=44):
    return d.sprite(pix.ROBOT, pix.robot_palette(P.ROLE[role]['body']), x, y, size / 12)

def chip_w(word):
    return int(FONT.getlength(word) + 18)

def text_lines(text, width):
    """Lines the text takes at 18 px in the given width, by greedy word wrap."""
    lines, cur = 1, ''
    for w in text.split(' '):
        trial = (cur + ' ' + w).strip()
        if FONT.getlength(trial) > width:
            lines += 1; cur = w
        else:
            cur = trial
    return lines

def draw_chips(x0, y0, words):
    x = x0
    for w in words:
        cw = chip_w(w)
        d.rect(x, y0, cw, CHIP_H, fill=SRC[WRITER[w]], stroke=CHIP_STROKE, sw=1, rounded=1, arc=3, label=w, fs=FSS)
        x += cw + CHIP_GAP
    return x - x0 - CHIP_GAP

def box(x, y, w, h, accent):
    d.rect(x, y, w, h, fill='#FFFFFF', stroke=LINE, sw=1.25, rounded=1, arc=6)
    d.rect(x, y + 6, 5, h - 12, fill=accent, stroke='none')

ROWS = [
 ('arbiter', 'Arbiter', 'gate',
  'Decide whether the design team should review training now. Answer wait while the goal measures are still improving, and wake once they have levelled off or are moving away from the goal. A plateau is not excused as early learning or as adaptation to a new norm.',
  ['goal measures', 'latest interval'], ['wait', 'wake']),
 ('reviewer', 'Reviewer', '',
  'You are the Reviewer. Keep a concise memory of the assessment principles tried so far, diagnose how the active norm’s assessments act, evaluate where training stands against the environment’s goal, and decide whether to keep, revise or replace the norm. You give no design advice.',
  ['history summary', 'course by norm', 'latest interval'], ['diagnosis', 'verdict']),
 ('advisor', 'Advisor', '',
  'You are the Advisor. The active norm will be changed. For each requested candidate, advise what it should implement and why, grounded in the diagnosis and in what earlier norms and pilots showed. State principles only, without writing a norm, formula or constants.',
  ['diagnosis', 'history summary', 'trial memory'], ['advice', 'trial memory']),
 ('designer', 'Designer', '',
  'You are the Designer. Implement the assigned task as a reputation norm that respects the assessment and sandbox contracts. State its principle as a self-contained intent and return exactly one assess function in JAX.',
  ['advice', 'active norm', 'environment', 'sandbox rules'], ['intent', 'assess function']),
 ('arbiter', 'Arbiter', 'adoption',
  'Choose the option whose measurements best meet the goal, the active norm included. Every option had the same adaptation and frozen-evaluation budget. Judge the measurements as they stand, without predicting future learning or choosing for exploration.',
  ['pilot evaluation', 'difference from active'], ['adopt', 'keep']),
]

chip_width = X_K_END - X_K - LBL - 2 * PAD - 6
text_width = X_P_END - X_P - 64
y = TOP
for role, name, call, instruction, inputs, outputs in ROWS:
    for words in (inputs, outputs):
        need = sum(chip_w(w) for w in words) + CHIP_GAP * (len(words) - 1)
        assert need <= chip_width, (words, need, chip_width)
    chips_h = 2 * CHIP_H + CHIP_GAP + 2 * PAD + 4
    h = max(chips_h, text_lines(instruction, text_width) * 22 + 14)
    robot(X_ROLE + 10, y + h / 2 - 22, role)
    d.text(X_ROLE + 64, y + h / 2 - (24 if call else 13), 150, 26, name, fs=FSN, bold=True)
    if call:
        d.text(X_ROLE + 64, y + h / 2, 150, 22, call, fs=FSS)
    box(X_P, y, X_P_END - X_P, h, ACCENT[role])
    doc(X_P + 16, y + (h - 30) / 2, ACCENT[role])
    d.text(X_P + 50, y + 6, text_width, h - 12, instruction, fs=FSS, valign='middle')
    box(X_K, y, X_K_END - X_K, h, ACCENT[role])
    cy = y + (h - (2 * CHIP_H + CHIP_GAP + 4)) / 2
    d.text(X_K + 14, cy, LBL - 10, CHIP_H, 'Input', fs=FSS)
    draw_chips(X_K + LBL + 6, cy, inputs)
    cy2 = cy + CHIP_H + CHIP_GAP + 4
    d.text(X_K + 14, cy2, LBL - 10, CHIP_H, 'Output', fs=FSS)
    draw_chips(X_K + LBL + 6, cy2, outputs)
    y += h + GAP

ky = y - GAP + 12
d.text(X_P, ky, 130, 26, 'Written by', fs=FSS)
kx = X_P + 96
for key, label in (('rl', 'training'), ('reviewer', 'Reviewer'), ('advisor', 'Advisor'), ('designer', 'Designer'), ('arbiter', 'Arbiter'), ('env', 'environment')):
    d.rect(kx, ky + 4, 18, 18, fill=SRC[key], stroke=CHIP_STROKE, sw=1, rounded=1, arc=3); kx += 24
    d.text(kx, ky, 200, 26, label, fs=FSS); kx += int(FONT.getlength(label) + 30)
H = ky + 26 + 20
d.height = H
d.cells.insert(0, f'<mxCell id="bg" value="" style="rounded=1;absoluteArcSize=1;arcSize=14;whiteSpace=wrap;html=1;fillColor={P.PANEL_A};strokeColor=none;" vertex="1" parent="1"><mxGeometry x="20" y="20" width="1760" height="{H - 40}" as="geometry"/></mxCell>')
d.text(X_P, 26, 300, 24, 'Instruction (abridged)', fs=FSS, bold=True)
d.text(X_K + 14, 26, 300, 24, 'Input and output', fs=FSS, bold=True)
out = sys.argv[1] if len(sys.argv) > 1 else 'fig2_roles_v11.drawio'
d.save(out); print('wrote', out, 'cells', len(d.cells), 'canvas', W, H)
