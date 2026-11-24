"""Create the insert template and results workbooks for download."""

from io import BytesIO

from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
NAVY = "15324B"
LIGHT_BLUE = "EDF5FA"
RESULT_HEADERS = {
    "part_number": "Part number",
    "normalized_designation": "Designation",
    "material_grade": "Material grade",
    "density_g_cm3": "Density (g/cm³)",
    "ic_mm": "Inscribed circle (mm)",
    "thickness_mm": "Thickness (mm)",
    "radius_mm": "Nose radius (mm)",
    "estimated_volume_mm3": "Estimated volume (mm³)",
    "estimated_weight_g": "Estimated weight (g)",
    "tol_d_mm": "IC tolerance ± (mm)",
    "tol_m_mm": "Edge position tolerance ± (mm)",
    "tol_s_mm": "Thickness tolerance ± (mm)",
}


def workbook_bytes(workbook):
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def style_header(sheet):
    sheet.sheet_view.showGridLines = False
    sheet.freeze_panes = "A2"
    sheet.row_dimensions[1].height = 26
    for cell in sheet[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor=NAVY)
        cell.alignment = Alignment(vertical="center")


def upload_template():
    workbook = Workbook()
    inserts = workbook.active
    inserts.title = "Part Numbers"
    inserts.append(["part_number", "hole_diameter_mm"])
    style_header(inserts)
    inserts.column_dimensions["A"].width = 36
    inserts.column_dimensions["A"].number_format = "@"
    inserts.column_dimensions["B"].width = 25
    instructions = workbook.create_sheet("Instructions")
    for line in (
        "ISO Insert Calculator · Upload template",
        "Paste one insert designation per row in column A of Part Numbers, starting at A2.",
        "Keep the column headers as provided. Example designation: CCGT 060202 Z1.",
        "Column B is optional. Enter a through-hole diameter in millimetres only when known.",
        "Save the workbook and upload it to the calculator. Select a grade or enter density in the app.",
    ):
        instructions.append([line])
    instructions.column_dimensions["A"].width = 108
    style_header(instructions)
    return workbook_bytes(workbook)


def results_workbook(frame):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Insert Results"
    priority = [
        "part_number", "normalized_designation", "status", "material_grade", "density_g_cm3",
        "ic_mm", "thickness_mm", "radius_mm", "estimated_volume_mm3", "estimated_weight_g",
    ]
    columns = [key for key in priority if key in frame] + [key for key in frame if key not in priority]
    headers = [RESULT_HEADERS.get(key, key.replace("_", " ").capitalize()) for key in columns]
    sheet.append(headers)
    clean = frame[columns].astype(object).where(frame[columns].notna(), None)
    widths = [len(label) for label in headers]
    for row_number, values in enumerate(clean.itertuples(index=False, name=None), start=2):
        for index, (key, value) in enumerate(zip(columns, values), start=1):
            if isinstance(value, str):
                # Treat uploaded part numbers and suffixes as literal text.
                value = ILLEGAL_CHARACTERS_RE.sub("", value)
            cell = sheet.cell(row_number, index, value)
            if isinstance(value, str):
                cell.data_type = "s"
            elif isinstance(value, (int, float)) and key.endswith(("_mm", "_in", "_g", "_mm3", "_cm3")):
                cell.number_format = "0.0000" if key.endswith(("_in", "_cm3")) else "0.000"
            if row_number % 2 == 0:
                cell.fill = PatternFill("solid", fgColor=LIGHT_BLUE)
            if value is not None:
                widths[index - 1] = max(widths[index - 1], len(str(value)))
    style_header(sheet)
    sheet.freeze_panes = "B2"
    sheet.auto_filter.ref = sheet.dimensions
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = min(52, max(12, width + 3))
    return workbook_bytes(workbook)
