#!/usr/bin/env python3
import sys
import time
import random
import os
import shutil

# ── ANSI ──────────────────────────────────────────────────────────────────────

def _supports_ansi():
    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

USE_COLOR = _supports_ansi()

def c(text, *codes):
    if not USE_COLOR:
        return text
    return "\033[" + ";".join(str(x) for x in codes) + "m" + text + "\033[0m"

def bold(t):         return c(t, 1)
def dim(t):          return c(t, 2)
def bold_red(t):     return c(t, 1, 91)
def bold_orange(t):  return c(t, 1, 33)
def bold_gold(t):    return c(t, 1, 93)
def bold_green(t):   return c(t, 1, 92)
def bold_cyan(t):    return c(t, 1, 96)
def bold_white(t):   return c(t, 1, 97)
def gold(t):         return c(t, 93)
def orange(t):       return c(t, 33)
def red(t):          return c(t, 91)

def move_up(n):
    if USE_COLOR and n > 0:
        sys.stdout.write(f"\033[{n}A")
        sys.stdout.flush()

def hide_cursor():
    if USE_COLOR:
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

def show_cursor():
    if USE_COLOR:
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

def clear_line():
    sys.stdout.write("\r\033[K" if USE_COLOR else "\r")
    sys.stdout.flush()

def write(s):
    sys.stdout.write(s)
    sys.stdout.flush()

# ── Symbols ───────────────────────────────────────────────────────────────────
#
# Each symbol: (key_char, 3-char display, dim_color_fn, lit_color_fn)
#
#  777 = Lucky Sevens   — gold
#  $$$ = Money          — green
#  @@@ = Wild Cherry    — red
#  BAR = Classic Bar    — cyan
#  *** = Star           — magenta

SYMBOLS = [
    ('7', '777', lambda t: c(t, 2, 33),  lambda t: c(t, 1, 93)),
    ('$', '$$$', lambda t: c(t, 2, 32),  lambda t: c(t, 1, 92)),
    ('@', '@@@', lambda t: c(t, 2, 31),  lambda t: c(t, 1, 91)),
    ('B', 'BAR', lambda t: c(t, 2, 36),  lambda t: c(t, 1, 96)),
    ('*', '***', lambda t: c(t, 2, 35),  lambda t: c(t, 1, 95)),
]

SYM_CHARS   = [s      for s, _, _, _ in SYMBOLS]
SYM_DISPLAY = {s: d   for s, d, _, _ in SYMBOLS}

def sym_dim(s):
    for ch, disp, fn, _ in SYMBOLS:
        if ch == s: return fn(disp)
    return s

def sym_lit(s):
    for ch, disp, _, fn in SYMBOLS:
        if ch == s: return fn(disp)
    return s

# ── Responses ─────────────────────────────────────────────────────────────────
#
# Format: (core_big_text, flavor_subtitle, tier)
# core  → shown in big block letters
# flavor → shown centered below in regular styled text
# tier  → "pos" / "neu" / "neg"

POSITIVE = [
    ("YES",              "GO FOR IT RIGHT NOW",                      "pos"),
    ("YES",              "DO NOT TALK YOURSELF OUT OF THIS",         "pos"),
    ("YES",              "THE MACHINE IS RARELY THIS CONFIDENT",     "pos"),
    ("YES",              "STOP OVERTHINKING AND START DOING",        "pos"),
    ("YES",              "YOU ALREADY KNEW — THE SLOTS CONFIRM IT",  "pos"),
    ("HELL YES",         "THE SLOTS DO NOT LIE",                     "pos"),
    ("HELL YES",         "FULL SEND — NO LOOKING BACK",              "pos"),
    ("ABSOLUTELY",       "WHAT ARE YOU WAITING FOR, EXACTLY",        "pos"),
    ("ABSOLUTELY",       "100% THE RIGHT CALL — GO",                 "pos"),
    ("DEFINITELY",       "TODAY IS THE DAY, NOT TOMORROW",           "pos"),
    ("DEFINITELY",       "THE NUMBERS ALL AGREE ON THIS ONE",        "pos"),
    ("DO IT",            "BEFORE YOU TALK YOURSELF OUT OF IT",       "pos"),
    ("DO IT",            "FUTURE YOU WILL BE GRATEFUL",              "pos"),
    ("DO IT",            "THE WINDOW IS OPEN — GO THROUGH IT",       "pos"),
    ("LOCKED IN",        "THE UNIVERSE ALREADY DECIDED FOR YOU",     "pos"),
    ("JACKPOT",          "FIVE SLOTS IN AGREEMENT — UNPRECEDENTED",  "pos"),
    ("GRAND SLAM",       "BET THE HOUSE — THE ORACLE IS CERTAIN",    "pos"),
    ("GO GO GO",         "ALL FIVE SLOTS POINT THE SAME DIRECTION",  "pos"),
    ("WINNER",           "THE SLOTS HAVE BLESSED YOUR PLAN",         "pos"),
    ("100%",             "SIGNED, SEALED, DELIVERED — YES",          "pos"),
    ("FOR SURE",         "STOP ASKING AND START DOING",              "pos"),
    ("OBVIOUS YES",      "EVERYONE ELSE ALREADY KNEW THIS",          "pos"),
    ("CLEAR YES",        "THE SIGNAL COULD NOT BE STRONGER",         "pos"),
    ("OH YES",           "THE SLOT GODS HAVE PERSONALLY APPROVED",   "pos"),
    ("YES PLEASE",       "AND THEN SOME — MAXIMUM YES",              "pos"),
]

