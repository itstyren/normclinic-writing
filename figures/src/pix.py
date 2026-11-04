"""Pixel sprites as character grids."""
import json, os
import palette as P

HERE = os.path.dirname(os.path.abspath(__file__))
ROBOT = json.load(open(os.path.join(HERE, 'sprites.json')))['robot']


def robot_palette(body):
    return {'o': P.OUTLINE, 'b': body, 'f': P.FACE, 'e': P.EYE}


AGENT = [
    '........',
    '..d..d..',
    '..dddd..',
    '..edde..',
    '.sdwwds.',
    '.sdddds.',
    '..dddd..',
    '..s..s..',
]
AGENT_PAL = {'d': '#5B6676', 's': '#3F4854', 'e': '#1E2228', 'w': '#FFFFFF'}


def agent_sprite(colour=None):
    """RL agent sprite; colour tints the body (environment thumbnails)."""
    pal = dict(AGENT_PAL)
    if colour:
        pal['d'] = colour
    return AGENT, pal


# --- environment thumbnails: 34 x 24 cells ---------------------------------
# legend: '.' sand, 'A'..'G' agents (2x2 blocks drawn by the builder), 'a' apple,
# 'g' grass, 'w' water, 'd' dirt, 'c' coin (gold), 'k' coin (pink), 'm' matrix tile
ENV_PAL = {'.': P.SAND, ',': P.SAND_DARK, 'a': P.APPLE, 'g': P.GRASS, 'w': P.WATER, 'd': P.DIRT,
           'c': P.COIN, 'k': P.COIN2, 'm': P.AGENT_LIGHT, 'o': P.OUTLINE, 't': P.TREE}
for i, col in enumerate(P.AGENT_COLOURS):
    ENV_PAL[chr(ord('A') + i)] = col

W, H = 34, 24

def blank(fill='.'):
    return [[fill] * W for _ in range(H)]

def put(grid, r, c, s):
    for i, ch in enumerate(s):
        if 0 <= r < H and 0 <= c + i < W and ch != ' ':
            grid[r][c + i] = ch

def agent(grid, r, c, ch):
    """A 3x3 agent: outline ring with coloured centre."""
    put(grid, r, c, 'ooo'); put(grid, r + 1, c, 'o' + ch + 'o'); put(grid, r + 2, c, 'ooo')

def apple_patch(grid, r, c):
    """A diamond of apples, 5 wide."""
    for dr, s in enumerate(['  a  ', ' aaa ', 'aaaaa', ' aaa ', '  a  ']):
        put(grid, r + dr, c, s)

def finish(grid):
    return [''.join(r) for r in grid]

def env_matrix():
    g = blank()
    # a block of 4x3 grey tiles = the population; one pair highlighted
    for i in range(3):
        for j in range(4):
            r, c = 3 + i * 6, 2 + j * 5
            put(g, r, c, 'mmmm'); put(g, r + 1, c, 'mmmm'); put(g, r + 2, c, 'mmmm'); put(g, r + 3, c, 'mmmm')
    agent(g, 8, 25, 'A'); agent(g, 8, 30, 'B')
    put(g, 9, 28, ','); put(g, 9, 29, ',')
    return finish(g)

def env_coins():
    g = blank()
    agent(g, 4, 5, 'A'); agent(g, 15, 24, 'D')
    for r, c, ch in [(5, 20, 'c'), (12, 9, 'k'), (18, 6, 'c'), (9, 28, 'k'), (19, 29, 'c')]:
        put(g, r, c, ch * 2); put(g, r + 1, c, ch * 2)
    return finish(g)

def env_harvest():
    g = blank()
    apple_patch(g, 1, 2); apple_patch(g, 1, 20); apple_patch(g, 9, 11); apple_patch(g, 15, 27); apple_patch(g, 16, 1)
    put(g, 1, 29, 'aa'); put(g, 2, 29, 'aa')
    agent(g, 8, 4, 'A'); agent(g, 4, 14, 'B'); agent(g, 12, 23, 'C'); agent(g, 19, 9, 'D'); agent(g, 10, 30, 'E'); agent(g, 20, 20, 'F'); agent(g, 3, 27, 'G')
    return finish(g)

def env_cleanup():
    g = blank()
    for r in range(0, 6):
        put(g, r, 0, 'w' * W)
    for r, c in [(1, 3), (2, 10), (1, 17), (3, 24), (4, 6), (2, 30), (4, 14)]:
        put(g, r, c, 'dd'); put(g, r + 1, c, 'dd')
    for r in range(18, 24):
        put(g, r, 0, 'g' * W)
    for r, c in [(19, 1), (20, 6), (19, 11), (21, 15), (19, 20), (20, 25), (19, 30), (22, 3), (22, 22)]:
        put(g, r, c, 'aa'); put(g, r + 1, c, 'aa')
    agent(g, 8, 4, 'A'); agent(g, 7, 14, 'B'); agent(g, 10, 24, 'C'); agent(g, 13, 9, 'D'); agent(g, 14, 29, 'E'); agent(g, 9, 19, 'F'); agent(g, 15, 17, 'G')
    return finish(g)

ENVS = [('Matrix game', env_matrix), ('Coins', env_coins), ('Harvest Open', env_harvest), ('Clean Up', env_cleanup)]

# an 11 x 11 egocentric local view (Harvest), 'S' = self
def local_view():
    g = [['.'] * 11 for _ in range(11)]
    for r, c in [(2, 7), (3, 6), (3, 7), (3, 8), (4, 7), (8, 2), (9, 1), (9, 2), (9, 3)]:
        g[r][c] = 'a'
    for (r, c, ch) in [(5, 5, 'S'), (2, 2, 'B'), (7, 8, 'C')]:
        g[r][c] = ch
    return [''.join(r) for r in g]

LOCAL_PAL = dict(ENV_PAL); LOCAL_PAL['S'] = P.AGENT_DARK
