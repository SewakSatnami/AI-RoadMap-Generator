from flask import Flask, render_template, request, redirect, session, jsonify, send_file
from pymongo import MongoClient
from flask_wtf import CSRFProtect
from groq import Groq
import os
import urllib.parse

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from io import BytesIO

# ---------------- GROQ SETUP ---------------- #
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY environment variable is required")

groq_client = Groq(api_key=groq_api_key)

# ---------------- FLASK ---------------- #
app = Flask(__name__)
app.secret_key = "samir_secret_123"

csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False

# ---------------- DATABASE ---------------- #
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["ai_roadmap"]
users_collection = db["users"]
roadmap_collection = db["roadmaps"]

# ---------------- HOME ---------------- #
@app.route("/")
def home():
    return redirect("/login")

# ---------------- LOGIN ---------------- #
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = users_collection.find_one({"username": username})

        if user and user["password"] == password:
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid username or password"

    return render_template("login.html")

# ---------------- SIGNUP ---------------- #
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return "Passwords do not match"

        if users_collection.find_one({"username": username}):
            return "User already exists"

        users_collection.insert_one({
            "username": username,
            "password": password
        })

        return redirect("/login")

    return render_template("signup.html")

# ---------------- DASHBOARD ---------------- #
@app.route("/dashboard")
def dashboard():
    if "user" in session:
        return render_template("dashboard.html")
    return redirect("/login")

# ---------------- GENERATE ROADMAP ---------------- #
@app.route('/generate', methods=['POST'])
def generate():

    topic = request.form.get("topic")
    level = request.form.get("level")
    weeks = request.form.get("weeks")

    prompt = f"""
    Create EXACTLY {weeks} weeks roadmap for {topic} at {level} level.

    RULES:
    - ONLY {weeks} weeks
    - Each week must have 3-5 short topics
    - NO explanation

    FORMAT:

    Week 1:
    - Topic
    - Topic
    """

    response = groq_client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    roadmap_content = response.choices[0].message.content.strip()

    # LIMIT WEEKS
    weeks_limit = int(weeks)
    split_weeks = roadmap_content.split("Week")[1:]
    split_weeks = split_weeks[:weeks_limit]

    new_roadmap = ""
    for i, w in enumerate(split_weeks, start=1):
        new_roadmap += f"Week {i}:\n{w.strip()}\n\n"

    return render_template(
        "roadmap.html",
        roadmap=new_roadmap,
        topic=topic,
        level=level,
        weeks=weeks
    )

# ---------------- DOWNLOAD PDF ---------------- #
@app.route("/download-pdf")
def download_pdf():
    roadmap = urllib.parse.unquote(request.args.get("roadmap", ""))
    topic = request.args.get("topic")
    level = request.args.get("level")
    weeks = request.args.get("weeks")

    if not roadmap:
        return "No roadmap data found"

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # CUSTOM STYLES
    title_style = ParagraphStyle(
        'title',
        parent=styles['Title'],
        textColor=colors.HexColor("#0ea5e9")
    )

    week_style = ParagraphStyle(
        'week',
        parent=styles['Heading3'],
        textColor=colors.HexColor("#2563eb")
    )

    elements = []

    # TITLE
    elements.append(Paragraph("Your AI Learning Roadmap", title_style))
    elements.append(Spacer(1, 10))

    # SUBTITLE
    elements.append(Paragraph(f"{topic} Roadmap ({level} • {weeks} Weeks)", styles['Heading2']))
    elements.append(Spacer(1, 20))

    # CONTENT
    weeks_list = roadmap.split("Week")[1:]

    for i, week in enumerate(weeks_list, start=1):
        elements.append(Paragraph(f"Week {i}", week_style))
        elements.append(Spacer(1, 8))

        items = []
        for line in week.split("\n"):
            if "-" in line:
                text = line.replace("-", "").strip()
                items.append(Paragraph(f"• {text}", styles['Normal']))

        elements.append(ListFlowable(items))
        elements.append(Spacer(1, 15))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="AI_Roadmap.pdf",
        mimetype='application/pdf'
    )

# ---------------- LOGOUT ---------------- #
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)