# Legal basis used by the prototype

## Primary Government sources

1. Legal Metrology (Packaged Commodities) Rules, 2011 — Government of India Gazette scan supplied with this project.
   - Rule 6, pages 5–7: package declarations including manufacturer/packer/importer identity, commodity name, net quantity, manufacture/packing/import month-year, MRP, dimensions where relevant, other prescribed declarations, and consumer-contact details.
   - Rule 7, pages 8–9: principal display panel and minimum numeral/letter heights. Table I applies when net quantity is declared by weight/volume; Table II applies when declared by length/area/number. The prototype stores these thresholds as a screening rule and requires physical image calibration before making a font-height conclusion.
   - Rule 8, page 9: required declarations are to be placed on the principal display panel, subject to the quantity-declaration placement provisions shown there.
   - Rule 9, page 9 onward: declarations are required to be conspicuous/readable; the prototype therefore treats OCR confidence and image quality as evidence rather than pretending OCR alone proves physical readability.

2. Department of Consumer Affairs current Legal Metrology overview.
   It lists the package declarations as manufacturer/packer/importer name and address, country of origin for imported products, common/generic name, net quantity, manufacture month/year, best-before/use-by where applicable, MRP inclusive of taxes, consumer care details, dimensions where relevant, and unit sale price.

3. Department of Consumer Affairs 18 January 2023 advisory on mandatory information on outer retail packages.
   It expressly lists the same ten declaration categories and states that unit sale price came into force from 01.02.2023 in that advisory. It also states that retail packages inside group/combination/multi-piece/gift packages require the necessary declarations under Rule 4.

4. G.S.R. 128(E), 13 February 2026 — supplied Gazette amendment.
   Effective 1 July 2026; adds Rule 6(10A) for e-commerce entities selling imported products to provide a searchable/sortable country-of-origin filter.

5. G.S.R. 312(E), 27 April 2026 — supplied Gazette amendment.
   Comes into force 1 July 2027; substitutes Rule 6(10A) with a revised country-of-origin filter wording for imported products.

6. G.S.R. 418(E), 29 May 2026 — supplied Gazette amendment.
   Effective on publication; permits mandatory declarations to be made at bonded warehouses of AEO Tier-2/Tier-3 operators subject to the retail package having all mandatory declarations before leaving those warehouses. It also adds the responsible director detail and annual update provision to Rule 27 and states registration certificates remain valid until cancelled.

## Engineering policy

- Every legal rule is versioned and should have an effective date.
- The engine must distinguish `PASS` (text detected), `FAIL` (required text not detected under the selected profile), and `REVIEW` (conditional or not measurable from the image alone).
- No LLM is allowed to invent a legal requirement. A human-readable rule reference is attached to each finding.
- Font-size compliance must not be declared from pixels alone. The system needs physical calibration (or a validated package/panel dimension) to convert pixels into millimetres.
- Commodity-specific legislation (for example food/cosmetics/seed requirements) must be implemented as separate rule packs rather than hard-coded into the generic Legal Metrology profile.
