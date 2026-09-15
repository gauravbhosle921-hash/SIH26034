import re
from dataclasses import dataclass

@dataclass
class Finding:
    id: str
    field: str
    status: str
    severity: str
    message: str
    evidence: str = ""
    confidence: float = 0.0
    rule_ref: str = ""

class ComplianceEngine:
    """Prototype rule engine. Legal rules are intentionally data-driven so amendments can be versioned."""
    def evaluate(self, ocr, is_imported=False, commodity_type="general", panel_area_cm2=None, mm_per_pixel=None):
        text = ocr["text"]
        low = text.lower()
        words = ocr["words"]
        findings = []

        def has(patterns):
            for p in patterns:
                m = re.search(p, low, re.I)
                if m: return m.group(0)
            return None

        checks = [
            ("manufacturer", "Manufacturer / packer / importer identity & address", [r"manufactured\s*by", r"manufactured at", r"packed\s*by", r"imported\s*by", r"importer", r"manufacturer"], "HIGH"),
            ("product_name", "Product name / identity", [r"product", r"biscuits?", r"rice", r"oil", r"shampoo", r"soap", r"detergent"], "HIGH"),
            ("net_quantity", "Net quantity", [r"net\s*(qty|quantity|wt|weight)", r"\bnet\b", r"\d+(?:\.\d+)?\s*(kg|g|mg|l|ml|litre|liter|cm|m)\b"], "CRITICAL"),
            ("mrp", "MRP / retail sale price", [r"\bmrp\b", r"maximum\s*retail\s*price", r"retail\s*price"], "CRITICAL"),
            ("date", "Manufacturing / packing date", [r"date\s*of\s*(mfg|manufacture|packing|pack)", r"mfg\.?\s*date", r"packed\s*on", r"manufactured\s*on"], "HIGH"),
            ("best_before", "Best-before / use-by where applicable", [r"best\s*before", r"use\s*by", r"expiry", r"expires?"], "MEDIUM"),
            ("consumer_care", "Consumer-care contact details", [r"consumer\s*care", r"customer\s*care", r"helpline", r"toll\s*free", r"contact\s*us", r"email"], "HIGH"),
            ("unit_sale_price", "Unit sale price (where applicable)", [r"unit\s*sale\s*price", r"price\s*per\s*(kg|g|l|litre|liter|unit)"], "MEDIUM"),
            ("country_of_origin", "Country of origin (imported products)", [r"country\s*of\s*origin", r"made\s*in", r"origin\s*[:\-]"], "HIGH"),
        ]
        extracted = {}
        for key, label, patterns, severity in checks:
            hit = has(patterns)
            extracted[key] = self._extract_value(key, text, hit)
            if hit:
                findings.append(Finding(key, label, "PASS", "INFO", f"Likely declaration detected: {hit}", hit, self._confidence(words, hit), self._rule_ref(key)).__dict__)
            else:
                if key == "country_of_origin" and not is_imported:
                    status, sev = "REVIEW", "LOW"
                    msg = "Not required by this screening profile because the package was not marked as imported."
                else:
                    status = "REVIEW" if key in {"best_before", "unit_sale_price", "country_of_origin"} else "FAIL"
                    sev = "MEDIUM" if status == "REVIEW" else severity
                    msg = "Declaration not confidently detected by OCR. Verify on the package image."
                findings.append(Finding(key, label, status, sev, msg, "", 0.0, self._rule_ref(key)).__dict__)

        if extracted["mrp"]:
            price = re.search(r"(?:rs\.?|₹)\s*([0-9]+(?:\.[0-9]+)?)", extracted["mrp"], re.I)
            if not price:
                findings.append(Finding("mrp_format", "MRP format", "REVIEW", "HIGH", "MRP keyword found, but a readable rupee/number value was not confidently extracted.", extracted["mrp"], 0.55, "Rule 6 / applicable MRP declaration").__dict__)

        if extracted["net_quantity"]:
            unit = re.search(r"\b(kg|g|mg|l|ml|litre|liter)\b", extracted["net_quantity"], re.I)
            if not unit:
                findings.append(Finding("net_quantity_unit", "Net quantity unit", "REVIEW", "HIGH", "Quantity-like text detected without a clear mass/volume unit.", extracted["net_quantity"], 0.55, "Rule 13 / applicable quantity declaration").__dict__)

        avg_h = self._token_height(words, ["net", "qty", "quantity", "weight", "wt"])
        if mm_per_pixel and avg_h:
            estimated_mm = round(avg_h * mm_per_pixel, 2)
            required = self._required_font_mm(extracted.get("net_quantity"), commodity_type, panel_area_cm2)
            if required:
                status = "PASS" if estimated_mm >= required else "FAIL"
                findings.append(Finding("font_size", "Net-quantity numeral height (estimated)", status, "HIGH", f"Estimated character height {estimated_mm} mm; screening threshold {required} mm.", f"OCR token height ≈ {avg_h} px × {mm_per_pixel} mm/px", 0.70, "Rule 7(2)-(3), Tables I-II").__dict__)
            else:
                findings.append(Finding("font_size", "Declaration readability / font height", "REVIEW", "MEDIUM", f"Estimated character height {estimated_mm} mm; select the applicable package-size table for legal verification.", f"OCR token height ≈ {avg_h} px", 0.60, "Rule 7(2)-(3), Tables I-II").__dict__)
        else:
            findings.append(Finding("font_size", "Declaration readability / font height", "REVIEW", "MEDIUM", "OCR detected text, but a physical image scale (mm per pixel) was not supplied, so exact minimum font height cannot be concluded automatically.", "Provide mm_per_pixel after package/panel calibration.", 0.55, "Rule 7(2)-(3), Tables I-II").__dict__)

        overall = self._overall(findings)
        return {"overall_status": overall, "summary": self._summary(findings), "extracted": extracted, "findings": findings, "ocr": {"text": text, "words": words}}

    def _extract_value(self, key, text, hit):
        if not hit: return None
        patterns = {
            "mrp": r"(?:mrp|maximum\s*retail\s*price)[^₹0-9]{0,20}(₹|rs\.?)[ ]*([0-9]+(?:\.[0-9]+)?)",
            "net_quantity": r"(?:net\s*(?:qty|quantity|wt|weight))?[^\n]{0,20}(\d+(?:\.\d+)?\s*(?:kg|g|mg|l|ml|litre|liter))",
            "date": r"(?:mfg\.?|manufactur(?:e|ed)|packed)[^\d]{0,20}(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2}[/-]\d{2,4})",
        }
        p = patterns.get(key)
        if p:
            m = re.search(p, text, re.I)
            if m: return m.group(0)
        idx = text.lower().find(hit.lower())
        return text[max(0, idx-25):idx+100] if idx >= 0 else hit

    def _token_height(self, words, anchors):
        hs=[]
        for w in words:
            t=w["text"].lower()
            if any(a in t for a in anchors) and w["h"]>0: hs.append(w["h"])
        return max(hs) if hs else None

    def _required_font_mm(self, qty, commodity_type, panel_area_cm2):
        if not qty: return None
        m=re.search(r"(\d+(?:\.\d+)?)\s*(kg|g|mg|l|ml|litre|liter)", qty, re.I)
        if m and m.group(2).lower() in {"kg","g","mg","l","ml","litre","liter"}:
            val=float(m.group(1)); u=m.group(2).lower()
            grams=val*(1000000 if u=="kg" else 1 if u=="g" else .001 if u=="mg" else 1000)
            return 1 if grams <= 200 else 2 if grams <= 500 else 4
        if panel_area_cm2 is not None:
            return 1 if panel_area_cm2 <= 100 else 2 if panel_area_cm2 <= 500 else 4 if panel_area_cm2 <= 2500 else 6
        return None

    def _confidence(self, words, hit):
        if not hit: return 0.0
        tokens = {x.lower() for x in re.findall(r"[a-z0-9₹]+", hit)}
        vals = [w["confidence"] for w in words if w["text"].lower() in tokens]
        return round(sum(vals)/len(vals)/100, 2) if vals else 0.65

    def _rule_ref(self, key):
        return {"manufacturer":"Rule 6 / applicable manufacturer-packer-importer declaration", "product_name":"Rule 6 / name of commodity", "net_quantity":"Rule 6 and Rule 13 / net quantity", "mrp":"Rule 6 / retail sale price", "date":"Rule 6 / month-year/date declaration as applicable", "best_before":"Rule 6 / commodity-specific applicability", "consumer_care":"Rule 6 / consumer complaints contact", "unit_sale_price":"Rule 6 / applicable unit sale price", "country_of_origin":"Rule 6 / imported product country-of-origin declaration"}.get(key, "Applicable PCR requirement")

    def _overall(self, findings):
        if any(f["status"] == "FAIL" for f in findings): return "NON-COMPLIANT / REVIEW REQUIRED"
        if any(f["status"] == "REVIEW" for f in findings): return "REVIEW REQUIRED"
        return "SCREENING PASS"

    def _summary(self, findings):
        return {s: sum(1 for f in findings if f["status"] == s) for s in ["PASS", "FAIL", "REVIEW"]}
