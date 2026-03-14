from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict
import logging
import random
import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import html

# ================= LOAD ENV =================
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Skill Assessment API v7")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= SUPABASE =================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("SUPABASE credentials missing")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

LEARNERS_TABLE = "learners"
RESULTS_TABLE = "assessment_results"
QUESTIONS_TABLE = "questions"

# ============ DOMAIN → SKILL MAPPING ============
DOMAIN_SKILLS = {
    "Software Development Engineer": {
        "name": "Software Development Engineer",
        "skill_ids": [1, 2, 3, 4, 5],
        "skills": {
            1: "Data Structures & Algorithms",
            2: "System Design",
            3: "Object-Oriented Programming",
            4: "Problem Solving",
            5: "Version Control"
        }
    },
    "Data Analyst": {
        "name": "Data Analyst",
        "skill_ids": [6, 7, 8, 9, 10],
        "skills": {
            6: "SQL Queries",
            7: "Data Visualization",
            8: "Excel Advanced",
            9: "Statistics & Probability",
            10: "Python for Data Analysis"
        }
    },
    "AI Engineer": {
        "name": "AI Engineer",
        "skill_ids": [11, 12, 13, 14, 15, 16],
        "skills": {
            11: "Python",
            12: "Machine Learning",
            13: "Deep Learning",
            14: "Generative AI / LLMs",
            15: "MLOps",
            16: "Cloud"
        }
    },
    "Backend Developer": {
        "name": "Backend Developer",
        "skill_ids": [17, 18, 19, 20, 21, 22, 23, 16],
        "skills": {
            17: "JavaScript",
            18: "Java Spring Boot",
            19: "REST / GraphQL APIs",
            20: "NoSQL",
            21: "Authentication",
            22: "Docker",
            23: "CI/CD",
            16: "Cloud"
        }
    },
    "Frontend Developer": {
        "name": "Frontend Developer",
        "skill_ids": [24, 25, 26, 27, 28, 29, 30, 5],
        "skills": {
            24: "HTML",
            25: "CSS",
            26: "TypeScript",
            27: "React",
            28: "Angular",
            29: "State Management",
            30: "Responsive Design",
            5: "Version Control"
        }
    },
    "Full Stack Developer": {
        "name": "Full Stack Developer",
        "skill_ids": [17, 18, 19, 20, 21, 22, 23, 16, 24, 25, 26, 27, 28, 29, 30, 5],
        "skills": {
            17: "JavaScript",
            18: "Java Spring Boot",
            19: "REST / GraphQL APIs",
            20: "NoSQL",
            21: "Authentication",
            22: "Docker",
            23: "CI/CD",
            16: "Cloud",
            24: "HTML",
            25: "CSS",
            26: "TypeScript",
            27: "React",
            28: "Angular",
            29: "State Management",
            30: "Responsive Design",
            5: "Version Control"
        }
    }
}

# ================= MODEL =================
class AssessmentSubmission(BaseModel):
    learner_id: str
    time_taken_seconds: int
    answers: Dict[str, str]

# ================= SAFE FETCH =================
def safe_fetch(response):
    if hasattr(response, "data") and response.data:
        return response.data
    return []

# ================= FETCH QUESTIONS =================
def fetch_questions(skill_ids, difficulty, limit):
    response = (
        supabase.table(QUESTIONS_TABLE)
        .select("*")
        .in_("skill_id", skill_ids)
        .eq("difficulty", difficulty)
        .execute()
    )
    data = safe_fetch(response)
    if len(data) > limit:
        data = random.sample(data, limit)
    return data

