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
    print("Use this app if the question is about:")
    print("Use this app when you see:")
    print("- electron between plates")
    print("- deflection or time to hit")
    print("- max height / turning point")
    print("- trajectory in uniform E")
    print("- acceleration from field")


def menu():
    print("\nMAIN MENU")
    print("A) Acceleration from E")
    print("  1) Acceleration a = (q/m)E")
    print("B) 1D motion (plates)")
    print("  2) Time to reach y_target")
    print("  3) Max y / turning point")
    print("  4) Impact check with plates")
    print("C) 2D summary")
    print("  5) x(t) with constant vx")
    print("  0) Exit")


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
    y0 = ask_float("y0 (cm): ") * cm
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    yT = ask_float("y_target (cm): ") * cm
    ts = solve_time(y0, vy0, ay, yT)
    print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
    print("Sub: y0={0}, vy0={1}, ay={2}, yT={3}".format(
        sci(y0), sci(vy0), sci(ay), sci(yT)))
    if not ts:
        print("No positive real time solution.")
        return
    t = min(ts)
    print("Result: t = {0} s".format(sci(t)))


def max_height():
    print("\n3) Max y / turning point")
    y0 = ask_float("y0 (cm): ") * cm
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    if abs(ay) < 1e-12:
        print("ay ~ 0: no turning point.")
        return
    t_turn = -vy0 / ay
    if t_turn <= 0:
        print("No positive turning time.")
        return
    y_max = y0 + vy0 * t_turn + 0.5 * ay * t_turn * t_turn
    print("Formula: t_turn = -vy0/ay, y_max = y(t_turn)")
    print("Sub: y0={0}, vy0={1}, ay={2}".format(
        sci(y0), sci(vy0), sci(ay)))
    print("t_turn = -vy0/ay = {0} s".format(sci(t_turn)))
    print("y_max = {0} m".format(sci(y_max)))


def impact_check():
    print("\n4) Impact check with plates")
    y_top = ask_float("Top plate y_top (cm): ") * cm
    y_bot = ask_float("Bottom plate y_bot (cm): ") * cm
    y0 = ask_float("y0 (cm): ") * cm
    vy0 = ask_float("vy0 (m/s): ")
    ay = ask_float("ay (m/s^2): ")
    print("Formula: y = y0 + vy0 t + 0.5 ay t^2")
    print("Sub: solve for y_top and y_bot")
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
        print("No impact with plates.")
        return
    print("Impact at {0} plate".format(plate))
    print("Time to hit = {0} s".format(sci(t_hit)))


def x_at_time():
    print("\n5) x(t) with constant vx")
    x0 = ask_float("x0 (cm): ") * cm
    vx = ask_float("vx (m/s): ")
    t = ask_float("time t (s): ")
    x = x0 + vx * t
    print("Formula: x = x0 + vx t")
    print("Sub: x0={0}, vx={1}, t={2}".format(
        sci(x0), sci(vx), sci(t)))
    print("Result: x = {0} m".format(sci(x)))


def main():
    banner()
    while True:
        menu()
        choice = ask_choice("Choose (1-5, 0 exit): ",
                            ["1", "2", "3", "4", "5", "0"])
        if choice == "0":
            break
        if choice == "1":
            accel_from_E()
        elif choice == "2":
            time_to_target()
        elif choice == "3":
            max_height()
        elif choice == "4":
            impact_check()
        elif choice == "5":
            x_at_time()
        pause()


if __name__ == "__main__":
    main()
