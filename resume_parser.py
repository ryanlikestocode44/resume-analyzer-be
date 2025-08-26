import re
import io
import pdfplumber
from langdetect import detect
from dateutil import parser as date_parser
from datetime import datetime
from nltk import sent_tokenize
import spacy
from spacy.cli import download
from recommender import recommend_courses, recommend_field, recommend_videos, recommend_skills

# Load spaCy models
print("⏳ Loading spaCy Models...")
try:
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("❌ English model not found. Downloading...")
    download("en_core_web_sm")
    nlp_en = spacy.load("en_core_web_sm")

SECTION_KEYWORDS = [
    "skills", "keterampilan", "kemampuan", "proficiencies", "keahlian", "kompetensi",
    "technical skills", "keahlian teknis", "soft skills", "keahlian soft", "hard skills",
    "keahlian hard", "expertise", "spesialisasi", "specializations", "skill set", "skillset",
    "capabilities", "kualifikasi"
]

def is_reasonable_skill(skill):
    return 2 < len(skill) <= 50 and not any(char.isdigit() for char in skill)

def extract_skills_from_text(text):
    pattern = r'(?i)(' + '|'.join(SECTION_KEYWORDS) + r')[\s:]*\n?(.*?)(\n\n|\Z)'
    matches = re.findall(pattern, text, re.DOTALL)
    skill_candidates = []
    for _, content, _ in matches:
        lines = content.split('\n')
        for line in lines:
            line = line.strip().lstrip('-•–~ ')
            fragments = re.split(r'[,\|•]', line)
            skill_candidates.extend(fragments)
    cleaned_skills = [
        s.strip().title() for s in skill_candidates if is_reasonable_skill(s.strip())
    ]
    return sorted(set(cleaned_skills))

