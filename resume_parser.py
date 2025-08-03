import os
import re
import pdfplumber
import pandas as pd
from datetime import datetime
from dateutil import parser as date_parser
from nltk import sent_tokenize
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline, logging
from tqdm import tqdm
import joblib
from recommender import recommend_courses, recommend_field, recommend_videos, recommend_skills

print("⏳ Loading IndoBERT NER model and skill cache...")
CACHE_DIR = "cached"
os.makedirs(CACHE_DIR, exist_ok=True)

# Auto-load IndoBERT
logging.set_verbosity_error()  # suppress loading logs

print("⏳ Loading IndoBERT NER model...")
NER_MODEL_ID = "cahya/bert-base-indonesian-NER"
NER_TOKENIZER = AutoTokenizer.from_pretrained(NER_MODEL_ID)
NER_MODEL = AutoModelForTokenClassification.from_pretrained(NER_MODEL_ID)
NER_PIPE = pipeline("ner", model=NER_MODEL, tokenizer=NER_TOKENIZER, aggregation_strategy="simple")

# Auto-generate skill cache from job_skills.csv
CACHE_FILE = os.path.join(CACHE_DIR, "cached_skills.pkl")
if os.path.exists(CACHE_FILE):
    SKILL_SET = joblib.load(CACHE_FILE)
    print(f"✅ Loaded skill cache from {CACHE_FILE} ({len(SKILL_SET)} skills)")
else:
    print("⚙️ Generating skill cache from datasets/job_skills.csv...")
    job_skills_csv = "datasets/job_skills.csv"
    if not os.path.exists(job_skills_csv):
        raise FileNotFoundError(f"Missing required dataset: {job_skills_csv}")
    
    df = pd.read_csv(job_skills_csv)
    skill_set = set()
    for skill_list in tqdm(df["job_skills"].dropna(), desc="Processing job_skills.csv"):
        for skill in skill_list.split(","):
            clean_skill = skill.strip().title()
            if 2 < len(clean_skill) <= 50:
                skill_set.add(clean_skill)
    SKILL_SET = sorted(skill_set)
    joblib.dump(SKILL_SET, CACHE_FILE)
    print(f"✅ Cached {len(SKILL_SET)} unique skills to {CACHE_FILE}")

