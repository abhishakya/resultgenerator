import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm,inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ================= CONFIG =================
OUTPUT_DIR = "report_cards"
os.makedirs(OUTPUT_DIR, exist_ok=True)

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = RIGHT_MARGIN = 18 * mm
TOP_MARGIN = 2 * inch
BOTTOM_MARGIN = 10 * mm
ALL_SUBJECTS = [
    "Hindi",
    "English",
    "Maths",
    "Science",
    "SST",
    "Computer",
    "Sanskrit"
]

USABLE_WIDTH = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN

# ================= STYLES =================
styles = getSampleStyleSheet()

title_style = ParagraphStyle(
    "title", parent=styles["Title"], alignment=TA_CENTER, fontSize=14
)

school_style = ParagraphStyle(
    "school", parent=styles["Normal"], alignment=TA_CENTER, fontSize=10
)

normal = ParagraphStyle(
    "normal", parent=styles["Normal"], fontSize=9
)

# ================= HELPERS =================
def safe(v):
    if pd.isna(v):
        return ""
    return str(v)

def grade(m):
    try:
        m = int(m)
    except:
        return ""
    if m >= 91: return "A1"
    if m >= 81: return "A2"
    if m >= 71: return "B1"
    if m >= 61: return "B2"
    if m >= 51: return "C1"
    if m >= 41: return "C2"
    if m >= 33: return "D"
    return "E"

def fmt_date(val):
    """Return formatted date like '08 Jan 2000' or blank placeholder."""
    if pd.isna(val) or val == "":
        return "__________"
    try:
        dt = pd.to_datetime(val)
        return dt.strftime("%d %b %Y")
    except Exception:
        return str(val)

# ================= PDF =================
def make_report(student):
    term1_total_all = 0
    term2_total_all = 0
    file_name = f"{student['admission_no']}_{student['name']}.pdf".replace(" ", "_")
    path = os.path.join(OUTPUT_DIR, file_name)

    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=LEFT_MARGIN,
        rightMargin=RIGHT_MARGIN,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN
    )

    el = []

    # ===== HEADER =====
    el.append(Paragraph("<b>Indus International Academy</b>", title_style))
    el.append(Spacer(1, 8))

    # ===== STUDENT INFO (FULL WIDTH) =====
    info = [
        ["Admission No.", student["admission_no"], "Class & Section", student["class"]],
        ["Roll No.", student["roll_no"], "Student Name", student["name"]],
        ["Father's Name", student["father"], "Mother's Name", student["mother"]],
        ["Date of Birth", student["dob"], "Attendance", student["attendance"]],
    ]

    info_t = Table(info, colWidths=[
        USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.32,
        USABLE_WIDTH * 0.18, USABLE_WIDTH * 0.32
    ])

    info_t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    el.append(info_t)
    el.append(Spacer(1, 6))

    # ===== MARKS TABLE (FULL WIDTH) =====
    h1 = [
        "Scholastic Areas\n\nSubject\nName",
        "TERM I EXAM", "", "", "", "", "",
        "TERM II EXAM", "", "", "", "", "",
        "Grand \nTotal"
    ]
    h2 = [
        "Subject",
        "PT 1\n10", "NB\n5", "SE\n5", "HY\n80", "Marks\n100", "Grade",
        "PT 2\n10", "NB\n5", "SE\n5", "Annual\n80", "Marks\n100", "Grade",
        "Marks\n200"
    ]

    data = [h1, h2]

    grand = 0
    subject_count = len(student["subjects"])

    for sub, m in student["subjects"].items():
        t1 = m["t1_total"]
        t2 = m["t2_total"]
        final = t1 + t2

        term1_total_all += t1
        term2_total_all += t2
        grand += final

        data.append([
            sub,
            m["t1_pt"], m["t1_nb"], m["t1_se"], m["t1_exam"], t1, grade(t1),
            m["t2_pt"], m["t2_nb"], m["t2_se"], m["t2_exam"], t2, grade(t2),
            final
        ])

    max_term1 = subject_count * 100
    max_term2 = subject_count * 100
    max_grand = subject_count * 200

    term1_percent = round((term1_total_all / max_term1) * 100, 2) if max_term1 else 0
    term2_percent = round((term2_total_all / max_term2) * 100, 2) if max_term2 else 0
    final_percent = round((grand / max_grand) * 100, 2) if max_grand else 0
    data.append([
    "Total Marks Obtained",
    "", "", "", "",
    f"{term1_total_all}/{max_term1}", "",     # Term I total
    "", "", "", "",
    f"{term2_total_all}/{max_term2}", "",     # Term II total
    f"{grand}/{max_grand}"                    # Grand total
    ])
    data.append([
    "Percentage",
    "", "", "", "",
    f"{term1_percent}%", "",     # Term I %
    "", "", "", "",
    f"{term2_percent}%", "",     # Term II %
    f"{final_percent}%"          # Final %
    ])

    col_widths = [USABLE_WIDTH * 0.14] + [USABLE_WIDTH * 0.066] * 13

    table = Table(data, repeatRows=2, colWidths=col_widths)

    table.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,1), colors.lightgrey),
        ("ALIGN", (1,2), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 8),

        ("SPAN", (0,0), (0,1)),
        ("SPAN", (1,0), (6,0)),
        ("SPAN", (7,0), (12,0)),
        ("SPAN", (13,0), (13,1)),
        ("SPAN", (0,-2), (4,-2)),
        ("SPAN", (0,-1), (4,-1)),
    ]))

    el.append(table)
    el.append(Spacer(1, 6))

    # ===== CO-SCHOLASTIC (FULL WIDTH) =====
    el.append(Paragraph(
        "<b>Co-Scholastic Areas : on a 3 point (A–C) grading scale</b>", normal
    ))

    co = Table([
        ["Co-Scholastic Area", "Term I", "Term II"],
        ["Moral Science", student["moral"], student["moral_1"]],
        ["Art", student["art"], student["art_1"]],
        ["P.T.", student["pt"], student["pt_1"]],
        ["G.K.", student["gk"], student["gk_1"]],
        ["Discipline", student["discipline"], student["discipline_1"]],
    ], colWidths=[
        USABLE_WIDTH * 0.5,
        USABLE_WIDTH * 0.25,
        USABLE_WIDTH * 0.25
    ])

    co.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (1,1), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))

    el.append(co)
    el.append(Spacer(1, 6))

    # ===== RESULT =====
    el.append(Paragraph(f"<b>Result :</b> {'Passed' if final_percent >= 33 else 'Failed'}", normal))
    el.append(Paragraph("<b>Promoted to Class :</b> VI", normal))
    el.append(Spacer(1, 6))

    # ===== SIGNATURE (FULL WIDTH) =====
    sign = Table([
        ["Date :", "Sign of Class Teacher", "Sign of Principal"],
        ["\n\n", "", ""]
    ], colWidths=[
        USABLE_WIDTH * 0.3,
        USABLE_WIDTH * 0.35,
        USABLE_WIDTH * 0.35
    ])

    sign.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ]))
    el.append(sign)
    el.append(Spacer(1, 6))

    # ===== GRADING SCALE (FULL WIDTH) =====
    grade_t = Table([
        ["Marks Range", "Grade", "Marks Range", "Grade"],
        ["91–100", "A1", "51–60", "C1"],
        ["81–90", "A2", "41–50", "C2"],
        ["71–80", "B1", "33–40", "D"],
        ["61–70", "B2", "32 & below", "E"],
    ], colWidths=[
        USABLE_WIDTH * 0.25,
        USABLE_WIDTH * 0.25,
        USABLE_WIDTH * 0.25,
        USABLE_WIDTH * 0.25
    ])

    grade_t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.black),
        ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("FONTSIZE", (0,0), (-1,-1), 7.5),
    ]))
    el.append(grade_t)

    doc.build(el)

