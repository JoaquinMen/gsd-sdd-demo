import os
from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class CimbalPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, "CIMBAL SA - Agricultural Equipment Operations & Technical Services", border=False, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()} | Confidential - Internal Dealer & Service Operations Only", align="C")

def build_warranty_guidelines_pdf(output_path: str):
    pdf = CimbalPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Equipment Warranty Guidelines & Harvest Emergency Policies", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Standard Manufacturer Warranty Coverage", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "Cimbal SA provides factory-backed warranty coverage for all new agricultural machinery sales:\n"
        "- Combine Harvesters (Series X9, S700): 24 months or 2,000 engine hours (whichever occurs first).\n"
        "- High-Horsepower Tractors (Series 8R, 9R): 36 months or 3,000 engine hours.\n"
        "- Row-Crop Planters (ExactEmerge) & Sprayers: 12 months comprehensive coverage.\n"
        "Warranty covers all OEM defect repairs, structural welds, hydraulic manifolds, and engine control unit (ECU) failures."
    ))
    pdf.ln(4)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Emergency Field Service & Harvest Season Multiplier (1.5x)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "During critical peak regional agricultural windows (Harvest Season: September 15 to November 15; "
        "Planting Season: April 1 to May 20), Cimbal SA authorizes emergency field service support:\n"
        "- All unscheduled field emergency repairs conducted after-hours (18:00 to 06:00) or on recognized national holidays "
        "qualify for an authorized Emergency Labor Multiplier of 1.5x the base regional hourly rate.\n"
        "- To qualify for warranty labor reimbursement under the 1.5x rate, the technician must document pre-authorization "
        "from the Regional Dealership Service Manager and log matching telematics trouble codes.\n"
        "- Routine maintenance and non-emergency scheduled inspections are strictly ineligible for the 1.5x rate."
    ))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Warranty Claim Submission & Reimbursement Protocol", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "Field technicians must record the customer name, machinery serial number, exact operating hours, and failed part numbers. "
        "Warranty claims must be submitted to the BigQuery operations warehouse within 72 hours of work completion. "
        "Claims flagged with is_warranty_claim = TRUE are reviewed by the Cimbal Warranty Audit Desk."
    ))
    
    pdf.output(output_path)

def build_operator_manuals_pdf(output_path: str):
    pdf = CimbalPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Machinery Operator Manual & Field Maintenance Specifications", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Preventive Maintenance Intervals", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "To maintain warranty validity, field technicians and owners must adhere to strict maintenance intervals:\n"
        "- Daily / Every 10 Engine Hours: Clean chaff spreaders, check engine oil dipstick, inspect hydraulic hoses for weeping.\n"
        "- Every 250 Engine Hours: Replace engine oil and filter (15W-40 Synthetic Blend), grease steering kingpins, inspect air pre-cleaner.\n"
        "- Every 500 Engine Hours: Replace primary fuel water-separator filter, service hydraulic reservoir filters, clean cooling pack.\n"
        "- Every 1,000 Engine Hours / Annual: Complete overhaul inspection, valve clearance adjustment, hydrostatic drive oil flush."
    ))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Onboard Telematics & Diagnostic Trouble Codes (DTC)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "Technicians diagnosing equipment in the field should correlate onboard ECU error codes:\n"
        "- DTC E-102 (Hydraulic High-Pressure Rail Drop): Indicates main pump relief valve cavitation or hydraulic cylinder seal blowout. Immediate shutdown required.\n"
        "- DTC T-204 (Hydrostatic Transmission Temperature Alert): Transmission sump fluid exceeds 95C. Inspect oil cooler fan clutch.\n"
        "- DTC F-301 (Common Rail Fuel Pressure Anomaly): High-pressure fuel pump delivering below 1,800 bar. Check fuel filters for particulate contamination."
    ))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Model Specifications: Combine Harvester X9 & Tractor 8R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "- Combine Harvester X9 1000: Dual rotary separator, 13.6L PowerTech engine (639 hp), 16,200L grain tank capacity.\n"
        "- Tractor 8R 410: 9.0L PowerTech engine (410 hp), e23 PowerShift transmission, Category 4 rear three-point hitch (9,072 kg lift capacity)."
    ))

    pdf.output(output_path)

def build_service_rates_pdf(output_path: str):
    pdf = CimbalPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Regional Dealership Field Labor Rates & Billing Schedule", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "1. Standard Regional Hourly Labor Rates (USD)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "Labor rates vary by regional operational hub reflecting local market costs and specialized tooling:\n"
        "- Midwest Hub (Des Moines / Omaha): $140.00 USD per labor hour.\n"
        "- South Hub (Dallas / Memphis): $130.00 USD per labor hour.\n"
        "- West Hub (Sacramento / Boise): $150.00 USD per labor hour.\n"
        "Customer invoices are calculated as: Total Charge = (Labor Hours * Regional Rate) + Parts Cost (USD)."
    ))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "2. Travel & Mileage Allowances", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "- Field service calls within a 30-mile radius of the regional dealership hub incur no travel fee.\n"
        "- For calls beyond 30 miles, a flat travel surcharge of $2.50 USD per round-trip mile applies.\n"
        "- Travel charges for valid warranty repairs on immobilized equipment are 100% absorbed by Cimbal SA."
    ))
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "3. Parts Pricing & Warranty Markups", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, (
        "Replacement parts installed during non-warranty maintenance are billed at standard catalog MSRP. "
        "Warranty parts are billed at internal dealer transfer cost ($0 charge to farm client)."
    ))

    pdf.output(output_path)

def generate_all_equipment_docs(output_dir: str = "data/equipment_docs") -> list[str]:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    
    files = [
        ("equipment_warranty_guidelines.pdf", build_warranty_guidelines_pdf),
        ("machinery_operator_manuals.pdf", build_operator_manuals_pdf),
        ("regional_service_rates.pdf", build_service_rates_pdf)
    ]
    
    generated = []
    for filename, builder in files:
        file_path = str(out_path / filename)
        builder(file_path)
        generated.append(file_path)
    
    return generated

if __name__ == "__main__":
    generated_files = generate_all_equipment_docs()
    print(f"Successfully generated {len(generated_files)} Cimbal equipment documentation PDFs:")
    for f in generated_files:
        print(f"  - {f}")
