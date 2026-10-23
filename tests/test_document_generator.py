import os
import pytest
from src.provisioning.generate_documents import generate_all_equipment_docs

def test_generate_all_equipment_docs(tmp_path):
    output_dir = tmp_path / "equipment_docs"
    generated_files = generate_all_equipment_docs(output_dir=str(output_dir))
    
    assert len(generated_files) == 3
    expected_filenames = [
        "equipment_warranty_guidelines.pdf",
        "machinery_operator_manuals.pdf",
        "regional_service_rates.pdf"
    ]
    for expected in expected_filenames:
        target_path = output_dir / expected
        assert target_path.exists(), f"Expected {expected} to be generated"
        assert target_path.stat().st_size > 1000, f"Expected {expected} to be non-empty"
