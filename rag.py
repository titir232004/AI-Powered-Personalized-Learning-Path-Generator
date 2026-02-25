import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"


def explain_learning_path(learner, phases):
    prompt = f"""
You are an expert AI career mentor aligned with NSQF standards.

Learner Profile:
- Target Job Role: {learner.get('target_job_role')}
- Education Level: {learner.get('education_level')}
- Weekly Study Hours: {learner.get('hours_per_week')}
- Timeline: {learner.get('timeline_months')} months
- Current Skills: {learner.get('current_skills')}

Learning Path Structure:
{json.dumps(phases, indent=2)}

Explain clearly:

1. Why each phase is necessary
2. What practical skills the learner will gain
3. How this roadmap improves job readiness
4. Expected real-world outcomes

Keep the response structured, concise, and motivating.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            return "AI explanation could not be generated."

        return data["response"].strip()

    except requests.exceptions.Timeout:
        return "AI explanation timed out. Please try again."

    except requests.exceptions.ConnectionError:
        return "Ollama server is not running."

    except Exception as e:
        return f"AI generation error: {str(e)}"