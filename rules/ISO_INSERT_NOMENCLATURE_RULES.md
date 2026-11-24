# ISO Turning Insert Nomenclature Rules

> Source basis: Machining Doctor, **ISO Inserts - Nomenclature, Dimensions & Tolerances**, which states its charts are based on ISO 1832. This file is a normalized rule/data specification for implementing a decoder. It is not a reproduction of the official ISO 1832 standard.

## 1. Parser scope

A standard turning insert designation has seven primary symbols:

`[1 Shape][2 Clearance][3 Tolerance][4 Configuration] [5 Size][6 Thickness][7 Corner radius]`

Examples:
- Metric / ISO: `CNMG 120408`
- Inch / ANSI dimensional notation: `CNMG 432`

Positions 1-4 are the **design group** and use the same letter system in ISO and ANSI notation. Positions 5-7 form the **dimensions group** and must be interpreted according to metric/ISO or inch/ANSI notation.

Implementation rule:
1. Normalize input to uppercase and trim whitespace.
2. Read the first four characters as design symbols.
3. Treat the remaining dimension string as metric/ISO or ANSI according to its valid token pattern or explicit user mode.
4. Do not infer manufacturer-specific chipbreaker geometry, coating, carbide grade, or undocumented tolerances from these seven symbols.

---

## 2. Position 1: insert shape

| Code | Nose angle | Shape | Cutting edges per side | Practical interpretation |
|---|---:|---|---:|---|
| C | 80 deg | Rhombic | 2 | Common general-turning shape; balance of strength and access |
| D | 55 deg | Rhombic | 2 | More profiling/access than C |
| V | 35 deg | Rhombic | 2 | High profiling flexibility; lower cutting force; finishing |
| S | 90 deg | Square | 4 | Very strong edge, many corners, less profiling flexibility |
| T | 60 deg | Triangle | 3 | Compact; moderate/limited flexibility and edge strength |
| W | 80 deg | Trigon | 3 | C-like 80 deg corners with three edges per side |
| R | 360 deg | Round | 6 | Very strong edge; high cutting force; roughing |
| L | 90 deg | Rectangular | 4 | Heavy-duty turning |
| K | 55 deg | Parallelogram | 2 | Associated with KNUX-style inserts |
| B | 82 deg | Parallelogram | 2 | Rare |
| A | 85 deg | Parallelogram | 2 | Commoner in milling than turning |
| E | 75 deg | Rhombic | 2 | Rare turning shape |
| M | 86 deg | Rhombic | 2 | Rare turning shape |
| P | 108 deg | Pentagonal | 5 | Mainly milling |
| H | 120 deg | Hexagonal | 6 | Mainly milling |
| O | 135 deg | Octagonal | 8 | Mainly milling |

### Shape-derived rules
- Nose angle and cutting-edge count are determined by position 1.
- For a double-sided negative insert (`clearance = N`), usable edge count may be twice the per-side count when both sides are actually usable.
- Do **not** blindly double edge count for every `N` code without considering configuration and actual insert construction.

---

## 3. Position 2: normal clearance angle

| Code | Clearance angle |
|---|---:|
| A | 3 deg |
| B | 5 deg |
| C | 7 deg |
| D | 15 deg |
| E | 20 deg |
| F | 25 deg |
| G | 30 deg |
| N | 0 deg |
| P | 11 deg |
| X | Other / special angle |

Interpretation:
- `N` = zero-clearance, commonly called a **negative insert**.
- Any non-zero clearance code = **positive insert**.
- Common practical codes include `N`, `C`, `P`, and `B`.
- More positive clearance generally reduces rubbing/cutting-force constraints and improves access, but reduces edge support/strength.

---

## 4. Position 3: tolerance class

The tolerance class controls tolerances on:
- `d`: inscribed-circle / size dimension
- `m`: cutting-edge position
- `s`: insert thickness

### Main tolerance rules

All values below are plus/minus tolerances.

