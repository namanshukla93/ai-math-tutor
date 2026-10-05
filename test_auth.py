# test_auth.py
import sqlite3
import auth_db

auth_db.init_db()
conn = sqlite3.connect("users.db")
cur = conn.cursor()
cur.execute("SELECT id, name, email, password_hash, class_level FROM users")
rows = cur.fetchall()

print(f"Total registered users: {len(rows)}")
for r in rows:
    is_bcrypt = r[3].startswith("$2b$") or r[3].startswith("$2a$")
    print(f"ID: {r[0]} | Name: {r[1]} | Email: {r[2]} | Class: {r[4]} | Bcrypt Hashed: {is_bcrypt}")

# Test authentication
ok, user, msg = auth_db.authenticate_user("ramanshukla2005@gmail.com", "naman123")
assert ok and user["name"] == "Naman Shukla", "Demo login failed!"
print("Demo login: PASS")

bad_ok, _, bad_msg = auth_db.authenticate_user("ramanshukla2005@gmail.com", "wrongpass")
assert not bad_ok, "Bad password should fail!"
print("Bad password rejection: PASS")

notfound_ok, _, notfound_msg = auth_db.authenticate_user("fake@user.com", "pass123")
assert not notfound_ok, "Unknown user should fail!"
print("Unknown user rejection: PASS")

print("ALL AUTH TESTS PASSED SUCCESSFULLY!")
