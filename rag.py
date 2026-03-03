import requests
import json
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def explain_learning_path(learner, phases):

    prompt = f"""
You are an expert AI career mentor aligned with NSQF standards.

Based on the learner profile and the structured 3-phase roadmap below,
explain each phase separately.

Return STRICTLY in this JSON format:

{{
  "explanation_basics": "...",
  "explanation_intermediate": "...",
  "explanation_advanced": "...",
  "explanation_outcomes": "..."
}}

DO NOT add markdown.
DO NOT add extra text.
ONLY return valid JSON.

Learner Profile:
- Target Job Role: {learner.get('target_job_role')}
- Education Level: {learner.get('education_level')}
- Weekly Study Hours: {learner.get('hours_per_week')}
- Timeline: {learner.get('timeline_months')} months
- Current Skills: {learner.get('current_skills')}
- Learning Style: {learner.get('learning_style')}

Learning Path:
{json.dumps(phases, indent=2)}
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
                ],
                "temperature": 0.3
            },
            timeout=30
        )

        response.raise_for_status()

        result = response.json()
        ai_content = result["choices"][0]["message"]["content"]

        # 🔥 Safe JSON parsing
        try:
            parsed = json.loads(ai_content)
        except Exception:
            print("⚠️ AI returned invalid JSON")
            parsed = {
                "explanation_basics": "Explanation unavailable.",
                "explanation_intermediate": "",
                "explanation_advanced": "",
                "explanation_outcomes": ""
            }

        return parsed

    except Exception as e:
        print("🚨 Groq API Error:", str(e))
        return {
            "explanation_basics": "Explanation unavailable.",
            "explanation_intermediate": "",
            "explanation_advanced": "",
            "explanation_outcomes": ""
        }
