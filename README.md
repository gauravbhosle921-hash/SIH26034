# LM-PACK Sentinel

AI-assisted packaged-product label screening for India's Legal Metrology (Packaged Commodities) Rules, 2011.

## Why I built it

Checking packaged-product labels against legal requirements can be repetitive and easy to miss. This project is a prototype for using OCR, computer vision, and a small data-driven rules engine to flag possible issues and produce a review-friendly report.

It was built as an SIH 2026 project prototype, with the goal of making the first-pass screening process faster while keeping the final decision with a human reviewer.

## What it does

- Accepts a packaged-product label image through a simple web interface.
- Extracts visible text with Tesseract OCR.
- Uses image processing to prepare the label for OCR.
- Checks extracted information against a versioned rules matrix.
- Highlights potential compliance gaps instead of presenting them as final legal conclusions.
- Generates a PDF report for review and sharing.
- Includes a small sample label and automated tests.
- Can be run locally or with Docker.

## Tech stack

- **Backend:** Python, FastAPI, Pydantic
- **OCR:** Tesseract / pytesseract
- **Computer vision:** OpenCV, Pillow, NumPy
- **Reports:** ReportLab
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** pytest
- **Deployment:** Docker / Docker Compose

## Project structure

```text
legal-metrology-scanner/
├── backend/
│   └── app/
│       ├── main.py
│       ├── services/
│       │   ├── ocr.py
│       │   ├── report.py
│       │   └── rules.py
│       └── static/
│           ├── app.js
│           ├── index.html
│           └── styles.css
├── data/
│   └── rules_2011.json
├── docs/
│   └── legal_basis.md
├── sample_data/
│   └── demo_label.png
├── tests/
│   └── test_rules.py
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── SECURITY.md
└── README.md
```

## Run locally

### 1. Install prerequisites

You need Python 3.11+ and Tesseract OCR installed on your system.

On macOS with Homebrew:

```bash
brew install tesseract
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

## Docker

```bash
docker compose up --build
```

Then open `http://127.0.0.1:8000`.

## API

The prototype exposes a small API:

- `GET /` — web interface
- `GET /api/health` — health check
- `POST /api/analyze` — analyze a label image
- `POST /api/report` — generate a PDF report from an analysis

## Example workflow

1. Upload a clear package-label image.
2. OCR extracts the visible text.
3. The rules service evaluates the extracted fields.
4. The UI shows findings and areas that may need attention.
5. A PDF report can be generated for further review.

## Testing

Run:

```bash
pytest -q
```

## Roadmap

Some useful next steps for the project are:

- Improve OCR accuracy for low-quality and curved package images.
- Add more product/category-specific rule checks.
- Support multilingual label text.
- Add stronger confidence scoring and field-level explanations.
- Add user authentication and audit logs for a production deployment.
- Expand the test set with real-world label variations.
- Add a production deployment with proper monitoring and secure file handling.

## Legal and data considerations

This is a prototype and should not be treated as a substitute for professional legal or regulatory review. Rules can change, and OCR can misread labels. The rule matrix in `data/rules_2011.json` is intended to make the prototype's checks explicit and reviewable.

See `docs/legal_basis.md` and `SECURITY.md` for additional context.

## SIH 2026

This repository contains the working prototype prepared for Smart India Hackathon 2026.

If you have ideas for improving the compliance checks, OCR pipeline, or user experience, feel free to open an issue or suggest a change.