NEUTRAL = [
    ("PROBABLY",         "BUT DON'T PLAN A PARADE JUST YET",         "neu"),
    ("PROBABLY",         "LEANING YES — DOUBLE-CHECK YOUR WORK",     "neu"),
    ("LEAN YES",         "THE ODDS FAVOR YOU, JUST BARELY",          "neu"),
    ("LEAN YES",         "BUT HAVE A BACKUP PLAN READY ANYWAY",      "neu"),
    ("COIN FLIP",        "CALL IT IN THE AIR AND COMMIT",            "neu"),
    ("TRY IT",           "WORST CASE YOU LEARN SOMETHING USEFUL",    "neu"),
    ("TRY IT",           "LOW STAKES? GO. HIGH STAKES? WAIT.",       "neu"),
    ("MAYBE YES",        "THE STARS ARE SQUINTING AT THIS ONE",      "neu"),
    ("MAYBE NOT",        "TIMING FEELS SLIGHTLY OFF — WAIT A BIT",   "neu"),
    ("LIKELY NOT",       "BUT STRANGER THINGS HAVE HAPPENED",        "neu"),
    ("FIFTY FIFTY",      "HONESTLY, THE MACHINE CANNOT PICK",        "neu"),
    ("WAIT A BIT",       "THE PICTURE IS CLEARER IN A FEW DAYS",     "neu"),
    ("CHECK AGAIN",      "COME BACK WHEN THE VIBES HAVE SETTLED",    "neu"),
    ("ON THE FENCE",     "SMALL TEST RUN FIRST, THEN COMMIT",        "neu"),
    ("RISKY",            "MIGHT PAY OFF — MIGHT NOT — YOUR CALL",    "neu"),
    ("POSSIBLE",         "BUT YOU WILL HAVE TO PUSH HARD FOR IT",    "neu"),
    ("HARD TO SAY",      "THE ORACLE NEEDS MORE INFORMATION",        "neu"),
    ("LEAN NO",          "40/60 AGAINST — THOSE AREN'T GREAT ODDS",  "neu"),
    ("NOT IDEAL",        "WORKABLE IF YOU MUST — BUT DO YOU MUST?",  "neu"),
    ("MIXED SIGNALS",    "FLIP A COIN AND TRUST YOUR GUT THIS TIME", "neu"),
    ("ASK AGAIN",        "AFTER YOU HAVE SLEPT ON IT ONCE MORE",     "neu"),
    ("UNCLEAR",          "TRY AGAIN WITH BETTER ENERGY TOMORROW",    "neu"),
    ("PROCEED CAREFULLY","EYES OPEN, SPEED LOW, EXITS VISIBLE",      "neu"),
    ("UNKNOWN",          "THE SLOTS HAVE SEEN BOTH OUTCOMES HERE",   "neu"),
    ("UNDECIDED",        "THE MACHINE FORMALLY ABSTAINS",            "neu"),
]

