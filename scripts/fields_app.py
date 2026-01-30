# FILE: fields_app.py
# TI-Nspire CX II Python - Forces & Electric Fields

from math import atan2, pi, sqrt

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
CHG_UNITS = {
    "c": 1.0,
    "kc": 1e3,
    "mc": 1e-3,
    "uc": 1e-6,
    "nc": 1e-9,
    "pc": 1e-12,
}
LEN_UNITS = {
    "m": 1.0,
    "cm": 1e-2,
    "mm": 1e-3,
    "um": 1e-6,
    "nm": 1e-9,
}
LAM_UNITS = {
    "c/m": 1.0,
    "mc/m": 1e-3,
    "uc/m": 1e-6,
    "nc/m": 1e-9,
}
SIG_UNITS = {
    "c/m^2": 1.0,
    "c/m2": 1.0,
    "mc/m^2": 1e-3,
    "mc/m2": 1e-3,
    "uc/m^2": 1e-6,
    "uc/m2": 1e-6,
    "nc/m^2": 1e-9,
    "nc/m2": 1e-9,
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
            print("Try: 5nC, 0.2m, 3cm.")


def ask_vec2(prompt, units, default_unit):
    while True:
        raw = input(prompt).strip()
        if raw.startswith("(") and raw.endswith(")"):
            raw = raw[1:-1].strip()
        parts = raw.split(",")
        if len(parts) != 2:
            print("Enter as x,y (ex: 3,4)")
            continue
        try:
            x = parse_with_unit(parts[0], units, default_unit)
            y = parse_with_unit(parts[1], units, default_unit)
            return (x, y)
        except:
            print("Bad x,y. Ex: 3cm,4cm")


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
    print("=== Forces & Electric Fields ===")
    print("What menu do I use?")
    print("Use this app if question about: forces/E")
    print("Tip: units 5nC/0.2m; coords x,y")
    print("- force between charges")
    print("- electric field at a point")
    print("- net field / superposition")
    print("- ring, disk, rod, plates")
    print("- direction or sign checks")


def menu_main():
    print("\nMAIN MENU")
    print("A) Point charges (F, E)")
    print("B) Many charges (superpos)")
    print("C) Shapes (ring/disk/plates)")
    print("D) Numerical backup (rod)")
    print("E) Concepts (dir/rules)")
    print("0) Exit")


def menu_point():
    print("\nA) Point charges")
    print(" 1) Coulomb force")
    print(" 2) E-field from one charge")
    print(" 0) Back")


def menu_many():
    print("\nB) Many charges")
    print(" 3) Net E-field at a point")
    print(" 4) Net force on one charge")
    print(" 0) Back")


def menu_shapes():
    print("\nC) Shapes")
    print(" 5) Ring on-axis field")
    print(" 6) Disk on-axis field")
    print(" 7) Infinite sheet/plates")
    print(" 0) Back")


def menu_numeric():
    print("\nD) Numerical backup")
    print(" 8) Finite rod (numeric)")
    print(" 0) Back")


def menu_concepts():
    print("\nE) Concepts")
    print(" 9) Direction checker")
    print("10) Superposition reminder")
    print(" 0) Back")


def coulomb_force():
    print("\n1) Coulomb force between two charges")
    mode = ask_choice("Mode (a=r, b=coords): ", ["a", "b"])
    if mode == "a":
        q1 = ask_val("q1 (uC): ", CHG_UNITS, "uc")
        q2 = ask_val("q2 (uC): ", CHG_UNITS, "uc")
        r = ask_val("distance r (cm): ", LEN_UNITS, "cm")
        while r <= 0:
            r = ask_val("r must be >0 (cm): ", LEN_UNITS, "cm")
        F = k * q1 * q2 / (r * r)
        Fmag = abs(F)
        rel = "attractive" if (q1 * q2) < 0 else "repulsive"
        print("Answer: |F| = {0} N ({1})".format(sci(Fmag), rel))
        print("Formula: F = k q1 q2 / r^2")
        print("Sub: k={0}, q1={1}, q2={2}, r={3}".format(
            sci(k), sci(q1), sci(q2), sci(r)))
        print("Result: F = {0} N".format(sci(F)))
        print("Mag: |F| = {0} N".format(sci(Fmag)))
        if (q1 * q2) > 0:
            print("Interp: repulsive; on q2 away from q1.")
        elif (q1 * q2) < 0:
            print("Interp: attractive; on q2 toward q1.")
        else:
            print("Interp: zero force (a charge is 0).")
    else:
        q1 = ask_val("q1 (uC): ", CHG_UNITS, "uc")
        q2 = ask_val("q2 (uC): ", CHG_UNITS, "uc")
        r1 = ask_vec2("pos1 x,y (cm): ", LEN_UNITS, "cm")
        r2 = ask_vec2("pos2 x,y (cm): ", LEN_UNITS, "cm")
        r_vec = v_sub(r2, r1)
        r = v_mag(r_vec)
        if r == 0:
            print("Error: positions are the same.")
            return
        scale = k * q1 * q2 / (r * r * r)
        F_vec = v_scale(r_vec, scale)
        Fmag = v_mag(F_vec)
        ang = rad2deg(atan2(clamp(F_vec[1]), clamp(F_vec[0])))
        rel = "attractive" if (q1 * q2) < 0 else "repulsive"
        print("Answer: |F|={0} N, ang={1} deg ({2})".format(
            sci(Fmag), sci(ang), rel))
        print("r_vec = " + v_format(r_vec, "m"))
        print("Formula: F = k q1 q2 / r^3 * r_vec")
        print("Sub: q1={0}, q2={1}, r={2}".format(
            sci(q1), sci(q2), sci(r)))
        print("Result: F = " + v_format(F_vec, "N"))
        print("|F| = {0} N, angle {1} deg".format(
            sci(Fmag), sci(ang)))
        if (q1 * q2) > 0:
            print("Interp: repulsive; on q2 away from q1.")
        elif (q1 * q2) < 0:
            print("Interp: attractive; on q2 toward q1.")
        else:
            print("Interp: zero force (a charge is 0).")


def field_one_charge():
    print("\n2) E-field from one point charge")
    Q = ask_val("Q (uC): ", CHG_UNITS, "uc")
    posQ = ask_vec2("Q pos x,y (cm): ", LEN_UNITS, "cm")
    point = ask_vec2("Point x,y (cm): ", LEN_UNITS, "cm")
    r_vec = v_sub(point, posQ)
    r = v_mag(r_vec)
    if r == 0:
        print("Error: point is at the charge location.")
        return
    scale = k * Q / (r * r * r)
    E_vec = v_scale(r_vec, scale)
    Emag = v_mag(E_vec)
    ang = rad2deg(atan2(clamp(E_vec[1]), clamp(E_vec[0])))
    if Q == 0:
        print("Answer: E = 0 (Q=0)")
    else:
        trend = "away" if Q > 0 else "toward"
        sign = "+Q" if Q > 0 else "-Q"
        print("Answer: |E|={0} N/C, ang={1} deg ({2} {3})".format(
            sci(Emag), sci(ang), trend, sign))
    print("Formula: E = k Q / r^3 * r_vec")
    print("Sub: k={0}, Q={1}, r={2}".format(
        sci(k), sci(Q), sci(r)))
    print("Result: E = " + v_format(E_vec, "N/C"))
    print("|E| = {0} N/C, angle {1} deg".format(
        sci(Emag), sci(ang)))
    if Q > 0:
        print("Interp: field points away from +Q.")
    elif Q < 0:
        print("Interp: field points toward -Q.")
    else:
        print("Interp: Q=0 so E=0.")


def net_field():
    print("\n3) Net E-field from N charges")
    n = ask_int("Number of charges N: ")
    while n <= 0:
        n = ask_int("N must be >0: ")
    charges = []
    for i in range(n):
        print("Charge {0}".format(i + 1))
        q = ask_val("  q (uC): ", CHG_UNITS, "uc")
        pos = ask_vec2("  pos x,y (cm): ", LEN_UNITS, "cm")
        charges.append((q, pos))
    point = ask_vec2("Field point x,y (cm): ", LEN_UNITS, "cm")
    contrib = []
    total = (0.0, 0.0)
    for i, (q, pos) in enumerate(charges, start=1):
        r_vec = v_sub(point, pos)
        r = v_mag(r_vec)
        if r == 0:
            print("Charge {0}: point is at charge.".format(i))
            return
        E_vec = v_scale(r_vec, k * q / (r * r * r))
        contrib.append(E_vec)
        total = v_add(total, E_vec)
    Emag = v_mag(total)
    ang = rad2deg(atan2(clamp(total[1]), clamp(total[0])))
    if Emag == 0:
        print("Answer: Net E = 0")
    else:
        print("Answer: |E|={0} N/C, ang={1} deg".format(
            sci(Emag), sci(ang)))
    print("Formula: E_i = k q / r^3 * r_vec")
    print("Sub: sum all E_i at the field point")
    for i, E_vec in enumerate(contrib, start=1):
        print("E{0} = {1}".format(i, v_format(E_vec, "N/C")))
    print("Net E = " + v_format(total, "N/C"))
    print("|E| = {0} N/C, angle {1} deg".format(
        sci(Emag), sci(ang)))
    print("Interp: vector sum of all fields.")


def net_force():
    print("\n4) Net force on one charge from N charges")
    n = ask_int("Number of charges N: ")
    while n <= 0:
        n = ask_int("N must be >0: ")
    charges = []
    for i in range(n):
        print("Charge {0}".format(i + 1))
        q = ask_val("  q (uC): ", CHG_UNITS, "uc")
        pos = ask_vec2("  pos x,y (cm): ", LEN_UNITS, "cm")
        charges.append((q, pos))
    target = ask_int("Target index (1..N): ")
    while target < 1 or target > n:
        target = ask_int("Target 1..N: ")
    q_t, pos_t = charges[target - 1]
    contrib = []
    total = (0.0, 0.0)
    for i, (q, pos) in enumerate(charges, start=1):
        if i == target:
            continue
        r_vec = v_sub(pos_t, pos)
        r = v_mag(r_vec)
        if r == 0:
            print("Charge {0}: same position as target.".format(i))
            return
        F_vec = v_scale(r_vec, k * q_t * q / (r * r * r))
        contrib.append((i, F_vec))
        total = v_add(total, F_vec)
    Fmag = v_mag(total)
    ang = rad2deg(atan2(clamp(total[1]), clamp(total[0])))
    if Fmag == 0:
        print("Answer: Net F = 0")
    else:
        print("Answer: |F|={0} N, ang={1} deg".format(
            sci(Fmag), sci(ang)))
    print("Formula: F_i = k q_t q / r^3 * r_vec")
    print("Sub: sum all F_i on target")
    for i, F_vec in contrib:
        print("F{0} = {1}".format(i, v_format(F_vec, "N")))
    print("Net F = " + v_format(total, "N"))
    print("|F| = {0} N, angle {1} deg".format(
        sci(Fmag), sci(ang)))
    print("Interp: forces add as vectors.")


def ring_field():
    print("\n5) Ring on-axis field")
    Q = ask_val("Total Q (uC): ", CHG_UNITS, "uc")
    x = ask_val("x from center (cm): ", LEN_UNITS, "cm")
    a = ask_val("Ring radius a (cm): ", LEN_UNITS, "cm")
    while a <= 0:
        a = ask_val("a must be >0 (cm): ", LEN_UNITS, "cm")
    denom = (x * x + a * a) ** 1.5
    E = k * Q * x / denom
    if E > 0:
        ans_dir = "+axis"
    elif E < 0:
        ans_dir = "-axis"
    else:
        ans_dir = "0"
    print("Answer: E = {0} N/C (along {1})".format(sci(E), ans_dir))
    print("Formula: E = k Q x / (x^2 + a^2)^(3/2)")
    print("Sub: k={0}, Q={1}, x={2}, a={3}".format(
        sci(k), sci(Q), sci(x), sci(a)))
    print("Result: E = {0} N/C".format(sci(E)))
    if E > 0:
        print("Interp: field along +axis (away from +Q).")
    elif E < 0:
        print("Interp: field along -axis (toward -Q).")
    else:
        print("Interp: field is zero at this point.")


def disk_field():
    print("\n6) Disk on-axis field")
    sigma = ask_val("sigma (uC/m^2): ", SIG_UNITS, "uc/m^2")
    x = ask_val("x distance (cm): ", LEN_UNITS, "cm")
    R = ask_val("Disk radius R (cm): ", LEN_UNITS, "cm")
    while R <= 0:
        R = ask_val("R must be >0 (cm): ", LEN_UNITS, "cm")
    x_abs = abs(x)
    factor = 1.0 - x_abs / sqrt(x_abs * x_abs + R * R)
    E_mag = abs(sigma) / (2 * eps0) * factor
    side_plus = yes_no("Point on +axis side?")
    dir_sign = 1 if side_plus else -1
    if sigma < 0:
        dir_sign *= -1
    E = E_mag * dir_sign
    if E > 0:
        ans_dir = "+axis"
    elif E < 0:
        ans_dir = "-axis"
    else:
        ans_dir = "0"
    print("Answer: E = {0} N/C (along {1})".format(sci(E), ans_dir))
    print("Formula: E = (sigma/2eps0)(1 - x/sqrt(x^2+R^2))")
    print("Sub: sigma={0}, x={1}, R={2}".format(
        sci(sigma), sci(x_abs), sci(R)))
    print("Result: E = {0} N/C".format(sci(E)))
    if E > 0:
        print("Interp: along +axis (away from +sigma).")
    elif E < 0:
        print("Interp: along -axis (toward -sigma).")
    else:
        print("Interp: field is zero.")


def sheet_plates():
    print("\n7) Infinite sheet / parallel plates")
    mode = ask_choice("(1) single sheet, (2) plates: ", ["1", "2"])
    if mode == "1":
        sigma = ask_val("sigma (uC/m^2): ", SIG_UNITS, "uc/m^2")
        E_mag = abs(sigma) / (2 * eps0)
        if sigma > 0:
            ans = "away from +sheet"
        elif sigma < 0:
            ans = "toward -sheet"
        else:
            ans = "0"
        print("Answer: E = {0} N/C ({1})".format(sci(E_mag), ans))
        print("Formula: E = |sigma| / (2 eps0)")
        print("Sub: sigma={0}".format(sci(sigma)))
        print("Result: E = {0} N/C".format(sci(E_mag)))
        print("Interp: field is perpendicular to sheet.")
        if sigma > 0:
            print("Direction: away from + sheet.")
        elif sigma < 0:
            print("Direction: toward - sheet.")
        else:
            print("Direction: none (sigma=0).")
    else:
        sigma = ask_val("|sigma| (uC/m^2): ", SIG_UNITS, "uc/m^2")
        sigma = abs(sigma)
        region = ask_choice("Region (b=between, o=outside): ",
                            ["b", "o"])
        if region == "o":
            print("Answer: E ~ 0 N/C (outside ideal plates)")
            print("Outside: E ~ 0 for ideal plates.")
            return
        E = sigma / eps0
        print("Answer: E = {0} N/C (from + to -)".format(sci(E)))
        print("Formula: E = sigma / eps0 (between plates)")
        print("Sub: sigma={0}".format(sci(sigma)))
        print("Result: E = {0} N/C".format(sci(E)))
        print("Direction: from + plate to - plate.")


def rod_numeric():
    print("\n8) Finite rod field (numeric, bisector)")
    L = ask_val("Rod length L (cm): ", LEN_UNITS, "cm")
    while L <= 0:
        L = ask_val("L must be >0 (cm): ", LEN_UNITS, "cm")
    x = ask_val("Point distance x (cm): ", LEN_UNITS, "cm")
    while x <= 0:
        x = ask_val("x must be >0 (cm): ", LEN_UNITS, "cm")
    N = ask_int("Slices N (>=10): ")
    while N < 10:
        print("Use N >= 10 for accuracy.")
        N = ask_int("Slices N (>=10): ")
    mode = ask_choice("Use (q) total Q or (l) lambda: ",
                      ["q", "l"])
    if mode == "q":
        Q = ask_val("Total Q (uC): ", CHG_UNITS, "uc")
        lam = Q / L
    else:
        lam = ask_val("lambda (uC/m): ", LAM_UNITS, "uc/m")
    dy = L / N
    y = -L / 2.0 + 0.5 * dy
    E = 0.0
    for i in range(N):
        r = sqrt(x * x + y * y)
        dE = k * lam * dy * x / (r * r * r)
        E += dE
        y += dy
    if E > 0:
        ans_dir = "+x"
    elif E < 0:
        ans_dir = "-x"
    else:
        ans_dir = "0"
    print("Answer: E = {0} N/C (along {1})".format(sci(E), ans_dir))
    print("Formula: sum dE = k dq x / r^3 (midpoint)")
    print("Sub: L={0}, x={1}, N={2}".format(
        sci(L), sci(x), N))
    print("Result: E = {0} N/C".format(sci(E)))
    if E > 0:
        print("Interp: along +x (away from +rod).")
    elif E < 0:
        print("Interp: along -x (toward -rod).")
    else:
        print("Interp: field is zero.")
    print("Note: accuracy depends on N.")


def direction_checker():
    print("\n9) Direction checker")
    sign_Q = ask_choice("Source charge sign (+/-): ", ["+", "-"])
    r_vec = ask_vec2("dx,dy (cm): ", LEN_UNITS, "cm")
    if v_mag(r_vec) == 0:
        print("Point cannot be at the source.")
        return
    if sign_Q == "+":
        E_dir = v_unit(r_vec)
        print("E points away from +Q.")
    else:
        E_dir = v_unit(v_scale(r_vec, -1))
        print("E points toward -Q.")
    print("Answer: E_dir ~ " + v_format(E_dir, "unit"))
    sign_q = ask_choice("Test charge sign (+/-/0): ",
                        ["+", "-", "0"])
    if sign_q == "0":
        print("No force for q=0.")
        return
    if sign_q == "+":
        print("Force direction = E direction.")
    else:
        print("Force direction = opposite E.")


def superposition_reminder():
    print("\n10) Superposition reminder")
    print("Fields add as vectors.")
    print("Potentials add as scalars.")
    print("Forces add as vectors on each charge.")


def main():
    banner()
    while True:
        menu_main()
        top = ask_choice("Choose (A-E, 0 exit): ",
                         ["a", "b", "c", "d", "e", "0"])
        if top == "0":
            break
        if top == "a":
            menu_point()
            choice = ask_choice("Choose (1-2, 0 back): ",
                                ["1", "2", "0"])
            if choice == "0":
                continue
            if choice == "1":
                coulomb_force()
            elif choice == "2":
                field_one_charge()
            pause()
        elif top == "b":
            menu_many()
            choice = ask_choice("Choose (3-4, 0 back): ",
                                ["3", "4", "0"])
            if choice == "0":
                continue
            if choice == "3":
                net_field()
            elif choice == "4":
                net_force()
            pause()
        elif top == "c":
            menu_shapes()
            choice = ask_choice("Choose (5-7, 0 back): ",
                                ["5", "6", "7", "0"])
            if choice == "0":
                continue
            if choice == "5":
                ring_field()
            elif choice == "6":
                disk_field()
            elif choice == "7":
                sheet_plates()
            pause()
        elif top == "d":
            menu_numeric()
            choice = ask_choice("Choose (8, 0 back): ",
                                ["8", "0"])
            if choice == "0":
                continue
            rod_numeric()
            pause()
        elif top == "e":
            menu_concepts()
            choice = ask_choice("Choose (9-10, 0 back): ",
                                ["9", "10", "0"])
            if choice == "0":
                continue
            if choice == "9":
                direction_checker()
            elif choice == "10":
                superposition_reminder()
            pause()


if __name__ == "__main__":
    main()
