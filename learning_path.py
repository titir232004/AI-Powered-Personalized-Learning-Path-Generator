from learners import fetch_learner
from assessment import fetch_latest_assessment
from rag import explain_learning_path


async def generate_learning_path(learner: dict):

    if not learner:
        raise ValueError("Learner not found")

    learner_id = learner["id"]
    current_skills = learner.get("current_skills", [])
    hours_per_week = learner.get("hours_per_week") or 10  # fallback
    timeline_months = learner.get("timeline_months") or 1  # fallback
    target_role = learner.get("target_job_role")

    # Fetch latest assessment
    assessment = fetch_latest_assessment(learner_id)
    if not assessment:
        raise ValueError("No assessment found")

    skill_gaps = assessment.get("skill_gaps", [])
    overall_percentage = float(assessment.get("overall_percentage") or 0)
    skill_report = assessment.get("skill_report", [])

    missing_skills = list(set(skill_gaps) - set(current_skills))
    skill_scores = {item["skill"]: float(item.get("percentage") or 0) for item in skill_report}

    foundation, intermediate, advanced = [], [], []
    for skill in missing_skills:
        score = skill_scores.get(skill, 0)
        if score < 40:
            foundation.append(skill)
        elif 40 <= score < 70:
            intermediate.append(skill)
        else:
            advanced.append(skill)

    # 3-phase roadmap
    phases = [
        {"phase": "Basics", "skills": foundation, "duration_weeks": max(2, len(foundation)*2)},
        {"phase": "Intermediate", "skills": intermediate, "duration_weeks": max(3, len(intermediate)*3)},
        {"phase": "Advanced", "skills": advanced, "duration_weeks": max(4, len(advanced)*4)}
    ]

    # Duration & success
    total_weeks = sum(p["duration_weeks"] for p in phases)
    adjusted_weeks = max(total_weeks, timeline_months*4)
    base_score = overall_percentage / 100
    effort_factor = min(hours_per_week / 40, 1)
    success_probability = round(min(0.95, 0.45 + base_score*0.35 + effort_factor*0.2), 2)

    # AI explanation
    explanations = explain_learning_path(learner, phases)
    # Ensure all keys exist and are dicts
    for key in ["explanation_basics", "explanation_intermediate", "explanation_advanced", "explanation_outcomes"]:
        if key not in explanations or explanations[key] is None:
            explanations[key] = {"text": f"{key} unavailable."}
        elif isinstance(explanations[key], str):
            explanations[key] = {"text": explanations[key]}

    return {
        "learner_id": learner_id,
        "learner_name": learner.get("full_name"),
        "phases": phases,
        "estimated_duration_weeks": adjusted_weeks,
        "success_probability": success_probability,
        **explanations
    }
