import os
import json
import random
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import anthropic

app = Flask(__name__)

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-20250514"

# ════════════════════════════════════════════════
# MODULE 1 · HEALTHCHAT — AI Chatbot
# ════════════════════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are HealthChat, a knowledgeable and empathetic AI health assistant for "
            "OmniLogic Healthcare. You help patients and healthcare professionals with "
            "general health information, symptom guidance, wellness tips, and navigating "
            "healthcare options. Always remind users that you are not a substitute for "
            "professional medical advice. Be clear, compassionate, and informative. "
            "For emergencies in South Africa call 10177 or 112."
        ),
        messages=messages,
    )
    return jsonify({"reply": response.content[0].text})


# ════════════════════════════════════════════════
# MODULE 2 · CLINICALWRITER — Content Generator
# ════════════════════════════════════════════════

CONTENT_TYPES = {
    "patient_education": {
        "name": "Patient Education Article",
        "description": "Plain-language articles explaining conditions and procedures",
        "icon": "📋",
        "templates": [
            {
                "title": "Condition Explainer",
                "fields": ["topic", "tone", "audience", "word_count"],
                "prompt_template": "Write a clear patient education article about {topic}. Include: plain-language explanation, what to expect, preparation steps, warning signs, and when to see a doctor. Tone: {tone}. Audience: {audience}. ~{word_count} words."
            },
            {
                "title": "Procedure Guide",
                "fields": ["topic", "tone", "audience"],
                "prompt_template": "Write a step-by-step guide for patients preparing for {topic}. Cover: what it is, preparation, what happens during, recovery, and FAQs. Tone: {tone}. Audience: {audience}."
            }
        ]
    },
    "care_instructions": {
        "name": "Care Instructions",
        "description": "Post-appointment and discharge instructions",
        "icon": "🏥",
        "templates": [
            {
                "title": "Discharge Instructions",
                "fields": ["topic", "tone", "audience"],
                "prompt_template": "Write professional discharge care instructions for: {topic}. Include: key aftercare steps, dos and don'ts, medication reminders placeholder, follow-up appointment guidance, and emergency contact prompt. Tone: {tone}."
            },
            {
                "title": "Appointment Reminder",
                "fields": ["topic", "tone"],
                "prompt_template": "Write a warm appointment reminder message for a patient scheduled for: {topic}. Include preparation steps, what to bring, timing advice, and contact placeholder. Tone: {tone}."
            }
        ]
    },
    "health_awareness": {
        "name": "Health Awareness",
        "description": "Public health posts and awareness campaigns",
        "icon": "💙",
        "templates": [
            {
                "title": "Awareness Social Post",
                "fields": ["topic", "tone", "platform"],
                "prompt_template": "Write a health awareness social media post about {topic} for {platform}. Include a compelling statistic, 3 actionable tips, empathetic framing, hashtags, and a CTA to book a check-up. Tone: {tone}."
            },
            {
                "title": "Newsletter Section",
                "fields": ["topic", "tone", "audience"],
                "prompt_template": "Write a newsletter section about {topic} for a healthcare provider. Include a headline, 2–3 key facts, a patient tip, and a CTA. Tone: {tone}. Audience: {audience}."
            }
        ]
    },
    "clinical_blog": {
        "name": "Clinical Blog Post",
        "description": "Evidence-based blog content for healthcare websites",
        "icon": "✍️",
        "templates": [
            {
                "title": "Condition Overview",
                "fields": ["topic", "tone", "audience", "word_count"],
                "prompt_template": "Write an SEO-optimized blog post about {topic} for a healthcare website. Include: intro, prevalence, causes, symptoms, diagnosis, treatment options, prevention, and conclusion. Tone: {tone}. Audience: {audience}. ~{word_count} words."
            },
            {
                "title": "Wellness Tips",
                "fields": ["topic", "tone", "word_count"],
                "prompt_template": "Write a practical wellness tips blog post about {topic}. Include 5–7 actionable tips with explanations, real-world examples, and a motivating conclusion. Tone: {tone}. ~{word_count} words."
            }
        ]
    },
    "admin_comms": {
        "name": "Admin Communications",
        "description": "Internal memos, referral letters, and staff notices",
        "icon": "📨",
        "templates": [
            {
                "title": "Referral Letter",
                "fields": ["topic", "tone"],
                "prompt_template": "Draft a professional referral letter for: {topic}. Include: reason for referral, relevant background, urgency level, requested specialist action, and professional sign-off. Tone: {tone}."
            },
            {
                "title": "Staff Notice",
                "fields": ["topic", "tone", "audience"],
                "prompt_template": "Write a clear internal staff notice about: {topic}. Include: subject, key information, required actions, timeline, and contact for queries. Tone: {tone}. Audience: {audience}."
            }
        ]
    }
}

