from backend.app.services.rules import ComplianceEngine

def test_compliant_like_text():
    text = 'COFFEE POWDER NET WEIGHT 500 g MRP ₹250 Manufactured by ABC Foods Pvt Ltd, Delhi Packed on 01/08/2026 Consumer Care 1800-123-4567 Email care@example.com'
    ocr = {'text': text, 'words': [{'text': w, 'confidence': 90, 'x':0,'y':0,'w':10,'h':10} for w in text.split()]}
    r = ComplianceEngine().evaluate(ocr)
    assert r['extracted']['mrp']
    assert r['extracted']['net_quantity']
    assert any(x['field'].startswith('Consumer') for x in r['findings'])

def test_missing_fields_are_flagged():
    ocr = {'text': 'SOAP 100 g', 'words': []}
    r = ComplianceEngine().evaluate(ocr)
    assert any(x['status'] == 'FAIL' for x in r['findings'])
