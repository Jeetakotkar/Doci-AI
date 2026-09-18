# Module 2 — Document Validation

## AI-Based Fake Identity & Document Screening System

**SIH Problem Statement:** 26188  
**Module:** Module 2 — Document Validation  
**Prototype Status:** In Development

---

## 1. Purpose

Module 2 is responsible for validating the information extracted from identity and travel documents by Module 1.

The module does **not** determine whether a document is definitively genuine or forged.

Instead, it checks whether:

- extracted fields are structurally valid
- values follow known document rules
- dates are logically valid
- MRZ data follows ICAO-style structure
- MRZ check digits are valid
- information printed in different document sections is consistent
- the document appears expired
- suspicious inconsistencies exist

The result is returned as structured validation evidence that can later be consumed by the risk-scoring and decision modules.

---

# 2. Current Prototype Architecture

```text
                    MODULE 1
              OCR / Data Extraction
                       │
                       │ JSON
                       ▼
             ┌─────────────────────┐
             │     MODULE 2        │
             │ Document Validation │
             └──────────┬──────────┘
                        │
             ┌──────────┴──────────┐
             │                     │
             ▼                     ▼
       Field Validation       MRZ Validation
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
                Cross-field Checks
                        │
                        ▼
               Validation Result
                        │
                        ▼
              Future Risk Engine
                        │
                        ▼
             Module 3 / Module 4
```

---

# 3. Module 2 Input

Module 2 expects a **standardized JSON object** from Module 1.

Module 1 is responsible for:

- image processing
- OCR
- MRZ detection
- field extraction
- basic OCR normalization

Module 2 should not need to know how OCR was performed.

### Example

```json
{
  "document_type": "PASSPORT",
  "passport_number": "P1234567",
  "name": "DOE<<JOHN",
  "nationality": "IND",
  "date_of_birth": "1995-05-20",
  "expiry_date": "2030-05-19",
  "sex": "M",
  "mrz": [
    "P<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",
    "P1234567<1IND9505209M3005198<<<<<<<<<<<<<<01"
  ]
}
```

---

# 4. Input Contract

## Required fields for passport prototype

| Field | Type | Required | Description |
|---|---|---:|---|
| `document_type` | string | Yes | Type of document |
| `passport_number` | string | Yes | Passport number |
| `name` | string | Yes | Name extracted from document |
| `nationality` | string | Yes | Three-letter nationality/country code |
| `date_of_birth` | string | Yes | Date of birth |
| `expiry_date` | string | Yes | Passport expiry date |
| `sex` | string | Yes | M/F/X or MRZ-compatible value |
| `mrz` | array | Recommended | Two MRZ lines |

---

# 5. Optional/Future Fields

The final system can extend the input object with fields such as:

```text
issuing_country
date_of_issue
place_of_birth
place_of_issue
personal_number
document_version
document_code
visa_information
ocr_confidence
mrz_confidence
image_quality
source_image_id
document_country
```

These should remain optional during the prototype.

---

# 6. Validation Layers

Module 2 is divided into multiple validation layers.

## Layer 1 — Basic Input Validation

Checks whether required information exists.

Examples:

- passport number missing
- name missing
- nationality missing
- date of birth missing
- expiry date missing
- sex missing

---

## Layer 2 — Field Validation

Checks whether individual fields have reasonable structures.

Examples:

### Passport number

Checks:

- reasonable length
- allowed characters
- empty value

Country-specific passport-number patterns should **not** be globally hardcoded.

Future implementation:

```text
country_rules/
├── IND.json
├── USA.json
├── GBR.json
└── ...
```

---

### Nationality

Prototype checks:

- exactly three characters
- alphabetic country code

Future implementation can use an authoritative country-code dataset.

---

### Dates

Checks:

- date can be parsed
- date is logically valid
- date of birth is not in the future
- passport expiry status

---

### Sex

Prototype accepts:

```text
M
F
X
<
```

Common textual representations such as:

```text
MALE
FEMALE
```

are normalized where appropriate.

---

# 7. MRZ Validation

For a standard TD3 passport MRZ, the prototype checks:

```text
Line 1 → 44 characters
Line 2 → 44 characters
```

It also checks that MRZ characters belong to the expected character set:

```text
A-Z
0-9
<
```

---

# 8. MRZ Check Digits

The prototype implements the standard MRZ check-digit calculation using:

```text
Weights:

7 3 1
```

repeated across the field.

Character values:

```text
0-9 → numeric value
A-Z → 10-35
<   → 0
```

The resulting value is reduced modulo 10.

The prototype currently validates check digits for:

- passport number
- date of birth
- expiry date
- composite MRZ data

---

# 9. Cross-Field Validation

One of the most important parts of Module 2 is comparing information from different document sections.

For example:

```text
Visual passport number
        │
        ▼
P1234567

MRZ passport number
        │
        ▼
P1234567
```

Result:

