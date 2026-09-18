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

"checks": [
{
"rule_id": "COMMON-001",
"status": "PASS",
"severity": "INFO",
"message": "Document type is supported.",
"field": "document_type",
"details": null
},
{
"rule_id": "COMMON-004",
"status": "PASS",
"severity": "INFO",
"message": "All required passport fields are present.",
"field": null,
"details": null
},
{
"rule_id": "PAS-NUM-002",
"status": "PASS",
"severity": "INFO",
"message": "Passport number has a structurally reasonable format.",
"field": "passport_number",
"details": null
},
{
"rule_id": "PAS-NAME-002",
"status": "PASS",
"severity": "INFO",
"message": "Passport name has a reasonable character structure.",
"field": "name",
"details": null
},
{
"rule_id": "PAS-NAT-002",
"status": "PASS",
"severity": "INFO",
"message": "Nationality uses a three-letter code.",
"field": "nationality",
"details": null
},
{
"rule_id": "PAS-DOB-001",
"status": "PASS",
"severity": "INFO",
"message": "Date of birth is parseable.",
"field": "date_of_birth",
"details": null
},
{
"rule_id": "PAS-DOB-002",
"status": "PASS",
"severity": "INFO",
"message": "Date of birth is not in the future.",
"field": "date_of_birth",
"details": null
},
{
"rule_id": "PAS-EXP-001",
"status": "PASS",
"severity": "INFO",
"message": "Passport expiry date is parseable.",
"field": "expiry_date",
"details": null
},
{
"rule_id": "PAS-EXP-002",
"status": "PASS",
"severity": "INFO",
"message": "Passport is currently within its stated validity period.",
"field": "expiry_date",
"details": null
},
{
"rule_id": "PAS-SEX-001",
"status": "PASS",
"severity": "INFO",
"message": "Sex field contains a supported MRZ-compatible value.",
"field": "sex",
"details": null
},
{
"rule_id": "PAS-MRZ-002",
"status": "PASS",
"severity": "INFO",
"message": "MRZ has the expected two-line TD3 structure.",
"field": "mrz",
"details": null
},
{
"rule_id": "PAS-MRZ-003",
"status": "PASS",
"severity": "INFO",
"message": "MRZ character set is structurally valid.",
"field": "mrz",
"details": null
},
{
"rule_id": "PAS-MRZ-005",
"status": "PASS",
"severity": "INFO",
"message": "MRZ check digit for passport_number is valid.",
"field": "passport_number",
"details": {
"calculated": 1,
"provided": 1
}
},
{
"rule_id": "PAS-MRZ-006",
"status": "PASS",
"severity": "INFO",
"message": "MRZ check digit for date_of_birth is valid.",
"field": "date_of_birth",
"details": {
"calculated": 9,
"provided": 9
}
},
{
"rule_id": "PAS-MRZ-007",
"status": "PASS",
"severity": "INFO",
"message": "MRZ check digit for expiry_date is valid.",
"field": "expiry_date",
"details": {
"calculated": 8,
"provided": 8
}
},
{
"rule_id": "PAS-MRZ-008",
"status": "PASS",
"severity": "INFO",
"message": "MRZ composite check digit is valid.",
"field": "composite",
"details": {
"calculated": 1,
"provided": 1
}
},
{
"rule_id": "PAS-MRZ-009",
"status": "PASS",
"severity": "INFO",
"message": "Passport number matches the MRZ.",
"field": "passport_number",
"details": {
"visual": "P1234567",
"mrz": "P1234567"
}
},
{
"rule_id": "PAS-MRZ-010",
"status": "PASS",
"severity": "INFO",
"message": "Nationality matches the MRZ.",
"field": "nationality",
"details": {
"visual": "IND",
"mrz": "IND"
}
},
{
"rule_id": "PAS-MRZ-011",
"status": "PASS",
"severity": "INFO",
"message": "Date of birth matches the MRZ.",
"field": "date_of_birth",
"details": {
"visual": "950520",
"mrz": "950520"
}
},
{
"rule_id": "PAS-MRZ-012",
"status": "PASS",
"severity": "INFO",
"message": "Expiry date matches the MRZ.",
"field": "expiry_date",
"details": {
"visual": "300519",
"mrz": "300519"
}
},
{
"rule_id": "PAS-MRZ-013",
"status": "PASS",
"severity": "INFO",
"message": "Sex matches the MRZ.",
"field": "sex",
"details": {
"visual": "M",
"mrz": "M"
}
},
{
"rule_id": "PAS-NAME-003",
"status": "PASS",
"severity": "INFO",
"message": "Name is consistent with the MRZ representation.",
"field": "name",
"details": {
"visual": "DOE JOHN",
"mrz": "DOE JOHN"
}
}
]
}
