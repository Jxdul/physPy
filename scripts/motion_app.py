# FILE: motion_app.py
# TI-Nspire CX II Python - Uniform E Motion / Plates

from math import pi, sqrt

# --- constants ---
k = 8.9875517923e9
eps0 = 8.8541878128e-12
e = 1.602176634e-19
me = 9.1093837015e-31
mp = 1.67262192369e-27

# --- unit multipliers ---
micro = 1e-6
nano = 1e-9
milli = 1e-3
cm = 1e-2
mm = 1e-3

# --- unit maps (lowercase keys) ---
LEN_UNITS = {
    "m": 1.0,
    "cm": 1e-2,
    "mm": 1e-3,
    "um": 1e-6,
    "nm": 1e-9,
}

# --- helpers ---
def clamp(x, tol=1e-40):
    if abs(x) < tol:
        return 0.0
    return x


def sci(x, sig=3):
    x = clamp(x)
    if x == 0:
        return "0"
    s = ("{0:." + str(sig) + "g}").format(x)
    return s.replace("E", "e")

def _split_num_unit(token):
    token = token.strip()
    last_good = None
    for i in range(1, len(token) + 1):
        try:
            float(token[:i])
            last_good = i
        except:
            pass
    if last_good is None:
        raise ValueError("bad number")
    return token[:last_good], token[last_good:].strip()


def parse_with_unit(raw, units, default_unit):
    raw = raw.strip()
    if not raw:
        raise ValueError("empty")
    parts = raw.split()
    if len(parts) == 1:
        num_s, unit = _split_num_unit(parts[0])
        if unit == "":
            unit = default_unit
    elif len(parts) == 2:
        num_s, unit = parts[0], parts[1]
    else:
        raise ValueError("too many parts")
    key = unit.lower()
    if key not in units:
        raise ValueError("bad unit")
    return float(num_s) * units[key]


def ask_val(prompt, units, default_unit):
    while True:
        raw = input(prompt)
        try:
            return parse_with_unit(raw, units, default_unit)
        except:
            print("Try: 3cm or 0.2m.")


def ask_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except:
            print("Enter a number.")


def ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except:
            print("Enter a whole number.")


def ask_choice(prompt, options):
    while True:
        raw = input(prompt).strip()
        if raw in options:
            return raw
        low = raw.lower()
        if low in options:
            return low
        print("Choose: " + ", ".join(options))


def yes_no(prompt):
    while True:
        raw = input(prompt + " (y/n): ").strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("Enter y or n.")


def pause():
    input("Press Enter to return to menu...")


def deg2rad(d):
    return d * pi / 180.0


def rad2deg(r):
    return r * 180.0 / pi


def v_add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def v_scale(v, s):
    return (v[0] * s, v[1] * s)


def v_mag(v):
    return sqrt(v[0] * v[0] + v[1] * v[1])


def v_unit(v):
    mag = v_mag(v)
    if mag == 0:
        return (0.0, 0.0)
    return (v[0] / mag, v[1] / mag)


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1]


def v_format(v, unit=""):
    text = "(" + sci(v[0]) + ", " + sci(v[1]) + ")"
    if unit:
        text += " " + unit
    return text


# --- app content ---

def banner():
    print("=== Motion in Uniform E ===")
    print("What menu do I use?")
    print("Use this app if question about: motion in E")
    print("Tip: lengths 3cm/0.2m")
    print("- electron between plates")
    print("- deflection or time to hit")
    print("- max height / turning point")
    print("- trajectory in uniform E")
    print("- acceleration from field")


def menu_main():
    print("\nMAIN MENU")
    print("A) Accel from E")
    print("B) 1D plates (time/max/hit)")
    print("C) 2D summary (x(t))")
    print("0) Exit")


def menu_accel():
    print("\nA) Accel from E")
    print(" 1) a = (q/m)E")
    print(" 0) Back")


def menu_plates():
    print("\nB) 1D plates")
    print(" 2) Time to reach y_target")
    print(" 3) Max y / turning point")
    print(" 4) Impact check with plates")
    print(" 0) Back")


def menu_2d():
    print("\nC) 2D summary")
    print(" 5) x(t) with constant vx")
    print(" 0) Back")


def accel_from_E():
    print("\n1) Acceleration from E")
    mode = ask_choice("(1) electron, (2) proton, (3) custom: ",
                      ["1", "2", "3"])
    if mode == "1":
        q = -e
        m = me
    elif mode == "2":
        q = e
        m = mp
    else:
        q = ask_float("Charge q (C, signed): ")
        m = ask_float("Mass m (kg): ")
    E = ask_float("E magnitude (N/C): ")
    a = q * E / m
    if q > 0:
        d = "along E"
    elif q < 0:
        d = "opp E"
    else:
        d = "none"
    print("Answer: a = {0} m/s^2 ({1})".format(sci(a), d))
    print("Formula: a = (q/m) E")
    print("Sub: q={0}, m={1}, E={2}".format(
        sci(q), sci(m), sci(E)))
    print("Result: a = {0} m/s^2".format(sci(a)))
    if q > 0:
        print("Interp: acceleration along E.")
    elif q < 0:
        print("Interp: acceleration opposite E.")
    else:
        print("Interp: q=0, no acceleration.")


