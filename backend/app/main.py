from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .services.ocr import OCRService
from .services.rules import ComplianceEngine
from .services.report import make_pdf_report

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
app = FastAPI(title="LM-PACK Sentinel", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
ocr = OCRService()
engine = ComplianceEngine()

@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "service": "LM-PACK Sentinel"}

@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), is_imported: bool = Form(False), commodity_type: str = Form("general"), panel_area_cm2: float | None = Form(None), mm_per_pixel: float | None = Form(None)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload a JPG, PNG, WEBP or other image file.")
    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(413, "Image is larger than 15 MB.")
    try:
        ocr_result = ocr.run(raw)
        result = engine.evaluate(ocr_result, is_imported=is_imported, commodity_type=commodity_type, panel_area_cm2=panel_area_cm2, mm_per_pixel=mm_per_pixel)
        result["filename"] = file.filename
        return result
    except Exception as exc:
        raise HTTPException(500, f"Analysis failed: {exc}") from exc

@app.post("/api/report")
async def report(payload: dict):
    pdf = make_pdf_report(payload)
    return FileResponse(pdf, media_type="application/pdf", filename="legal-metrology-report.pdf")
