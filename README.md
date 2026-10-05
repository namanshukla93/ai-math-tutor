# 🧮 AI Math Tutor — Powered by Gemini

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://ai-math-tutor-bynamanshukla.streamlit.app/)

> **Covers Class 1 to Class 12 — from basic counting to calculus basics**

> 🌐 **Live Working Demo:** [https://ai-math-tutor-bynamanshukla.streamlit.app/](https://ai-math-tutor-bynamanshukla.streamlit.app/)  
> 💻 **GitHub Repository:** [github.com/namanshukla93/ai-math-tutor](https://github.com/namanshukla93/ai-math-tutor)

---

## 📌 Problem

Many school students (Class 1–12) struggle with math but don't always have a teacher available to clear doubts. Hiring a private tutor is expensive. Existing AI tools often just dump the final answer without explaining the steps — or refuse to provide full solutions, leaving students confused.

## 💡 Solution

An AI math tutor with a **Teach First, Then Test (Worked Example + Practice)** model:
- **Detailed Step-by-Step Solution First**: Explains the concept simply, shows complete step-by-step working, and highlights the final answer.
- **Auto-Generated Similar Practice Question**: Immediately after solving, the tutor creates a similar practice problem on its own so the student can apply what they just learned.
- **Active Evaluation**: When the student replies with their answer, the tutor checks it, celebrates correct solutions 🎉, and gently guides them through any mistakes.
- **ChatGPT & Gemini Style Interface**: Clean, minimalist conversational UI with direct image/photo attachment right in the prompt bar.

## 🎯 Target Users

Students of **Class 1 through Class 12** — covering topics from basic counting and shapes (Class 1–3), to fractions, decimals, and word problems (Class 4–6), to algebra, geometry, and trigonometry (Class 7–10), to statistics and calculus basics (Class 11–12).

---

## ✨ Features

| Feature | Description |
|---|---|
| 🌐 **Live Web App** | 24/7 accessible on any device at [ai-math-tutor-bynamanshukla.streamlit.app](https://ai-math-tutor-bynamanshukla.streamlit.app/) |
| ✳️ **Claude-Style Interface** | Iconic warm terracotta & dark charcoal theme with Newsreader & Plus Jakarta Sans typography |
| 📁 **Multi-File Access & Scanner** | Upload **PDFs, Images (PNG/JPG), Text notes, Worksheets, or Code** directly in the chat bar |
| 📄 **File Creation (Claude Artifacts)** | Creates downloadable **Practice Worksheets**, **Formula Cheat Sheets**, and **Solved Problem Sets** (`.md`) |
| 🎓 **Class Selector** | Class 1 to 12 — automatically adapts vocabulary, examples, and CBSE/NCERT curriculum difficulty |
| 📝 **Detailed Worked Solutions** | Clear step-by-step conceptual walkthroughs showing every single calculation |
| 🎯 **Auto Similar Practice** | Tutor automatically creates a similar practice problem for active self-testing |
| 📋 **Parent / Session Summary** | Generates a concise progress report for parents and teachers |

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