| Class | d | m | s |
|---|---:|---:|---:|
| M | Shape/size table below | Shape/size table below | 0.13 mm (0.005 in) |
| G | 0.025 mm (0.001 in) | 0.025 mm (0.001 in) | 0.13 mm (0.005 in) |
| E | 0.025 mm (0.001 in) | 0.025 mm (0.001 in) | 0.025 mm (0.001 in) |
| A | 0.025 mm (0.001 in) | 0.005 mm (0.0002 in) | 0.025 mm (0.001 in) |
| F | 0.013 mm (0.0005 in) | 0.005 mm (0.0002 in) | 0.025 mm (0.001 in) |
| C | 0.025 mm (0.001 in) | 0.013 mm (0.0005 in) | 0.025 mm (0.001 in) |
| H | 0.013 mm (0.0005 in) | 0.013 mm (0.0005 in) | 0.025 mm (0.001 in) |
| J | 0.005 mm (0.0002 in) | 0.025 mm (0.001 in) | not specified on source chart |
| K | 0.013 mm (0.0005 in) | 0.025 mm (0.001 in) | not specified on source chart |
| L | 0.025 mm (0.001 in) | 0.025 mm (0.001 in) | not specified on source chart |
| N | 0.025 mm (0.001 in) | not specified on source chart | not specified on source chart |
| U | 0.13 mm (0.005 in) | not specified on source chart | not specified on source chart |

Practical notes from the source:
- `M` is commonly associated with pressed inserts.
- `G` is commonly associated with ground inserts.
- `E` is rare and uses a tighter thickness tolerance than G.

### M-class complementary d/m table

| Shape condition | IC/size range | d tolerance | m tolerance |
|---|---|---:|---:|
| D | 4-10 mm (3/16-3/8 in) | 0.05 mm (0.002 in) | 0.11 mm (0.004 in) |
| D | 12.7 mm (1/2 in) | 0.08 mm (0.003 in) | 0.15 mm (0.006 in) |
| D | 15.87-19.05 mm (5/8-3/4 in) | 0.10 mm (0.004 in) | 0.18 mm (0.007 in) |
| V | any size | 0.05 mm (0.002 in) | 0.16 mm (0.006 in) |
| All other shapes | 4-10 mm (3/16-3/8 in) | 0.05 mm (0.002 in) | 0.08 mm (0.003 in) |
| All other shapes | 12.0-12.7 mm (1/2 in) | 0.08 mm (0.003 in) | 0.13 mm (0.005 in) |
| All other shapes | 15.87-20 mm (5/8-3/4 in) | 0.10 mm (0.004 in) | 0.15 mm (0.006 in) |
| All other shapes | 25.0-25.4 mm (1 in) | 0.13 mm (0.005 in) | 0.18 mm (0.007 in) |
| All other shapes | 31.75-32 mm (1 1/4 in) | 0.15 mm (0.006 in) | 0.20 mm (0.008 in) |

Important: the source notes that these standard tolerance classes do not define every physical feature. Do not invent nose-radius or manufacturer-specific geometry tolerances.

---

## 5. Position 4: configuration, fixing hole, countersink and chipbreaker

This letter encodes a combination of fixing-hole/countersink style and chipbreaker presence.

| Code | Fixing / countersink configuration | Chipbreaker |
|---|---|---|
| G | Cylindrical fixing hole | Both faces |
| M | Cylindrical fixing hole | One face |
| A | Cylindrical fixing hole | None |
| T | Cylindrical hole + 40-60 deg countersink on one side | One face |
| W | Cylindrical hole + 40-60 deg countersink on one side | None |
| U | Cylindrical hole + 40-60 deg countersinks on both sides | Both faces |
| Q | Cylindrical hole + 40-60 deg countersinks on both sides | None |
| H | Cylindrical hole + 70-90 deg countersink on one side | One face |
| B | Cylindrical hole + 70-90 deg countersink on one side | None |
| J | Cylindrical hole + 70-90 deg countersinks on both sides | Both faces |
| C | Cylindrical hole + 70-90 deg countersinks on both sides | None |
| F | No fixing hole | Both faces |
| R | No fixing hole | One face |
| N | No fixing hole | None |
| X | Special | Requires drawing/detailed definition |

### Mounting-style classification
1. **No fixing hole**: frequently relevant to ceramics/full-CBN constructions.
2. **Cylindrical hole**: compatible with lever-lock type arrangements.
3. **Cylindrical hole with countersink(s)**: commonly enables screw clamping and compact holders.

Do not infer exact chipbreaker **geometry** from position 4; this symbol only indicates its presence/face arrangement.

---

## 6. Position 5: size

### ISO metric logic
For metric ISO designations, size is shape-dependent and relates approximately to cutting-edge length. Use the lookup table rather than assuming the two-digit token always equals the inscribed-circle diameter.

### ANSI inch logic
For ANSI dimensional notation, the size token relates to the inscribed-circle diameter and is approximately `8 x IC_inch`.

### Size lookup

