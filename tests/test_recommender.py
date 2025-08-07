import pytest
from unittest.mock import patch
from recommender import recommend_field, recommend_skills, recommend_courses, recommend_videos

mock_skills = {
    "Data Science": {"python", "pandas", "numpy"},
    "Web Development": {"html", "css", "javascript"},
}

mock_courses = {
    "Data Science": ["DS Course 1", "DS Course 2"],
    "Web Development": ["Web Course 1"]
}

mock_resume_videos = ["https://yt.com/resume1", "https://yt.com/resume2"]
mock_interview_videos = ["https://yt.com/interview1", "https://yt.com/interview2"]

@patch("recommender.ds_skills", mock_skills["Data Science"])
@patch("recommender.web_skills", mock_skills["Web Development"])
@patch("recommender.cloud_skills", set())
@patch("recommender.android_skills", set())
@patch("recommender.ios_skills", set())
@patch("recommender.uiux_skills", set())
@patch("recommender.iot_skills", set())
@patch("recommender.ml_skills", set())
@patch("recommender.cs_skills", set())
def test_recommend_field_with_ds_skills():
    skills = ["Python", "Pandas"]
    result = recommend_field(skills)
    assert result["field"] == "Data Science"
    assert set(result["matched_skills"]) == {"python", "pandas"}
    assert result["match_percent"] > 0

@patch("recommender.ds_skills", {"python", "pandas", "numpy"})
@patch("recommender.web_skills", {"html", "css", "javascript"})
@patch("recommender.cloud_skills", set())
@patch("recommender.android_skills", set())
@patch("recommender.ios_skills", set())
@patch("recommender.uiux_skills", set())
@patch("recommender.iot_skills", set())
@patch("recommender.ml_skills", set())
@patch("recommender.cs_skills", set())
def test_recommend_skills_filter_and_limit():
    detected = ["Python"]
    result = recommend_skills(detected, top_n=2)
    assert "Python" not in [s.lower() for s in result]
    assert len(result) <= 2

def test_recommend_field_empty_input():
    result = recommend_field([])
    assert result["field"] is None
    assert result["match_percent"] == 0

@patch("recommender.ds_course", ["DS Course A", "DS Course B"])
@patch("recommender.web_course", ["Web Course A"])
@patch("recommender.android_course", [])
@patch("recommender.ios_course", [])
@patch("recommender.uiux_course", [])
def test_recommend_courses():
    ds_result = recommend_courses("Data Science")
    web_result = recommend_courses("Web Development")
    unknown_result = recommend_courses("Unknown Field")

    assert ds_result == ["DS Course A", "DS Course B"]
    assert web_result == ["Web Course A"]
    assert unknown_result == []

@patch("recommender.resume_videos", ["https://resume1.com"])
@patch("recommender.interview_videos", ["https://interview1.com", "https://interview2.com"])
def test_recommend_videos():
    videos = recommend_videos()
    assert videos["resume_video_url"] in ["https://resume1.com"]
    assert videos["interview_video_url"] in ["https://interview1.com", "https://interview2.com"]
    assert videos["resume_video_url"] != videos["interview_video_url"] or len(set(videos.values())) == 1