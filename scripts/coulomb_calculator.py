#!/usr/bin/env python3
"""
Compute electrostatic force vectors between point charges.
"""

from math import atan2, pi, sqrt


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


def _vector_unit(v):
    magnitude = _vector_norm(v)
    if magnitude == 0.0:
        return None
    return tuple(component / magnitude for component in v)


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
    # Vector from charge2 to charge1
    r_vec = _vector_sub(r1, r2)
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
            raise ValueError("Source charge {}: {}".format(index, exc)) from exc
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
            raise ValueError(
                "Source charge {}: point cannot match source position.".format(index)
            )
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


def _prompt_label(prompt: str, default_label: str) -> str:
    raw = input(prompt).strip()
    return raw if raw else default_label


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


def _prompt_force_direction(label1: str, label2: str) -> str:
    while True:
        print("Compute force on:")
        print("  1) {} due to {}".format(label1, label2))
        print("  2) {} due to {}".format(label2, label1))
        raw = input("Choose 1 or 2: ").strip()
        if raw in {"1", "2"}:
            return raw
        print("Please choose 1 or 2.")


def _prompt_force_unit() -> tuple:
    while True:
        print("Force output unit:")
        for index, (label, _) in enumerate(_FORCE_UNIT_OPTIONS, start=1):
            print("  {}) {}".format(index, label))
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
            print("  {}) {}".format(index, label))
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
    for ch in "(),[]":
        text = text.replace(ch, " ")
    parts = text.split()

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
    if len(parts) == 2 * dims:
        values = []
        for index in range(0, len(parts), 2):
            values.append(_parse_value_with_unit(parts[index] + parts[index + 1], _LENGTH_UNITS, None))
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
                example = "1 0 mm, 1 m 0 m, or (1, 0) mm"
            else:
                example = "1 0 -2 m, 1 m 0 m -2 m, or (1, 0, -2) m"
            print(
                "Enter values like '1cm 2cm 3cm', '1 2 3 cm', or '1 m 2 m 3 m' "
                "(units: m, km, cm, mm, um, nm). Example: {}".format(example)
            )


def _scale_vector(vector, factor: float) -> tuple:
    return tuple(component / factor for component in vector)


def _format_scalar(value) -> str:
    return "{:.6g}".format(value)


def _format_vector(vector) -> str:
    return "(" + ", ".join(_format_scalar(component) for component in vector) + ")"


def _print_vector_result(label: str, vector, unit_label: str) -> None:
    print("{} ({}): {}".format(label, unit_label, _format_vector(vector)))
    magnitude = _vector_norm(vector)
    print("{} magnitude ({}): {}".format(label, unit_label, _format_scalar(magnitude)))
    direction = _vector_unit(vector)
    if direction is None:
        print("{} direction: undefined (zero magnitude)".format(label))
        return
    print("{} direction (unit vector): {}".format(label, _format_vector(direction)))
    if len(vector) == 2:
        angle_deg = atan2(vector[1], vector[0]) * (180.0 / pi)
        print(
            "{} direction angle from +x (deg): {}".format(
                label, _format_scalar(angle_deg)
            )
        )


def _print_two_charge_summary(
    label1,
    q1,
    r1,
    label2,
    q2,
    r2,
    target_label,
    source_label,
) -> None:
    print("Summary:")
    print(
        "  {} = {} C at {} m".format(label1, _format_scalar(q1), _format_vector(r1))
    )
    print(
        "  {} = {} C at {} m".format(label2, _format_scalar(q2), _format_vector(r2))
    )
    print("  Compute force on {} due to {}".format(target_label, source_label))


def _print_net_force_summary(target_label, target_charge, target_pos, sources) -> None:
    print("Summary:")
    print(
        "  {} = {} C at {} m".format(
            target_label, _format_scalar(target_charge), _format_vector(target_pos)
        )
    )
    for label, charge, pos in sources:
        print(
            "  {} = {} C at {} m".format(
                label, _format_scalar(charge), _format_vector(pos)
            )
        )
    print("  Compute net force on {}".format(target_label))


def _print_field_summary(point_pos, sources) -> None:
    print("Summary:")
    print("  Point at {} m".format(_format_vector(point_pos)))
    for label, charge, pos in sources:
        print(
            "  {} = {} C at {} m".format(
                label, _format_scalar(charge), _format_vector(pos)
            )
        )
    print("  Compute electric field at point")


