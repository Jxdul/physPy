# FILE: gauss_flux_app.py
# TI-Nspire CX II Python - Flux, Gauss, Conductors, Cavities

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
    print("=== Flux, Gauss, Conductors ===")
    print("What menu do I use?")
    print("Use this app if the question is about:")
    print("Use this app when you see:")
    print("- flux through a surface")
    print("- Gaussian surfaces")
    print("- infinite line/sheet")
    print("- conductors or cavities")
    print("- symmetry traps")


def menu():
    print("\nMAIN MENU")
    print("A) Flux tools")
    print("  1) Flux in uniform field, flat area")
    print("  2) Enclosed charge from flux")
    print("B) Gauss-law solve E")
    print("  3) Sphere (outside)")
    print("  4) Infinite line")
    print("  5) Infinite sheet")
    print("  6) Parallel plates")
    print("C) Conductors & cavities")
    print("  7) Conductor surface field")
    print("  8) Cavity induced-charge checker")
    print("D) Gauss applicability checker")
    print("  9) Can I use Gauss to find E?")
    print("  0) Exit")


def flux_uniform():
    print("\n1) Flux through flat area")
    E = ask_float("E (N/C): ")
    A_cm2 = ask_float("Area A (cm^2): ")
    theta = ask_float("theta (deg, to outward normal): ")
    A = A_cm2 * cm * cm
    phi = E * A * cos(deg2rad(theta))
    print("Formula: Phi = E A cos(theta)")
    print("Sub: E={0}, A={1}, theta={2} deg".format(
        sci(E), sci(A), sci(theta)))
    print("Result: Phi = {0} N m^2/C".format(sci(phi)))
    if phi > 0:
        print("Interp: field leaves surface (positive flux).")
    elif phi < 0:
        print("Interp: field enters surface (negative flux).")
    else:
        print("Interp: zero flux (parallel or zero E).")


def charge_from_flux():
    print("\n2) Enclosed charge from flux")
    phi = ask_float("Flux Phi (N m^2/C): ")
    Q = eps0 * phi
    print("Formula: Qenc = eps0 * Phi")
    print("Sub: Phi = {0}".format(sci(phi)))
    print("Result: Qenc = {0} C".format(sci(Q)))


def sphere_gauss():
    print("\n3) Sphere (outside) using Gauss")
    Q_uc = ask_float("Enclosed Q (microC): ")
    r_cm = ask_float("r (cm): ")
    Q = Q_uc * micro
    r = r_cm * cm
    if r <= 0:
        print("r must be > 0.")
        return
    E = k * Q / (r * r)
    phi = E * 4 * pi * r * r
    print("Formula: E = k Q / r^2")
    print("Sub: Q = {0}, r = {1}".format(sci(Q), sci(r)))
    print("Result: E = {0} N/C".format(sci(E)))
    print("Flux: Phi = E 4pi r^2 = {0}".format(sci(phi)))


def line_gauss():
    print("\n4) Infinite line")
    lam_uc = ask_float("lambda (microC/m): ")
    r_cm = ask_float("r (cm): ")
    lam = lam_uc * micro
    r = r_cm * cm
    E = lam / (2 * pi * eps0 * r)
    print("Formula: E = lambda / (2pi eps0 r)")
    print("Sub: lambda = {0}, r = {1}".format(sci(lam), sci(r)))
    print("Result: E = {0} N/C".format(sci(E)))
    if lam > 0:
        print("Interp: field points radially outward.")
    else:
        print("Interp: field points radially inward.")


def sheet_gauss():
    print("\n5) Infinite sheet")
    sigma_uc = ask_float("sigma (microC/m^2): ")
    sigma = sigma_uc * micro
    E = sigma / (2 * eps0)
    print("Formula: E = sigma / (2 eps0)")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E)))
    if sigma > 0:
        print("Interp: away from + sheet.")
    else:
        print("Interp: toward - sheet.")


def plates_gauss():
    print("\n6) Parallel plates")
    sigma_uc = ask_float("|sigma| (microC/m^2): ")
    sigma = sigma_uc * micro
    region = ask_choice("Region (b=between, o=outside): ",
                        ["b", "o"])
    if region == "o":
        print("Outside: E ~ 0 for ideal plates.")
        return
    E = sigma / eps0
    print("Formula: E = sigma / eps0 (between)")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E)))
    print("Direction: from + plate to - plate.")


def conductor_surface():
    print("\n7) Conductor surface field")
    sigma_uc = ask_float("sigma (microC/m^2): ")
    sigma = sigma_uc * micro
    E = sigma / eps0
    print("Formula: E = sigma / eps0")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E)))
    print("Interp: E is perpendicular to surface.")


def cavity_checker():
    print("\n8) Cavity induced-charge checker")
    neutral = yes_no("Conductor initially neutral?")
    if neutral:
        Q0 = 0.0
    else:
        Q0_uc = ask_float("Net conductor charge (microC): ")
        Q0 = Q0_uc * micro
    has_q = yes_no("Charge inside cavity?")
    if has_q:
        q_uc = ask_float("Cavity charge q (microC): ")
        q = q_uc * micro
    else:
        q = 0.0
    inner = -q
    outer = Q0 + q
    print("Inner surface charge = {0} C".format(sci(inner)))
    print("Outer surface charge = {0} C".format(sci(outer)))
    if has_q:
        print("Interp: inner = -q to cancel field in conductor.")
    print("Interp: outer holds remaining net charge.")


def gauss_checker():
    print("\n9) Can I use Gauss to find E?")
    sym = yes_no("Symmetry (spherical/cyl/planar/infinite)?")
    same = yes_no("Is E same magnitude on Gaussian surface?")
    if sym and same:
        print("YES: Gauss likely works.")
        print("Try menu B for a matching symmetry.")
    else:
        print("NO: Gauss not directly helpful.")
        print("Use fields_app superposition or integration.")


def main():
    banner()
    while True:
        menu()
        choice = ask_choice("Choose (1-9, 0 exit): ",
                            ["1", "2", "3", "4", "5",
                             "6", "7", "8", "9", "0"])
        if choice == "0":
            break
        if choice == "1":
            flux_uniform()
        elif choice == "2":
            charge_from_flux()
        elif choice == "3":
            sphere_gauss()
        elif choice == "4":
            line_gauss()
        elif choice == "5":
            sheet_gauss()
        elif choice == "6":
            plates_gauss()
        elif choice == "7":
            conductor_surface()
        elif choice == "8":
            cavity_checker()
        elif choice == "9":
            gauss_checker()
        pause()


if __name__ == "__main__":
    main()
