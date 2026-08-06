from report_generator import generate_custom_report

print("Testing generate_custom_report('daily')...")
pdf_path, msg = generate_custom_report('daily')
print("PDF Path:", pdf_path)
print("Generated Message Snippet:\n", msg[:400] if msg else "EMPTY")