NEGATIVE = [
    ("NO",               "WALK AWAY WHILE YOU STILL CAN",            "neg"),
    ("NO",               "NOT NOW AND PROBABLY NOT EVER",            "neg"),
    ("NO",               "THE MACHINE IS RARELY THIS CERTAIN",       "neg"),
    ("NO",               "TRUST THE SLOTS — THEY HAVE SEEN THIS MOVIE", "neg"),
    ("HARD NO",          "THIS IS NOT THE WAY — FIND ANOTHER",       "neg"),
    ("HARD NO",          "WHATEVER YOU ARE THINKING — DON'T",        "neg"),
    ("NOPE",             "THE NUMBERS ARE VERY CLEAR HERE",          "neg"),
    ("NOPE",             "BAD MATH, BAD VIBES, BAD CALL",            "neg"),
    ("NEVER",            "DELETE THIS IDEA IMMEDIATELY",             "neg"),
    ("NEVER",            "FUTURE YOU SAYS YOU ARE WELCOME",          "neg"),
    ("BAD CALL",         "THE ORACLE HAS SEEN HOW THIS ENDS",        "neg"),
    ("BAD CALL",         "EVERY REEL IS TELLING YOU TO STOP",        "neg"),
    ("ABORT",            "STOP. JUST STOP. RIGHT NOW.",              "neg"),
    ("ABORT",            "THE SLOT GODS ARE ACTIVELY OPPOSED",       "neg"),
    ("WRONG MOVE",       "RETHINK THIS FROM THE VERY BEGINNING",     "neg"),
    ("WRONG MOVE",       "YOU KNOW THIS ALREADY — TRUST THAT FEELING", "neg"),
    ("WRONG MOVE",       "YOU WILL DIE BY TRAIN", "neg"),
    ("NOT TODAY",        "COME BACK WHEN THE ODDS IMPROVE",          "neg"),
    ("NOT TODAY",        "AND PROBABLY NOT TOMORROW EITHER",         "neg"),
    ("CEASE",            "THIS PATH HAS A KNOWN BAD ENDING",         "neg"),
    ("CEASE",            "THE SLOTS HAVE SEEN THE FUTURE — ABORT",   "neg"),
    ("DON'T",            "FUTURE YOU WILL THANK YOU FOR STOPPING",   "neg"),
    ("DON'T",            "THE MACHINE CANNOT BE MORE DIRECT",        "neg"),
    ("DANGER",           "HIGH RISK, VERY LOW REWARD, WALK AWAY",    "neg"),
    ("DANGER",           "FIVE SLOTS IN OPPOSITION — NOTABLE",       "neg"),
    ("STAY PUT",         "THIS ONE IS A TRAP — THE MACHINE KNOWS",   "neg"),
]

def get_response(reels):
    counts = {s: reels.count(s) for s in SYM_CHARS}
    max_count = max(counts.values())

    if max_count >= 4:
        tier = POSITIVE
    elif max_count == 3:
        dominant = max(counts, key=lambda s: counts[s])
        idx = SYM_CHARS.index(dominant)
        tier = POSITIVE if idx <= 2 else NEUTRAL   # 777 / $$$ / @@@ → pos; BAR / *** → neu
    elif max_count == 2:
        pairs = sum(1 for v in counts.values() if v >= 2)
        tier = NEUTRAL if pairs >= 2 else random.choice([NEUTRAL, NEUTRAL, NEGATIVE])
    else:
        tier = NEGATIVE  # all 5 different — clean loss

    return random.choice(tier)

# ── Machine frame ─────────────────────────────────────────────────────────────
#
# Visual (NUM_REELS=5, CELL_W=7, MACHINE_W=41):
#
#  ╔═══════════════════════════════════════╗
#  ║     ★ ★   S P I N Q U I R Y   ★ ★    ║
#  ╠═══════╦═══════╦═══════╦═══════╦═══════╣
#  ║  dim  │  dim  │  dim  │  dim  │  dim  ║   blur row
#  ║  dim  │  dim  │  dim  │  dim  │  dim  ║   blur row
#  ╠───────┼───────┼───────┼───────┼───────╣
# ▶║  SYM  │  SYM  │  SYM  │  SYM  │  SYM  ║◀  payline
#  ╠───────┼───────┼───────┼───────┼───────╣
#  ║  dim  │  dim  │  dim  │  dim  │  dim  ║   blur row
#  ║  dim  │  dim  │  dim  │  dim  │  dim  ║   blur row
#  ╚═══════╩═══════╩═══════╩═══════╩═══════╝
#    HOLD    HOLD     --    HOLD     --

