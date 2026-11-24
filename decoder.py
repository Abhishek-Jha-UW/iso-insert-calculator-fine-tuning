"""Decode the primary ISO/ANSI fields using the versioned rule tables."""

import json
import re
from collections import defaultdict
from itertools import product
from pathlib import Path

RULES_DIR = Path(__file__).parent / "rules"
RULES = json.loads((RULES_DIR / "iso_insert_tables.json").read_text(encoding="utf-8"))
CATALOG_OVERRIDES = {
    designation: entry
    for entry in json.loads((RULES_DIR / "catalog_dimension_overrides.json").read_text(encoding="utf-8"))
    for designation in entry["designations"]
}
MODES = ("Auto", "ISO metric", "ANSI inch")
THICKNESS = {row["iso"]: row["mm"] for row in RULES["thickness"]}
ANSI_SIZES = {row["ansi"]: row["inch"] * 25.4 for row in RULES["sizes"]}
ANSI_THICKNESS = {row["ansi"]: row["mm"] for row in RULES["thickness"]}
ANSI_RADII = {row["ansi"]: row["mm"] for row in RULES["radius"]}
ANSI_DESIGNATIONS = defaultdict(list)
for size, thickness, radius in product(ANSI_SIZES, ANSI_THICKNESS, ANSI_RADII):
    candidate = (size, thickness, radius, ANSI_SIZES[size],
                 ANSI_THICKNESS[thickness], ANSI_RADII[radius])
    ANSI_DESIGNATIONS[(size, thickness, radius)].append(candidate)
    ANSI_DESIGNATIONS[(size + thickness + radius,)].append(candidate)


def metric_candidates(shape, dimensions):
    end = r"(?:[ -]*M0(?![A-Z0-9]))?" if shape == "R" else ""
    pattern = rf"([0-9]{{2}}|L3) *([0-9]{{2}}|T[0-9])(?: *([0-9]{{2}}))?({end})(.*)"
    match = re.fullmatch(pattern, dimensions)
    if not match:
        return []
    size, thickness, radius, marker, remainder = match.groups()
    if (radius is None and shape != "R") or not valid_suffix(remainder):
        return []
    round_m0 = bool(marker)
    suffix = remainder.strip()
    if round_m0:
        suffix = " ".join(filter(None, ("-M0", suffix)))
    if round_m0:
        ic = RULES["round_m0"].get(size)
    else:
        ic = next(
            (row["mm"] for row in RULES["sizes"] if row["iso"].get(shape) == size),
            None,
        )
    return [(size, thickness, radius, ic, THICKNESS.get(thickness),
             int(radius) / 10 if radius is not None else None, suffix)]


def valid_suffix(remainder):
    # A letter may start an attached modifier, such as W. A digit or decimal
    # cannot start one because that would silently truncate a dimension token.
    return not remainder or bool(re.match(r"(?:[A-Z]| *[-/;,(_]| +[A-Z])", remainder))


def ansi_candidates(dimensions):
    # Read a compact number or three separate tokens, preserving decimals.
    # Prefer the complete three-token form over a shorter numeric prefix.
    for pattern in (r"([0-9.]+ +[0-9.]+ +[0-9.]+)(.*)", r"([0-9.]+)(.*)"):
        match = re.fullmatch(pattern, dimensions)
        if match:
            numeric, remainder = match.groups()
            if valid_suffix(remainder):
                return [(*row, remainder.strip())
                        for row in ANSI_DESIGNATIONS.get(tuple(numeric.split()), ())]
    return []


def tolerances(grade, shape, ic):
    d, m, s = RULES["tolerances"][grade]
    if grade == "M":
        for group, bounds, table_d, table_m in RULES["m_tolerances"]:
            applicable = group == shape or (group == "All other shapes" and shape not in "DV")
            if applicable and (not bounds or (ic is not None and bounds[0] <= ic <= bounds[-1])):
                d, m = table_d, table_m
                break
    return d, m, s


