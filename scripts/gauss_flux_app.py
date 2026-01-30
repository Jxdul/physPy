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
AREA_UNITS = {
    "m^2": 1.0,
    "m2": 1.0,
    "cm^2": 1e-4,
    "cm2": 1e-4,
    "mm^2": 1e-6,
    "mm2": 1e-6,
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
    print("Use this app if question about: flux/Gauss")
    print("Tip: units 5nC/0.2m")
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
    A = ask_val("Area A (cm^2): ", AREA_UNITS, "cm^2")
    theta = ask_float("theta (deg, to outward normal): ")
    phi = E * A * cos(deg2rad(theta))
    if phi > 0:
        tag = "positive"
    elif phi < 0:
        tag = "negative"
    else:
        tag = "zero"
    print("Answer: Phi = {0} ({1})".format(sci(phi), tag))
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
    print("Answer: Qenc = {0} C".format(sci(Q)))
    print("Formula: Qenc = eps0 * Phi")
    print("Sub: Phi = {0}".format(sci(phi)))
    print("Result: Qenc = {0} C".format(sci(Q)))


def sphere_gauss():
    print("\n3) Sphere (outside) using Gauss")
    Q = ask_val("Enclosed Q (uC): ", CHG_UNITS, "uc")
    r = ask_val("r (cm): ", LEN_UNITS, "cm")
    if r <= 0:
        print("r must be > 0.")
        return
    E_mag = k * abs(Q) / (r * r)
    phi = Q / eps0
    if Q > 0:
        d = "outward"
    elif Q < 0:
        d = "inward"
    else:
        d = "none"
    print("Answer: E = {0} N/C ({1})".format(sci(E_mag), d))
    print("Formula: E = k |Q| / r^2")
    print("Sub: Q = {0}, r = {1}".format(sci(Q), sci(r)))
    print("Result: E = {0} N/C".format(sci(E_mag)))
    if Q > 0:
        print("Interp: field is radial outward.")
    elif Q < 0:
        print("Interp: field is radial inward.")
    else:
        print("Interp: Q=0 so E=0.")
    print("Flux: Phi = Q/eps0 = {0} N m^2/C".format(sci(phi)))


def line_gauss():
    print("\n4) Infinite line")
    lam = ask_val("lambda (uC/m): ", LAM_UNITS, "uc/m")
    r = ask_val("r (cm): ", LEN_UNITS, "cm")
    if r <= 0:
        print("r must be > 0.")
        return
    E_mag = abs(lam) / (2 * pi * eps0 * r)
    if lam > 0:
        d = "outward"
    elif lam < 0:
        d = "inward"
    else:
        d = "none"
    print("Answer: E = {0} N/C ({1})".format(sci(E_mag), d))
    print("Formula: E = |lambda| / (2pi eps0 r)")
    print("Sub: lambda = {0}, r = {1}".format(sci(lam), sci(r)))
    print("Result: E = {0} N/C".format(sci(E_mag)))
    if lam > 0:
        print("Interp: field points radially outward.")
    elif lam < 0:
        print("Interp: field points radially inward.")
    else:
        print("Interp: lambda=0 so E=0.")


def sheet_gauss():
    print("\n5) Infinite sheet")
    sigma = ask_val("sigma (uC/m^2): ", SIG_UNITS, "uc/m^2")
    E_mag = abs(sigma) / (2 * eps0)
    if sigma > 0:
        d = "away"
    elif sigma < 0:
        d = "toward"
    else:
        d = "none"
    print("Answer: E = {0} N/C ({1})".format(sci(E_mag), d))
    print("Formula: E = |sigma| / (2 eps0)")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E_mag)))
    if sigma > 0:
        print("Interp: away from + sheet.")
    elif sigma < 0:
        print("Interp: toward - sheet.")
    else:
        print("Interp: sigma=0 so E=0.")


def plates_gauss():
    print("\n6) Parallel plates")
    sigma = ask_val("|sigma| (uC/m^2): ", SIG_UNITS, "uc/m^2")
    sigma = abs(sigma)
    region = ask_choice("Region (b=between, o=outside): ",
                        ["b", "o"])
    if region == "o":
        print("Answer: E ~ 0 (outside)")
        print("Outside: E ~ 0 for ideal plates.")
        return
    E = sigma / eps0
    print("Answer: E = {0} N/C (between)".format(sci(E)))
    print("Formula: E = sigma / eps0 (between)")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E)))
    print("Direction: from + plate to - plate.")


def conductor_surface():
    print("\n7) Conductor surface field")
    sigma = ask_val("sigma (uC/m^2): ", SIG_UNITS, "uc/m^2")
    E_mag = abs(sigma) / eps0
    if sigma > 0:
        d = "away"
    elif sigma < 0:
        d = "toward"
    else:
        d = "none"
    print("Answer: E = {0} N/C ({1})".format(sci(E_mag), d))
    print("Formula: E = |sigma| / eps0")
    print("Sub: sigma = {0}".format(sci(sigma)))
    print("Result: E = {0} N/C".format(sci(E_mag)))
    print("Interp: E is perpendicular to surface.")
    if sigma > 0:
        print("Direction: away from surface.")
    elif sigma < 0:
        print("Direction: toward surface.")


def cavity_checker():
    print("\n8) Cavity induced-charge checker")
    neutral = yes_no("Conductor initially neutral?")
    if neutral:
        Q0 = 0.0
    else:
        Q0 = ask_val("Net conductor charge (uC): ", CHG_UNITS, "uc")
    has_q = yes_no("Charge inside cavity?")
    if has_q:
        q = ask_val("Cavity charge q (uC): ", CHG_UNITS, "uc")
    else:
        q = 0.0
    inner = -q
    outer = Q0 + q
    print("Answer: inner={0} C, outer={1} C".format(
        sci(inner), sci(outer)))
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
        print("Answer: YES")
        print("YES: Gauss likely works.")
        print("Try menu B for a matching symmetry.")
    else:
        print("Answer: NO")
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