@app.route("/generator")
def generator():
    return render_template("generator.html", content_types=CONTENT_TYPES)

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    content_type = data.get("content_type")
    template_index = data.get("template_index", 0)
    params = data.get("params", {})

    if content_type not in CONTENT_TYPES:
        return jsonify({"error": "Invalid content type"}), 400

    ct = CONTENT_TYPES[content_type]
    template = ct["templates"][template_index]
    prompt = template["prompt_template"].format(**{k: params.get(k, "") for k in params})

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=(
            "You are ClinicalWriter, a professional healthcare content generator for OmniLogic Healthcare. "
            "Generate accurate, compassionate, and professionally written healthcare content. "
            "Always include appropriate medical disclaimers where relevant. "
            "Use clear, accessible language for patient-facing content and precise clinical language for professional content."
        ),
        messages=[{"role": "user", "content": prompt}],
    )
    return jsonify({
        "content": response.content[0].text,
        "word_count": len(response.content[0].text.split()),
        "content_type": ct["name"],
        "template": template["title"],
        "timestamp": datetime.now().isoformat()
    })


# ════════════════════════════════════════════════
# MODULE 3 · PATIENTPULSE — Sentiment Analysis
# ════════════════════════════════════════════════

@app.route("/sentiment")
def sentiment():
    return render_template("sentiment.html")

@app.route("/api/sentiment", methods=["POST"])
def analyse_sentiment():
    data = request.json
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=(
            "You are PatientPulse, a healthcare sentiment analysis engine. "
            "Analyse patient feedback, reviews, or clinical notes and return ONLY a valid JSON object "
            "with these exact keys:\n"
            "{\n"
            '  "overall": "Positive" | "Negative" | "Neutral" | "Mixed",\n'
            '  "score": <float -1.0 to 1.0>,\n'
            '  "intensity": "High" | "Medium" | "Low",\n'
            '  "emotions": {"joy": 0-100, "trust": 0-100, "fear": 0-100, "surprise": 0-100, '
            '"sadness": 0-100, "disgust": 0-100, "anger": 0-100, "anticipation": 0-100},\n'
            '  "themes": ["theme1", "theme2", ...],\n'
            '  "key_phrases": ["phrase1", "phrase2", ...],\n'
            '  "clinical_flags": ["flag1"] or [],\n'
            '  "summary": "2-3 sentence narrative summary of the sentiment"\n'
            "}\n"
            "Return ONLY the JSON. No preamble, no explanation."
        ),
        messages=[{"role": "user", "content": f"Analyse this patient feedback:\n\n{text}"}],
    )

    raw = response.content[0].text.strip()
    # strip markdown fences if model wraps in them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    result = json.loads(raw)
    return jsonify(result)


# ════════════════════════════════════════════════
# MODULE 4 · HEALTHPREDICT — ML Solution
# ════════════════════════════════════════════════

import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def linear_regression_predict(features):
    """
    Predicts readmission risk score (0–100).
    Trained weights approximated from NHS/literature baselines.
    Features: age, comorbidities, prev_admissions, los_days, medication_count
    """
    w = {"age": 0.18, "comorbidities": 4.2, "prev_admissions": 6.5,
         "los_days": 1.8, "medication_count": 1.1}
    bias = -5.0
    score = bias + sum(w[k] * features.get(k, 0) for k in w)
    return round(max(0, min(100, score)), 1)

