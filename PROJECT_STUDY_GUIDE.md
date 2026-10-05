# 🎓 ApexSolve — Complete Master Project Guide & Interview Playbook

> **Author:** Naman Shukla  
> **Contact:** namanshukla9889@gmail.com  
> **Target Audience:** College Students, Job Aspirants, Interviewers, and Software Beginners.  
> **Purpose:** Ye document is tarah likha gaya hai ki ek beginner ya school/college student bhi isko padhkar poora project samajh sake, khud se bana sake, aur kisi bhi technical interviewer ko confidently explain kar sake.

---

## 📑 Table of Contents

1. [Project Overview & Problem Statement](#1-project-overview--problem-statement)
2. [Why ApexSolve? (Key Differentiators)](#2-why-apexsolve-key-differentiators)
3. [System Architecture & Workflow](#3-system-architecture--workflow)
4. [Deep Dive into Every Code File](#4-deep-dive-into-every-code-file)
   - `database.py` (Data Storage & Security)
   - `solver.py` (AI Logic & Prompt Engineering)
   - `formula_book.py` (Curated Pocketbook)
   - `app.py` (Frontend & User Experience)
   - `run_tests.py` (Automated Quality Assurance)
5. [How AI Solves & Generates Practice Problems](#5-how-ai-solves--generates-practice-problems)
6. [Top Interview Questions & Perfect Answers](#6-top-interview-questions--perfect-answers)
7. [Step-by-Step: How to Build This Project from Scratch](#7-step-by-step-how-to-build-this-project-from-scratch)

---

## 1. Project Overview & Problem Statement

### 🎯 Problem Statement:
Jab students maths ya logical reasoning ke questions solve karte hain aur stuck ho jaate hain, to unke paas do options hote hain:
1. **Book ke peeche ka solution dekhna**: Jisme usually intermediate steps skip kar diye jaate hain (Direct likh dete hain: *"On solving we get x = 4"*). Student ko samajh nahi aata ki wo step kaise aaya.
2. **Generic AI Chatbots (ChatGPT wagera)**: Ye generic text generate karte hain, aksar calculation me galti (hallucination) karte hain, aur structured student-friendly format nahi dete.

### 💡 ApexSolve Solution:
**ApexSolve** ek dedicated **Maths aur Logical Reasoning Web App** hai jo:
- **Har step ko mathematically prove aur explain karti hai** bina kisi step ko skip kiye.
- **Textbook-grade KaTeX LaTeX formatting** me mathematical formulas render karti hai.
- Solution ke baad student ko **similar practice problems** (Foundation, Standard, Challenge) deti hai jisme student apna answer type karke instant verify kar sakta hai, hint dekh sakta hai, ya full solution check kar sakta hai.
- Student ki saari solved questions history, bookmarks, aur accuracy ko secure local database me save karti hai.

---

## 2. Why ApexSolve? (Key Differentiators)

| Feature | Generic Chatbot / Solution App | ApexSolve AI |
| :--- | :--- | :--- |
| **Mathematical Precision** | High hallucination risk in calculations | Enforced low temperature (0.1) + structured verification |
| **Domain Specialization** | Mixed answers with irrelevant conversational fluff | Strict focus: Pure Maths & Logical Reasoning only |
| **Immediate Practice** | Student has to search other questions manually | Automatically creates 2–3 adaptive practice problems on the spot |
| **Formula & Rule Reference** | Student has to open external books | In-app high-yield Formula & Reasoning concept pocketbook |
| **Data Privacy & Security** | Data sent to unknown 3rd party stores | Local SQLite database + salted `bcrypt` password encryption |

---

## 3. System Architecture & Workflow

### 🏗️ High-Level Diagram:
```
+-------------------------------------------------------------+
|                 Student's Web Browser                       |
|   (Interactive UI, LaTeX Equations, Scratchpad, Practice)   |
+------------------------------+------------------------------+
                               |
                               v
+-------------------------------------------------------------+
|                     Streamlit UI Layer                      |
|      (State Management, Navigation, Theme Styling)          |
+---------------+-----------------------------+---------------+
                |                             |
                v                             v
+-------------------------------+  +--------------------------+
|      database.py (SQLite)     |  |   solver.py (AI Engine)  |
| - Users table (bcrypt auth)   |  | - System Prompt Rules    |
| - Solved Questions archive    |  | - Fallback Model Client  |
| - Practice Logs & Analytics   |  | - JSON Schema Parser     |
+-------------------------------+  +------------+-------------+
                                                |
                                                v
                                   +--------------------------+
                                   |  Google Gemini API       |
                                   |  (High-Speed Flash LLM)  |
                                   +--------------------------+
```

### 🔄 End-to-End Request Flow:
1. **Input**: Student apna math question likhta hai ya image upload karta hai.
2. **Prompt Construction**: `solver.py` system instructions aur student question ko bundle karke Gemini client ko bhejta hai.
3. **Deterministic Generation**: Model temperature ko `0.1` par rakha gaya hai taaki calculations 100% stable aur accurate rahein.
4. **Structured JSON Parsing**: AI model strict JSON return karta hai jisme Core Concept, Step-by-Step Proof, Final Answer, Pro Exam Tip, aur Similar Practice Problems hote hain.
5. **Persistence**: `database.py` solution aur practice questions ko user ke account ke under SQLite database me save kar deta hai.
6. **Rendering**: `app.py` solution ko clean visually pleasing cards aur KaTeX math me display karta hai, aur practice questions me interactive check button enable kar deta hai.

---

## 4. Deep Dive into Every Code File

### 1. `database.py` (Local Data Storage & Security)
- **Kyu banaya?**: Students ke accounts, passwords, solved questions ka archive, aur practice tests ki accuracy ko locally store karne ke liye.
- **Key Concepts Used**:
  - `sqlite3`: Python ki built-in zero-configuration SQL database engine.
  - `bcrypt`: Industry-standard password hashing algorithm. Password ko plaintext me save nahi kiya jaata; pehle 12 rounds ka salt add karke hash kiya jaata hai (`bcrypt.hashpw`).
- **Main Tables**:
  - `users`: `id`, `name`, `email` (UNIQUE), `password_hash`, `target_exam`.
  - `questions`: `user_id`, `category` (Math/Reasoning), `topic`, `question_text`, `solution_markdown`, `practice_json`, `is_bookmarked`.
  - `practice_logs`: `user_id`, `question_id`, `student_answer`, `correct_answer`, `is_correct`, `attempted_at`.

### 2. `solver.py` (The Brain of the Application)
- **Kyu banaya?**: Gemini AI model ko call karna, prompt format karna, aur mathematical reasoning rules enforce karna.
- **Key Concepts Used**:
  - `google.genai`: Modern official Google GenAI Python SDK.
  - **Failover Mechanism (Self-Healing)**: Agar koi ek AI model temporarily high-demand ya unavailable ho (e.g. 503 error), to ye automatically fallback models (`gemini-flash-lite-latest`, `gemini-3.1-flash-lite-preview`, `gemini-flash-latest`) par switch kar leta hai. App kabhi crash nahi hota.
  - **Structured Output**: AI ko force kiya gaya hai ki wo pure JSON object return kare taaki UI har step ko alag styling ke sath show kar sake.

### 3. `formula_book.py` (Student Handbook)
- **Kyu banaya?**: Ek student ko revision karte waqt baar-baar Google ya formula books na kholni padein.
- **Content**:
  - **Pure Maths**: Quadratic roots, AP/GP formulas, Logarithm laws, Trigonometric identities, Standard derivatives & integrals, Combinatorics.
  - **Logical Reasoning**: Alphabetical EJOTY rule, Reverse pairs (Sum = 27), Difference of differences in series, Blood relation shorthand, Direction sense Pythagoras logic.

### 4. `app.py` (Streamlit Frontend & Controller)
- **Kyu banaya?**: Modern, dark-mode, responsive web interface.
- **Pages / Views**:
  - `render_auth_page()`: Clean login aur registration form with 1-click demo student login.
  - `render_solver_view()`: Core solver interface with text area, preset example buttons, image uploader, KaTeX renderer, and interactive practice arena.
  - `render_practice_arena_view()`: Unlimited custom topic practice generator.
  - `render_handbook_view()`: Tabbed revision pocketbook.
  - `render_history_view()`: Searchable, filterable question archive with bookmarking.
  - `render_analytics_view()`: Visual progress metrics and accuracy gauge.

### 5. `run_tests.py` (Automated Test Suite)
- **Kyu banaya?**: Interview me sabse badi quality hoti hai **Automated Testing**.
- **Kya test karta hai?**:
  1. Security compliance (Ensures zero forbidden emails).
  2. Database operations (User creation, login, question saving, bookmarking).
  3. Formula book integrity.
  4. Live AI Math solving & practice problem verification.
  5. Live AI Reasoning series deduction.

---

## 5. How AI Solves & Generates Practice Problems

### Math Solving Logic:
Jab user koi question deta hai (e.g., $3x^2 - 10x + 3 = 0$):
1. **Topic Identification**: Model topic identify karta hai: `Quadratic Equations`.
2. **Formula Selection**: Model standard formula define karta hai:
   $$x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}$$
3. **Step Decomposition**:
   - Step 1: Identify coefficients ($a=3, b=-10, c=3$).
   - Step 2: Compute discriminant ($\Delta = (-10)^2 - 4(3)(3) = 100 - 36 = 64$).
   - Step 3: Compute square root ($\sqrt{64} = 8$).
   - Step 4: Calculate both roots ($x = \frac{10 \pm 8}{6} \implies x = 3, x = \frac{1}{3}$).
4. **Practice Generation**:
   - Level 1: $2x^2 - 7x + 3 = 0$ (Foundation).
   - Level 2: $x^2 - 5x + 6 = 0$ (Standard).
   - Level 3: $4x^2 - 12x + 9 = 0$ with equal roots (Challenge).

---

## 6. Top Interview Questions & Perfect Answers

### Q1: "Can you explain what ApexSolve is and why you built it?"
> **Answer**:  
> "ApexSolve is an intelligent web application built for students and competitive exam aspirants. Most generic AI chatbots either hallucinate math calculations or give high-level answers that skip intermediate algebraic steps. I built ApexSolve to act like a personal professor: it proves every step rigorously using LaTeX, highlights the core governing principle, provides pro exam shortcuts, and immediately generates adaptive practice questions on that exact concept so the student can test their mastery in real-time."

### Q2: "How do you prevent the AI model from hallucinating or giving wrong math?"
> **Answer**:  
> "I tackled this in three ways:  
> 1. **Low Temperature**: Set `temperature=0.1` in the Gemini API config to minimize randomness and maximize deterministic mathematical deduction.  
> 2. **Explicit Verification Instruction**: In the system prompt, the AI is instructed to perform step-by-step verification (such as substituting the roots back into the equation).  
> 3. **Structured JSON Output**: By forcing the model to emit a strict JSON schema, it separates the core concept, intermediate step calculations, final answer, and practice problems into discrete, verifiable fields."

### Q3: "Why did you choose Streamlit instead of a traditional React + FastAPI stack?"
> **Answer**:  
> "For an AI-powered academic platform, time-to-value, Python ecosystem compatibility, and native scientific rendering are critical. Streamlit allows direct in-memory state management in Python, native KaTeX LaTeX rendering (`st.latex`), and effortless integration with Google's Python GenAI SDK without the boilerplate of multi-repo REST synchronization. Furthermore, by keeping the architecture modular (`database.py`, `solver.py`, `formula_book.py`), the backend can easily be exposed via FastAPI in the future if a mobile app is needed."

### Q4: "How is user security handled in this project?"
> **Answer**:  
> "We implement industry-standard authentication using `bcrypt`. Passwords are never stored in plaintext. They are salted with 12 rounds of entropy and hashed before storing in SQLite. The database queries use parameterized SQL statements to eliminate SQL injection vulnerabilities."

### Q5: "How do you handle API downtime or rate limits?"
> **Answer**:  
> "In `solver.py`, I implemented an automatic model fallback mechanism. If the primary model `gemini-flash-lite-latest` experiences a temporary 503 spike or quota limit, the function catches the exception and immediately retries with candidate backup models like `gemini-3.1-flash-lite-preview` or `gemini-flash-latest`. This ensures high availability."

---

## 7. Step-by-Step: How to Build This Project from Scratch

Agar kisi ko ye project 0 se banana ho, to steps ye hain:

### Step 1: Environment Setup
```bash
# 1. Project folder banayein
mkdir apexsolve-ai
cd apexsolve-ai

# 2. Virtual environment create aur activate karein
python -m venv venv
venv\Scripts\activate

# 3. Required packages install karein
pip install streamlit google-genai python-dotenv pillow bcrypt
```

### Step 2: API Key Configuration
Ek `.env` file banayein:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Google AI Studio se free key generate karein).*

### Step 3: Database & Security Module (`database.py`)
- SQLite database connect karein.
- `users`, `questions`, aur `practice_logs` tables create karein.
- `bcrypt` se password hash aur verify function likhein.

### Step 4: AI Engine Module (`solver.py`)
- `google.genai.Client` initialize karein.
- Math aur Reasoning ke liye detailed System Prompt likhein.
- Structured JSON output parsing logic banayein.

### Step 5: Web UI Module (`app.py`)
- Streamlit page configuration aur custom CSS set karein.
- Sidebar navigation, question input, KaTeX output card, aur practice answer checker components design karein.

### Step 6: Testing & Verification (`run_tests.py`)
- Automated scripts likhein jo database, authentication, aur solver calls ko automated run karke verify karein.

### Step 7: Run & Present
```bash
streamlit run app.py
```
App browser me open ho jayegi! 🎉

---

## 📞 Author & Contact

- **Developer:** Naman Shukla
- **Email:** `namanshukla9889@gmail.com`
- **GitHub Repository:** [https://github.com/namanshukla93/ai-math-tutor](https://github.com/namanshukla93/ai-math-tutor)
