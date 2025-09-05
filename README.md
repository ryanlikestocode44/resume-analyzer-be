# INDONESIAN
---------------------------------------

# 📂 Resume Analyzer - Backend

Program **Resume Analyzer** dibangun menggunakan **Python (Flask)** untuk menangani proses ekstraksi informasi, pemberian skor, dan rekomendasi berbasis aturan (rule-based), string matching, serta Named Entity Recognition (NER) ringan.

Program ini merupakan bagian dari **Tugas Akhir/Skripsi** dengan judul:  
**"Implementasi Ekstraksi Informasi, Penilaian, dan Rekomendasi Rule-Based dan Named Entity Recognition pada Program Web Resume Analyzer."**

## 🚀 Fitur Backend
- Ekstraksi informasi dari resume (*ATS-friendly PDF*), termasuk:
  - Nama, email, nomor telepon, tautan LinkedIn/GitHub
  - Pendidikan, pengalaman, proyek, keterampilan
- Penilaian resume:
  - Skor pengalaman
  - Skor kelengkapan konten
  - Skor keseluruhan
- Rekomendasi bidang pekerjaan, skill tambahan, kursus daring, dan video tutorial.
- API berbasis Flask yang siap diintegrasikan dengan frontend.

## 🛠️ Instalasi Backend

1. **Clone repository & masuk folder backend**
   ```bash
   cd backend
2. **Buat Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
4. **Unduh Model spaCy dan Resource NLTK**
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
5. **Jalankan Server**
   ```bash
   python app.py
   atau
   flask run

## 👨‍🎓 Catatan
Backend ini dibuat sebagai bagian dari penyusunan Tugas Akhir/Skripsi dan dirancang untuk mendukung program Resume Analyzer berbasis web.


ENGLISH
-------------------------------------------------------
# 📂 Resume Analyzer - Backend

The **Resume Analyzer** backend is built using **Python (Flask)** to handle information extraction, resume scoring, and recommendations using rule-based methods, string matching, and lightweight Named Entity Recognition (NER).

This program is developed as part of a **Bachelor Thesis/Final Project** with the title:  
**"Implementation of Information Extraction, Evaluation, and Recommendations Using Rule-Based and Named Entity Recognition on a Web-Based Resume Analyzer Program."**

## 🚀 Backend Features
- Extracts information from ATS-friendly PDF resumes, including:
  - Name, email, phone number, LinkedIn/GitHub links
  - Education, experience, projects, and skills
- Resume evaluation:
  - Experience score
  - Content completeness score
  - Overall score
- Recommendations for job roles, additional skills, online courses, and tutorial videos.
- Flask-based REST API ready to integrate with the frontend.

---

## 🛠️ Backend Installation

1. **Clone the repository & navigate to the backend folder**
   ```bash
   cd backend
2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
4. **Download spaCy model and NLTK resource**
   ```bash
   python -m spacy download en_core_web_sm
   python -m nltk.downloader punkt stopwords averaged_perceptron_tagger
5. **Run the server**
   ```bash
   python app.py
   # or
   flask run

👨‍🎓 Notes
This backend is developed as part of a Bachelor Thesis/Final Project and is designed to support the web-based Resume Analyzer program.