`X` = combination not provided in the source chart.

| IC mm | IC in | ANSI token | S | T | C | D | E | V | W | R |
|---:|---:|---:|---|---|---|---|---|---|---|---|
| 3.97 | 0.15625 | 1.2 | 03 | 06 | X | 04 | X | 06 | 02 | X |
| 4.76 | 0.1875 | 1.5 | 04 | 08 | 04 | 05 | 04 | 08 | L3 | X |
| 5.56 | 0.21875 | 1.8 | 05 | 09 | 05 | 06 | 05 | 09 | 03 | X |
| 6.35 | 0.25 | 2 | 06 | 11 | 06 | 07 | 06 | 11 | 04 | 06 |
| 7.94 | 0.3125 | 2.5 | 07 | 13 | 08 | 09 | 08 | 13 | 05 | 07 |
| 9.525 | 0.375 | 3 | 09 | 16 | 09 | 11 | 09 | 16 | 06 | 09 |
| 12.7 | 0.5 | 4 | 12 | 22 | 12 | 15 | 13 | 22 | 08 | 12 |
| 15.875 | 0.625 | 5 | 15 | 27 | 16 | 19 | 16 | 27 | 10 | 15 |
| 19.05 | 0.75 | 6 | 19 | 33 | 19 | 23 | 19 | 33 | 13 | 19 |
| 25.4 | 1 | 8 | 25 | 44 | 25 | 31 | 26 | 44 | 17 | 25 |
| 31.75 | 1.25 | 10 | 31 | 54 | 32 | 38 | 32 | 54 | 21 | 31 |

### Round metric inserts with `-M0`
For round R inserts only, an `M0` suffix changes size interpretation to an exact metric diameter table.

| Size token | Diameter |
|---|---:|
| 06 | 6 mm |
| 08 | 8 mm |
| 10 | 10 mm |
| 12 | 12 mm |
| 16 | 16 mm |
| 20 | 20 mm |
| 25 | 25 mm |
| 32 | 32 mm |

Critical example:
- `RNMG 1204` / `RNMG 120400`: normal table => nominal diameter 12.7 mm.
- `RNMG 1204-M0`: M0 table => diameter 12.0 mm.

Parser rule: check the `-M0` suffix **before** decoding round-insert size.

---

## 7. Position 6: thickness

Thickness is measured from the clamping/bottom plane to the highest point of the cutting edge.

### Metric/ISO
The token roughly corresponds to thickness in millimetres, but it must be decoded by table. `T` variants distinguish nearby thicknesses that cannot be represented unambiguously by the normal leading-zero convention.

### ANSI/inch
The nominal numerical relationship is approximately:

`thickness_inch = ANSI_thickness_symbol / 16`

Use the lookup values for exact nominal output.

| ISO token | ANSI token | Thickness mm | Thickness in |
|---|---:|---:|---:|
| 01 | 1 | 1.59 | 0.0625 |
| 02 | 1.5 | 2.38 | 0.0938 |
| 03 | 2 | 3.18 | 0.1250 |
| 04 | 3 | 4.76 | 0.1875 |
| 05 | 3.5 | 5.56 | 0.2188 |
| 06 | 4 | 6.35 | 0.2500 |
| 07 | 5 | 7.94 | 0.3125 |
| 09 | 6 | 9.52 | 0.3750 |
| 12 | 8 | 12.70 | 0.5000 |
| T1 | 1.2 | 1.98 | 0.0781 |
| T3 | 2.5 | 3.97 | 0.1563 |

---

## 8. Position 7: corner / nose radius

### ISO metric calculation

`radius_mm = integer(ISO_radius_token) / 10`

A leading zero is retained when needed. Example: `08 => 0.8 mm`.

### ANSI inch calculation

Nominally, the symbol is based on `64 x radius_inch`, subject to the designation rounding convention. Prefer the lookup table for decoder output.

| ISO token | ANSI token | Radius mm | Radius in |
|---|---:|---:|---:|
| 00 | 0 | 0 | 0 |
| 01 | 0.25 | 0.1 | 0.0040 |
| 02 | 0.5 | 0.2 | 0.0080 |
| 04 | 1 | 0.4 | 0.0156 |
| 08 | 2 | 0.8 | 0.0313 |
| 12 | 3 | 1.2 | 0.0469 |
| 16 | 4 | 1.6 | 0.0625 |
| 24 | 6 | 2.4 | 0.0938 |
| 32 | 8 | 3.2 | 0.1250 |

