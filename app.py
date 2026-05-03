from flask import Flask, render_template, request
import PyPDF2
import spacy
import os

app = Flask(__name__)

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Skill database
SKILLS_DB = [
    "python","java","sql","html","css","javascript",
    "machine learning","data analysis","communication","teamwork","excel"
]

# Job roles
JOB_ROLES = {
    "Data Analyst": ["python","sql","data analysis","excel"],
    "Web Developer": ["html","css","javascript"],
    "ML Engineer": ["python","machine learning"]
}

# -------------------------------
# Extract text from PDF
# -------------------------------
def extract_text(file):
    text = ""
    try:
        pdf = PyPDF2.PdfReader(file)
        for page in pdf.pages:
            content = page.extract_text()
            if content:
                text += content
    except:
        return ""
    return text.lower()


# -------------------------------
# Extract Name (improved)
# -------------------------------
def extract_name(text):
    doc = nlp(text)

    # Try NLP first
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text) > 2:
            return ent.text.title()

    # fallback → first line
    lines = text.split("\n")
    for line in lines[:5]:
        line = line.strip()
        if len(line.split()) <= 3 and line.isalpha():
            return line.title()

    return "Not Found"


# -------------------------------
# Extract Skills
# -------------------------------
def extract_skills(text):
    found = []
    for skill in SKILLS_DB:
        if f" {skill} " in f" {text} ":
            found.append(skill)
    return list(set(found))


# -------------------------------
# Recommend Jobs
# -------------------------------
def recommend_jobs(skills):
    results = {}

    for role, req in JOB_ROLES.items():
        match = len([s for s in req if s in skills])
        score = (match / len(req)) * 100 if req else 0
        results[role] = round(score, 2)

    return sorted(results.items(), key=lambda x: x[1], reverse=True)


# -------------------------------
# Generate Feedback
# -------------------------------
def generate_feedback(score, missing):
    if score >= 80:
        return "🔥 Excellent profile. You are highly job-ready."
    elif score >= 50:
        return "⚡ Good profile. Improve these skills: " + ", ".join(missing)
    else:
        return "⚠️ Needs improvement. Focus on: " + ", ".join(missing)


# -------------------------------
# Main Route
# -------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    data = None

    if request.method == "POST":
        file = request.files.get("resume")

        if file and file.filename.endswith(".pdf"):
            text = extract_text(file)

            name = extract_name(text)
            skills = extract_skills(text)

            jobs = recommend_jobs(skills)
            best_role = jobs[0][0]
            score = jobs[0][1]

            missing = [s for s in JOB_ROLES[best_role] if s not in skills]

            feedback = generate_feedback(score, missing)

            data = {
                "name": name,
                "skills": skills,
                "jobs": jobs,
                "score": score,
                "missing": missing,
                "feedback": feedback
            }

    return render_template("index.html", data=data)


# -------------------------------
# Run (Render + Local compatible)
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))