NUM_REELS = 5
CELL_W    = 7
VISIBLE   = 5     # symbol rows per column (2 blur + payline + 2 blur)
PAY_IDX   = 2     # payline = middle of VISIBLE
# ║ + CELL_W*NUM_REELS + (NUM_REELS-1)×│ + ║
MACHINE_W = 2 + NUM_REELS * CELL_W + (NUM_REELS - 1)  # 41

def lpad(payline=False):
    w = shutil.get_terminal_size((80, 24)).columns
    p = max(1, (w - MACHINE_W) // 2)
    return max(0, p - 1) if payline else p

def pref(payline=False):
    return " " * lpad(payline)

# ── Frame lines ───────────────────────────────────────────────────────────────

def ln_top(B):
    return pref() + B("╔" + "═" * (MACHINE_W - 2) + "╗")

def ln_header(B):
    title   = "S P I N Q U I R Y"
    content = "★ ★   " + title + "   ★ ★"
    inner   = MACHINE_W - 2
    pad     = inner - len(content)
    lp, rp  = pad // 2, pad - pad // 2
    return pref() + B("║") + bold_gold(" " * lp + content + " " * rp) + B("║")

def _hsep(B, left, mid, right, dash):
    s = dash * CELL_W
    return pref() + B(left + s + (mid + s) * (NUM_REELS - 1) + right)

def ln_col_sep(B):  return _hsep(B, "╠", "╦", "╣", "═")
def ln_pay_sep(B):  return _hsep(B, "╠", "┼", "╣", "─")
def ln_bot(B):      return _hsep(B, "╚", "╩", "╝", "═")

def _cell(sym, lit):
    disp = SYM_DISPLAY[sym]                    # 3 chars
    s    = sym_lit(sym) if lit else sym_dim(sym)
    pad  = (CELL_W - len(disp)) // 2          # 2 spaces each side
    return " " * pad + s + " " * (CELL_W - len(disp) - pad)

def ln_reel(strips, row, B):
    cells = [_cell(strips[col][row], False) for col in range(NUM_REELS)]
    return pref() + B("║") + B("│").join(cells) + B("║")

def ln_payline(strips, B):
    cells = [_cell(strips[col][PAY_IDX], True) for col in range(NUM_REELS)]
    return pref(payline=True) + bold_gold("▶") + B("║") + B("│").join(cells) + B("║") + bold_gold("◀")

def ln_hold(locked):
    parts = []
    for lk in locked:
        label = "  HOLD " if lk else "   --  "   # exactly CELL_W=7 chars each
        parts.append(bold_gold(label) if lk else dim(label))
    return pref() + " " + " ".join(parts) + " "

# ── Full machine draw ─────────────────────────────────────────────────────────

# Lines per frame:
# 1  ln_top
# 2  ln_header
# 3  ln_col_sep
# 4  blur row 0
# 5  blur row 1
# 6  ln_pay_sep
# 7  ln_payline
# 8  ln_pay_sep
# 9  blur row 3
# 10 blur row 4
# 11 ln_bot
# 12 ln_hold
MACHINE_LINES = 12

def draw_machine(strips, locked, first=False, border_fn=None):
    B = border_fn or bold_gold
    if not first:
        move_up(MACHINE_LINES)
    rows = [
        ln_top(B),
        ln_header(B),
        ln_col_sep(B),
        ln_reel(strips, 0, B),
        ln_reel(strips, 1, B),
        ln_pay_sep(B),
        ln_payline(strips, B),
        ln_pay_sep(B),
        ln_reel(strips, 3, B),
        ln_reel(strips, 4, B),
        ln_bot(B),
        ln_hold(locked),
    ]
    write("\n".join(rows) + "\n")

# ── Spin animation ────────────────────────────────────────────────────────────

def rand_sym(): return random.choice(SYM_CHARS)

def init_strips():
    return [[rand_sym() for _ in range(VISIBLE)] for _ in range(NUM_REELS)]

def scroll_strip(strip):
    return strip[1:] + [rand_sym()]

def spin_animation(final_reels, duration=4.0, fps=22):
    strips  = init_strips()
    locked  = [False] * NUM_REELS
    lock_at = [duration * (0.30 + 0.15 * i) for i in range(NUM_REELS)]
    # staggered: 30%, 45%, 60%, 75%, 90%

    draw_machine(strips, locked, first=True)
    start = time.time()

    while True:
        elapsed = time.time() - start

        for i in range(NUM_REELS):
            if not locked[i] and elapsed >= lock_at[i]:
                locked[i] = True
                strips[i][PAY_IDX] = final_reels[i]

        for i in range(NUM_REELS):
            if not locked[i]:
                strips[i] = scroll_strip(strips[i])

        draw_machine(strips, locked)

        if all(locked):
            break
        time.sleep(1.0 / fps)

    time.sleep(0.3)
    draw_machine(strips, locked)
    return [strips[i][PAY_IDX] for i in range(NUM_REELS)]

# ── Jackpot flash ─────────────────────────────────────────────────────────────

def jackpot_flash(strips, locked, flashes=5):
    for _ in range(flashes):
        move_up(MACHINE_LINES)
        draw_machine(strips, locked, border_fn=bold_white)
        time.sleep(0.10)
        move_up(MACHINE_LINES)
        draw_machine(strips, locked)
        time.sleep(0.10)

# ── Big block text ────────────────────────────────────────────────────────────

LETTERS = {
    'A': ["  █  "," █ █ ","█████","█   █","█   █"],
    'B': ["████ ","█   █","████ ","█   █","████ "],
    'C': [" ████","█    ","█    ","█    "," ████"],
    'D': ["████ ","█   █","█   █","█   █","████ "],
    'E': ["█████","█    ","████ ","█    ","█████"],
    'F': ["█████","█    ","████ ","█    ","█    "],
    'G': [" ████","█    ","█  ██","█   █"," ████"],
    'H': ["█   █","█   █","█████","█   █","█   █"],
    'I': ["█████","  █  ","  █  ","  █  ","█████"],
    'J': ["█████","    █","    █","█   █"," ███ "],
    'K': ["█   █","█  █ ","███  ","█  █ ","█   █"],
    'L': ["█    ","█    ","█    ","█    ","█████"],
    'M': ["█   █","██ ██","█ █ █","█   █","█   █"],
    'N': ["█   █","██  █","█ █ █","█  ██","█   █"],
    'O': [" ███ ","█   █","█   █","█   █"," ███ "],
    'P': ["████ ","█   █","████ ","█    ","█    "],
    'Q': [" ███ ","█   █","█ █ █","█  ██"," ████"],
    'R': ["████ ","█   █","████ ","█  █ ","█   █"],
    'S': [" ████","█    "," ███ ","    █","████ "],
    'T': ["█████","  █  ","  █  ","  █  ","  █  "],
    'U': ["█   █","█   █","█   █","█   █"," ███ "],
    'V': ["█   █","█   █","█   █"," █ █ ","  █  "],
    'W': ["█   █","█   █","█ █ █","██ ██","█   █"],
    'X': ["█   █"," █ █ ","  █  "," █ █ ","█   █"],
    'Y': ["█   █"," █ █ ","  █  ","  █  ","  █  "],
    'Z': ["█████","   █ ","  █  "," █   ","█████"],
    ' ': ["     ","     ","     ","     ","     "],
    '.': ["     ","     ","     ","     ","  █  "],
    '!': ["  █  ","  █  ","  █  ","     ","  █  "],
    '?': [" ███ ","    █","  ██ ","     ","  █  "],
    '-': ["     ","     ","█████","     ","     "],
    "'": ["  █  ","  █  ","     ","     ","     "],
    '%': ["█   █","   █ ","  █  "," █   ","█   █"],
    '/': ["    █","   █ ","  █  "," █   ","█    "],
}
FALLBACK = ["█████","█████","█████","█████","█████"]

def big_text_lines(text, term_w=None):
    if term_w is None:
        term_w = shutil.get_terminal_size((80, 24)).columns
    rows = [""] * 5
    for ch in text.upper():
        g = LETTERS.get(ch, FALLBACK)
        for i in range(5):
            rows[i] += g[i] + " "
    raw_w = max(len(r) for r in rows)
    pad   = max(0, (term_w - raw_w) // 2)
    return [" " * pad + r for r in rows]

def print_big(text, color_fn, term_w=None):
    for line in big_text_lines(text, term_w):
        print(color_fn(line))

# ── Response reveal ───────────────────────────────────────────────────────────

TIER_COLORS = {
    "pos": (bold_gold,    bold_green),    # big text, flavor
    "neu": (bold_orange,  orange),
    "neg": (bold_red,     red),
}

def reveal_response(core, flavor, tier):
    term_w            = shutil.get_terminal_size((80, 24)).columns
    big_color, fl_color = TIER_COLORS[tier]

    print()
    sep = bold_gold("═" * term_w)
    print(sep)
    print()

    # Word-wrap core into lines that fit as big text (~6px per char)
    max_chars = max(6, term_w // 6 - 1)
    words     = core.split()
    chunks, cur = [], []
    for w in words:
        if len(" ".join(cur + [w])) <= max_chars:
            cur.append(w)
        else:
            if cur: chunks.append(" ".join(cur))
            cur = [w]
    if cur: chunks.append(" ".join(cur))

    for chunk in chunks:
        print_big(chunk, big_color, term_w)
        print()

    pad = max(0, (term_w - len(flavor)) // 2)
    print(fl_color(" " * pad + flavor))
    print()
    print(sep)
    print()

# ── Spinning dots ─────────────────────────────────────────────────────────────

def spinning_dots(label, duration):
    frames = ["   ", ".  ", ".. ", "..."]
    start, i = time.time(), 0
    while time.time() - start < duration:
        clear_line()
        write(bold_gold(label) + dim(frames[i % len(frames)]))
        time.sleep(0.18)
        i += 1
    clear_line()

# ── Banner ────────────────────────────────────────────────────────────────────

BANNER = (
    r"   ___        _                       _"           "\n"
    r"  / __|  _ __(_)_ _  __ _ _  _  ___ (_)_ _ _  _"  "\n"
    r"  \__ \ | '_ \ | ' \/ _` | || ||___|| | '_| || |" "\n"
    r"  |___/ | .__/_|_||_\__, |\_,_|     |_|_|  \_, |" "\n"
    r"        |_|          |___|                  |__/"
)

def print_banner():
    term_w = shutil.get_terminal_size((80, 24)).columns
    for line in BANNER.splitlines():
        pad = max(0, (term_w - len(line)) // 2)
        print(bold_gold(" " * pad + line))
    tag = "The Oracle of Spinning Reels  ·  777  $$$  @@@  BAR  ***"
    pad = max(0, (term_w - len(tag)) // 2)
    print(dim(" " * pad + tag))
    print()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    hide_cursor()
    try:
        _run()
    finally:
        show_cursor()

def _run():
    print_banner()

    print(bold_gold("  Ask your question:"))
    try:
        question = input(gold("  ▶ "))
    except (EOFError, KeyboardInterrupt):
        print()
        return

    question = question.strip() or "Whatever you're thinking about"
    q_disp   = question[:72] + ("..." if len(question) > 72 else "")

    print()
    print(dim(f"  Consulting the reels for: {q_disp}"))
    print()

    final_reels = [rand_sym() for _ in range(NUM_REELS)]

    spinning_dots("  Channeling cosmic energies", 0.9)
    print()
    print()

    locked_result = spin_animation(final_reels, duration=4.0, fps=22)

    # Flash for 3+ matching on payline
    counts    = {s: locked_result.count(s) for s in SYM_CHARS}
    max_match = max(counts.values())
    if max_match >= 3:
        strips = [[locked_result[i]] * VISIBLE for i in range(NUM_REELS)]
        jackpot_flash(strips, [True] * NUM_REELS, flashes=4 + max_match)

    print()
    spinning_dots("  The oracle deliberates", 1.0)

    core, flavor, tier = get_response(locked_result)
    reveal_response(core, flavor, tier)

    sym_row = "  ".join(sym_lit(s) for s in locked_result)
    print(dim("  Reels: ") + sym_row)
    print()
    print(dim("  [ Enter to spin again  ·  Ctrl+C to exit ]"))

    try:
        input()
    except (EOFError, KeyboardInterrupt):
        print()
        return

    if USE_COLOR:
        write("\033[2J\033[H")
    _run()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show_cursor()
        print()
