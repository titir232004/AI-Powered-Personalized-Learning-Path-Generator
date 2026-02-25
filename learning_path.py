from learners import fetch_learner
from assessment import fetch_latest_assessment
from rag import explain_learning_path


def generate_learning_path(user_id: str):

    # -------------------------------
    # 1. Fetch Learner Data
    # -------------------------------
    learner = fetch_learner(user_id)

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
    # 4. Phase Structuring Logic
    # -------------------------------
    foundation = []
    intermediate = []
    advanced = []

    for skill in missing_skills:
        if difficulty.get("easy", 0) < 60:
            foundation.append(skill)
        elif difficulty.get("medium", 0) < 60:
            intermediate.append(skill)
        else:
            advanced.append(skill)

    phases = []

    if foundation:
        phases.append({
            "phase": "Foundation Phase",
            "skills": foundation,
            "duration_weeks": len(foundation) * 2
        })

    if intermediate:
        phases.append({
            "phase": "Intermediate Phase",
            "skills": intermediate,
            "duration_weeks": len(intermediate) * 3
        })

    if advanced:
        phases.append({
            "phase": "Advanced Phase",
            "skills": advanced,
            "duration_weeks": len(advanced) * 4
        })

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

    explanation = explain_learning_path(context_prompt)

    # -------------------------------
    # 8. Final Output
    # -------------------------------
    return {
        "learner_id": learner_id,
        "phases": phases,
        "estimated_duration_weeks": adjusted_weeks,
        "success_probability": success_probability,
        "explanation": explanation
    }