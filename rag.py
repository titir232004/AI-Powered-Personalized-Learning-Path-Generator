import requests
import json
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def explain_learning_path(learner, phases):

    prompt = f"""
You are an expert AI career mentor aligned with NSQF standards.

The learning roadmap ALWAYS has 3 phases:
1. Basics
2. Intermediate
3. Advanced

Learner Profile:
- Target Job Role: {learner.get('target_job_role')}
- Education Level: {learner.get('education_level')}
- Weekly Study Hours: {learner.get('hours_per_week')}
- Timeline: {learner.get('timeline_months')} months
- Current Skills: {learner.get('current_skills')}
- Learning Style: {learner.get('learning_style')}

Learning Path Structure:
{json.dumps(phases, indent=2)}

Explain clearly and separately:

1. Why the Basics phase is important
2. Why the Intermediate phase builds career readiness
3. Why the Advanced phase ensures job-level competency
4. What practical outcomes the learner can expect

Tailor your explanation to the learner's learning style.
Keep the explanation structured, concise, and motivating.
"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        print("STATUS:", response.status_code)

        response.raise_for_status()

        result = response.json()

        explanation = result["choices"][0]["message"]["content"]

        return explanation

    except Exception as e:
        print("🚨 Groq API Error:", str(e))
        return "AI explanation temporarily unavailable."
