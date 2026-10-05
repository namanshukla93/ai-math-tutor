"""
solver.py - AI Core Engine for ApexSolve Math & Reasoning Master
Handles AI prompt engineering, Gemini API calls with robust model fallbacks,
structured step-by-step solutions, and automatic practice problem generation.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv
from google import genai
from PIL import Image

load_dotenv()

# Priority model list for high speed, accuracy, and zero downtime
CANDIDATE_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-3.1-flash-lite-preview",
    "gemini-flash-latest"
]


def get_gemini_client() -> Optional[genai.Client]:
    """Initializes and returns the Google GenAI client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None


SYSTEM_PROMPT = """You are ApexSolve AI — an elite, world-class Mathematics and Logical Reasoning Professor and Personal Tutor.
Your mission is to provide 100% mathematically rigorous, logically flawless, and crystal-clear explanations that empower students to master the subject.

GUIDELINES FOR MATHEMATICS:
1. Clearly identify the domain (e.g., Algebra, Calculus, Geometry, Trigonometry, Probability, Number Theory).
2. State the fundamental theorem, formula, or principle applied.
3. Show every intermediate step. Never skip algebraic steps. Use standard LaTeX notation (enclosed in $...$ for inline or $$...$$ for block formulas).
4. Verify the solution at the end (e.g., substitute back, check domain constraints, or verify edge cases).
5. Highlight common student pitfalls or traps.

GUIDELINES FOR LOGICAL & ANALYTICAL REASONING:
1. Clearly identify the reasoning type (e.g., Number/Letter Series, Syllogisms, Blood Relations, Direction Sense, Seating Arrangement, Coding-Decoding, Puzzles).
2. For Series: State the underlying pattern or difference sequence (e.g., differences of differences, primes, powers).
3. For Syllogisms: Use Venn diagram logic or Euler circles explanation and strict formal logic (All A are B, Some B are C).
4. For Blood Relations / Direction: Break into a family tree or 2D coordinate diagram representation in clear text.
5. Deduce the answer step-by-step without making unsubstantiated assumptions.

PRACTICE PROBLEM REQUIREMENTS:
Generate 2 to 3 SIMILAR practice problems directly reinforcing the exact concept just taught:
- Practice 1: Foundation (Same pattern/concept with different numbers)
- Practice 2: Intermediate (Requires one additional step or slight twist)
- Practice 3: Challenge (Competitive exam level: JEE / SSC / CAT / Olympiad style)
Provide for each practice problem: Question, Difficulty, Hint, Short Answer, and Complete Step-by-Step Solution.

OUTPUT FORMAT:
You MUST respond strictly in valid JSON format with the following structure:
{
  "category": "Mathematics" or "Reasoning",
  "topic": "Specific Topic Name (e.g., Quadratic Equations, Number Series, Syllogisms)",
  "difficulty": "Beginner" or "Intermediate" or "Advanced",
  "core_concept": "1-2 sentence definition of the key formula, law, or rule utilized",
  "key_formulas": ["Formula or rule 1 in LaTeX", "Formula or rule 2"],
  "step_by_step_solution": [
    {
      "step_number": 1,
      "step_title": "Descriptive Title for this step",
      "explanation": "Clear explanation of what we are doing and WHY",
      "math_expression": "Formula or mathematical working in LaTeX or text if applicable"
    }
  ],
  "final_answer": "Crisp, unambiguous final answer with appropriate units or option letter",
  "pro_tip": "High-value exam tip, mental math shortcut, or verification trick",
  "practice_problems": [
    {
      "id": 1,
      "level": "Foundation",
      "question": "Practice question text",
      "hint": "Subtle hint to guide the student without revealing the answer",
      "correct_answer": "Final concise answer",
      "step_by_step_solution": "Complete step-by-step solution to this practice problem"
    },
    {
      "id": 2,
      "level": "Standard",
      "question": "Practice question text",
      "hint": "Helpful hint",
      "correct_answer": "Final concise answer",
      "step_by_step_solution": "Complete step-by-step solution"
    }
  ]
}
"""


def clean_json_text(raw_text: str) -> str:
    """Strips markdown code fences and cleans JSON output."""
    text = raw_text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def parse_solution_response(raw_text: str, fallback_category: str = "Mathematics") -> Dict[str, Any]:
    """Parses JSON response with robust error recovery."""
    cleaned = clean_json_text(raw_text)
    try:
        data = json.loads(cleaned)
        return data
    except Exception:
        # Attempt regex extraction if JSON wrapper has surrounding text
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        # Fallback structured object from raw text
        return {
            "category": fallback_category,
            "topic": "General Problem Solving",
            "difficulty": "Intermediate",
            "core_concept": "Logical & Mathematical Deduction",
            "key_formulas": [],
            "step_by_step_solution": [
                {
                    "step_number": 1,
                    "step_title": "Comprehensive Solution",
                    "explanation": raw_text,
                    "math_expression": ""
                }
            ],
            "final_answer": "Refer to the comprehensive solution above.",
            "pro_tip": "Review intermediate steps carefully to ensure algebraic and logical consistency.",
            "practice_problems": []
        }


def solve_question(question_text: str, image_file: Optional[Image.Image] = None,
                   preferred_category: Optional[str] = "Auto-Detect") -> Tuple[bool, Dict[str, Any], str]:
    """
    Solves a math or reasoning problem using Gemini API with automatic model failover.
    Returns: (success: bool, solution_data: dict, message: str)
    """
    client = get_gemini_client()
    if not client:
        return False, {}, "Gemini API key is not configured. Please set GEMINI_API_KEY in .env file."

    if not question_text.strip() and not image_file:
        return False, {}, "Please provide a question in text or upload an image."

    prompt_content = []
    user_instruction = f"""Solve this problem with extreme mathematical/logical rigor and provide practice problems:
User Category Preference: {preferred_category or 'Auto-Detect'}

Problem Statement:
{question_text.strip() if question_text else 'Extract and solve the problem from the attached image.'}
"""
    prompt_content.append(user_instruction)

    if image_file:
        prompt_content.append(image_file)

    last_error = ""
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_content,
                config=genai.types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.1,  # Low temperature for highest precision and deterministic math
                    response_mime_type="application/json"
                )
            )

            if response and response.text:
                solution_data = parse_solution_response(
                    response.text,
                    fallback_category="Reasoning" if preferred_category == "Reasoning" else "Mathematics"
                )
                return True, solution_data, f"Solved successfully using {model_name}!"
        except Exception as e:
            last_error = str(e)
            continue

    return False, {}, f"Unable to reach AI solver: {last_error}"
