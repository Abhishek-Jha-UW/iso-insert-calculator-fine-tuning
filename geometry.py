"""Compute explicitly scoped geometric estimates in millimetres and grams."""

from math import isfinite, pi, radians, sin, tan


def area_factor(shape, nose_angle):
    """Area divided by squared inradius for supported idealized outlines."""
    if shape == "R":
        return pi
    if shape in {"C", "D", "V", "E", "M"}:
        return 4 / sin(radians(nose_angle))
    sides = {"S": 4, "T": 3, "P": 5, "H": 6, "O": 8}.get(shape)
    return sides * tan(pi / sides) if sides else None


def estimate(decoded, density, hole_diameter=None):
    if density is not None and (not isfinite(density) or density <= 0):
        raise ValueError("Density must be a positive, finite number.")
    if hole_diameter is not None and (not isfinite(hole_diameter) or hole_diameter <= 0):
        raise ValueError("Hole diameter must be a positive, finite number.")
    result = dict.fromkeys(("gross_volume_mm3", "estimated_volume_mm3", "estimated_weight_g"))
    result["density_g_cm3"] = density
    factor = area_factor(decoded["shape_code"], decoded["nose_angle_deg"])
    ic, height = decoded["ic_mm"], decoded["thickness_mm"]
    clearance = decoded["clearance_deg"]
    issues = [
        label for missing, label in (
            (ic is None, "Missing size lookup"),
            (height is None, "Missing thickness lookup"),
            (clearance is None, "Unknown clearance angle"),
            (factor is None, "Unsupported shape geometry"),
        ) if missing
    ]
    if issues:
        result["geometry_issue"] = issues[0]
        result["geometry_notes"] = "Volume unavailable. " + ". ".join(issues) + "."
        return result

    top = ic / 2
    bottom = top - height * tan(radians(clearance))
    if bottom <= 0:
        result["geometry_issue"] = "Invalid clearance taper"
        result["geometry_notes"] = "The idealized clearance taper leaves no valid bottom face."
        return result

    gross = factor * height * (top**2 + top * bottom + bottom**2) / 3
    estimated = gross
    notes = ["Idealized tapered body" if clearance else "Idealized straight-sided body"]
    if decoded["shape_code"] != "R" and decoded["radius_mm"] != 0:
        notes.append("corner rounding excluded")
    configuration = decoded["configuration_code"]
    if hole_diameter is not None:
        if configuration in "FRNX":
            raise ValueError("A hole diameter requires a configuration with a standard fixing hole.")
        if hole_diameter >= 2 * bottom:
            raise ValueError("Hole diameter must be smaller than the modeled bottom inscribed circle.")
        estimated -= pi * (hole_diameter / 2)**2 * height
        notes.append("supplied cylindrical through-hole deducted")
    elif configuration not in "FRNX":
        notes.append("fixing hole excluded from deductions because its diameter is unknown")
    if configuration in "TWUQHBJC":
        notes.append("countersink deductions excluded")
    if decoded["chipbreaker_faces"] in {"One face", "Both faces"}:
        notes.append("chipbreaker deductions excluded")
    if configuration == "X":
        notes.append("special configuration features excluded")
    if decoded["suffixes"] and decoded["suffixes"] != "-M0":
        notes.append("manufacturer-specific features excluded")

    result.update(
        gross_volume_mm3=gross,
        estimated_volume_mm3=estimated,
        estimated_weight_g=(estimated / 1000) * density if density is not None else None,
        geometry_notes="; ".join(notes),
    )
    return result