# ================= START ASSESSMENT =================
@app.get("/assessment/start/{learner_id}")
def start_assessment(learner_id: str):
    learner_resp = (
        supabase.table(LEARNERS_TABLE)
        .select("*")
        .eq("id", learner_id)
        .single()
        .execute()
    )
    learner = learner_resp.data
    if not learner:
        raise HTTPException(404, "Learner not found")

    domain = learner.get("target_job_role") or learner.get("target_role") or learner.get("domain")
    logger.info(f"Learner domain from DB: {domain}")
    logger.info(f"Supported domains in backend: {list(DOMAIN_SKILLS.keys())}")
    if not domain or domain not in DOMAIN_SKILLS:
        raise HTTPException(status_code=400, detail=f"Unsupported domain: {domain}")

    skill_ids = DOMAIN_SKILLS[domain]["skill_ids"]
    easy = fetch_questions(skill_ids,"Easy",6)
    medium = fetch_questions(skill_ids,"Medium",6)
    hard = fetch_questions(skill_ids,"Hard",3)
    questions = easy + medium + hard
    random.shuffle(questions)

    return {
        "learner": {
            "id": learner["id"],
            "name": learner.get("full_name") or learner.get("name"),
            "email": learner.get("email"),
            "target_role": domain
        },
        "domain": domain,
        "domain_name": DOMAIN_SKILLS[domain]["name"],
        "skills_tested": list(DOMAIN_SKILLS[domain]["skills"].values()),
        "total_questions": len(questions),
        "questions": questions,
        "started_at": datetime.utcnow().isoformat()
    }

# ================= SUBMIT ASSESSMENT =================
@app.post("/assess/{domain}")
def submit_assessment(domain: str, submission: AssessmentSubmission):
    learner_id = submission.learner_id
    answers = submission.answers or {}
    time_taken = submission.time_taken_seconds or 0

    # verify learner exists
    learner_resp = (
        supabase.table(LEARNERS_TABLE)
        .select("*")
        .eq("id", learner_id)
        .single()
        .execute()
    )
    learner = learner_resp.data
    if not learner:
        raise HTTPException(404,"Learner not found")

    # compute attempt_number (max previous attempt_number for this learner + 1)
    prev_resp = supabase.table(RESULTS_TABLE).select("attempt_number").eq("learner_id", learner_id).execute()
    prev = safe_fetch(prev_resp)
    max_attempt = 0
    for r in prev:
        try:
            if r and r.get("attempt_number") is not None:
                max_attempt = max(max_attempt, int(r["attempt_number"]))
        except Exception:
            continue
    attempt_number = max_attempt + 1

    # fetch DB questions details for the qids we received
    qids = list(answers.keys())
    question_resp = (
        supabase.table(QUESTIONS_TABLE)
        .select("*")
        .in_("q_id", qids)
        .execute()
    )
    db_questions = safe_fetch(question_resp)
    db_map = {str(q["q_id"]): q for q in db_questions}

    correct = 0
    difficulty_stats = {
        "Easy":{"correct":0,"total":0},
        "Medium":{"correct":0,"total":0},
        "Hard":{"correct":0,"total":0}
    }
    skill_stats = {}
    question_details = []

    for qid, user_ans in answers.items():
        q = db_map.get(str(qid))
        if not q:
            # If we don't have question metadata in DB: store minimal info
            question_details.append({
                "q_id": qid,
                "question_text": None,
                "options": None,
                "your_answer": user_ans,
                "correct_answer": None,
                "is_correct": False,
                "difficulty": None,
                "skill": None
            })
            continue

        correct_ans = q.get("correct_answer")
        is_correct = False
        try:
            if user_ans is not None and correct_ans is not None:
                is_correct = str(user_ans).strip().upper() == str(correct_ans).strip().upper()
        except Exception:
            is_correct = False

        if is_correct:
            correct += 1

        difficulty = q.get("difficulty") or "Medium"
        difficulty_stats.setdefault(difficulty, {"correct":0,"total":0})
        difficulty_stats[difficulty]["total"] += 1
        if is_correct:
            difficulty_stats[difficulty]["correct"] += 1

        skill = q.get("skill_name") or q.get("skill") or "Unknown"
        if skill not in skill_stats:
            skill_stats[skill] = {"correct":0,"total":0}
        skill_stats[skill]["total"] += 1
        if is_correct:
            skill_stats[skill]["correct"] += 1

        # include question_text and options so front-end and PDF can show full review
        question_details.append({
            "q_id": qid,
            "question_text": q.get("question_text"),
            "options": {
                "A": q.get("option_a"),
                "B": q.get("option_b"),
                "C": q.get("option_c"),
                "D": q.get("option_d")
            },
            "your_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "difficulty": difficulty,
            "skill": skill
        })

    total_answered = len(answers) if answers else 0
    percentage = round((correct/total_answered)*100,2) if total_answered>0 else 0.0

    skill_report = []
    skill_gaps = []
    for skill_name, data in skill_stats.items():
        perc = round((data["correct"]/data["total"])*100,2) if data["total"]>0 else 0.0
        skill_report.append({"skill": skill_name, "percentage": perc})
        if perc < 60:
            skill_gaps.append(skill_name)

    # Insert record into DB (include attempt_number)
    insert_payload = {
        "learner_id": learner_id,
        "domain": domain,
        "target_role": domain,
        "attempt_number": attempt_number,
        "started_at": datetime.utcnow().isoformat(),
        "submitted_at": datetime.utcnow().isoformat(),
        "time_taken_seconds": time_taken,
        "total_questions": total_answered,
        "correct_answers": correct,
        "overall_percentage": percentage,
        "difficulty_breakdown": difficulty_stats,
        "skill_report": skill_report,
        "skill_gaps": skill_gaps,
        "question_details": question_details,
        "raw_answers": answers
    }

    insert = supabase.table(RESULTS_TABLE).insert(insert_payload).execute()
    inserted = safe_fetch(insert)
    if not inserted:
        raise HTTPException(500, "Failed to save assessment result")

    assessment_id = inserted[0].get("id") or inserted[0].get("ID") or None

    return {
        "assessment_id": assessment_id,
        "attempt_number": attempt_number,
        "overall_percentage": percentage,
        "correct": correct,
        "total": total_answered,
        "time_taken_seconds": time_taken,
        "learner": {
            "name": learner.get("full_name") or learner.get("name"),
            "email": learner.get("email"),
            "target_role": domain
        },
        "difficulty_breakdown": difficulty_stats,
        "skill_report": skill_report,
        "skill_gaps": skill_gaps,
        "question_details": question_details
    }

