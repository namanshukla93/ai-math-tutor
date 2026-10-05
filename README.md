# 🧮 AI Math Tutor — Powered by Gemini

> **Covers Class 1 to Class 12 — from basic counting to calculus basics**

> **Live Demo:** *(link will be added after deployment in Phase 8)*

---

## 📌 Problem

Many school students (Class 1–12) struggle with math but don't always have a teacher
available to answer doubts. Hiring a private tutor is expensive. Existing AI tools
often just give the final answer — which means students don't actually learn.

## 💡 Solution

An AI tutor that behaves like a **good human teacher**:
- It **never gives the final answer directly**.
- Instead, it gives **hints and guiding questions**, one step at a time.
- It is **kind and encouraging** — never discouraging.
- If the student is wrong, it **explains gently** and helps them try again.
- If the student asks something non-math, it **politely redirects** to math.

## 🎯 Target Users

Students of **Class 1 through Class 12** — covering topics from basic counting and
shapes (Class 1–3), to fractions, decimals, and word problems (Class 4–6), to
algebra, geometry, and trigonometry (Class 7–10), to statistics and calculus
basics (Class 11–12).

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎓 Class selector | Choose Class 1 to 12 — tutor adjusts language and difficulty |
| 📷 Scan / Upload Problem | Snap a photo or upload an image of your notebook/textbook problem (powered by Gemini Vision) |
| 💬 Step-by-Step Chat | Ask questions and get interactive Socratic guidance (never direct answers) |
| 🎲 Practice question | Instant class-appropriate practice question generator |
| ✅ Check my answer | Submit answers for verification with gentle hints if incorrect |
| 📋 Parent summary | One-click comprehensive session summary for parents and teachers |
| 🚫 Safe scope | Off-topic and non-math questions are politely redirected |
| 🎨 High-Contrast Dark UI | Enhanced typography with Plus Jakarta Sans and formatted KaTeX equations |

---

## 🗂️ Project Structure

```
ai-math-tutor/
│
├── app.py                  # Main Streamlit web app (UI + chat logic)
├── tutor_prompt.py         # The system prompt that controls tutor behavior
├── utils.py                # Helper functions (call Gemini API, format responses)
│
├── tests/
│   └── test_questions.csv  # 30 test questions with expected behaviors
│
├── run_tests.py            # Script to test all 30 questions automatically
├── requirements.txt        # Python packages needed to run the app
│
├── .env.example            # Template showing which env variables are needed
├── .gitignore              # Prevents secrets from being committed to git
└── README.md               # This file
```

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Steps

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd ai-math-tutor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your API key
#    Copy .env.example to .env and fill in your key
copy .env.example .env
# Then open .env and replace "your_key_here" with your actual key

# 4. Run the app
streamlit run app.py
```

---

## 🧪 Test Results

Automated test suite: **30 questions × 10 categories** — run with `python run_tests.py`.

### Final Score: 30/30 PASS — 100% ✅ *(after prompt tuning)*

| Category | Tests | Pass | Notes |
|---|---|---|---|
| Normal Math | 7 | 7 | ✅ All pass, incl. shape-name hint test |
| Word Problem | 4 | 4 | ✅ |
| Algebra | 3 | 3 | ✅ |
| Geometry | 2 | 2 | ✅ |
| Trigonometry | 1 | 1 | ✅ Tutor correct; AI judge hit rate limit (auto-retried) |
| Statistics | 1 | 1 | ✅ |
| Calculus | 2 | 2 | ✅ |
| Demands Answer | 3 | 3 | ✅ Politely refuses, gives hint instead |
| Wrong Answer | 3 | 3 | ✅ Asks student to verify by substitution first |
| Off-Topic | 4 | 4 | ✅ Always redirects to math |

**Prompt iterations needed:** 2 tuning passes
- v1 → 66.7% (8 rate-limit errors, 2 behavioral fails)
- v2 → 93.3% (rate-limit retry fix + Rule 5 rewrite)
- v3 → **100%** (Rule 1 strengthened to block answer leaks via cultural references)

### How tests are evaluated

Each question is checked with a **2-layer pipeline**:

1. **Keyword check** (instant, no API cost) — did the tutor include any forbidden direct-answer phrases?
2. **AI-as-judge** — a second Gemini call reads the tutor response and verifies it follows the expected behavior. Retries automatically on rate limits (10s → 20s → 40s backoff).

```bash
python run_tests.py                        # run all 30 tests
python run_tests.py --fast                 # keyword check only (no API cost)
python run_tests.py --category off_topic   # filter one category
python run_tests.py --save results.md      # export markdown report
```

---

## ⚠️ Limitations

- AI can make mistakes — always verify with a teacher or textbook.
- Works best with standard Class 1–12 Indian school math curriculum.
- Requires an internet connection (calls Gemini API).
- No login or history saved between sessions.

---

## 🔮 Future Work (not built yet)

- Multilingual support (Hindi, regional languages)
- Progress tracking with a database
- Voice input for younger students

---

## 🛠️ Tech Stack

| Tool | Why we chose it |
|---|---|
| Python | Simple, widely used, beginner-friendly |
| Streamlit | Turns Python code into a web app with almost no extra effort |
| Google Gemini API | Free tier available, great at instruction-following for all grade levels |
| python-dotenv | Loads the API key from a .env file safely |

---

## 📸 Screenshots

*(Will be added after Phase 6 — UI polish)*

---

*Built as a portfolio project for an internship application to Cuemath.*
*⚠️ AI can make mistakes — always ask a teacher to verify important answers.*