class ResumeParser:
    def __init__(self, file_bytes):
        self.file_bytes = file_bytes
        self.text = self.extract_text()
        self.cleaned_text = self.clean_text(self.text)
        self.language = detect(self.cleaned_text)
        self.doc = nlp_en(self.cleaned_text)
        self.sections = self.segment_sections()
        self.details = self.build_details()

    def extract_text(self):
        with pdfplumber.open(io.BytesIO(self.file_bytes)) as pdf:
            return "\n".join([page.extract_text() or '' for page in pdf.pages])

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def segment_sections(self):
        section_patterns = {
            "experience": r"(?i)(work experience|pengalaman kerja|pengalaman|riwayat pekerjaan|freelance|internship|magang|career history|experiences|riwayat karir)",
            "education": r"(?i)(education|pendidikan|academic background|riwayat pendidikan|educational background|academic history|academic qualifications|educations|qualifications|kualifikasi|academic credentials|academic achievements)",
            "skills": r"(?i)(skills|keterampilan|keahlian|kemampuan|proficiencies|technical skills|soft skills|hard skills|expertise|skill set|capabilities|kualifikasi)",
            "projects": r"(?i)(projects|portfolio|projek|proyek|project experience|project history|project portfolio|project work|project details|capstones|project work|project contributions|project showcases|project highlights|project accomplishments|project achievements|project summaries|project descriptions|project overviews|project outlines|project briefs|project reports|project documentation)",
        }
        lines = self.text.split('\n')
        sections = {}
        current_section = "general"
        sections[current_section] = []
        for line in lines:
            line_clean = line.strip()
            
            matched_section = None
            for key, pattern in section_patterns.items():
                if re.match(pattern, line_clean):
                    matched_section = key
                    break
            if matched_section:
                current_section = matched_section
                sections[current_section] = []
            sections[current_section].append(line_clean)
        return {sec: '\n'.join(lines) for sec, lines in sections.items()}

    def extract_name(self):
        names = [ent.text.strip() for ent in self.doc.ents if ent.label_ == "PER"]
        if names:
            return names[0]
        first_line = self.text.strip().split('\n')[0]
        return first_line if len(first_line.split()) <= 5 else ""

    def extract_email(self):
        match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", self.cleaned_text)
        return match.group(0) if match else None

    def extract_phone(self):
        match = re.search(r'(\+62[\s\-]?\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4})', self.cleaned_text)
        return re.sub(r'\D', '', match.group(1)) if match else None

    def extract_links(self):
        linkedin = github = None
        links = re.findall(r'(https?://[^\s]+|www\.[^\s]+|[^\s]+\.com/[^\s]+)', self.cleaned_text)
        for link in links:
            if 'linkedin.com' in link:
                linkedin = link.strip('.,')
            elif 'github.com' in link:
                github = link.strip('.,')
        return linkedin, github

    def extract_skills(self):
        return extract_skills_from_text(self.cleaned_text)

    def extract_education(self):
        edu_text = self.sections.get("education", "")
        
        # Pola umum untuk pendidikan
        patterns = [
            r'(High School|SMA|SMK|MA|SMU)[^\n,]{0,80}',
            r'(S1|Sarjana|Bachelor(?:\s+of\s+\w+)?)[^\n,]{0,80}',
            r'(S2|Magister|Master(?:\s+of\s+\w+)?)[^\n,]{0,80}',
            r'(S3|Doktor|Doctor|PhD)[^\n,]{0,80}',
            r'(Diploma(?:\s+[1-4])?)[^\n,]{0,80}',
            r'(Universitas|University|Institut|Academy|College)[^\n,]{0,80}'
        ]
        
        results = []
        for pattern in patterns:
            matches = re.findall(pattern, edu_text, re.IGNORECASE)
            results.extend(matches)

        # Ambil kalimat mengandung kata kunci pendidikan (backup heuristic)
        sentences = self.nlp_en(edu_text)
        keywords = ['universitas', 'institute', 'college', 'school', 'academy', 'bachelor', 'master', 'phd', 's1', 's2', 's3', 'diploma']
        for sent in sentences:
            if any(kw in sent.lower() for kw in keywords):
                results.append(sent.strip())

        # Bersihkan dan unik
        cleaned = list(set(r.strip() for r in results if len(r.strip()) >= 5))
        return cleaned
        
    def extract_projects(self):
        project_text = self.sections.get("projects", "")
        lines = project_text.split("\n")

        project_titles = []
        for line in lines:
            clean_line = line.strip("-• \t")

            if not clean_line or len(clean_line) < 5:
                continue

            # Regex kombinasi ID & EN
            match = re.search(
                r'(?i)(?:project|proyek|projek|karya|portofolio|portfolio|projects)\s*[:\-–]\s*(.+)', clean_line)

            if match:
                title = match.group(1).strip()
            elif re.match(r'(?i)^(create|determine|provide|membangun|membuat|merancang|mengembangkan|developed|built|created|designed)\b', clean_line):
                title = clean_line
            else:
                # fallback: jika baris terlihat seperti judul (title case atau pendek)
                if clean_line.istitle() or len(clean_line.split()) <= 6:
                    title = clean_line
                else:
                    continue

            project_titles.append(title)

        return list({t for t in project_titles if len(t) >= 5})

    def extract_experience(self):
        exp_text = self.sections.get("experience", "")
        lines = exp_text.split('\n')

        experience_titles = []
        for line in lines:
            clean_line = line.strip("-•\u2022 \t")
            if not clean_line or len(clean_line) < 5:
                continue

            # Cari format: Posisi – Perusahaan – Tahun (dalam EN atau ID)
            match = re.match(
                r'(?i)(?:bekerja sebagai|worked as|pengalaman sebagai)?\s*([\w\s/().,-]{3,100})\s+(?:di|at|@)\s+([\w\s().,&-]+)', clean_line)
            if match:
                title = match.group(1).strip()
                experience_titles.append(title)
            else:
                # fallback: deteksi baris kapitalisasi mirip jabatan
                words = clean_line.split()
                if 2 <= len(words) <= 8 and any(w[0].isupper() for w in words[:2]):
                    experience_titles.append(clean_line)

        return list({t for t in experience_titles if len(t) >= 5})

    def get_total_experience_from_text(self):
        # Map bulan Bahasa Indonesia ke Inggris untuk didukung dateutil.parser
        indo_months = {
            "januari": "January", "februari": "February", "maret": "March",
            "april": "April", "mei": "May", "juni": "June",
            "juli": "July", "agustus": "August", "september": "September",
            "oktober": "October", "november": "November", "desember": "December"
        }

        # Gabungkan pola bulan Inggris dan Indonesia
        month_pattern = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember)\.?\s?\d{4}'
        date_ranges = re.findall(rf'({month_pattern})\s*[-–]\s*((?:Present|Now|Sekarang|\d{{4}}))', self.text, re.IGNORECASE)

        total_months = 0
        for start_str, end_str in date_ranges:
            try:
                # Ganti nama bulan Indonesia ke Inggris
                for indo, eng in indo_months.items():
                    start_str = re.sub(indo, eng, start_str, flags=re.IGNORECASE)
                    end_str = re.sub(indo, eng, end_str, flags=re.IGNORECASE)

                # Parse tanggal
                start = date_parser.parse(start_str, fuzzy=True, default=datetime(2000, 1, 1))
                end = datetime.now() if re.search(r'present|now|sekarang', end_str.lower()) else date_parser.parse(end_str, fuzzy=True)

                # Hitung durasi
                total_months += max(0, (end.year - start.year) * 12 + (end.month - start.month))
            except Exception as e:
                print(f"Error parsing date range '{start_str} - {end_str}': {e}")
                continue

        return round(total_months / 12, 2)

    def score_experience(self):
        # Jumlah entitas yang berhubungan dengan pengalaman
        count_org = sum(1 for ent in self.doc.ents if ent.label_ == "ORG")
        count_date = sum(1 for ent in self.doc.ents if ent.label_ == "DATE")
        count_loc = sum(1 for ent in self.doc.ents if ent.label_ in ["LOC", "GPE"])
        count_person = sum(1 for ent in self.doc.ents if ent.label_ == "PERSON")
        numerics = sum(1 for ent in self.doc.ents if ent.label_ in ["CARDINAL", "QUANTITY"])

        # Kata kerja aksi (action verbs) dalam bahasa Inggris & Indonesia
        action_verbs = [
            "develop", "manage", "lead", "create", "optimize", "analyze", "design",
            "mengembangkan", "memimpin", "menganalisis", "mendesain", "mengelola", "membuat"
        ]
        verb_count = sum(self.cleaned_text.lower().count(v) for v in action_verbs)

        # Pecah kalimat untuk memberikan bonus jika teks terstruktur
        try:
            sentences = sent_tokenize(self.text, language='english')  # fallback default
            if len(sentences) <= 1:
                sentences = sent_tokenize(self.text, language='indonesian')
        except():
            sentences = [self.text]

        sentence_bonus = min(len(sentences) // 3, 3) * 1.0  # max 3 poin

        # Perhitungan skor total dengan batas maksimum tiap kategori
        score = 3 * min(count_org, 3)
        score += 2 * min(count_date, 3)
        score += 1.5 * min(count_loc, 2)
        score += 1.0 * min(count_person, 2)
        score += 2 * min(numerics, 2)
        score += 1.5 * min(verb_count, 5)
        score += sentence_bonus

        return round(min(score, 30), 1)
    
    def score_content_completeness(self):
        """Hitung skor kelengkapan konten resume (0–100)."""
        components = {
            "name": bool(self.extract_name()),
            "email": bool(self.extract_email()),
            "phone": bool(self.extract_phone()),
            "linkedin": bool(self.extract_links()[0]),
            "github": bool(self.extract_links()[1]),
            "skills": len(self.extract_skills()) > 0,
            "education": len(self.extract_education()) > 0,
            "projects": len(self.extract_projects()) > 0,
            "experience": len(self.extract_experience()) > 0
        }

        # Bobot tiap komponen (total 1.0)
        weights = {
            "name": 0.1,
            "email": 0.1,
            "phone": 0.1,
            "linkedin": 0.05,
            "github": 0.05,
            "skills": 0.2,
            "education": 0.15,
            "projects": 0.1,
            "experience": 0.15
        }

        score = sum(weights[k] for k, v in components.items() if v) * 100
        return round(score, 1)

    def calculate_overall_score(self, skill_match_percent):
        completeness = self.score_content_completeness()
        experience = self.score_experience() * (100 / 30)
        skill_match = skill_match_percent or 0

        w_completeness = 0.4
        w_experience = 0.35
        w_skill_match = 0.25

        overall = (completeness * w_completeness) + \
                (experience * w_experience) + \
                (skill_match * w_skill_match)

        return round(overall, 1)

    def build_details(self):
        linkedin, github = self.extract_links()
        raw_skills = self.extract_skills()
        matched_skills = [s for s in raw_skills]
        recommended_skills = recommend_skills(matched_skills)
        field_info = recommend_field(matched_skills)
        recommended_courses = recommend_courses(field_info["field"])
        videos = recommend_videos()
        
        details = {
            "name": self.extract_name(),
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "linkedin": linkedin,
            "github": github,
            "skills": matched_skills,
            "education": self.extract_education(),
            "projects": self.extract_projects(),
            "experience_items": self.extract_experience(),
            "total_experience_years": self.get_total_experience_from_text(),
            "experience_score": self.score_experience(),
            "resume_score": self.score_content_completeness(),
            "recommended_field": field_info["field"],
            "matched_field_skills": field_info["matched_skills"],
            "field_match_percent": field_info["match_percent"],
            "recommended_skills": recommended_skills,
            "recommended_courses": recommended_courses,
            "resume_video_url": videos["resume_video_url"],
            "interview_video_url": videos["interview_video_url"],
        }

        # Hitung skor keseluruhan
        details["overall_score"] = self.calculate_overall_score(details["field_match_percent"])
        return details

    def get_extracted_data(self):
        return self.details
