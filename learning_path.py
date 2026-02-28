from learners import fetch_learner
from assessment import fetch_latest_assessment
from rag import explain_learning_path


async def generate_learning_path(learner: str):

    # -------------------------------
    # 1. Fetch Learner Data
    # -------------------------------

    if not learner:
        raise ValueError("Learner not found")

    learner_id = learner["id"]
    current_skills = learner.get("current_skills", [])
    hours_per_week = learner["hours_per_week"]
    timeline_months = learner["timeline_months"]
    target_role = learner["target_job_role"]

    # -------------------------------
    # 2. Fetch Latest Assessment
    # -------------------------------
    assessment = fetch_latest_assessment(learner_id)

    if not assessment:
        raise ValueError("No assessment found")

    skill_gaps = assessment.get("skill_gaps", [])
    difficulty = assessment.get("difficulty_breakdown", {})
    overall_percentage = float(assessment.get("overall_percentage", 0))

    # -------------------------------
    # 3. Identify Final Skill Gaps
    # -------------------------------
    missing_skills = list(set(skill_gaps) - set(current_skills))

    # -------------------------------
    # 4. Phase Structuring Logic (STRICT 3 PHASES)
    # -------------------------------

    foundation = []
    intermediate = []
    advanced = []

    skill_report = assessment.get("skill_report", [])

    # Convert report to dict for fast lookup
    skill_scores = {
        item["skill"]: float(item["percentage"])
        for item in skill_report
    }

    for skill in missing_skills:

        score = skill_scores.get(skill, 0)

        if score < 40:
            foundation.append(skill)

        elif 40 <= score < 70:
            intermediate.append(skill)

        else:
            advanced.append(skill)

    # Ensure 3 phases always exist
    phases = [
        {
            "phase": "Basics",
            "skills": foundation,
            "duration_weeks": max(2, len(foundation) * 2)
        },
        {
            "phase": "Intermediate",
            "skills": intermediate,
            "duration_weeks": max(3, len(intermediate) * 3)
        },
        {
            "phase": "Advanced",
            "skills": advanced,
            "duration_weeks": max(4, len(advanced) * 4)
        }
    ]

    # -------------------------------
    # 5. Duration Calculation
    # -------------------------------
    total_weeks = sum(p["duration_weeks"] for p in phases)

    # Adjust by weekly learning hours
    adjusted_weeks = max(
        total_weeks,
        timeline_months * 4
    )

    # -------------------------------
    # 6. Success Probability
    # -------------------------------
    base_score = overall_percentage / 100
    effort_factor = min(hours_per_week / 40, 1)

    success_probability = round(
        min(0.95, base_score * 0.6 + effort_factor * 0.4),
        2
    )

    # -------------------------------
    # 7. AI Explanation (Ollama)
    # -------------------------------
    context_prompt = f"""
    Learner Target Role: {target_role}
    Current Skills: {current_skills}
    Identified Skill Gaps: {missing_skills}
    Overall Assessment Score: {overall_percentage}
    Weekly Study Hours: {hours_per_week}

    Explain why this learning path is suitable and how it improves job readiness.
    """

    # -------------------------------
    # 7. AI Explanation (Ollama)
    # -------------------------------

    explanation = explain_learning_path(learner, phases)

    # -------------------------------
    # 8. Final Output
    # -------------------------------
    return {
        "learner_id": learner_id,
        "learner_name": learner.get("full_name"),
        "phases": phases,
        "estimated_duration_weeks": adjusted_weeks,
        "success_probability": success_probability,
        "explanation": explanation
    }