import pytest
from resume_parser import ResumeParser
import fitz  # PyMuPDF

# Membuat PDF dummy untuk keperluan pengujian
@pytest.fixture(scope="module")
def dummy_pdf_bytes():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), 
        "John Doe\n"
        "john.doe@email.com\n"
        "+62 812-3456-7890\n"
        "LinkedIn: linkedin.com/in/johndoe\n"
        "GitHub: github.com/johndoe\n"
        "\n"
        "Skills\nPython, Machine Learning, Data Analysis\n\n"
        "Education\nBachelor of Science in Computer Science\nUniversitas Indonesia\n\n"
        "Experience\nSoftware Engineer at ABC Corp\nJan 2020 - Dec 2022\n\n"
        "Projects\nDeveloped Machine Learning model for fraud detection\n"
    )
    pdf_bytes = doc.write()
    doc.close()
    return pdf_bytes

def test_extract_text(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    assert "john.doe@email.com" in parser.text.lower()

def test_extract_email(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    email = parser.extract_email()
    assert email == "john.doe@email.com"

def test_extract_phone(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    phone = parser.extract_phone()
    assert phone.startswith("62812") or phone.startswith("0812")

def test_extract_name(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    name = parser.extract_name()
    assert name.lower().startswith("john")

def test_extract_links(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    linkedin, github = parser.extract_links()
    assert "linkedin.com" in linkedin
    assert "github.com" in github

def test_extract_skills(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    skills = parser.extract_skills()
    assert "Python" in skills or "Machine Learning" in skills

def test_extract_education(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    edu = parser.extract_education()
    assert any("universitas" in e.lower() or "bachelor" in e.lower() for e in edu)

def test_extract_experience(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    exp = parser.extract_experience()
    assert any("engineer" in e.lower() or "abc" in e.lower() for e in exp)

def test_extract_projects(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    projects = parser.extract_projects()
    assert any("machine learning" in p.lower() for p in projects)

def test_total_experience_years(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    years = parser.get_total_experience_from_text()
    assert years >= 2

def test_build_details(dummy_pdf_bytes):
    parser = ResumeParser(dummy_pdf_bytes)
    details = parser.get_extracted_data()
    assert details["email"]
    assert details["skills"]
    assert isinstance(details["experience_score"], float)
