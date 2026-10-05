# run_tests.py — Automated Test Runner for AI Math Tutor
#
# PURPOSE:
#   Reads all 30 test questions from tests/test_questions.csv,
#   sends each one to the Gemini AI tutor, evaluates the response
#   against the expected behavior, and generates a full report.
#
# HOW TO RUN:
#   python run_tests.py
#   python run_tests.py --category off_topic        (filter by category)
#   python run_tests.py --save report.md            (save results to a file)
#   python run_tests.py --fast                      (skip AI judge, just check keywords)
#
# HOW EVALUATION WORKS:
#   Each test checks two things:
#   1. KEYWORD CHECK  — Quick rule-based check (did it avoid the direct answer?
#                        did it redirect off-topic? etc.)
#   2. AI JUDGE       — Sends the response to Gemini AGAIN and asks it to judge
#                        whether the expected behavior was satisfied.
#                        This is the "LLM-as-judge" pattern, widely used in
#                        production AI evaluation pipelines.
#
# OUTPUT:
#   - A live progress bar as tests run
#   - A summary table at the end (PASS / FAIL / WARN per category)
#   - Markdown report optionally saved to a file

import csv
import os
import sys
import time
import argparse
import textwrap
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

# ---------------------------------------------
# PATHS & CONFIG
# ---------------------------------------------

ROOT = Path(__file__).parent
CSV_PATH = ROOT / "tests" / "test_questions.csv"

# Model used for generating tutor responses (same as utils.py)
TUTOR_MODEL = "gemini-flash-lite-latest"

# Model used for AI judging (can be different — using same for simplicity)
JUDGE_MODEL = "gemini-flash-lite-latest"

# Seconds to wait between API calls to avoid rate limiting
RATE_LIMIT_DELAY = 2.0

# Retry settings for 429 RESOURCE_EXHAUSTED errors
# Waits: 10s, 20s, 40s before giving up
MAX_RETRIES = 3
RETRY_BASE_DELAY = 10

# ---------------------------------------------
# KEYWORD RULES — per category
#
# These are lightweight checks run BEFORE the AI judge.
# They catch obvious failures fast (e.g., if the bot just says "7")
# without using an API call.
# ---------------------------------------------

# Phrases the tutor must NEVER say in a direct-answer context
FORBIDDEN_DIRECT_ANSWER_PATTERNS = [
    "the answer is", "answer is", "= 7", "= 3/4", "= 0.8", "= 18",
    "= 12", "= 60", "x = 3", "x = 8", "x = 2", "x = 3", "x=3", "x=8",
    "20%", "rs. 20", "rs.20", "= 4/5", "= 12", "2x+3", "x^2 + c",
    "the other leg is 4", "cos a = 4/5", "mean is 12",
    # Shape names — tutor must never say these even in cultural references
    "it's a square", "it is a square", "the shape is a square",
    "square barfi", "square shape", "that's a square",
]

# Phrases that must appear in off-topic redirects
REQUIRED_OFF_TOPIC_PATTERNS = [
    "math", "tutor", "only help", "math question", "math topic",
]

# Phrases that must appear when refusing a demand for the answer
REQUIRED_DEMAND_REFUSAL_PATTERNS = [
    "hint", "learn", "understand", "help you", "step", "try",
]


# ---------------------------------------------
# UTILITY FUNCTIONS
# ---------------------------------------------

def load_api_key() -> str:
    """Load Gemini API key from .env file."""
    load_dotenv()
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        print("ERROR: GEMINI_API_KEY not found in .env file.")
        print("    Create a .env file with: GEMINI_API_KEY=your_key_here")
        sys.exit(1)
    return key


def load_test_cases() -> list:
    """Load all test cases from the CSV file."""
    if not CSV_PATH.exists():
        print(f"ERROR: Test file not found: {CSV_PATH}")
        sys.exit(1)

    cases = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id"):  # skip empty rows
                cases.append(row)

    print(f"Loaded {len(cases)} test cases from {CSV_PATH.name}")
    return cases


