import random
import time
from skills import (
    ds_skills, web_skills, android_skills, ios_skills, uiux_skills,
    cloud_skills, iot_skills, ml_skills, cs_skills
)
from courses import (
    ds_course, web_course, android_course, ios_course, uiux_course,
)
from videos import resume_videos, interview_videos


# === FUNGSI ===
def recommend_field(skills):
    if not skills:
        return {
            "field": None,
            "matched_skills": [],
            "match_percent": 0
        }

    skill_set = set(skill.lower() for skill in skills)

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

    for field, keywords in field_map.items():
        matched = skill_set & keywords
        scores[field] = len(matched)
        matched_skills_map[field] = list(matched)

    best_field = max(scores, key=scores.get)

    if scores[best_field] == 0:
        return {
            "field": None,
            "matched_skills": [],
            "match_percent": 0
        }

    max_score = scores[best_field]
    total_keywords = len(field_map[best_field])
    match_percent = round((max_score / total_keywords) * 100, 1) if total_keywords else 0

    return {
        "field": best_field,
        "matched_skills": matched_skills_map[best_field],
        "match_percent": match_percent,
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