# FILE: potential_energy_app.py
# TI-Nspire CX II Python - V, U, Work, Speed from Voltage

from math import cos, pi, sqrt

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
    print("=== Potential, Energy, Work ===")
    print("What menu do I use?")
    print("Use this app if the question is about:")
    print("Use this app when you see:")
    print("- electric potential V")
    print("- potential energy U or work")
    print("- voltage differences")
    print("- speed from voltage")
    print("- direction vs potential")


def menu():
    print("\nMAIN MENU")
    print("A) Potential V")
    print("  1) V of a point charge")
    print("  2) Net V from N charges")
    print("  3) Delta V between two points")
    print("B) Potential energy / Work")
    print("  4) U of two charges")
    print("  5) Delta U from Delta V")
    print("  6) Work in uniform E")
    print("C) Speed from voltage")
    print("  7) Speed from potential diff")
    print("D) Concept checkers")
    print("  8) Field vs potential reminder")
    print("  0) Exit")


def V_point():
    print("\n1) Potential of a point charge")
    Q_uc = ask_float("Q (microC): ")
    r_cm = ask_float("r (cm): ")
    Q = Q_uc * micro
    r = r_cm * cm
    if r <= 0:
        print("r must be > 0.")
        return
    V = k * Q / r
    print("Formula: V = k Q / r")
    print("Sub: Q = {0}, r = {1}".format(sci(Q), sci(r)))
    print("Result: V = {0} V".format(sci(V)))
    if Q > 0:
        print("Interp: V is positive near +Q.")
    else:
        print("Interp: V is negative near -Q.")


def V_net():
    print("\n2) Net potential from N charges")
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
    xp = ask_float("Point x (cm): ") * cm
    yp = ask_float("Point y (cm): ") * cm
    point = (xp, yp)
    print("Formula: V_i = k q / r, Vnet = sum V_i")
    print("Sub: use each charge and the point")
    Vtot = 0.0
    for i, (q, pos) in enumerate(charges, start=1):
        r = v_mag(v_sub(point, pos))
        if r == 0:
            print("Charge {0}: point is at charge.".format(i))
            return
        Vi = k * q / r
        Vtot += Vi
        print("V{0} = {1} V".format(i, sci(Vi)))
    print("Net V = {0} V".format(sci(Vtot)))
    print("Interp: potentials add as scalars.")


def delta_V():
    print("\n3) Delta V between two points")
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
    ax = ask_float("Point A x (cm): ") * cm
    ay = ask_float("Point A y (cm): ") * cm
    bx = ask_float("Point B x (cm): ") * cm
    by = ask_float("Point B y (cm): ") * cm
    A = (ax, ay)
    B = (bx, by)
    print("Formula: V = sum k q / r, Delta V = VB - VA")
    print("Sub: evaluate at A and B")
    VA = 0.0
    VB = 0.0
    for i, (q, pos) in enumerate(charges, start=1):
        rA = v_mag(v_sub(A, pos))
        rB = v_mag(v_sub(B, pos))
        if rA == 0 or rB == 0:
            print("Charge {0}: point at charge.".format(i))
            return
        VA += k * q / rA
        VB += k * q / rB
    dV = VB - VA
    print("VA = {0} V".format(sci(VA)))
    print("VB = {0} V".format(sci(VB)))
    print("Delta V = VB - VA = {0} V".format(sci(dV)))


def U_two_charges():
    print("\n4) Potential energy of two charges")
    q1_uc = ask_float("q1 (microC): ")
    q2_uc = ask_float("q2 (microC): ")
    r_cm = ask_float("r (cm): ")
    q1 = q1_uc * micro
    q2 = q2_uc * micro
    r = r_cm * cm
    if r <= 0:
        print("r must be > 0.")
        return
    U = k * q1 * q2 / r
    print("Formula: U = k q1 q2 / r")
    print("Sub: q1={0}, q2={1}, r={2}".format(
        sci(q1), sci(q2), sci(r)))
    print("Result: U = {0} J".format(sci(U)))
    if U > 0:
        print("Interp: U>0 (repulsive, like charges).")
    elif U < 0:
        print("Interp: U<0 (attractive, unlike charges).")
    else:
        print("Interp: U=0 (one charge is zero).")


def delta_U_from_V():
    print("\n5) Delta U from Delta V")
    q_uc = ask_float("Charge q (microC): ")
    dV = ask_float("Delta V (V): ")
    q = q_uc * micro
    dU = q * dV
    W = -dU
    print("Formula: Delta U = q Delta V")
    print("Sub: q={0}, Delta V={1}".format(sci(q), sci(dV)))
    print("Result: Delta U = {0} J".format(sci(dU)))
    print("Work by E: W = -Delta U = {0} J".format(sci(W)))


def work_uniform_E():
    print("\n6) Work in uniform E")
    q_uc = ask_float("Charge q (microC): ")
    E = ask_float("E magnitude (N/C): ")
    d_cm = ask_float("Displacement (cm): ")
    theta = ask_float("Angle to E (deg): ")
    q = q_uc * micro
    d = d_cm * cm
    W = q * E * d * cos(deg2rad(theta))
    print("Formula: W = q E d cos(theta)")
    print("Sub: q={0}, E={1}, d={2}, theta={3}".format(
        sci(q), sci(E), sci(d), sci(theta)))
    print("Result: W = {0} J".format(sci(W)))
    if W > 0:
        print("Interp: field does positive work.")
    elif W < 0:
        print("Interp: field does negative work.")
    else:
        print("Interp: zero work.")


def speed_from_voltage():
    print("\n7) Speed from potential difference")
    mode = ask_choice("(1) electron, (2) proton, (3) custom: ",
                      ["1", "2", "3"])
    if mode == "1":
        q = -e
        m = me
    elif mode == "2":
        q = e
        m = mp
    else:
        q = ask_float("Charge q (C, signed +/-): ")
        m = ask_float("Mass m (kg): ")
    Vi = ask_float("Vi (V): ")
    Vf = ask_float("Vf (V): ")
    K = q * (Vi - Vf)
    print("Formula: K = q (Vi - Vf)")
    print("Sub: q={0}, Vi={1}, Vf={2}".format(
        sci(q), sci(Vi), sci(Vf)))
    print("K = {0} J".format(sci(K)))
    if K < 0:
        print("K<0: it would slow down.")
        print("From rest: not reachable.")
        return
    v = sqrt(2 * K / m) if K > 0 else 0.0
    print("v = sqrt(2K/m) = {0} m/s".format(sci(v)))


def concept_reminder():
    print("\n8) Field vs potential reminder")
    print("Field points toward decreasing V.")
    print("In 1D: Ex = -dV/dx.")


def main():
    banner()
    while True:
        menu()
        choice = ask_choice("Choose (1-8, 0 exit): ",
                            ["1", "2", "3", "4",
                             "5", "6", "7", "8", "0"])
        if choice == "0":
            break
        if choice == "1":
            V_point()
        elif choice == "2":
            V_net()
        elif choice == "3":
            delta_V()
        elif choice == "4":
            U_two_charges()
        elif choice == "5":
            delta_U_from_V()
        elif choice == "6":
            work_uniform_E()
        elif choice == "7":
            speed_from_voltage()
        elif choice == "8":
            concept_reminder()
        pause()


if __name__ == "__main__":
    main()