---

## 9. Deterministic decoding example: CNMG 120408

Parse:
- `C` -> 80 deg rhombic, 2 cutting corners per side.
- `N` -> 0 deg clearance; negative insert.
- `M` -> tolerance class M / commonly pressed.
- `G` -> cylindrical fixing hole, chipbreakers on both faces.
- `12` with shape C -> nominal IC 12.7 mm from the size table.
- `04` -> thickness 4.76 mm.
- `08` -> corner radius 0.8 mm.

For M tolerance class and C shape at ~12.7 mm:
- `d`: plus/minus 0.08 mm.
- `m`: plus/minus 0.13 mm.
- `s`: plus/minus 0.13 mm.

A backend should return both the decoded raw fields and useful derived fields such as:
- shape name
- nose angle
- nominal edge count per side
- clearance angle
- positive/negative classification
- tolerance values
- fixing-hole style
- countersink style
- chipbreaker-face indicator
- nominal IC/size
- thickness
- nose radius
- metric and inch conversions when available

---

## 10. Validation rules for a web backend

### Required validations
- Reject fewer than four design characters.
- Validate positions 1-4 against their individual code tables.
- Do not treat arbitrary letters as valid except explicit special code `X` where supported.
- Do not calculate metric size solely from the numeric token; **shape is required**.
- Recognize non-numeric metric thickness tokens such as `T1` and `T3`.
- Recognize the special W-shape size token `L3` if supporting that table row.
- Check the `-M0` suffix before decoding round metric size.
- Return `unknown / requires manufacturer data` rather than inventing a value when a standard field is not encoded.

### Format detection recommendation
Prefer an explicit frontend selector (`ISO metric`, `ANSI inch`, or `Auto`) because some strings can otherwise be ambiguous.

For Auto mode, a pragmatic decoder can:
1. Split the four-letter design group from dimensions.
2. If the dimension group clearly consists of three 2-character ISO tokens, decode as metric.
3. If it clearly matches valid ANSI size/thickness/radius tokens, decode as ANSI.
4. If both interpretations are valid, return an ambiguity warning and require the user to choose.

### Units
Store canonical numeric values in millimetres where practical and derive inches using:

`inch = mm / 25.4`

Do not use approximate symbol relationships when an explicit lookup is available.

---

## 11. Common family labels useful for validation/autocomplete

These are common market combinations rather than the only valid ISO combinations:

- CCGT
- CCMT
- CNMA
- CNMG
- CNMM
- DCGT
- DCMT
- DNMG
- SCMT
- SNMA
- SNMG
- SNMM
- TCGT
- TCMT
- TNMA
- TNMG
- TMPT
- VBGT
- VBMT
- VCGT
- VCMT
- VNGG
- VNMG
- WNMG

Never reject an otherwise valid designation merely because it is absent from this convenience list.

---

## 12. Backend output contract recommendation

For each decoded insert, return at least:

- `input`
- `standard_mode`
- `shape_code`, `shape`, `nose_angle_deg`, `edge_count_per_side`
- `clearance_code`, `clearance_deg`, `positive_negative`
- `tolerance_class`, `tol_d_mm`, `tol_m_mm`, `tol_s_mm`
- `configuration_code`, `fixing_hole`, `countersink`, `chipbreaker_faces`
- `size_code`, `ic_mm` or applicable nominal size
- `thickness_code`, `thickness_mm`
- `radius_code`, `radius_mm`
- `suffixes`
- `warnings`
- `source_rule_version`

Keep rules/data separate from parsing code so the Markdown (or a generated JSON version of it) can be versioned in GitHub.

---

## 13. Boundary of this ruleset

This file decodes the seven primary ISO/ANSI turning-insert nomenclature positions and the dimensional/tolerance tables present on the cited page. It does **not** claim to encode:
- manufacturer-specific grades or coatings;
- manufacturer-specific chipbreaker names or chipbreaker geometry;
- undocumented dimensional tolerances;
- all optional ISO 1832 positions 8-13;
- full CBN/PCD/wiper detail beyond what the primary seven positions reveal.

For production use, verify edge cases and optional designation positions against a licensed/current copy of **ISO 1832** and any manufacturer-specific catalog rules you intend to support.

## Source

Machining Doctor, *ISO Inserts - Nomenclature, Dimensions & Tolerances*: https://www.machiningdoctor.com/isoturn/

Prepared as a normalized implementation reference from the source page, not as a verbatim copy.
