import io
import pytest
from app import app as flask_app
from unittest.mock import patch
from reportlab.pdfgen import canvas

@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client()

def generate_pdf_file(content="Test Resume Content"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, content)
    p.save()
    buffer.seek(0)
    return buffer

@patch("app.ResumeParser")
def test_upload_success(mock_parser_class, client):
    # Mocking ResumeParser().get_extracted_data()
    mock_parser = mock_parser_class.return_value
    mock_parser.get_extracted_data.return_value = {
        "name": "John Doe",
        "email": "john@example.com",
        "skills": ["Python", "Data Analysis"]
    }

    pdf_file = generate_pdf_file()
    data = {
        'resume': (pdf_file, 'resume.pdf')
    }

    response = client.post('/upload', content_type='multipart/form-data', data=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert "name" in json_data
    assert "skills" in json_data

def test_upload_no_file(client):
    response = client.post("/upload")
    assert response.status_code == 400
    assert response.get_json()["error"] == "No file uploaded"

def test_upload_empty_file(client):
    data = {
        'resume': (io.BytesIO(b''), 'resume.pdf')
    }
    response = client.post("/upload", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Uploaded file is empty"

def test_upload_invalid_filetype(client):
    data = {
        'resume': (io.BytesIO(b'Some text'), 'resume.docx')
    }
    response = client.post("/upload", content_type='multipart/form-data', data=data)
    assert response.status_code == 400
    assert response.get_json()["error"] == "Only PDF files are supported"

@patch("app.ResumeParser")
def test_parser_returns_none(mock_parser_class, client):
    mock_parser = mock_parser_class.return_value
    mock_parser.get_extracted_data.return_value = None

    pdf_file = generate_pdf_file()
    data = {
        'resume': (pdf_file, 'resume.pdf')
    }

    response = client.post('/upload', content_type='multipart/form-data', data=data)
    assert response.status_code == 500
    assert "error" in response.get_json()
