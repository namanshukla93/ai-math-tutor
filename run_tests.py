"""
run_tests.py - Complete Verification Suite for ApexSolve AI Math & Reasoning Master
Runs database, authentication, math solver, reasoning solver, and security checks.
"""

import os
import sys
import glob

def check_security_compliance():
    """Strictly checks that the forbidden email never appears anywhere in the project."""
    print("--- [1/5] Checking Security & Policy Compliance ---")
    forbidden = "".join(["raman", "shukla", "2005", "@", "gmail.com"])
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    violated_files = []
    for root, dirs, files in os.walk(project_dir):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f == "run_tests.py":
                continue
            if f.endswith((".py", ".md", ".txt", ".json", ".toml", ".html", ".env.example")):
                filepath = os.path.join(root, f)
                try:
                    with open(filepath, "r", encoding="utf-8", errors="ignore") as handle:
                        content = handle.read()
                        if forbidden.lower() in content.lower():
                            violated_files.append(filepath)
                except Exception:
                    pass

    if violated_files:
        print(f"[FAIL] Forbidden email found in: {violated_files}")
        return False
    
    print("[PASS] Security Check Passed: No forbidden emails found anywhere in repository.")
    return True


def run_database_tests():
    print("\n--- [2/5] Running Database & Authentication Tests ---")
    import database
    database.init_db()
    ok, msg, u = database.authenticate_user("namanshukla9889@gmail.com", "naman123")
    if not ok or u["name"] != "Naman Shukla":
        print(f"[FAIL] Demo login failed: {msg}")
        return False
    
    stats = database.get_student_dashboard_stats(u["id"])
    if not isinstance(stats, dict) or "total_questions" not in stats:
        print("[FAIL] Stats computation failed")
        return False

    print("[PASS] Database and bcrypt authentication passed.")
    return True


def run_formula_book_tests():
    print("\n--- [3/5] Verifying Formula Pocketbook Contents ---")
    import formula_book
    if not formula_book.MATH_FORMULAS or not formula_book.REASONING_CONCEPTS:
        print("[FAIL] Formula book missing sections")
        return False
    print(f"[PASS] Formula book verified ({len(formula_book.MATH_FORMULAS)} Math sections, {len(formula_book.REASONING_CONCEPTS)} Reasoning sections).")
    return True


def run_ai_math_test():
    print("\n--- [4/5] Testing AI Math Solver & Practice Generation ---")
    import solver
    test_q = "Solve the linear equation: 5x - 15 = 35"
    ok, data, msg = solver.solve_question(test_q, preferred_category="Mathematics")
    if not ok:
        print(f"[FAIL] AI Math Solver call failed: {msg}")
        return False
    
    if "final_answer" not in data or not data.get("step_by_step_solution"):
        print("[FAIL] Incomplete solution structure")
        return False

    print(f"[PASS] Math Solver passed: Final Answer = {data.get('final_answer')}")
    print(f"       Generated Practice Problems count: {len(data.get('practice_problems', []))}")
    return True


def run_ai_reasoning_test():
    print("\n--- [5/5] Testing AI Logical Reasoning Solver ---")
    import solver
    test_q = "Find the next number in sequence: 3, 6, 12, 24, ?"
    ok, data, msg = solver.solve_question(test_q, preferred_category="Reasoning")
    if not ok:
        print(f"[FAIL] AI Reasoning Solver call failed: {msg}")
        return False

    print(f"[PASS] Reasoning Solver passed: Topic = {data.get('topic')}, Answer = {data.get('final_answer')}")
    return True


def main():
    print("=" * 60)
    print("      ApexSolve AI — Full Verification Test Suite")
    print("=" * 60)
    
    checks = [
        check_security_compliance(),
        run_database_tests(),
        run_formula_book_tests(),
        run_ai_math_test(),
        run_ai_reasoning_test()
    ]
    
    print("=" * 60)
    if all(checks):
        print(">>> ALL 5/5 TEST PHASES PASSED WITH 100% SUCCESS! <<<")
        print("=" * 60)
        sys.exit(0)
    else:
        print(">>> SOME TESTS FAILED. PLEASE CHECK LOGS ABOVE. <<<")
        print("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()