# ================= PDF REPORT =================
@app.get("/assessment/{assessment_id}/report.pdf")
def generate_pdf(assessment_id: str):
    resp = supabase.table(RESULTS_TABLE).select("*").eq("id", assessment_id).single().execute()
    data = resp.data
    # Fetch learner details from learners table
    learner_resp = (
        supabase.table(LEARNERS_TABLE)
        .select("full_name, email")
        .eq("id", data["learner_id"])
        .single()
        .execute()
    )
    learner = learner_resp.data if learner_resp.data else {}
    learner_name = learner.get("full_name", "—")
    learner_email = learner.get("email", "—")
    if not data:
        raise HTTPException(404, "Assessment not found")

    filename = f"/tmp/assessment_{assessment_id}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    header_style = ParagraphStyle("Header", parent=styles["Heading1"], alignment=1, spaceAfter=12)
    normal = styles["Normal"]
    elements = []

    # Header
    elements.append(Paragraph("Assessment Report", header_style))
    elements.append(Spacer(1, 8))

    # Score block
    score_par = f"Score: {data.get('correct_answers','—')} / {data.get('total_questions','—')}"
    perc_par = f"Percentage: {data.get('overall_percentage','—')}%"
    time_par = f"Time Taken: {data.get('time_taken_seconds','—')} seconds"
    attempt_par = f"Attempt: {data.get('attempt_number', '—')}"
    elements.append(Paragraph(score_par, normal))
    elements.append(Paragraph(perc_par, normal))
    elements.append(Paragraph(time_par, normal))
    elements.append(Paragraph(attempt_par, normal))
    elements.append(Spacer(1, 12))

    # Learner info
    elements.append(Paragraph(f"Learner ID: {data['learner_id']}", styles["Normal"]))
    elements.append(Paragraph(f"Name: {learner_name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {learner_email}", styles["Normal"]))
    elements.append(Paragraph(f"Domain: {data['domain']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # Difficulty breakdown table
    elements.append(Paragraph("Performance by Difficulty", styles["Heading2"]))
    diff = data.get("difficulty_breakdown", {})
    rows = [["Level", "Correct", "Total", "Percentage"]]
    for lvl in ["Easy", "Medium", "Hard"]:
        d = diff.get(lvl, {"correct":0,"total":0})
        total = d.get("total", 0)
        correct_count = d.get("correct", 0)
        percent = f"{round((correct_count/total)*100,2)}%" if total>0 else "—"
        rows.append([lvl, str(correct_count), str(total), percent])
    tbl = Table(rows, hAlign="LEFT", colWidths=[120,80,80,100])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    elements.append(tbl)
    elements.append(Spacer(1, 12))

    # Skill gap table (use skill_report, required threshold 60%)
    elements.append(Paragraph("Skill Gap Analysis (required threshold: 60%)", styles["Heading2"]))
    rows = [["Skill", "Current (%)", "Required", "Gap", "Status"]]
    skill_report = data.get("skill_report") or []
    for s in skill_report:
        skill = s.get("skill") or s.get("name") or "Unknown"
        cur = s.get("percentage", 0)
        required = 60
        gap = max(0, required - cur)
        status = "PASS" if cur >= required else "NEEDS IMPROVEMENT"
        rows.append([skill, f"{cur}%", str(required)+"%", f"{gap}%", status])
    sktbl = Table(rows, hAlign="LEFT", colWidths=[180,80,80,80,120])
    sktbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f0f0")),
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("LEFTPADDING",(0,0),(-1,-1),6),
        ("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    elements.append(sktbl)
    elements.append(Spacer(1, 12))

    # Answer review
    elements.append(Paragraph("Answer Review", styles["Heading2"]))
    qlist = data.get("question_details") or []
    for q in qlist:
        qid = q.get("q_id")
        qtext = q.get("question_text") or "Question text not available"
        safe_qtext = html.escape(str(qtext))
        elements.append(Paragraph(f"QID {qid} | Q: {safe_qtext}", styles["Normal"]))
        # options
        options = q.get("options") or {}
        for label in ["A", "B", "C", "D"]:
            txt = options.get(label) or ""
            marker = ""
            # mark your answer / correct answer in-line
            if q.get("your_answer") and str(q.get("your_answer")).strip().upper() == label:
                marker += " (Your answer)"
            if q.get("correct_answer") and str(q.get("correct_answer")).strip().upper() == label:
                marker += " (Correct)"
            safe_txt = html.escape(str(txt))
            elements.append(Paragraph(f"{label}. {safe_txt}{marker}", normal))
        # summary line
        elements.append(Paragraph(f"Your Answer: {q.get('your_answer')} | Correct Answer: {q.get('correct_answer')}", normal))
        elements.append(Spacer(1,8))

    doc.build(elements)
    file_path = f"{assessment_id}.pdf"
    
    # Upload to Supabase Storage
    with open(filename, "rb") as f:
        supabase.storage.from_("reports").upload(
        file_path,
        f,
        {"content-type": "application/pdf", "x-upsert": "true"}
    )
        
    # Get public URL
    public_url = supabase.storage.from_("reports").get_public_url(file_path)
    
    # Save URL into database
    supabase.table(RESULTS_TABLE).update({
        "pdf_url": public_url
}).eq("id", assessment_id).execute()
    
    # Return file to browser
    return FileResponse(filename, media_type="application/pdf", filename=filename)


# ================= START SERVER =================
if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting Skill Assessment Server v3 - Learner Aware")
    logger.info(f"📚 Domains: {list(DOMAIN_SKILLS.keys())}")
    logger.info(f"🗄️ Database: Supabase")
    logger.info(f"📝 Per assessment: 15 MCQs (6E + 6M + 3H)")
    logger.info(f"👤 Learner-aware: YES")
    logger.info(f"💾 Saves to: {RESULTS_TABLE}")
    logger.info(f"📊 Data flows to: AI Learning Path Generator module")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)