```text
MATCH
```

But:

```text
Visual passport number
        │
        ▼
P1234567

MRZ passport number
        │
        ▼
P9999999
```

Result:

```text
MISMATCH
```

This creates useful evidence for later risk scoring.

---

# 10. Current Passport Rules

Current prototype rule IDs include:

| Rule ID | Purpose |
|---|---|
| `COMMON-001` | Document type validation |
| `COMMON-004` | Required-field validation |
| `PAS-NUM-002` | Passport number structure |
| `PAS-NAME-002` | Name structure |
| `PAS-NAT-002` | Nationality structure |
| `PAS-DOB-001` | DOB parsing |
| `PAS-DOB-002` | Future DOB detection |
| `PAS-EXP-001` | Expiry-date parsing |
| `PAS-EXP-002` | Expired passport detection |
| `PAS-SEX-001` | Sex field validation |
| `PAS-MRZ-001` | MRZ presence |
| `PAS-MRZ-002` | MRZ TD3 structure |
| `PAS-MRZ-003` | MRZ character validation |
| `PAS-MRZ-005` | Passport-number check digit |
| `PAS-MRZ-006` | DOB check digit |
| `PAS-MRZ-007` | Expiry check digit |
| `PAS-MRZ-008` | Composite check digit |
| `PAS-MRZ-009` | Passport number vs MRZ |
| `PAS-MRZ-010` | Nationality vs MRZ |
| `PAS-MRZ-011` | DOB vs MRZ |
| `PAS-MRZ-012` | Expiry date vs MRZ |
| `PAS-MRZ-013` | Sex vs MRZ |
| `PAS-NAME-003` | Name vs MRZ |

Rule IDs should remain stable because future modules may consume them.

---

# 11. Validation Status

Each validation check can return:

```text
PASS
FAIL
WARNING
NOT_CHECKED
```

### PASS

The tested condition is satisfied.

### FAIL

The value violates a deterministic validation rule.

### WARNING

Something deserves review but does not necessarily mean the document is invalid.

Example:

```text
Passport is expired.
```

### NOT_CHECKED

The system did not have sufficient information to perform the check.

This is important because:

> Missing information should not automatically be treated as proof of fraud.

---

# 12. Severity

Each check can have a severity:

```text
INFO
LOW
MEDIUM
HIGH
CRITICAL
```

Example:

```text
Expired document
→ MEDIUM
```

while:

```text
Passport number differs between visual field and MRZ
→ HIGH
```

Severity is evidence for the future risk engine.

It should **not** be treated as a final fraud probability.

---

# 13. Overall Result

The current prototype produces:

```text
VALID
REVIEW
INVALID
```

### VALID

No validation failures were detected.

### REVIEW

No deterministic invalidity was found, but warnings require attention.

### INVALID

One or more deterministic validation rules failed.

---

# 14. Output Structure

Module 2 returns:

```json
{
  "document_type": "PASSPORT",
  "overall_status": "VALID",
  "summary": {
    "total_checks": 22,
    "passed": 22,
    "failed": 0,
    "warnings": 0,
    "not_checked": 0
  },
  "checks": []
}
```

Every check contains:

```text
rule_id
status
severity
message
field
details
```

This makes the system explainable.

---

# 15. Why Explainability Matters

The system should not simply return:

```text
Risk = 87%
```

without explaining why.

Instead, downstream systems should be able to see evidence such as:

```text
PAS-MRZ-005
FAIL
HIGH

Passport number check digit is invalid.
```

and:

```text
PAS-MRZ-009
FAIL
HIGH

Passport number does not match the MRZ.
```

This allows a border-security operator to understand what triggered further review.

---

# 16. India-Specific Considerations

The SIH problem is intended for an Indian government/security context.

The prototype therefore leaves room for India-specific validation without pretending to have access to restricted government systems.

Future integrations may include authorized verification against appropriate government or departmental systems.

For the prototype:

```text
Government API access
        ↓
NOT REQUIRED
        ↓
Mock/local validation layer
```

No government database credentials, private APIs, or restricted datasets should be embedded in the prototype.

---

# 17. Future India-Specific Validation

Potential future validation layers:

```text
Passport issuing authority verification
Passport status verification
Lost/stolen document verification
Immigration/travel-history verification
Visa verification
Blacklist/watchlist verification
Identity database verification
```

These must be implemented only through officially authorized interfaces and access mechanisms.

For now they should remain mocked or disabled.

---

# 18. What Module 2 Does NOT Do

Module 2 does not currently perform:

```text
❌ OCR
❌ Face recognition
❌ Face matching
❌ Photo tampering detection
❌ Document image forgery detection
❌ Stamp forgery detection
❌ Metadata forensics
❌ Government database verification
❌ Watchlist screening
❌ Final fraud classification
```

Those belong to other modules or future integrations.

---

# 19. Relationship With Other Modules

### Module 1

