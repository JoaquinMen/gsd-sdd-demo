import pytest
from jinja2 import Environment, FileSystemLoader

def test_index_template_renders_user_and_branding():
    env = Environment(loader=FileSystemLoader("src/agent/templates"))
    template = env.get_template("index.html")
    
    context = {
        "user": {
            "email": "marcus.vance@cimbal.com",
            "role": "Certified Operations Specialist",
            "sub": "accounts.google.com:9876543210",
        },
        "project_id": "cimbal-agri-prod",
        "bq_table": "cimbal-agri-prod.cimbal_operations.equipment_service_billing",
        "search_ds": "cimbal-equipment-policies-ds",
    }
    
    html = template.render(context)
    assert "Cimbal SA" in html
    assert "marcus.vance@cimbal.com" in html
    assert "Certified Operations Specialist" in html
    assert "IAP Protected" in html
    assert "chat-container" in html
    assert "Direct VPC Egress" in html
