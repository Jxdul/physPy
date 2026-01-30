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
    print("=== Forces & Electric Fields ===")
    print("What menu do I use?")
    print("Use this app if the question is about:")
    print("Use this app when you see:")
    print("- force between charges")
    print("- electric field at a point")
    print("- net field / superposition")
    print("- ring, disk, rod, plates")
    print("- direction or sign checks")


def menu():
    print("\nMAIN MENU")
    print("A) Point charge tools")
    print("  1) Coulomb force between two charges")
    print("  2) E-field from one point charge")
    print("B) Many charges (superposition)")
    print("  3) Net E-field at a point (N charges)")
    print("  4) Net force on one charge (N charges)")
    print("C) Common continuous shapes")
    print("  5) Ring on-axis field")
    print("  6) Disk on-axis field")
    print("  7) Infinite sheet / plates")
    print("D) Numerical backup")
    print("  8) Finite rod (numeric, bisector)")
    print("E) Concept checkers")
    print("  9) Direction checker")
    print(" 10) Superposition reminder")
    print("  0) Exit")


def coulomb_force():
    print("\n1) Coulomb force between two charges")
    mode = ask_choice("Mode (a=r, b=coords): ", ["a", "b"])
    if mode == "a":
        q1_uc = ask_float("q1 (microC): ")
        q2_uc = ask_float("q2 (microC): ")
        r_cm = ask_float("distance r (cm): ")
        while r_cm <= 0:
            r_cm = ask_float("r must be >0 (cm): ")
        q1 = q1_uc * micro
        q2 = q2_uc * micro
        r = r_cm * cm
        F = k * q1 * q2 / (r * r)
        Fmag = abs(F)
        print("Formula: F = k q1 q2 / r^2")
        print("Sub: F = {0}*{1}*{2}/{3}^2".format(
            sci(k), sci(q1), sci(q2), sci(r)))
        print("Result: F = {0} N".format(sci(F)))
        print("Mag: |F| = {0} N".format(sci(Fmag)))
        if q1 * q2 > 0:
            print("Interp: repulsive; on q2 away from q1.")
        else:
            print("Interp: attractive; on q2 toward q1.")
    else:
        q1_uc = ask_float("q1 (microC): ")
        q2_uc = ask_float("q2 (microC): ")
        x1 = ask_float("x1 (cm): ") * cm
        y1 = ask_float("y1 (cm): ") * cm
        x2 = ask_float("x2 (cm): ") * cm
        y2 = ask_float("y2 (cm): ") * cm
        q1 = q1_uc * micro
        q2 = q2_uc * micro
        r_vec = (x2 - x1, y2 - y1)
        r = v_mag(r_vec)
        if r == 0:
            print("Error: positions are the same.")
            return
        scale = k * q1 * q2 / (r * r * r)
        F_vec = v_scale(r_vec, scale)
        Fmag = v_mag(F_vec)
        ang = rad2deg(atan2(clamp(F_vec[1]), clamp(F_vec[0])))
        print("r_vec = " + v_format(r_vec, "m"))
        print("Formula: F = k q1 q2 / r^3 * r_vec")
        print("Sub: q1={0}, q2={1}, r={2}".format(
            sci(q1), sci(q2), sci(r)))
        print("Result: F = " + v_format(F_vec, "N"))
        print("|F| = {0} N, angle {1} deg".format(
            sci(Fmag), sci(ang)))
        if q1 * q2 > 0:
            print("Interp: repulsive; on q2 away from q1.")
        else:
            print("Interp: attractive; on q2 toward q1.")


