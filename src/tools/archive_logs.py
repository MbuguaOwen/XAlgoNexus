from fpdf import FPDF
import os

log_dir = "logs"
output = "logs/xalgo_run_report.pdf"

pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

for file in os.listdir(log_dir):
    if file.endswith(".log"):
        with open(os.path.join(log_dir, file)) as f:
            pdf.set_font("Arial", style='B', size=14)
            pdf.cell(200, 10, txt=file, ln=True)
            pdf.set_font("Arial", size=10)
            for line in f:
                pdf.multi_cell(0, 5, line.strip())

pdf.output(output)
print(f"📄 Archived PDF: {output}")