def decode(part_number, mode="Auto"):
    if mode not in MODES:
        raise ValueError("Select a valid designation mode.")
    if len(part_number) > 120:
        raise ValueError("Part number exceeds 120 characters.")
    normalized = " ".join(part_number.upper().split()).replace("–", "-").replace("—", "-")
    match = re.fullmatch(r"([A-Z]{4}) *-? *([0-9L].*)", normalized)
    if not match:
        raise ValueError("Expected four design letters followed by dimension symbols.")
    design, dimensions = match.groups()
    shape, clearance, grade, configuration = design
    for code, table in zip(design, ("shapes", "clearance", "tolerances", "configuration")):
        if code not in RULES[table]:
            raise ValueError(f"Unsupported {table} code {code}.")
    round_m0 = bool(re.match(r"[0-9]{2} *(?:[0-9]{2}|T[0-9])(?: *[0-9]{2})?[ -]*M0(?![A-Z0-9])",
                             dimensions))
    if round_m0 and shape != "R":
        raise ValueError("The -M0 size rule applies to round inserts.")
    candidates = []
    if mode != "ANSI inch":
        candidates.extend(("ISO metric", row) for row in metric_candidates(shape, dimensions))
    if mode != "ISO metric" and not round_m0:
        candidates.extend(("ANSI inch", row) for row in ansi_candidates(dimensions))
    if not candidates:
        raise ValueError("Dimension symbols do not match the selected mode or rule tables.")
    if len(candidates) > 1:
        raise ValueError("Ambiguous designation. Choose ISO or ANSI, or separate ANSI tokens with spaces.")
    standard, (size, thickness, radius, ic, thickness_mm, radius_mm, suffix) = candidates[0]
    separator = " " if standard == "ANSI inch" else ""
    normalized_dimensions = separator.join(filter(None, (size, thickness, radius)))
    if round_m0:
        normalized_dimensions += "-M0"
    designation = f"{design} {normalized_dimensions}"
    catalog_entry = CATALOG_OVERRIDES.get(designation) if standard == "ISO metric" else None
    if catalog_entry is not None:
        ic = catalog_entry["ic_mm"]
        thickness_mm = catalog_entry["thickness_mm"]
    d, m, s = tolerances(grade, shape, ic)
    fixing, chipbreakers = RULES["configuration"][configuration]
    warnings = []
    if ic is None:
        warnings.append(f"No matching size lookup for {shape} {size}{' M0' if round_m0 else ''}.")
    if thickness_mm is None:
        warnings.append(f"No matching thickness lookup for {thickness}.")
    if suffix and suffix != "-M0":
        warnings.append("Manufacturer suffix retained without interpreting its geometry.")
    if grade == "M" and d is None:
        warnings.append("No matching M-class size tolerance in the supplied rules.")
    angle = RULES["clearance"][clearance]
    return {
        "standard_mode": standard, "shape_code": shape, **RULES["shapes"][shape],
        "normalized_designation": designation,
        "dimension_basis": "Catalog base designation" if catalog_entry is not None else "Nomenclature tables",
        "dimension_source_url": catalog_entry["source"] if catalog_entry is not None else None,
        "clearance_code": clearance, "clearance_deg": angle,
        "positive_negative": "Special" if angle is None else ("Negative" if angle == 0 else "Positive"),
        "tolerance_class": grade, "tol_d_mm": d, "tol_m_mm": m, "tol_s_mm": s,
        "configuration_code": configuration, "fixing_hole": fixing,
        "chipbreaker_faces": chipbreakers, "size_code": size, "ic_mm": ic,
        "ic_in": ic / 25.4 if ic is not None else None,
        "thickness_code": thickness, "thickness_mm": thickness_mm,
        "thickness_in": thickness_mm / 25.4 if thickness_mm is not None else None,
        "radius_code": radius, "radius_mm": radius_mm,
        "radius_in": radius_mm / 25.4 if radius_mm is not None else None,
        "suffixes": suffix, "source_rule_version": RULES["version"], "warnings": warnings,
    }