def field_one_charge():
    print("\n2) E-field from one point charge")
    q_uc = ask_float("Q (microC): ")
    xq = ask_float("xQ (cm): ") * cm
    yq = ask_float("yQ (cm): ") * cm
    xp = ask_float("x point (cm): ") * cm
    yp = ask_float("y point (cm): ") * cm
    Q = q_uc * micro
    r_vec = (xp - xq, yp - yq)
    r = v_mag(r_vec)
    if r == 0:
        print("Error: point is at the charge location.")
        return
    scale = k * Q / (r * r * r)
    E_vec = v_scale(r_vec, scale)
    Emag = v_mag(E_vec)
    ang = rad2deg(atan2(clamp(E_vec[1]), clamp(E_vec[0])))
    print("Formula: E = k Q / r^3 * r_vec")
    print("Sub: k={0}, Q={1}, r={2}".format(
        sci(k), sci(Q), sci(r)))
    print("Result: E = " + v_format(E_vec, "N/C"))
    print("|E| = {0} N/C, angle {1} deg".format(
        sci(Emag), sci(ang)))
    if Q > 0:
        print("Interp: field points away from +Q.")
    else:
        print("Interp: field points toward -Q.")


def net_field():
    print("\n3) Net E-field from N charges")
    n = ask_int("Number of charges N: ")
    while n <= 0:
        n = ask_int("N must be >0: ")
    charges = []
    for i in range(n):
        print("Charge {0}".format(i + 1))
        q_uc = ask_float("  q (microC): ")
        x = ask_float("  x (cm): ") * cm
        y = ask_float("  y (cm): ") * cm
        charges.append((q_uc * micro, (x, y)))
    xp = ask_float("Field point x (cm): ") * cm
    yp = ask_float("Field point y (cm): ") * cm
    point = (xp, yp)
    print("Formula: E_i = k q / r^3 * r_vec")
    print("Sub: sum all E_i at the field point")
    total = (0.0, 0.0)
    for i, (q, pos) in enumerate(charges, start=1):
        r_vec = v_sub(point, pos)
        r = v_mag(r_vec)
        if r == 0:
            print("Charge {0}: point is at charge.".format(i))
            return
        scale = k * q / (r * r * r)
        E_vec = v_scale(r_vec, scale)
        total = v_add(total, E_vec)
        print("E{0} = {1}".format(i, v_format(E_vec, "N/C")))
    Emag = v_mag(total)
    ang = rad2deg(atan2(clamp(total[1]), clamp(total[0])))
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
        q_uc = ask_float("  q (microC): ")
        x = ask_float("  x (cm): ") * cm
        y = ask_float("  y (cm): ") * cm
        charges.append((q_uc * micro, (x, y)))
    target = ask_int("Target index (1..N): ")
    while target < 1 or target > n:
        target = ask_int("Target 1..N: ")
    q_t, pos_t = charges[target - 1]
    print("Formula: F_i = k q_t q / r^3 * r_vec")
    print("Sub: sum all F_i on target")
    total = (0.0, 0.0)
    for i, (q, pos) in enumerate(charges, start=1):
        if i == target:
            continue
        r_vec = v_sub(pos_t, pos)
        r = v_mag(r_vec)
        if r == 0:
            print("Charge {0}: same position as target.".format(i))
            return
        scale = k * q_t * q / (r * r * r)
        F_vec = v_scale(r_vec, scale)
        total = v_add(total, F_vec)
        print("F{0} = {1}".format(i, v_format(F_vec, "N")))
    Fmag = v_mag(total)
    ang = rad2deg(atan2(clamp(total[1]), clamp(total[0])))
    print("Net F = " + v_format(total, "N"))
    print("|F| = {0} N, angle {1} deg".format(
        sci(Fmag), sci(ang)))
    print("Interp: forces add as vectors.")