def main() -> None:
    print("Electrostatic force calculator (Coulomb's law).")
    mode = _prompt_mode()
    dims = _prompt_dimension()
    axis_labels = {1: "x", 2: "x y", 3: "x y z"}[dims]

    if mode == "1":
        label1 = _prompt_label("Label for charge 1 (default q1): ", "q1")
        label2 = _prompt_label("Label for charge 2 (default q2): ", "q2")
        q1 = _prompt_charge("Charge {} (e.g. 5 nC, 2e-6 C): ".format(label1))
        q2 = _prompt_charge("Charge {} (e.g. 5 nC, 2e-6 C): ".format(label2))
        r1 = _prompt_vector(
            "Position of {} ({}) in meters: ".format(label1, axis_labels),
            dims,
        )
        r2 = _prompt_vector(
            "Position of {} ({}) in meters: ".format(label2, axis_labels),
            dims,
        )

        direction = _prompt_force_direction(label1, label2)
        if direction == "2":
            target_label = label2
            source_label = label1
            target_charge = q2
            source_charge = q1
            target_pos = r2
            source_pos = r1
        else:
            target_label = label1
            source_label = label2
            target_charge = q1
            source_charge = q2
            target_pos = r1
            source_pos = r2

        _print_two_charge_summary(
            label1,
            q1,
            r1,
            label2,
            q2,
            r2,
            target_label,
            source_label,
        )

        try:
            force = calculate_force_vector(
                target_charge,
                source_charge,
                target_pos,
                source_pos,
            )
        except ValueError as exc:
            print("Error: {}".format(exc))
            return

        unit_label, unit_factor = _prompt_force_unit()
        scaled = _scale_vector(force, unit_factor)
        _print_vector_result(
            "Force on {} due to {}".format(target_label, source_label),
            scaled,
            unit_label,
        )
    else:
        if mode == "2":
            target_label = _prompt_label("Target label (default Q): ", "Q")
            target_charge = _prompt_charge(
                "Target charge {} (e.g. 5 nC, 2e-6 C): ".format(target_label)
            )
            target_pos = _prompt_vector(
                "Position of {} ({}) in meters: ".format(target_label, axis_labels),
                dims,
            )
            source_count = _prompt_positive_int("Number of source charges: ")
            sources = []
            source_entries = []
            for index in range(1, source_count + 1):
                default_label = "q{}".format(index)
                label = _prompt_label(
                    "Label for source {} (default {}): ".format(index, default_label),
                    default_label,
                )
                charge = _prompt_charge(
                    "Source charge {} (e.g. 5 nC, 2e-6 C): ".format(label)
                )
                pos = _prompt_vector(
                    "Position of {} ({}) in meters: ".format(label, axis_labels),
                    dims,
                )
                sources.append((charge, pos))
                source_entries.append((label, charge, pos))

            _print_net_force_summary(target_label, target_charge, target_pos, source_entries)

            try:
                contributions = []
                for label, charge, pos in source_entries:
                    force_vec = calculate_force_vector(
                        target_charge, charge, target_pos, pos
                    )
                    contributions.append((label, force_vec))
            except ValueError as exc:
                print("Error: Source charge {}: {}".format(label, exc))
                return

            total = [0.0] * len(target_pos)
            for _, force_vec in contributions:
                total = [t + f for t, f in zip(total, force_vec)]
            force = tuple(total)

            unit_label, unit_factor = _prompt_force_unit()
            scaled = _scale_vector(force, unit_factor)
            _print_vector_result(
                "Net force on {}".format(target_label), scaled, unit_label
            )
            print("Force contributions on {}:".format(target_label))
            for label, force_vec in contributions:
                scaled_force = _scale_vector(force_vec, unit_factor)
                _print_vector_result(
                    "Force on {} due to {}".format(target_label, label),
                    scaled_force,
                    unit_label,
                )
        else:
            point = _prompt_vector(
                "Point position ({}) in meters: ".format(axis_labels),
                dims,
            )
            source_count = _prompt_positive_int("Number of source charges: ")
            sources = []
            source_entries = []
            for index in range(1, source_count + 1):
                default_label = "q{}".format(index)
                label = _prompt_label(
                    "Label for source {} (default {}): ".format(index, default_label),
                    default_label,
                )
                charge = _prompt_charge(
                    "Source charge {} (e.g. 5 nC, 2e-6 C): ".format(label)
                )
                pos = _prompt_vector(
                    "Position of {} ({}) in meters: ".format(label, axis_labels),
                    dims,
                )
                sources.append((charge, pos))
                source_entries.append((label, charge, pos))

            _print_field_summary(point, source_entries)

            try:
                field = calculate_field_vector(point, sources)
            except ValueError as exc:
                print("Error: {}".format(exc))
                return

            field_label, field_factor = _prompt_field_unit()
            scaled_field = _scale_vector(field, field_factor)
            _print_vector_result("Electric field at point", scaled_field, field_label)

            if _prompt_yes_no("Compute force on a test charge? (y/n): "):
                test_label = _prompt_label("Test charge label (default Q): ", "Q")
                test_charge = _prompt_charge(
                    "Test charge {} (e.g. 5 nC, 2e-6 C): ".format(test_label)
                )
                print(
                    "Test charge {} = {} C".format(
                        test_label, _format_scalar(test_charge)
                    )
                )
                force = tuple(component * test_charge for component in field)
                unit_label, unit_factor = _prompt_force_unit()
                scaled_force = _scale_vector(force, unit_factor)
                _print_vector_result(
                    "Force on {}".format(test_label), scaled_force, unit_label
                )


if __name__ == "__main__":
    main()