# ================= MAIN =================
def generate(excel):
    students = pd.read_excel(excel, "STUDENTS")
    marks = pd.read_excel(excel, "MARKS")
    co = pd.read_excel(excel, "CO_SCHOLASTIC")

    students["admission_no"] = students["admission_no"].astype(str)
    marks["admission_no"] = marks["admission_no"].astype(str)
    co["admission_no"] = co["admission_no"].astype(str)

    for _, s in students.iterrows():
        adm = s["admission_no"]
        sm = marks[marks["admission_no"] == adm]
        sc = co[co["admission_no"] == adm]

        subjects = {}
        for sub in ALL_SUBJECTS:
            subjects[sub] = {
            "t1_pt": 0,
            "t1_nb": 0,
            "t1_se": 0,
            "t1_exam": 0,
            "t2_pt": 0,
            "t2_nb": 0,
            "t2_se": 0,
            "t2_exam": 0,
            "t1_total": 0,
            "t2_total": 0,
            }

        # 2️⃣ Overwrite ONLY subjects present in Excel
        for _, m in sm.iterrows():
            sub = m["subject"]
            if sub in subjects:
                subjects[sub] = {
                    "t1_pt": m["T1_periodic"],
                    "t1_nb": m["T1_notebook"],
                    "t1_se": m["T1_enrichment"],
                    "t1_exam": m["T1_exam"],
                    "t2_pt": m["T2_periodic"],
                    "t2_nb": m["T2_notebook"],
                    "t2_se": m["T2_enrichment"],
                    "t2_exam": m["T2_exam"],
                    "t1_total": m["T1_periodic"] + m["T1_notebook"] + m["T1_enrichment"] + m["T1_exam"],
                    "t2_total": m["T2_periodic"] + m["T2_notebook"] + m["T2_enrichment"] + m["T2_exam"],
                }

        c = sc.iloc[0] if not sc.empty else {}

        student = {
            "admission_no": adm,
            "name": safe(s["name"]),
            "class": safe(s["class"]),
            "roll_no": safe(s["roll_no"]),
            "father": safe(s["father"]),
            "mother": safe(s["mother"]),
            "dob": safe(s["dob"]),
            "attendance": safe(s["attendance"]),
            "subjects": subjects,
            "moral": safe(c.get("moral","")),
            "art": safe(c.get("art","")),
            "pt": safe(c.get("pt","")),
            "gk": safe(c.get("gk","")),
            "discipline": safe(c.get("discipline","")),
            "moral_1": safe(c.get("moral_1","")),
            "art_1": safe(c.get("art_1","")),
            "pt_1": safe(c.get("pt_1","")),
            "gk_1": safe(c.get("gk_1","")),
            "discipline_1": safe(c.get("discipline_1","")),
        }

        make_report(student)

# ================= GUI =================
def start():
    root = tk.Tk()
    root.withdraw()

    file = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel Files", "*.xlsx")]
    )
    if not file:
        return

    try:
        generate(file)
        messagebox.showinfo("Success", "CBSE Report Cards Generated Successfully!")
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    start()
