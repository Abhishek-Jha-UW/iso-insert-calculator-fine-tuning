"""Streamlit entry point for the ISO insert calculator."""

from csv import DictReader
from io import BytesIO
from math import isfinite
from pathlib import Path
from zipfile import BadZipFile

import pandas as pd
import streamlit as st
from openai import OpenAIError

from branding import render_header
from decoder import MODES, RULES, decode
from excel_output import MIME_XLSX, results_workbook, upload_template
from geometry import estimate
from interpretation import available, interpret
from shape_icons import shape_thumbnail

SAMPLE = Path(__file__).parent / "samples" / "sample_inserts.csv"
GRADE_TABLE = Path(__file__).parent / "rules" / "grade_densities.csv"
TOLERANCE_COLUMNS = {
    "tol_d_mm": "Inscribed circle d (mm)",
    "tol_m_mm": "Cutting-edge position m (mm)",
    "tol_s_mm": "Thickness s (mm)",
}


def material_input():
    with GRADE_TABLE.open(encoding="utf-8", newline="") as file:
        densities = {row["grade"]: row["density_g_cm3"] for row in DictReader(file)}
    grade = st.selectbox(
        "Material grade", [None, *densities],
        format_func=lambda value: "Custom density" if value is None else value,
    )
    preset = densities.get(grade)
    if preset:
        st.caption(f"Grade density · {preset} g/cm³")
        if grade == "Demo grade":
            st.caption("Illustrative density for testing. Use Custom density for actual parts.")
        return grade, float(preset)
    if grade is not None:
        st.caption("Density unavailable in the grade table. Enter a known value if available.")
    density = st.number_input(
        "Material density (g/cm³)", min_value=0.0, value=None,
        placeholder="Enter density", format="%.4f",
        key=f"manual_density:{grade or 'custom'}",
    )
    st.caption("Leave density blank to calculate dimensions and volume only.")
    return grade, density


def read_upload(upload):
    if upload is None:
        source = pd.read_csv(SAMPLE, dtype=str, keep_default_na=False)
    elif upload.name.lower().endswith(".csv"):
        source = pd.read_csv(BytesIO(upload.getvalue()), dtype=str, keep_default_na=False)
    else:
        source = pd.read_excel(BytesIO(upload.getvalue()), dtype=str, keep_default_na=False)
    source.columns = source.columns.str.strip().str.lower()
    if source.columns.duplicated().any():
        raise ValueError("Column names must be unique.")
    if "part_number" not in source and "name" in source:
        source = source.rename(columns={"name": "part_number"})
    if "part_number" not in source:
        raise ValueError("Include a part_number or Name column in your file.")
    if source.empty:
        raise ValueError("Add at least one insert to the file.")
    return source


def calculate(source, mode, density, grade=None):
    results = []
    for row_number, row in enumerate(source.to_dict("records"), start=2):
        part_number = row["part_number"]
        result = {
            "file_row": row_number, "part_number": part_number,
            "material_grade": grade, "density_g_cm3": density,
        }
        try:
            decoded = decode(part_number, mode)
            decoded["warnings"] = " | ".join(decoded["warnings"])
            result.update(decoded)
            hole = row.get("hole_diameter_mm", "").strip()
            try:
                hole_diameter = float(hole) if hole else None
            except ValueError as exc:
                raise ValueError("hole_diameter_mm must be numeric.") from exc
            calculation = estimate(decoded, density, hole_diameter)
            result.update(calculation)
            result["status"] = (
                "Estimated" if calculation["estimated_volume_mm3"] is not None else "Dimensions only"
            )
        except ValueError as exc:
            result.update(status="Review input", error=str(exc))
        results.append(result)
    return results


def render_results(frame, results):
    columns = [
        "part_number", "normalized_designation", "status", "shape", "clearance_deg",
        "tolerance_class", "ic_mm", "thickness_mm", "radius_mm", "gross_volume_mm3",
        "estimated_volume_mm3", "estimated_weight_g",
    ]
    st.subheader("Results")
    total, estimates, review = st.columns(3)
    estimated = sum(row["status"] == "Estimated" for row in results)
    total.metric("Parts loaded", len(results))
    estimates.metric("Volume estimates", estimated)
    review.metric("Exceptions", len(results) - estimated)
    st.caption("Volume and weight estimates use simplified geometry. Manufacturer-specific features may affect the estimate.")
    if st.toggle("Show per-insert tolerances"):
        index = columns.index("tolerance_class") + 1
        columns[index:index] = TOLERANCE_COLUMNS
    display = frame.reindex(columns=columns)
    display["status"] = [row.get("geometry_issue", row["status"]) for row in results]
    display.insert(display.columns.get_loc("shape"), "shape_icon", [
        shape_thumbnail(row.get("shape_code"), row.get("nose_angle_deg")) for row in results
    ])
    display["shape"] = [
        f'{row["nose_angle_deg"]}° {row["shape"]}' if row.get("shape") in {"Rhombic", "Parallelogram"}
        else row.get("shape")
        for row in results
    ]
    st.dataframe(
        display, hide_index=True,
        column_config={
            "part_number": "Part number",
            "normalized_designation": "Designation",
            "status": "Status",
            "shape_icon": st.column_config.ImageColumn(
                "Outline", width="small", help="Schematic plan view of the coded shape."
            ),
            "shape": "Shape",
            "clearance_deg": st.column_config.NumberColumn("Clearance", format="%d°"),
            "tolerance_class": "Tolerance class",
            **{
                key: st.column_config.NumberColumn(label, format="±%.3f")
                for key, label in TOLERANCE_COLUMNS.items()
            },
            "ic_mm": st.column_config.NumberColumn("Inscribed circle (mm)", format="%.3f"),
            "thickness_mm": st.column_config.NumberColumn("Thickness (mm)", format="%.3f"),
            "radius_mm": st.column_config.NumberColumn("Nose radius (mm)", format="%.3f"),
            "gross_volume_mm3": st.column_config.NumberColumn("Gross volume (mm³)", format="%.2f"),
            "estimated_volume_mm3": st.column_config.NumberColumn("Estimated volume (mm³)", format="%.2f"),
            "estimated_weight_g": st.column_config.NumberColumn("Estimated weight (g)", format="%.3f"),
        },
    )
    st.download_button(
        "Download Excel results", results_workbook(frame), "insert_results.xlsx",
        mime=MIME_XLSX, type="primary",
    )


