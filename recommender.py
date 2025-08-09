import random
import time
import difflib
from skills import (
    ds_skills, web_skills, android_skills, ios_skills, uiux_skills,
    cloud_skills, iot_skills, ml_skills, cs_skills
)
from courses import (
    ds_course, web_course, android_course, ios_course, uiux_course,
)
from videos import resume_videos, interview_videos

# === FUNGSI ===
def recommend_field(skills, experiences=None, top_n=3):
    """
    Rekomendasi bidang pekerjaan berdasarkan skill dan pengalaman kandidat.
    skills: list keterampilan kandidat
    experiences: list pengalaman kerja/proyek kandidat
    """
    if not skills and not experiences:
        return {
            "field": None,
            "matched_skills": [],
            "matched_experiences": [],
            "match_percent": 0,
            "alternative_fields": []
        }

    skill_set = set(skill.lower().strip() for skill in (skills or []) if skill.strip())
    exp_set = set(exp.lower().strip() for exp in (experiences or []) if exp.strip())

    # Daftar bidang pekerjaan & skill kata kuncinya
    field_map = {
        "Data Science": ds_skills,
        "Web Development": web_skills,
        "Android Development": android_skills,
        "iOS Development": ios_skills,
        "UI/UX": uiux_skills,
        "Cloud Computing": cloud_skills,
        "Internet of Things": iot_skills,
        "Machine Learning": ml_skills,
        "Cyber Security": cs_skills,
    }

    scores = {}
    matched_skills_map = {}
    matched_exps_map = {}

    for field, keywords in field_map.items():
        normalized_keywords = set(k.lower().strip() for k in keywords)

        # Pencocokan skill
        matched_skills = set()
        for skill in skill_set:
            match = difflib.get_close_matches(skill, normalized_keywords, n=1, cutoff=0.85)
            if match:
                matched_skills.add(match[0])

        # Pencocokan pengalaman (menggunakan kata kunci skill juga)
        matched_exps = set()
        for exp in exp_set:
            for kw in normalized_keywords:
                if kw in exp:
                    matched_exps.add(kw)

        # Bobot skor: 70% skill, 30% pengalaman
        skill_score = len(matched_skills)
        exp_score = len(matched_exps)
        final_score = (skill_score * 0.7) + (exp_score * 0.3)

        scores[field] = final_score
        matched_skills_map[field] = list(matched_skills)
        matched_exps_map[field] = list(matched_exps)

    # Urutkan hasil
    sorted_fields = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_field, best_score = sorted_fields[0]

    if best_score == 0:
        return {
            "field": None,
            "matched_skills": [],
            "matched_experiences": [],
            "match_percent": 0,
            "alternative_fields": []
        }

    total_keywords = len(field_map[best_field])
    match_percent = round((best_score / total_keywords) * 100, 1) if total_keywords else 0

    # Alternatif bidang
    alternative_fields = []
    for field, score in sorted_fields[1:top_n]:
        if score > 0:
            percent = round((score / len(field_map[field])) * 100, 1)
            alternative_fields.append({
                "field": field,
                "matched_skills": matched_skills_map[field],
                "matched_experiences": matched_exps_map[field],
                "match_percent": percent
            })

    return {
        "field": best_field,
        "matched_skills": matched_skills_map[best_field],
        "matched_experiences": matched_exps_map[best_field],
        "match_percent": match_percent,
        "alternative_fields": alternative_fields
    }

def recommend_skills(detected_skills, top_n=10):
    """
    Memberikan rekomendasi skill berdasarkan bidang dominan dari recommend_field,
    menghindari skill yang sudah terdeteksi, dan mengacak urutan skill yang direkomendasikan.
    """
    field_result = recommend_field(detected_skills)
    field_name = field_result['field']

    if not field_name:
        return []

    field_skills = {
        "Data Science": ds_skills,
        "Web Development": web_skills,
        "Android Development": android_skills,
        "iOS Development": ios_skills,
        "UI/UX": uiux_skills,
        "Cloud Computing": cloud_skills,
        "Internet of Things": iot_skills,
        "Machine Learning": ml_skills,
        "Cyber Security": cs_skills,
    }

    predefined_skills = set(skill.lower() for skill in field_skills[field_name])
    matched = set(skill.lower() for skill in detected_skills)

    remaining = list(predefined_skills - matched)

    # Acak hasil dan batasi jumlahnya
    random.shuffle(remaining)
    return [skill.title() for skill in remaining[:top_n]]

def recommend_courses(field):
    return {
        "Data Science": ds_course,
        "Web Development": web_course,
        "Android Development": android_course,
        "iOS Development": ios_course,
        "UI/UX": uiux_course,
    }.get(field, [])

def recommend_videos():
    random.seed(time.time_ns())
    resume_video = random.choice(resume_videos)
    interview_video = random.choice([v for v in interview_videos if v != resume_video]) or resume_video
    return {
        "resume_video_url": resume_video,
        "interview_video_url": interview_video
    }