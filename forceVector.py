#!/usr/bin/env python3
"""
Compute electrostatic force vectors between point charges.
"""

from __future__ import annotations

from math import sqrt


K_COULOMB = 8.9875517923e9  # N·m^2/C^2
_CHARGE_UNITS = {
    "c": 1.0,
    "kc": 1e3,
    "mc": 1e-3,
    "uc": 1e-6,
    "nc": 1e-9,
    "pc": 1e-12,
}
_LENGTH_UNITS = {
    "m": 1.0,
    "km": 1e3,
    "cm": 1e-2,
    "mm": 1e-3,
    "um": 1e-6,
    "nm": 1e-9,
}
def _vector_sub(a, b):
    if len(a) != len(b):
        raise ValueError("Position vectors must have the same dimension.")
    return tuple(ai - bi for ai, bi in zip(a, b))


def _vector_norm(v) -> float:
    return sqrt(sum(component * component for component in v))


def calculate_force_vector(
    q1: float,
    q2: float,
    r1,
    r2,
    k: float = K_COULOMB,
) -> tuple:
    """
    Compute force on q1 at position r1 due to q2 at position r2.
    """
    # Vector from charge1 to charge2
    r_vec = _vector_sub(r2, r1)
    r_mag = _vector_norm(r_vec)
    if r_mag == 0.0:
        raise ValueError("Charges cannot occupy the same position.")

    scale = k * q1 * q2 / (r_mag ** 3)
    return tuple(scale * component for component in r_vec)


def calculate_net_force(
    target_charge: float,
    target_pos,
    sources,
    k: float = K_COULOMB,
) -> tuple:
    """
    Compute the net force on a target charge due to multiple source charges.
    """
    dims = len(target_pos)
    total = [0.0] * dims
    for index, (charge, pos) in enumerate(sources, start=1):
        try:
            force = calculate_force_vector(target_charge, charge, target_pos, pos, k)
        except ValueError as exc:
            raise ValueError(f"Source charge {index}: {exc}") from exc
        total = [t + f for t, f in zip(total, force)]
    return tuple(total)


def _prompt_float(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("Please enter a numeric value.")


def _parse_value_with_unit(
    raw: str,
    units: dict,
    default_unit,
) -> float:
    text = raw.strip()
    if not text:
        raise ValueError("Empty input.")

    parts = text.split()
    if len(parts) == 1:
        number_text, unit = _split_number_unit(parts[0])
        number = float(number_text)
        unit = unit or default_unit
    elif len(parts) == 2:
        number = float(parts[0])
        unit = parts[1]
    else:
        raise ValueError("Too many tokens.")

    if unit is None:
        raise ValueError("Missing unit.")

    unit_key = unit.lower()
    if unit_key not in units:
        raise ValueError("Unknown unit.")

    return number * units[unit_key]


def _prompt_charge(prompt: str) -> float:
    while True:
        raw = input(prompt)
        try:
            return _parse_value_with_unit(raw, _CHARGE_UNITS, "c")
        except ValueError:
            print("Enter a charge like 5nC, 2e-6 C, or 0.1 mC (units: C, kC, mC, uC, nC, pC).")


def _prompt_dimension() -> int:
    while True:
        raw = input("Choose dimension (1, 2, or 3): ").strip()
        if raw in {"1", "2", "3"}:
            return int(raw)
        print("Please choose 1, 2, or 3.")


def _prompt_positive_int(prompt: str) -> int:
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            value = int(raw)
            if value > 0:
                return value
        print("Please enter a positive whole number.")


def _prompt_mode() -> str:
    while True:
        print("Select mode:")
        print("  1) Force between two charges")
        print("  2) Net force on a target from multiple charges")
        raw = input("Choose 1 or 2: ").strip()
        if raw in {"1", "2"}:
            return raw
        print("Please choose 1 or 2.")


def _split_number_unit(token: str) -> tuple:
    if not token:
        raise ValueError("Empty input.")

    start = 0
    if token[0] in "+-":
        start = 1

    idx = start
    has_digit = False
    while idx < len(token) and token[idx].isdigit():
        has_digit = True
        idx += 1

    if idx < len(token) and token[idx] == ".":
        idx += 1
        while idx < len(token) and token[idx].isdigit():
            has_digit = True
            idx += 1

    if not has_digit:
        raise ValueError("Invalid number format.")

    if idx < len(token) and token[idx] in "eE":
        idx += 1
        if idx < len(token) and token[idx] in "+-":
            idx += 1
        exp_start = idx
        while idx < len(token) and token[idx].isdigit():
            idx += 1
        if exp_start == idx:
            raise ValueError("Invalid exponent format.")

    number_text = token[:idx]
    unit_text = token[idx:]
    if unit_text and not unit_text.isalpha():
        raise ValueError("Invalid unit format.")
    return number_text, unit_text


def _parse_vector_with_unit(raw: str, dims: int) -> tuple:
    text = raw.strip()
    if not text:
        raise ValueError("Empty input.")
    parts = text.replace(",", " ").split()

    if len(parts) == dims:
        values = [_parse_value_with_unit(part, _LENGTH_UNITS, "m") for part in parts]
        return tuple(values)
    if len(parts) == dims + 1:
        unit = parts[-1]
        values = [
            _parse_value_with_unit(part + unit, _LENGTH_UNITS, None)
            for part in parts[:-1]
        ]
        return tuple(values)

    raise ValueError("Invalid vector format.")


def _prompt_vector(prompt: str, dims: int) -> Tuple[float, ...]:
    while True:
        raw = input(prompt).strip()
        try:
            return _parse_vector_with_unit(raw, dims)
        except ValueError:
            if dims == 1:
                example = "2.5 cm"
            elif dims == 2:
                example = "1 0 mm"
            else:
                example = "1 0 -2 m"
            print(
                "Enter values like '1cm 2cm 3cm' or '1 2 3 cm' "
                f"(units: m, km, cm, mm, um, nm). Example: {example}"
            )


def main() -> None:
    print("Electrostatic force calculator (Coulomb's law).")
    mode = _prompt_mode()
    dims = _prompt_dimension()
    axis_labels = {1: "x", 2: "x y", 3: "x y z"}[dims]
    if mode == "1":
        q1 = _prompt_charge("Charge 1 (e.g. 5 nC, 2e-6 C): ")
        q2 = _prompt_charge("Charge 2 (e.g. 5 nC, 2e-6 C): ")
        r1 = _prompt_vector(
            f"Position of charge 1 ({axis_labels}) in meters: ",
            dims,
        )
        r2 = _prompt_vector(
            f"Position of charge 2 ({axis_labels}) in meters: ",
            dims,
        )

        try:
            force = calculate_force_vector(q1, q2, r1, r2)
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        print("Force vector on charge1 (N):")
    else:
        target_charge = _prompt_charge("Target charge (e.g. 5 nC, 2e-6 C): ")
        target_pos = _prompt_vector(
            f"Position of target ({axis_labels}) in meters: ",
            dims,
        )
        source_count = _prompt_positive_int("Number of source charges: ")
        sources = []
        for index in range(1, source_count + 1):
            charge = _prompt_charge(f"Source charge {index} (e.g. 5 nC, 2e-6 C): ")
            pos = _prompt_vector(
                f"Position of source {index} ({axis_labels}) in meters: ",
                dims,
            )
            sources.append((charge, pos))

        try:
            force = calculate_net_force(target_charge, target_pos, sources)
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        print("Net force vector on target (N):")

    formatted = ", ".join(f"{component:.6g}" for component in force)
    print(f"({formatted})")


if __name__ == "__main__":
    main()