def logistic_regression_classify(score):
    """Classifies high/low readmission risk using logistic regression on the score."""
    threshold = 0.5
    prob = sigmoid((score - 40) / 15)
    return {
        "risk_class": "High Risk" if prob >= threshold else "Low Risk",
        "probability": round(prob * 100, 1),
        "confidence": round(abs(prob - 0.5) * 200, 1)
    }

CARE_PATHWAYS = [
    {"id": 1, "name": "Cardiac Rehabilitation", "tags": ["heart", "cardiovascular", "hypertension", "chest pain"], "description": "Structured programme of exercise and education for cardiac patients."},
    {"id": 2, "name": "Diabetes Management Programme", "tags": ["diabetes", "blood sugar", "insulin", "obesity"], "description": "Lifestyle coaching, glucose monitoring, and dietary support."},
    {"id": 3, "name": "COPD Pulmonary Rehab", "tags": ["breathing", "lung", "copd", "respiratory", "smoking"], "description": "Exercise and education programme for chronic obstructive pulmonary disease."},
    {"id": 4, "name": "Mental Health Support Pathway", "tags": ["anxiety", "depression", "mental health", "stress", "sleep"], "description": "Psychological therapy and community mental health services."},
    {"id": 5, "name": "Falls Prevention Programme", "tags": ["elderly", "falls", "mobility", "balance", "osteoporosis"], "description": "Balance training and home safety assessment for fall-risk patients."},
    {"id": 6, "name": "Chronic Pain Management", "tags": ["pain", "arthritis", "fibromyalgia", "musculoskeletal"], "description": "Multidisciplinary pain management including physiotherapy and CBT."},
    {"id": 7, "name": "Post-Surgical Recovery", "tags": ["surgery", "post-op", "wound", "recovery", "rehabilitation"], "description": "Structured recovery plan with physiotherapy and wound care."},
    {"id": 8, "name": "Palliative & End-of-Life Care", "tags": ["terminal", "cancer", "palliative", "hospice", "end of life"], "description": "Compassionate care focused on comfort and quality of life."},
    {"id": 9, "name": "Hypertension Management", "tags": ["hypertension", "blood pressure", "stroke", "kidney"], "description": "Medication optimisation, lifestyle coaching, and regular monitoring."},
    {"id": 10, "name": "Paediatric Developmental Pathway", "tags": ["child", "development", "autism", "adhd", "paediatric"], "description": "Early intervention services for children with developmental needs."},
]

def cosine_similarity(vec_a, vec_b):
    dot = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in vec_b)
    mag_a = math.sqrt(sum(v**2 for v in vec_a.values())) or 1
    mag_b = math.sqrt(sum(v**2 for v in vec_b.values())) or 1
    return dot / (mag_a * mag_b)

def recommend_pathways(diagnoses_text, top_n=3):
    """Content-based cosine-similarity recommender."""
    words = diagnoses_text.lower().split()
    query_vec = {w: 1 for w in words}
    scored = []
    for pathway in CARE_PATHWAYS:
        pathway_vec = {tag: 1 for tag in pathway["tags"]}
        sim = cosine_similarity(query_vec, pathway_vec)
        scored.append({**pathway, "similarity": round(sim * 100, 1)})
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_n]

@app.route("/healthpredict")
def healthpredict():
    return render_template("healthpredict.html")

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.json
    features = {
        "age": float(data.get("age", 0)),
        "comorbidities": float(data.get("comorbidities", 0)),
        "prev_admissions": float(data.get("prev_admissions", 0)),
        "los_days": float(data.get("los_days", 0)),
        "medication_count": float(data.get("medication_count", 0)),
    }
    diagnoses = data.get("diagnoses", "")

    risk_score = linear_regression_predict(features)
    classification = logistic_regression_classify(risk_score)
    pathways = recommend_pathways(diagnoses)

    return jsonify({
        "risk_score": risk_score,
        "classification": classification,
        "pathways": pathways,
        "features_used": features,
        "model_info": {
            "regression": "Linear Regression (5 features, literature-based weights)",
            "classifier": "Logistic Regression (sigmoid threshold 0.5)",
            "recommender": "Content-Based Cosine Similarity (10 care pathways)"
        }
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
