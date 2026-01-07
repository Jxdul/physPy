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
_FORCE_UNIT_OPTIONS = [
    ("N", 1.0),
    ("kN", 1e3),
    ("mN", 1e-3),
    ("uN", 1e-6),
]
_FIELD_UNIT_OPTIONS = [
    ("N/C", 1.0),
    ("kN/C", 1e3),
    ("mN/C", 1e-3),
    ("uN/C", 1e-6),
]


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


def calculate_field_vector(
    point,
    sources,
    k: float = K_COULOMB,
) -> tuple:
    """
    Compute the electric field at a point due to multiple source charges.
    """
    dims = len(point)
    total = [0.0] * dims
    for index, (charge, pos) in enumerate(sources, start=1):
        r_vec = _vector_sub(point, pos)
        r_mag = _vector_norm(r_vec)
        if r_mag == 0.0:
            raise ValueError(f"Source charge {index}: point cannot match source position.")
        scale = k * charge / (r_mag ** 3)
        field = tuple(scale * component for component in r_vec)
        total = [t + f for t, f in zip(total, field)]
    return tuple(total)


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


def _prompt_yes_no(prompt: str) -> bool:
    while True:
        raw = input(prompt).strip().lower()
        if raw in {"y", "yes"}:
            return True
        if raw in {"n", "no"}:
            return False
        print("Please enter y or n.")


def _prompt_output_mode() -> str:
    while True:
        print("Output style:")
        print("  1) Vector only")
        print("  2) Magnitude only")
        print("  3) Both vector and magnitude")
        raw = input("Choose 1, 2, or 3: ").strip()
        if raw in {"1", "2", "3"}:
            return raw
        print("Please choose 1, 2, or 3.")


def _prompt_mode() -> str:
    while True:
        print("Select mode:")
        print("  1) Force between two charges")
        print("  2) Net force on a target from multiple charges")
        print("  3) Electric field at a point (optional force on a test charge)")
        raw = input("Choose 1, 2, or 3: ").strip()
        if raw in {"1", "2", "3"}:
            return raw
        print("Please choose 1, 2, or 3.")


def _prompt_use_example() -> bool:
    return _prompt_yes_no("Use a built-in example? (y/n): ")


def _prompt_example(mode: str) -> dict:
    if mode == "1":
        examples = [
            (
                "Two charges on x-axis (25 nC, -75 nC, 3 cm apart)",
                {
                    "dims": 1,
                    "q1": 25e-9,
                    "q2": -75e-9,
                    "r1": (0.0,),
                    "r2": (0.03,),
                },
            ),
            (
                "Two charges in 2D (2 nC at (0,0), -1 nC at (3 cm, 4 cm))",
                {
                    "dims": 2,
                    "q1": 2e-9,
                    "q2": -1e-9,
                    "r1": (0.0, 0.0),
                    "r2": (0.03, 0.04),
                },
            ),
        ]
    elif mode == "2":
        examples = [
            (
                "Net force on target (q3 at 0, q1 at 2 cm, q2 at 4 cm)",
                {
                    "dims": 1,
                    "target_charge": 5e-9,
                    "target_pos": (0.0,),
                    "sources": [
                        (1e-9, (0.02,)),
                        (-3e-9, (0.04,)),
                    ],
                },
            ),
        ]
    else:
        examples = [
            (
                "Field on x-axis (q at 2 cm, point at 0)",
                {
                    "dims": 1,
                    "point": (0.0,),
                    "sources": [(5e-9, (0.02,))],
                },
            ),
        ]

    while True:
        print("Examples:")
        for index, (label, _) in enumerate(examples, start=1):
            print(f"  {index}) {label}")
        raw = input("Choose an example: ").strip()
        if raw.isdigit():
            choice = int(raw) - 1
            if 0 <= choice < len(examples):
                return examples[choice][1]
        print("Please choose a valid example number.")


def _prompt_force_direction() -> str:
    while True:
        print("Compute force on:")
        print("  1) Charge 1 due to charge 2")
        print("  2) Charge 2 due to charge 1")
        raw = input("Choose 1 or 2: ").strip()
        if raw in {"1", "2"}:
            return raw
        print("Please choose 1 or 2.")


