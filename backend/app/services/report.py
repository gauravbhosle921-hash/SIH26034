from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

def make_pdf_report(payload):
    out = Path(tempfile.gettempdir()) / "legal_metrology_report.pdf"
    doc = SimpleDocTemplate(str(out), pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet(); story = []
    story.append(Paragraph("LM-PACK Sentinel — Legal Metrology Screening Report", styles["Title"]))
    story.append(Paragraph(f"Overall status: {payload.get('overall_status','Unknown')}", styles["Heading2"]))
    story.append(Spacer(1, 10))
    rows = [["Field", "Status", "Severity", "Evidence / message", "Rule reference"]]
    for f in payload.get("findings", []):
        rows.append([f.get("field",""), f.get("status",""), f.get("severity",""), f.get("evidence") or f.get("message",""), f.get("rule_ref","")])
    t = Table(rows, repeatRows=1, colWidths=[90,55,55,190,110])
    t.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.4,colors.grey),("BACKGROUND",(0,0),(-1,0),colors.lightgrey),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),7)]))
    story.append(t); story.append(Spacer(1,12))
    story.append(Paragraph("Important: this is an OCR-based screening tool. A PASS means the declaration was detected, not that every legal condition, exemption, font-size, placement, commodity-specific rule, or physical legibility requirement has been conclusively satisfied.", styles["BodyText"]))
    doc.build(story)
    return str(out)
