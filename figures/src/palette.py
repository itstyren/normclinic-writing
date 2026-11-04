"""Flat colours for the schematics. Wong (2011) hues, tints for fills."""
# Wong palette
BLACK = '#000000'; ORANGE = '#E69F00'; SKY = '#56B4E9'; GREEN = '#009E73'
YELLOW = '#F0E442'; BLUE = '#0072B2'; VERMILLION = '#D55E00'; PURPLE = '#CC79A7'

INK = '#000000'
LINE = '#262A31'
GREY = '#8C929B'        # reward lines, muted
MEM_LINE = '#707D8C'    # dashed memory reads
PANEL_A = '#F5F6F8'
PANEL_B = '#FBF8F3'
BAND = '#ECEEF2'

# LLM roles: sprite body colour and a light tint for their boxes
ROLE = {
    'arbiter':  dict(body=PURPLE, tint='#F3E5EE'),
    'reviewer': dict(body=BLUE,   tint='#D9E8F3'),
    'advisor':  dict(body=YELLOW, tint='#FBF8D4'),
    'designer': dict(body=GREEN,  tint='#D6EEE6'),
}
# reputation channel
REP = ORANGE; REP_TINT = '#F8E3B8'
# RL agent sprite
AGENT_DARK = '#3A3F47'; AGENT_LIGHT = '#A0A6AE'
# outline / face / eye of the robot sprite
OUTLINE = '#262A31'; FACE = '#3A3F47'; EYE = '#FFFFFF'
# environments
SAND = '#E6DCC3'; SAND_DARK = '#D9CDB0'; APPLE = '#D65858'; APPLE_DARK = '#C24F4F'
GRASS = '#BCCB83'; WATER = '#4F8FBF'; DIRT = '#66333D'; TREE = '#358431'; COIN = '#D8AE2C'; COIN2 = '#DC6A85'
AGENT_COLOURS = ['#5470D6', '#EE8E4A', '#3E9E83', '#DC6A85', '#D8AE2C', '#8B9A3A', '#647D8B']