def _prompt_force_unit() -> tuple:
    while True:
        print("Force output unit:")
        for index, (label, _) in enumerate(_FORCE_UNIT_OPTIONS, start=1):
            print(f"  {index}) {label}")
        raw = input("Choose 1, 2, 3, or 4: ").strip()
        if raw.isdigit():
            choice = int(raw) - 1
            if 0 <= choice < len(_FORCE_UNIT_OPTIONS):
                return _FORCE_UNIT_OPTIONS[choice]
        print("Please choose 1, 2, 3, or 4.")


def _prompt_field_unit() -> tuple:
    while True:
        print("Field output unit:")
        for index, (label, _) in enumerate(_FIELD_UNIT_OPTIONS, start=1):
            print(f"  {index}) {label}")
        raw = input("Choose 1, 2, 3, or 4: ").strip()
        if raw.isdigit():
            choice = int(raw) - 1
            if 0 <= choice < len(_FIELD_UNIT_OPTIONS):
                return _FIELD_UNIT_OPTIONS[choice]
        print("Please choose 1, 2, 3, or 4.")


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


def _prompt_vector(prompt: str, dims: int) -> tuple:
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


def _scale_vector(vector, factor: float) -> tuple:
    return tuple(component / factor for component in vector)


def _format_vector(vector) -> str:
    return "(" + ", ".join(f"{component:.6g}" for component in vector) + ")"


def _print_vector_result(label: str, vector, unit_label: str, output_mode: str) -> None:
    if output_mode in {"1", "3"}:
        print(f"{label} ({unit_label}): {_format_vector(vector)}")
    if output_mode in {"2", "3"}:
        magnitude = _vector_norm(vector)
        print(f"{label} magnitude ({unit_label}): {magnitude:.6g}")


def main() -> None:
    print("Electrostatic force calculator (Coulomb's law).")
    mode = _prompt_mode()
    example = _prompt_example(mode) if _prompt_use_example() else None
    dims = example["dims"] if example else _prompt_dimension()
    axis_labels = {1: "x", 2: "x y", 3: "x y z"}[dims]
    output_mode = _prompt_output_mode()

    if mode == "1":
        if example:
            q1 = example["q1"]
            q2 = example["q2"]
            r1 = example["r1"]
            r2 = example["r2"]
        else:
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

        direction = _prompt_force_direction()
        if direction == "2":
            q1, q2 = q2, q1
            r1, r2 = r2, r1
            label = "Force on charge2 due to charge1"
        else:
            label = "Force on charge1 due to charge2"

        try:
            force = calculate_force_vector(q1, q2, r1, r2)
        except ValueError as exc:
            print(f"Error: {exc}")
            return

        unit_label, unit_factor = _prompt_force_unit()
        scaled = _scale_vector(force, unit_factor)
        _print_vector_result(label, scaled, unit_label, output_mode)
    else:
        if mode == "2":
            if example:
                target_charge = example["target_charge"]
                target_pos = example["target_pos"]
                sources = example["sources"]
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

            unit_label, unit_factor = _prompt_force_unit()
            scaled = _scale_vector(force, unit_factor)
            _print_vector_result("Net force on target", scaled, unit_label, output_mode)
        else:
            if example:
                point = example["point"]
                sources = example["sources"]
            else:
                point = _prompt_vector(
                    f"Point position ({axis_labels}) in meters: ",
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
                field = calculate_field_vector(point, sources)
            except ValueError as exc:
                print(f"Error: {exc}")
                return

            field_label, field_factor = _prompt_field_unit()
            scaled_field = _scale_vector(field, field_factor)
            _print_vector_result("Electric field at point", scaled_field, field_label, output_mode)

            if _prompt_yes_no("Compute force on a test charge? (y/n): "):
                test_charge = _prompt_charge("Test charge (e.g. 5 nC, 2e-6 C): ")
                force = tuple(component * test_charge for component in field)
                unit_label, unit_factor = _prompt_force_unit()
                scaled_force = _scale_vector(force, unit_factor)
                _print_vector_result("Force on test charge", scaled_force, unit_label, output_mode)


if __name__ == "__main__":
    main()