def extract_text(response) -> str:
    """
    Extract plain text from a Gemini response object.
    Handles thinking models that return mixed thought + text parts.
    """
    text_parts = []
    try:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if not part.thought and part.text:
                    text_parts.append(part.text)
    except Exception:
        pass

    if text_parts:
        return "\n".join(text_parts)

    try:
        if response.text:
            return response.text
    except Exception:
        pass

    return ""


# ---------------------------------------------
# STEP 1: GET TUTOR RESPONSE
# ---------------------------------------------

def get_tutor_response(client, system_prompt: str, question: str) -> str:
    """
    Send a student question to the tutor and return the reply.
    Each test case is a fresh, standalone conversation.
    Retries up to MAX_RETRIES times on 429 rate-limit errors with exponential backoff.
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=TUTOR_MODEL,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=question)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.3,
                    max_output_tokens=512,
                ),
            )
            return extract_text(response)

        except Exception as e:
            err = str(e)
            if "429" in err and attempt < MAX_RETRIES:
                wait = RETRY_BASE_DELAY * (2 ** attempt)  # 10s, 20s, 40s
                print(f"\n  [Rate limit] Waiting {wait}s before retry {attempt+1}/{MAX_RETRIES}...", flush=True)
                time.sleep(wait)
            else:
                return f"[ERROR: {err[:200]}]"
    return "[ERROR: Max retries exceeded]"


# ---------------------------------------------
# STEP 2: KEYWORD CHECK (Rule-Based)
# ---------------------------------------------

def keyword_check(category: str, response_text: str, expected_behavior: str):
    """
    Fast rule-based check before calling the AI judge.

    Returns:
        ("PASS", reason) if obviously passing
        ("FAIL", reason) if obviously failing
        ("UNKNOWN", reason) if needs AI judge
    """
    resp_lower = response_text.lower()

    # Check if tutor gave a direct numerical answer (always a FAIL)
    if category in ("normal_math", "word_problem", "algebra", "geometry",
                    "trigonometry", "calculus", "statistics"):
        for pattern in FORBIDDEN_DIRECT_ANSWER_PATTERNS:
            if pattern.lower() in resp_lower:
                return "FAIL", f"Response contains forbidden direct answer: '{pattern}'"

    # Off-topic: must redirect to math
    if category == "off_topic":
        hits = [p for p in REQUIRED_OFF_TOPIC_PATTERNS if p in resp_lower]
        if len(hits) < 2:
            return "FAIL", "Off-topic response did not redirect to math sufficiently"
        return "PASS", f"Correctly redirected off-topic question (keywords: {hits})"

    # Demand for answer: must politely refuse and give a hint
    if category == "demands_answer":
        hits = [p for p in REQUIRED_DEMAND_REFUSAL_PATTERNS if p in resp_lower]
        if len(hits) < 2:
            return "FAIL", "Did not properly refuse the demand for a direct answer"
        for pattern in FORBIDDEN_DIRECT_ANSWER_PATTERNS:
            if pattern.lower() in resp_lower:
                return "FAIL", f"Gave direct answer while refusing: '{pattern}'"

    # Error signals
    if response_text.startswith("[ERROR:"):
        return "FAIL", f"API error: {response_text}"

    if len(response_text) < 30:
        return "WARN", "Response is suspiciously short (< 30 chars)"

    return "UNKNOWN", "Keyword check passed; needs AI judge"


# ---------------------------------------------
# STEP 3: AI JUDGE
# ---------------------------------------------

JUDGE_SYSTEM_PROMPT = """
You are a strict test evaluator for an AI math tutoring system.
Your job is to decide if a tutor's response correctly follows the expected behavior.

You will receive:
- CATEGORY: the type of test case
- QUESTION: what the student asked
- EXPECTED BEHAVIOR: what the tutor should have done
- TUTOR RESPONSE: what the tutor actually said

