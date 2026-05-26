# OmniLogic Healthcare AI

**End-to-end AI platform for the healthcare industry** — Week 4 Capstone Project

Four integrated AI modules covering LLMs, prompt engineering, NLP sentiment analysis, supervised regression/classification, and unsupervised recommendation.

---

## Modules

| # | Module | Technology | Description |
|---|--------|-----------|-------------|
| 01 | **HealthChat** | LLM (Claude) | Compassionate multi-turn AI health assistant |
| 02 | **ClinicalWriter** | Prompt Engineering | Generate patient education, care instructions, awareness content |
| 03 | **PatientPulse** | NLP Sentiment (LLM) | Analyse patient feedback with Plutchik 8-emotion scoring |
| 04 | **HealthPredict** | Linear Regression + Logistic Regression + Cosine Similarity | Predict readmission risk and recommend care pathways |

---

## ML Solution (HealthPredict)

- **Linear Regression** — 5 clinical features → continuous readmission risk score (0–100)
- **Logistic Regression** — sigmoid function → binary High/Low risk classification with probability
- **Content-Based Recommender** — cosine similarity between diagnosis terms and 10 care pathway profiles

---

## Deploy to Render

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit - OmniLogic Healthcare AI"
git remote add origin https://github.com/YOUR_USERNAME/omnilogic-healthcare.git
git push -u origin main
```

### Step 2 — Create Web Service on Render
1. Go to [render.com](https://render.com) → **New +** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `omnilogic-healthcare`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### Step 3 — Set Environment Variable
In your Render service → **Environment** tab:
- Key: `ANTHROPIC_API_KEY`
- Value: your Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

### Step 4 — Deploy
Render deploys automatically on every `git push`.

---

## Local Development

```bash
# Clone and set up
git clone https://github.com/YOUR_USERNAME/omnilogic-healthcare.git
cd omnilogic-healthcare

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt

# Set API key
export ANTHROPIC_API_KEY=your_key_here   # Windows: set ANTHROPIC_API_KEY=your_key_here

python app.py
# Open http://localhost:5000
```

---

## Tech Stack

- **Backend**: Python / Flask
- **AI**: Anthropic API (claude-sonnet-4-20250514)
- **ML**: Pure Python (no scikit-learn required — runs on free Render tier)
- **Frontend**: Vanilla HTML/CSS/JS (no build step)
- **Deployment**: Render (Gunicorn)

---

## Author
[@nonhleB](https://github.com/nonhleB) — Week 4 Capstone · AI Solution Development & Portfolio Finalisation