def solve_time(y0, vy0, ay, y_target):
    a = 0.5 * ay
    b = vy0
    c = y0 - y_target
    if abs(a) < 1e-12:
        if abs(b) < 1e-12:
            return []
        t = -c / b
        return [t] if t > 0 else []
    disc = b * b - 4 * a * c
    if disc < 0 and disc > -1e-12:
        disc = 0.0
    if disc < 0:
        return []
    root = sqrt(disc)
    t1 = (-b + root) / (2 * a)
    t2 = (-b - root) / (2 * a)
    out = []
    if t1 > 0:
        out.append(t1)
    if t2 > 0:
        out.append(t2)
    return out


def time_to_target():
    print("\n2) Time to reach y_target")
    y0 = ask_val("y0 (cm): ", LEN_UNITS, "cm")
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    yT = ask_val("y_target (cm): ", LEN_UNITS, "cm")
    ts = solve_time(y0, vy0, ay, yT)
    if not ts:
        print("Answer: no + real t")
        print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
        print("Sub: y0={0}, vy0={1}, ay={2}, yT={3}".format(
            sci(y0), sci(vy0), sci(ay), sci(yT)))
        print("No positive real time solution.")
        return
    t = min(ts)
    print("Answer: t = {0} s".format(sci(t)))
    print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
    print("Sub: y0={0}, vy0={1}, ay={2}, yT={3}".format(
        sci(y0), sci(vy0), sci(ay), sci(yT)))
    print("Result: t = {0} s".format(sci(t)))


def max_height():
    print("\n3) Max y / turning point")
    y0 = ask_val("y0 (cm): ", LEN_UNITS, "cm")
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    if abs(ay) < 1e-12:
        print("Answer: no turning point (ay~0)")
        print("ay ~ 0: no turning point.")
        return
    t_turn = -vy0 / ay
    if t_turn <= 0:
        print("Answer: no turning time (t<=0)")
        print("No positive turning time.")
        return
    y_max = y0 + vy0 * t_turn + 0.5 * ay * t_turn * t_turn
    print("Answer: y_max={0} m at t={1} s".format(
        sci(y_max), sci(t_turn)))
    print("Formula: t_turn = -vy0/ay, y_max = y(t_turn)")
    print("Sub: y0={0}, vy0={1}, ay={2}".format(
        sci(y0), sci(vy0), sci(ay)))
    print("t_turn = -vy0/ay = {0} s".format(sci(t_turn)))
    print("y_max = {0} m".format(sci(y_max)))


def impact_check():
    print("\n4) Impact check with plates")
    y_top = ask_val("Top plate y_top (cm): ", LEN_UNITS, "cm")
    y_bot = ask_val("Bottom plate y_bot (cm): ", LEN_UNITS, "cm")
    y0 = ask_val("y0 (cm): ", LEN_UNITS, "cm")
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    if y_top < y_bot:
        y_top, y_bot = y_bot, y_top
        print("Note: swapped plates so y_top > y_bot.")
    tol = 1e-12
    if abs(y0 - y_top) < tol:
        print("Answer: already at top (t=0)")
        return
    if abs(y0 - y_bot) < tol:
        print("Answer: already at bottom (t=0)")
        return
    t_top = solve_time(y0, vy0, ay, y_top)
    t_bot = solve_time(y0, vy0, ay, y_bot)
    t_hit = None
    plate = None
    if t_top:
        t_hit = min(t_top)
        plate = "top"
    if t_bot:
        t2 = min(t_bot)
        if t_hit is None or t2 < t_hit:
            t_hit = t2
            plate = "bottom"
    if t_hit is None:
        print("Answer: no impact")
        print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
        print("Sub: solve for y_top and y_bot")
        print("No impact with plates.")
        return
    print("Answer: hits {0} at t={1} s".format(plate, sci(t_hit)))
    print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
    print("Sub: solve for y_top and y_bot")
    print("Impact at {0} plate".format(plate))
    print("Time to hit = {0} s".format(sci(t_hit)))


def x_at_time():
    print("\n5) x(t) with constant vx")
    x0 = ask_val("x0 (cm): ", LEN_UNITS, "cm")
    vx = ask_float("vx (m/s): ")
    t = ask_float("time t (s): ")
    x = x0 + vx * t
    print("Answer: x = {0} m".format(sci(x)))
    print("Formula: x = x0 + vx t")
    print("Sub: x0={0}, vx={1}, t={2}".format(
        sci(x0), sci(vx), sci(t)))
    print("Result: x = {0} m".format(sci(x)))


def main():
    banner()
    while True:
        menu_main()
        top = ask_choice("Choose (A-C, 0 exit): ",
                         ["a", "b", "c", "0"])
        if top == "0":
            break
        if top == "a":
            menu_accel()
            choice = ask_choice("Choose (1, 0 back): ",
                                ["1", "0"])
            if choice == "0":
                continue
            accel_from_E()
            pause()
        elif top == "b":
            menu_plates()
            choice = ask_choice("Choose (2-4, 0 back): ",
                                ["2", "3", "4", "0"])
            if choice == "0":
                continue
            if choice == "2":
                time_to_target()
            elif choice == "3":
                max_height()
            elif choice == "4":
                impact_check()
            pause()
        elif top == "c":
            menu_2d()
            choice = ask_choice("Choose (5, 0 back): ",
                                ["5", "0"])
            if choice == "0":
                continue
            x_at_time()
            pause()


if __name__ == "__main__":
    main()