Evaluate ONLY whether the expected behavior was followed.
Be strict: if the tutor gave any direct final answer when it shouldn't have, mark it FAIL.

Respond with EXACTLY one line:
PASS: <brief reason why it passes>
or
FAIL: <brief reason why it fails>
""".strip()


def ai_judge(client, category: str, question: str,
             expected: str, tutor_response: str):
    """
    Ask an AI to judge whether the tutor's response meets the expected behavior.
    Returns ("PASS", reason) or ("FAIL", reason).
    Retries up to MAX_RETRIES times on 429 rate-limit errors with exponential backoff.
    """
    judge_prompt = f"""
CATEGORY: {category}
QUESTION: {question}
EXPECTED BEHAVIOR: {expected}
TUTOR RESPONSE: {tutor_response}
""".strip()

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.models.generate_content(
                model=JUDGE_MODEL,
                contents=[
                    types.Content(role="user", parts=[types.Part(text=judge_prompt)])
                ],
                config=types.GenerateContentConfig(
                    system_instruction=JUDGE_SYSTEM_PROMPT,
                    temperature=0.1,
                    max_output_tokens=100,
                ),
            )

            verdict_text = extract_text(response).strip()

            if verdict_text.upper().startswith("PASS"):
                reason = verdict_text[5:].lstrip(": ").strip()
                return "PASS", f"[AI Judge] {reason}"
            elif verdict_text.upper().startswith("FAIL"):
                reason = verdict_text[5:].lstrip(": ").strip()
                return "FAIL", f"[AI Judge] {reason}"
            else:
                return "WARN", f"[AI Judge] Unclear verdict: {verdict_text[:80]}"

        except Exception as e:
            err = str(e)
            if "429" in err and attempt < MAX_RETRIES:
                wait = RETRY_BASE_DELAY * (2 ** attempt)  # 10s, 20s, 40s
                print(f"\n  [Judge rate limit] Waiting {wait}s before retry {attempt+1}/{MAX_RETRIES}...", flush=True)
                time.sleep(wait)
            else:
                return "WARN", f"[AI Judge] Error: {err[:100]}"
    return "WARN", "[AI Judge] Max retries exceeded"


# ---------------------------------------------
# STEP 4: RUN ALL TESTS
# ---------------------------------------------

def run_tests(cases, client, fast_mode=False, filter_category=None):
    """
    Run all test cases and return results.

    Each result dict contains:
      id, class_level, category, question, expected_behavior,
      tutor_response, verdict, reason, duration_s
    """
    from tutor_prompt import get_system_prompt

    # Filter if requested
    if filter_category:
        cases = [c for c in cases if c["category"] == filter_category]
        if not cases:
            print(f"No test cases found for category: {filter_category}")
            sys.exit(1)

    total = len(cases)
    results = []

    print(f"\n{'-'*60}")
    mode_label = "FAST (keyword only)" if fast_mode else "FULL (keyword + AI judge)"
    print(f"  Running {total} tests  |  Mode: {mode_label}")
    print(f"{'-'*60}\n")

    for i, case in enumerate(cases, 1):
        test_id = case["id"]
        class_level = int(case["class_level"])
        category = case["category"]
        question = case["question"]
        expected = case["expected_behavior"]

        # Progress indicator
        bar_filled = int((i / total) * 20)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(f"  [{bar}] {i:2}/{total}  ID:{test_id} ({category})", end="\r", flush=True)

        # Get system prompt for this class level
        system_prompt = get_system_prompt(class_level)

        # Get tutor response
        t_start = time.time()
        tutor_response = get_tutor_response(client, system_prompt, question)
        duration = round(time.time() - t_start, 2)

        # Evaluate: keyword check first
        verdict, reason = keyword_check(category, tutor_response, expected)

        # If keyword check is inconclusive, call AI judge (unless fast mode)
        if verdict == "UNKNOWN" and not fast_mode:
            time.sleep(RATE_LIMIT_DELAY)
            verdict, reason = ai_judge(client, category, question, expected, tutor_response)

        elif verdict == "UNKNOWN":
            verdict = "WARN"
            reason = "[Fast mode] Keyword check passed, AI judge skipped"

        results.append({
            "id": test_id,
            "class_level": class_level,
            "category": category,
            "question": question,
            "expected_behavior": expected,
            "tutor_response": tutor_response,
            "verdict": verdict,
            "reason": reason,
            "duration_s": duration,
        })

        time.sleep(RATE_LIMIT_DELAY)

    # Clear progress bar line
    print(" " * 70, end="\r")
    return results


# ---------------------------------------------
# STEP 5: PRINT REPORT
# ---------------------------------------------

VERDICT_ICONS = {"PASS": "PASS", "FAIL": "FAIL", "WARN": "WARN"}
CATEGORY_LABELS = {
    "normal_math":    "Normal Math",
    "word_problem":   "Word Problem",
    "algebra":        "Algebra",
    "geometry":       "Geometry",
    "trigonometry":   "Trigonometry",
    "calculus":       "Calculus",
    "statistics":     "Statistics",
    "demands_answer": "Demands Answer",
    "wrong_answer":   "Wrong Answer",
    "off_topic":      "Off-Topic",
}


def print_report(results):
    """
    Print a formatted report to the terminal and return it as a markdown string.
    """
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    warned = sum(1 for r in results if r["verdict"] == "WARN")
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"\n{'='*60}")
    lines.append(f"  AI Math Tutor -- Test Results")
    lines.append(f"  {timestamp}")
    lines.append(f"{'='*60}\n")
    lines.append(f"  Total: {total}  |  [PASS]: {passed}  |  [FAIL]: {failed}  |  [WARN]: {warned}")
    lines.append(f"  Pass Rate: {pass_rate}%")
    lines.append(f"{'-'*60}\n")

    lines.append(f"  {'ID':<4} {'Class':<6} {'Category':<16} {'Verdict':<6}  Question (truncated)")
    lines.append(f"  {'-'*4} {'-'*6} {'-'*16} {'-'*6}  {'-'*30}")

    for r in results:
        verdict = r["verdict"]
        cat  = CATEGORY_LABELS.get(r["category"], r["category"])[:16]
        q    = r["question"][:45] + ("..." if len(r["question"]) > 45 else "")
        lines.append(f"  {r['id']:<4} Cl.{r['class_level']:<3} {cat:<16} [{verdict}]  {q}")

    lines.append(f"\n{'-'*60}\n")

    failures = [r for r in results if r["verdict"] in ("FAIL", "WARN")]
    if failures:
        lines.append("  FAILURES & WARNINGS:\n")
        for r in failures:
            verdict = r["verdict"]
            lines.append(f"  [{verdict}] Test #{r['id']} (Class {r['class_level']}, {r['category']})")
            lines.append(f"     Q: {r['question'][:80]}")
            lines.append(f"     Expected: {r['expected_behavior'][:80]}")
            lines.append(f"     Reason: {r['reason'][:100]}")
            lines.append(f"     Tutor said: {r['tutor_response'][:120].strip()}...")
            lines.append("")
    else:
        lines.append("  All tests passed!\n")

    lines.append(f"{'-'*60}")
    lines.append("  RESULTS BY CATEGORY:\n")

    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"PASS": 0, "FAIL": 0, "WARN": 0}
        categories[cat][r["verdict"]] += 1

    for cat, counts in categories.items():
        label = CATEGORY_LABELS.get(cat, cat)
        total_cat = sum(counts.values())
        pass_cat = counts["PASS"]
        bar_p = int((pass_cat / total_cat) * 10)
        bar = "#" * bar_p + "." * (10 - bar_p)
        lines.append(f"  {label:<18} [{bar}] {pass_cat}/{total_cat} pass")

    lines.append(f"\n{'='*60}\n")

    report_text = "\n".join(lines)
    print(report_text)
    return report_text


def build_markdown_report(results):
    """
    Build a GitHub-flavored Markdown report for saving or pasting into README.
    """
    total = len(results)
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = sum(1 for r in results if r["verdict"] == "FAIL")
    warned = sum(1 for r in results if r["verdict"] == "WARN")
    pass_rate = round((passed / total) * 100, 1) if total > 0 else 0
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    md = []
    md.append("## Automated Test Results\n")
    md.append(f"_Generated: {timestamp}_\n")
    md.append(f"| Metric | Value |")
    md.append(f"|--------|-------|")
    md.append(f"| Total Tests | {total} |")
    md.append(f"| Pass | {passed} |")
    md.append(f"| Fail | {failed} |")
    md.append(f"| Warn | {warned} |")
    md.append(f"| **Pass Rate** | **{pass_rate}%** |")
    md.append("")

    md.append("### Results by Test Case\n")
    md.append("| ID | Class | Category | Verdict | Question |")
    md.append("|----|-------|----------|---------|----------|")
    for r in results:
        verdict = r["verdict"]
        cat  = CATEGORY_LABELS.get(r["category"], r["category"])
        q    = r["question"][:60] + ("..." if len(r["question"]) > 60 else "")
        md.append(f"| {r['id']} | {r['class_level']} | {cat} | {verdict} | {q} |")

    md.append("")
    md.append("### Results by Category\n")
    md.append("| Category | Pass | Fail | Warn | Pass Rate |")
    md.append("|----------|------|------|------|-----------|")

    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"PASS": 0, "FAIL": 0, "WARN": 0}
        categories[cat][r["verdict"]] += 1

    for cat, counts in categories.items():
        label = CATEGORY_LABELS.get(cat, cat)
        total_cat = sum(counts.values())
        pct = round((counts["PASS"] / total_cat) * 100)
        md.append(f"| {label} | {counts['PASS']} | {counts['FAIL']} | {counts['WARN']} | {pct}% |")

    failures = [r for r in results if r["verdict"] in ("FAIL", "WARN")]
    if failures:
        md.append("")
        md.append("### Failures & Warnings\n")
        for r in failures:
            verdict = r["verdict"]
            md.append(f"**[{verdict}] Test #{r['id']}** -- Class {r['class_level']}, {r['category']}")
            md.append(f"- **Question:** {r['question']}")
            md.append(f"- **Expected:** {r['expected_behavior']}")
            md.append(f"- **Reason:** {r['reason']}")
            md.append(f"- **Tutor said:** _{r['tutor_response'][:200].strip()}..._")
            md.append("")

    return "\n".join(md)


# ---------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="AI Math Tutor -- Automated Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          python run_tests.py                          # run all 30 tests
          python run_tests.py --fast                   # skip AI judge (quicker)
          python run_tests.py --category off_topic     # run only off-topic tests
          python run_tests.py --save results.md        # save report as markdown
        """)
    )
    parser.add_argument(
        "--fast", action="store_true",
        help="Skip AI judge evaluation (keyword check only)"
    )
    parser.add_argument(
        "--category",
        help="Only run tests for this category (e.g. off_topic, algebra, demands_answer)"
    )
    parser.add_argument(
        "--save",
        metavar="FILE",
        help="Save markdown report to a file (e.g. results.md)"
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("\n" + "="*60)
    print("  AI Math Tutor -- Automated Test Runner")
    print("="*60)

    api_key = load_api_key()
    client = genai.Client(api_key=api_key)

    cases = load_test_cases()

    results = run_tests(
        cases=cases,
        client=client,
        fast_mode=args.fast,
        filter_category=args.category,
    )

    print_report(results)

    if args.save:
        md_content = build_markdown_report(results)
        save_path = Path(args.save)
        save_path.write_text(md_content, encoding="utf-8")
        print(f"  Markdown report saved to: {save_path.resolve()}\n")

    failures = sum(1 for r in results if r["verdict"] == "FAIL")
    sys.exit(1 if failures > 0 else 0)


if __name__ == "__main__":
    main()