Provides:

```text
Document image
      ↓
OCR
      ↓
Structured document data
```

### Module 2

Provides:

```text
Structured document data
      ↓
Rule validation
      ↓
Validation evidence
```

### Module 3

Will eventually provide:

```text
Image/document forensics
      ↓
Tampering evidence
```

### Module 4

Will eventually provide:

```text
Live/person image
      ↓
Face verification
      ↓
Identity-match evidence
```

### Future Risk Engine

Can combine:

```text
Module 2
   +
Module 3
   +
Module 4
   +
Authorized database results
   ↓
Risk assessment
```

---

# 20. Current Prototype Limitations

The prototype intentionally uses simplified rules.

Examples:

- country-specific document formats are not fully implemented
- government databases are not connected
- OCR confidence is not yet incorporated
- image-level analysis is not implemented
- visa validation is not implemented
- national ID validation is not implemented
- driving-license validation is not implemented
- permit validation is not implemented

These are planned extensions.

---

# 21. Future Architecture

The intended architecture is:

```text
                    ┌───────────────┐
                    │    Module 1   │
                    │      OCR      │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  Normalized   │
                    │ Document JSON  │
                    └───────┬───────┘
                            │
                            ▼
             ┌──────────────────────────┐
             │        Module 2          │
             │    Document Validation   │
             └────────────┬─────────────┘
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
        Field Rules    MRZ Rules   DB Rules
             │            │            │
             └────────────┼────────────┘
                          ▼
                  Validation Evidence
                          │
             ┌────────────┼────────────┐
             ▼            ▼            ▼
          Module 3     Module 4    Future DB
          Tampering      Face       Checks
             │            │            │
             └────────────┼────────────┘
                          ▼
                    Risk Engine
                          │
                          ▼
                   Final Screening
```

---

# 22. Development Philosophy

The prototype should follow these principles:

### Deterministic first

Rules should produce repeatable results.

### Explainable

Every failure should have a rule ID and explanation.

### Modular

Adding visa validation should not require rewriting passport validation.

### Configurable

Country-specific rules should eventually live in configuration files.

### Privacy-aware

Do not unnecessarily store identity-document images or extracted PII.

### Fail safely

A missing field should generally result in:

```text
NOT_CHECKED / REVIEW
```

rather than automatically meaning:

```text
FAKE
```

### Government integrations should be isolated

External verification should be implemented as a separate integration layer.

---

# 23. Current Folder Structure

```text
module2/
│
├── README.md
│
├── schemas.py
│
├── rules/
│   ├── __init__.py
│   ├── common_rules.py
│   ├── passport_rules.py
│   ├── visa_rules.py
│   ├── national_id_rules.py
│   ├── driving_license_rules.py
│   └── permit_rules.py
│
├── validators/
│   ├── __init__.py
│   └── passport_validator.py
│
├── tests/
│   ├── __init__.py
│   └── test_passport_validator.py
│
├── samples/
│   ├── sample_input.json
│   └── sample_output.json
│
└── data/
    └── mock_database.json
```

---

# 24. Current Prototype → Final Product

| Prototype | Future System |
|---|---|
| Local JSON | API-based document object |
| Static rules | Versioned rule engine |
| Mock data | Authorized databases |
| Passport validation | Multiple document types |
| Basic MRZ checks | Full document standards |
| Simple status | Risk assessment |
| Local execution | Secure backend |
| Manual testing | Automated test suite |
| Basic logs | Auditable screening trail |

---

## 25. Immediate Development Roadmap

### Phase 1 — Prototype

- [x] Passport validator
- [x] Basic field validation
- [x] MRZ structure validation
- [x] MRZ check digits
- [x] Cross-field validation
- [ ] Better test coverage
- [ ] Visa validator
- [ ] National ID validator
- [ ] Driving-license validator
- [ ] Permit validator

### Phase 2 — Integration

- [ ] Standard Module 1 → Module 2 contract
- [ ] FastAPI endpoint
- [ ] Input schema validation
- [ ] Structured API response
- [ ] Frontend integration

### Phase 3 — Intelligence

- [ ] Module 3 tampering results
- [ ] Module 4 face verification results
- [ ] Risk engine
- [ ] Explainable risk factors

### Phase 4 — Production-oriented

- [ ] Authentication
- [ ] Encryption
- [ ] Audit logging
- [ ] Role-based access
- [ ] Authorized government integrations
- [ ] Data-retention controls
- [ ] Monitoring
- [ ] Model/rule versioning

---

## 26. Important Prototype Disclaimer

This prototype is a **decision-support and screening system**, not an autonomous authority for determining a person's identity, citizenship, admissibility, or criminal status.

A validation failure should be interpreted as:

> "This document contains an inconsistency requiring further verification."

It should not automatically be interpreted as:

> "This person is fraudulent."

Final operational decisions should remain with authorized personnel and applicable official procedures.