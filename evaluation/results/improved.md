# Improved RAG

- Cases: 22
- Success rate: 1.0
- Document hit rate: 1.0
- Mean reciprocal rank: 0.889
- Avg latency ms: None

## By type

- access_control: 1.0
- ambiguous: 1.0
- conversational: 1.0
- multi_document: 1.0
- no_answer: 1.0
- straightforward: 1.0
- version_conflict: 1.0

## Notes

- Retrieval-only mode scores clarification/refusal without LLM generation.
- Baseline = vector-only; Improved = hybrid + rerank + packing + sufficiency/ambiguity.

## Cases

- `sales_current_enterprise_price` [PASS] type=version_conflict hit=True sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Sales/Pricing2026.pdf']
- `professional_api_change` [PASS] type=multi_document hit=True sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Finance/ExpensePolicy.pdf']
- `pricing_after_jan_2026` [PASS] type=version_conflict hit=True sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Sales/Pricing2026.pdf']
- `professional_2026_price` [PASS] type=straightforward hit=True sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Sales/Discounts.xlsx']
- `prepaid_discount_compare` [PASS] type=multi_document hit=True sources=['KnowledgeBase/Sales/Discounts.xlsx', 'KnowledgeBase/Sales/Discounts.xlsx']
- `sick_leave_days` [PASS] type=straightforward hit=True sources=['KnowledgeBase/HR/LeavePolicy.pdf', 'KnowledgeBase/HR/LeavePolicy.pdf']
- `pto_sick_carryover` [PASS] type=multi_document hit=True sources=['KnowledgeBase/HR/LeavePolicy.pdf', 'KnowledgeBase/HR/LeavePolicy.pdf']
- `retirement_match` [PASS] type=straightforward hit=True sources=['KnowledgeBase/HR/Benefits.pdf', 'KnowledgeBase/HR/Benefits.pdf']
- `vpn_portal` [PASS] type=straightforward hit=True sources=['KnowledgeBase/IT/VPNGuide.pdf', 'KnowledgeBase/IT/VPNGuide.pdf']
- `password_length` [PASS] type=straightforward hit=True sources=['KnowledgeBase/IT/PasswordPolicy.docx', 'KnowledgeBase/IT/PasswordPolicy.docx']
- `expense_meal_approval` [PASS] type=multi_document hit=True sources=['KnowledgeBase/Finance/ExpensePolicy.pdf', 'KnowledgeBase/Finance/ExpensePolicy.pdf']
- `travel_policy_effective` [PASS] type=straightforward hit=True sources=['KnowledgeBase/Finance/ExpensePolicy.pdf', 'KnowledgeBase/Finance/TravelPolicy.docx']
- `nda_retention` [PASS] type=straightforward hit=True sources=['KnowledgeBase/Finance/TravelPolicy.docx', 'KnowledgeBase/Finance/ExpensePolicy.pdf']
- `vendor_renewal` [PASS] type=straightforward hit=True sources=['KnowledgeBase/Sales/Discounts.xlsx', 'KnowledgeBase/Legal/VendorContract.pdf']
- `ambiguous_limit` [PASS] type=ambiguous hit=False sources=[]
- `ambiguous_approval` [PASS] type=ambiguous hit=False sources=[]
- `no_answer_refund` [PASS] type=no_answer hit=False sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Finance/ExpensePolicy.pdf']
- `no_answer_canada_leave` [PASS] type=no_answer hit=False sources=['KnowledgeBase/Finance/ExpensePolicy.pdf', 'KnowledgeBase/HR/LeavePolicy.pdf']
- `no_answer_ceo_travel` [PASS] type=no_answer hit=False sources=['KnowledgeBase/Finance/TravelPolicy.docx', 'KnowledgeBase/Finance/ExpensePolicy.pdf']
- `access_control_hr` [PASS] type=access_control hit=False sources=[]
- `access_control_legal` [PASS] type=access_control hit=False sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Sales/Pricing2026.pdf']
- `conversational_followup` [PASS] type=conversational hit=True sources=['KnowledgeBase/Sales/Pricing2026.pdf', 'KnowledgeBase/Sales/Pricing2026.pdf']