def ring_field():
    print("\n5) Ring on-axis field")
    q_uc = ask_float("Total Q (microC): ")
    x_cm = ask_float("x from center (cm, signed): ")
    a_cm = ask_float("Ring radius a (cm): ")
    Q = q_uc * micro
    x = x_cm * cm
    a = a_cm * cm
    denom = (x * x + a * a) ** 1.5
    E = k * Q * x / denom
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
    sigma_uc = ask_float("sigma (microC/m^2): ")
    x_cm = ask_float("x distance from center (cm): ")
    R_cm = ask_float("Disk radius R (cm): ")
    sigma = sigma_uc * micro
    x = x_cm * cm
    R = R_cm * cm
    x_abs = abs(x)
    factor = 1.0 - x_abs / sqrt(x_abs * x_abs + R * R)
    E_mag = abs(sigma) / (2 * eps0) * factor
    side_plus = yes_no("Point on +axis side?")
    dir_sign = 1 if side_plus else -1
    if sigma < 0:
        dir_sign *= -1
    E = E_mag * dir_sign
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
        sigma_uc = ask_float("sigma (microC/m^2): ")
        sigma = sigma_uc * micro
        E = sigma / (2 * eps0)
        print("Formula: E = sigma / (2 eps0)")
        print("Sub: sigma={0}".format(sci(sigma)))
        print("Result: E = {0} N/C".format(sci(E)))
        print("Interp: field is perpendicular to sheet.")
        if sigma > 0:
            print("Direction: away from + sheet.")
        else:
            print("Direction: toward - sheet.")
    else:
        sigma_uc = ask_float("|sigma| (microC/m^2): ")
        sigma = sigma_uc * micro
        region = ask_choice("Region (b=between, o=outside): ",
                            ["b", "o"])
        if region == "o":
            print("Outside: E ~ 0 for ideal plates.")
            return
        E = sigma / eps0
        print("Formula: E = sigma / eps0 (between plates)")
        print("Sub: sigma={0}".format(sci(sigma)))
        print("Result: E = {0} N/C".format(sci(E)))
        print("Direction: from + plate to - plate.")


def rod_numeric():
    print("\n8) Finite rod field (numeric, bisector)")
    L_cm = ask_float("Rod length L (cm): ")
    x_cm = ask_float("Point distance x (cm): ")
    N = ask_int("Slices N (>=10): ")
    while N < 10:
        print("Use N >= 10 for accuracy.")
        N = ask_int("Slices N (>=10): ")
    mode = ask_choice("Use (q) total Q or (l) lambda: ",
                      ["q", "l"])
    if mode == "q":
        Q_uc = ask_float("Total Q (microC): ")
        Q = Q_uc * micro
        L = L_cm * cm
        lam = Q / L
    else:
        lam_uc = ask_float("lambda (microC/m): ")
        lam = lam_uc * micro
        L = L_cm * cm
    x = x_cm * cm
    dy = L / N
    y = -L / 2.0 + 0.5 * dy
    E = 0.0
    for i in range(N):
        r = sqrt(x * x + y * y)
        dE = k * lam * dy * x / (r * r * r)
        E += dE
        y += dy
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
    dx = ask_float("dx from source to point (cm): ")
    dy = ask_float("dy from source to point (cm): ")
    if dx == 0 and dy == 0:
        print("Point cannot be at the source.")
        return
    r_vec = (dx, dy)
    if sign_Q == "+":
        E_dir = v_unit(r_vec)
        print("E points away from +Q.")
    else:
        E_dir = v_unit(v_scale(r_vec, -1))
        print("E points toward -Q.")
    print("E direction ~ " + v_format(E_dir, "unit"))
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
        menu()
        choice = ask_choice("Choose (1-10, 0 exit): ",
                            ["1", "2", "3", "4", "5",
                             "6", "7", "8", "9", "10",
                             "0"])
        if choice == "0":
            break
        if choice == "1":
            coulomb_force()
        elif choice == "2":
            field_one_charge()
        elif choice == "3":
            net_field()
        elif choice == "4":
            net_force()
        elif choice == "5":
            ring_field()
        elif choice == "6":
            disk_field()
        elif choice == "7":
            sheet_plates()
        elif choice == "8":
            rod_numeric()
        elif choice == "9":
            direction_checker()
        elif choice == "10":
            superposition_reminder()
        pause()


if __name__ == "__main__":
    main()
