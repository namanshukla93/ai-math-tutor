"""
test_auth.py - Unit tests for ApexSolve authentication and database
"""

import database

def test_database_and_auth():
    print("Testing ApexSolve Database and Authentication...")
    database.init_db()

    # 1. Test Demo User Login
    ok, msg, user = database.authenticate_user("namanshukla9889@gmail.com", "naman123")
    assert ok, f"Demo login failed: {msg}"
    assert user["name"] == "Naman Shukla"
    assert user["email"] == "namanshukla9889@gmail.com"
    print("[OK] Demo User authentication successful")

    # 2. Test Invalid Password
    bad_ok, bad_msg, _ = database.authenticate_user("namanshukla9889@gmail.com", "wrongpass")
    assert not bad_ok
    print("[OK] Invalid password correctly rejected")

    # 3. Test New User Registration
    test_email = "teststudent@apexsolve.edu"
    reg_ok, reg_msg, new_u = database.register_user("Test Student", test_email, "studentpass123", "JEE Mains")
    if reg_ok:
        print("[OK] New student registration successful")
    else:
        # If already exists from earlier run, verify login works
        login_ok, _, _ = database.authenticate_user(test_email, "studentpass123")
        assert login_ok
        print("[OK] Existing test student login verified")

    # 4. Test Question Saving & History
    demo_sol = {
        "category": "Mathematics",
        "topic": "Algebra",
        "difficulty": "Intermediate",
        "core_concept": "Quadratic Factorization",
        "step_by_step_solution": [{"step_number": 1, "step_title": "Factor", "explanation": "Factor terms", "math_expression": "x^2 - 4 = 0"}],
        "final_answer": "x = 2, -2",
        "practice_problems": [{"id": 1, "level": "Foundation", "question": "Solve x^2 - 9 = 0", "correct_answer": "x = 3, -3"}]
    }
    qid = database.save_solved_question(
        user_id=user["id"],
        category="Mathematics",
        topic="Algebra",
        question_text="Solve x^2 - 4 = 0",
        solution_markdown=str(demo_sol),
        practice_problems=demo_sol["practice_problems"]
    )
    assert qid > 0
    print("[OK] Question successfully saved to database")

    # 5. Test History retrieval
    history = database.get_user_history(user["id"])
    assert len(history) > 0
    print(f"[OK] History retrieval working (Found {len(history)} records)")

    # 6. Test Bookmarking
    bm_status = database.toggle_bookmark(qid, user["id"])
    assert bm_status is True
    print("[OK] Bookmark toggle working")

    # 7. Test Dashboard Stats
    stats = database.get_student_dashboard_stats(user["id"])
    assert stats["total_questions"] >= 1
    assert stats["bookmarked_questions"] >= 1
    print("[OK] Dashboard stats calculation accurate")

    print("\nALL DATABASE & AUTH TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_database_and_auth()