def format_tolerance(value):
    return f"±{value:.3f}" if value is not None else "—"


def render_tolerance_reference():
    with st.expander("Tolerance reference"):
        class_rows = []
        for grade, values in RULES["tolerances"].items():
            limits = [format_tolerance(value) for value in values]
            if grade == "M":
                limits[:2] = ["See class M table"] * 2
            class_rows.append([grade, *limits])
        st.caption("Limits are in millimetres. A dash indicates that the rules provide no value.")
        st.dataframe(pd.DataFrame(class_rows, columns=["Class", *TOLERANCE_COLUMNS.values()]), hide_index=True)

        st.markdown("**Class M by shape and inscribed-circle size**")
        size_rows = [
            [shape, " to ".join(f"{value:g}" for value in bounds) if bounds else "Any size",
             format_tolerance(d), format_tolerance(m)]
            for shape, bounds, d, m in RULES["m_tolerances"]
        ]
        st.dataframe(
            pd.DataFrame(size_rows, columns=["Shape code", "Inscribed circle (mm)",
                                             TOLERANCE_COLUMNS["tol_d_mm"], TOLERANCE_COLUMNS["tol_m_mm"]]),
            hide_index=True,
        )


def render_exceptions(results):
    exceptions = [
        {"File row": row["file_row"], "Part number": row["part_number"],
         "Reason": row.get("error") or row.get("geometry_notes")}
        for row in results if row["status"] != "Estimated"
    ]
    with st.expander(f"Exceptions ({len(exceptions)})"):
        if exceptions:
            st.dataframe(pd.DataFrame(exceptions), hide_index=True)
        else:
            st.caption("All rows produced volume estimates.")


def render_assistant(results):
    with st.expander("Material density and result interpretation"):
        if not available():
            st.caption("AI assistance is unavailable on this deployment.")
            return
        st.caption("Request an indicative density range or an explanation of one calculated insert.")
        options = [None] + [i for i, row in enumerate(results) if "shape" in row]
        with st.form("interpretation"):
            material = st.text_input("Material or grade", max_chars=100, placeholder="e.g. WC–Co carbide")
            index = st.selectbox(
                "Insert to explain", options,
                format_func=lambda i: "Density guidance only" if i is None else
                f'{results[i]["part_number"]} · row {results[i]["file_row"]}',
            )
            submit = st.form_submit_button("Get AI guidance")
        if submit:
            if not material.strip() and index is None:
                st.info("Enter a material or choose an insert.")
                return
            with st.spinner("Getting guidance…"):
                try:
                    answer = interpret(material.strip(), None if index is None else results[index])
                except (OpenAIError, RuntimeError):
                    st.error("AI guidance is temporarily unavailable. Calculation results are still available.")
                else:
                    st.text(answer)


def main():
    st.set_page_config(page_title="ISO Insert Calculator", layout="wide")
    render_header(
        "ISO Insert Calculator",
        "Decode turning insert designations and estimate dimensions, volume, and weight.",
    )

    with st.sidebar:
        st.header("Inputs")
        upload = st.file_uploader("Upload part numbers", type=["csv", "xlsx"])
        st.download_button(
            "Download Excel template", upload_template(), "insert_upload_template.xlsx", mime=MIME_XLSX,
        )
        mode = st.selectbox("Designation format", MODES)
        grade, density = material_input()

    if density is not None and (not isfinite(density) or density <= 0):
        st.error("Enter a positive, finite density.")
        return

    try:
        source = read_upload(upload)
    except (ValueError, OSError, ImportError, BadZipFile) as exc:
        st.error(f"Unable to read the upload. {exc}")
        return
    if upload is None:
        st.info("Showing the sample file. Upload a CSV or Excel file to analyze your inserts.")

    results = calculate(source, mode, density, grade)
    render_results(pd.DataFrame(results), results)
    render_tolerance_reference()
    render_exceptions(results)
    render_assistant(results)


if __name__ == "__main__":
    main()
