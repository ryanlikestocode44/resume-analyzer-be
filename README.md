# 📂 Resume Analyzer - Backend

Program **Resume Analyzer** dibangun menggunakan **Python (Flask)** untuk menangani proses ekstraksi informasi, pemberian skor, dan rekomendasi berbasis aturan (rule-based), string matching, serta Named Entity Recognition (NER) ringan.

Program ini merupakan bagian dari **Tugas Akhir/Skripsi** dengan judul:  
**"Implementasi Ekstraksi Informasi, Penilaian, dan Rekomendasi Rule-Based dan Named Entity Recognition pada Program Web Resume Analyzer."**

---

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

---

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
   ```bash
   flask run

👨‍🎓 **Catatan**
Backend ini dibuat sebagai bagian dari penyusunan Tugas Akhir/Skripsi dan dirancang untuk mendukung program Resume Analyzer berbasis web.