# Skills Section Keywords
SECTION_KEYWORDS = [
    "skills", "keterampilan", "kemampuan", "proficiencies", "keahlian", "kompetensi", "technical skills", "keahlian teknis", "soft skills", "keahlian soft", "hard skills", "keahlian hard", "expertise", "spesialisasi", "specializations", "skill set", "skillset", "capabilities", "kualifikasi"
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
            line = line.strip().lstrip('-\u2022\u2013~ ')
            fragments = re.split(r'[,\|\u2022]', line)
            skill_candidates.extend(fragments)

    cleaned_skills = [
        s.strip().title() for s in skill_candidates if is_reasonable_skill(s.strip())
    ]
    return sorted(set(cleaned_skills))

class ResumeParser:
    def segment_sections(self):
        """
        Pisahkan teks berdasarkan heading resume seperti Experience, Education, Skills, Projects, dll.
        """
        section_patterns = {
            "experience": r"(?i)(work experience|pengalaman kerja|pengalaman|riwayat pekerjaan|freelance|internship|magang|career history|experiences|riwayat karir)",
            "education": r"(?i)(education|pendidikan|academic background|riwayat pendidikan|educational background|academic history|academic qualifications|educations|qualifications|kualifikasi|academic credentials|academic achievements)",
            "skills": r"(?i)(skills|keterampilan|keahlian|kemampuan|proficiencies|technical skills|soft skills|hard skills|expertise|skill set|capabilities|kualifikasi)",
            "projects": r"(?i)(projects|portfolio|projek|proyek|project experience|project history|project portfolio|project work|project details|capstones|project work|project contributions|project showcases|project highlights|project accomplishments|project achievements|project summaries|project descriptions|project overviews|project outlines|project briefs|project reports|project documentation)",
            "certifications": r"(?i)(certifications|sertifikat|licenses| lisensi|certificates|professional certifications|professional licenses|professional certificates|professional qualifications|professional accreditations|professional credentials)",
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
    
    def __init__(self, file_bytes):
        self.file_bytes = file_bytes
        self.text = self.extract_text()
        self.cleaned_text = self.clean_text(self.text)
        self.ner_results = self.ner_with_indobert()
        self.sections = self.segment_sections()
        self.predefined_skills = self.load_skill_dataset()
        self.details = self.build_details()

    def extract_text(self):
        import io
        with pdfplumber.open(io.BytesIO(self.file_bytes)) as pdf:
            return "\n".join([page.extract_text() or '' for page in pdf.pages])

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()
    
    def ner_with_indobert(self):
        sentences = re.split(r'(?<=[.!?]) +', self.cleaned_text)
        return [ent for sentence in sentences for ent in NER_PIPE(sentence[:512])]

    def load_skill_dataset(self):
        return SKILL_SET

    def extract_name_from_ner(self):
        ner_results = self.ner_results
        names = [ent['word'] for ent in ner_results if ent['entity_group'] == 'PERSON']
        
        clean_names = []
        for name in names:
            name = name.strip().replace('_', ' ')
            if not re.search(r'\d|\@|\.com', name, re.IGNORECASE):
                clean_names.append(name)

        seen = set()
        final_name = []
        for word in clean_names:
            word = word.strip()
            if word.lower() not in seen:
                final_name.append(word)
                seen.add(word.lower())

        if final_name:
            return " ".join(final_name).strip()
        
        # fallback ke baris pertama resume
        first_line = self.text.strip().split('\n')[0]
        if len(first_line.split()) <= 5:
            return first_line.strip()
        return ""

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
        pattern = r'(SMA|SMK|Sarjana|S1|S2|S3|Bachelor|Master|Doctor|Universitas|Institut)[^\n]{0,80}'
        matches = re.findall(pattern, edu_text, re.IGNORECASE)
        return list(set(matches))

    def extract_projects(self):
        project_text = self.sections.get("projects", "")
        lines = project_text.split("\n")
        return [line.strip("-• ") for line in lines if len(line.strip()) > 5]

    def extract_experience(self):
        exp_text = self.sections.get("experience", "")
        lines = exp_text.split('\n')
        experience_list = []
        for line in lines:
            line = line.strip("-•\u2022 \t")
            if len(line) > 5:
                experience_list.append(line)
        return list(set(experience_list))

    def get_total_experience_from_text(self):
        date_ranges = re.findall(
            r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?\s?\d{4})\s*[-\u2013]\s*((?:Present|Now|\d{4}))',
            self.text, re.IGNORECASE)
        total_months = 0
        for start_str, end_str in date_ranges:
            try:
                start = date_parser.parse(start_str, fuzzy=True, default=datetime(2000, 1, 1))
                end = datetime.now() if re.search(r'present|now', end_str.lower()) else date_parser.parse(end_str, fuzzy=True)
                total_months += max(0, (end.year - start.year) * 12 + (end.month - start.month))
            except (ValueError, TypeError, OverflowError) as e:
                print(f"Error parsing date range '{start_str} - {end_str}': {e}")
                continue
        return round(total_months / 12, 2)

    def score_experience_with_ner(self):
        score = 0
        orgs, dates, locations = set(), set(), set()
        numerics = 0

        # Gabungkan word bertokenisasi bertipe subword
        full_text = ""
        previous = ""
        for ent in self.ner_results:
            word = ent["word"]
            if word.startswith("##"):
                previous += word[2:]
            else:
                full_text += " " + previous
                previous = word
        full_text += " " + previous

        # Re-evaluate entities using cleaned text
        for ent in self.ner_results:
            label = ent["entity_group"].upper()
            word = ent["word"].lower()

            if label == "ORG":
                orgs.add(word)
            elif label == "DATE":
                dates.add(word)
            elif label == "LOC":
                locations.add(word)
            elif label in ["MONEY", "PERCENT", "CARDINAL"]:
                numerics += 1

        # Lebih banyak action verbs + variasinya
        verbs = [
            "develop", "manage", "lead", "create", "optimize", "analyze", "design", "build",
            "coordinate", "supervise", "plan", "initiate", "execute", "implement", "improve"
        ]
        verb_count = sum(full_text.lower().count(v) for v in verbs)

        # Tambahkan nilai jika ada lebih dari 2 kalimat di bagian pengalaman
        try:
            exp_sents = sent_tokenize(self.text, language='english')
        except Exception as e:
            print(f"Sent Tokenizer failed: {e}")
            exp_sents = [self.text]  # fallback: treat whole text as one sentence
            
        sentence_bonus = min(len(exp_sents) // 3, 3) * 1.0  # up to +3

        # Skoring final
        score += min(len(orgs), 3) * 3
        score += min(len(dates), 3) * 2
        score += min(len(locations), 2) * 2
        score += min(numerics, 2) * 2
        score += min(verb_count, 5) * 1.5
        score += sentence_bonus

        return round(min(score, 30), 1)

    def build_details(self):
        linkedin, github = self.extract_links()
        raw_skills = self.extract_skills()
        matched_skills = [s for s in raw_skills if s in self.predefined_skills]
        recommended_skills = recommend_skills(matched_skills)
        field_info = recommend_field(matched_skills)
        recommended_courses = recommend_courses(field_info["field"])
        videos = recommend_videos()
        
        # print("=== Field Info ===")
        # print(field_info)

        return {
            "name": self.extract_name_from_ner(),
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "linkedin": linkedin,
            "github": github,
            "skills": matched_skills,
            "education": self.extract_education(),
            "projects": self.extract_projects(),
            "experience_items": self.extract_experience(),
            "recommended_skills": recommended_skills,
            "recommended_field": field_info["field"],
            "matched_field_skills": field_info["matched_skills"],
            "field_match_percent": field_info["match_percent"],
            "recommended_courses": recommended_courses,
            "resume_video_url": videos["resume_video_url"],
            "interview_video_url": videos["interview_video_url"],
            "resume_score": round(60 + 0.5 * len(matched_skills)),
            "experience_score": self.score_experience_with_ner(),
            "total_experience_years": self.get_total_experience_from_text(),
        }

    def get_extracted_data(self):
        return self.details
