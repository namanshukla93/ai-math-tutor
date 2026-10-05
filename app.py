# app.py — AI Math Tutor
#
# Creator: Naman Shukla (ramanshukla2005@gmail.com)
# GitHub: https://github.com/namanshukla93/ai-math-tutor
#
# Features:
#   - Name: "AI Tutor" (Zero Streamlit branding, 100% bespoke identity)
#   - Dynamic User Identity: Logged-in username & ID appears across entire UI
#   - Real-time Streaming: Token-by-token streaming using st.write_stream & generate_content_stream
#   - Sidebar Multi-Session History: "➕ Start new chat" + list of recent chats with titles
#   - Multi-File Access: Images, PDFs, Text notes, Worksheets, Code
#   - Claude-Style Artifacts: Generate & download printable worksheets, cheat sheets & solution sets
#   - Dedicated "About" section: Creator details (Naman Shukla) & Product specification
#   - Profile Menu: Settings, Font Style, Problem Solved Notifications, Focus Stopwatch, Logout/Login

import time
import streamlit as st
from tutor_prompt import get_system_prompt
from utils import (
    load_api_key,
    get_gemini_response,
    get_gemini_stream,
    generate_parent_summary,
    extract_content_from_file,
    create_math_artifact,
    GENAI_AVAILABLE,
    GENAI_ERROR,
    GENAI_BACKEND,
)
from auth_db import (
    init_db,
    register_user,
    authenticate_user,
)

# Initialize SQLite database for users
init_db()


# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {
        "Chat 1": {
            "title": "Chat 1",
            "messages": [],
            "gemini_history": [],
        }
    }

if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = "Chat 1"

if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.chat_sessions["Chat 1"]["messages"]

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = st.session_state.chat_sessions["Chat 1"]["gemini_history"]

if "class_level" not in st.session_state:
    st.session_state.class_level = 5

if "artifacts" not in st.session_state:
    st.session_state.artifacts = []

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "💬 Chat"

# User Identity & Profile State (Authenticated via SQLite users.db)
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "font_style" not in st.session_state:
    st.session_state.font_style = "Modern Sans"

if "notify_solved" not in st.session_state:
    st.session_state.notify_solved = True

if "focus_mode" not in st.session_state:
    st.session_state.focus_mode = False

if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""


# ─────────────────────────────────────────────
# DYNAMIC FONT & BESPOKE LUXURY DARK CSS
# (ZERO STREAMLIT BRANDING)
# ─────────────────────────────────────────────

font_css_map = {
    "Modern Sans": "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif",
    "Classic Editorial": "'Newsreader', Georgia, serif",
    "Clean Mono": "'JetBrains Mono', Consolas, monospace",
}
current_font_family = font_css_map.get(st.session_state.font_style, font_css_map["Modern Sans"])

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap');

/* ── Completely Hide All Streamlit Branding & Chrome ── */
#MainMenu {{visibility: hidden !important; display: none !important;}}
footer {{visibility: hidden !important; display: none !important;}}
header {{visibility: hidden !important; display: none !important;}}
[data-testid="stToolbar"] {{display: none !important; visibility: hidden !important;}}
[data-testid="stDecoration"] {{display: none !important;}}
[data-testid="stStatusWidget"] {{display: none !important;}}
.viewerBadge_container__1QSob, [class*="viewerBadge"] {{display: none !important;}}
[data-testid="manage-app-button"] {{display: none !important;}}
button[title="View app in Streamlit Community Cloud"] {{display: none !important;}}
a[href*="streamlit.io"] {{display: none !important;}}

/* ── Typography & Global Elements ── */
html, body, [class*="css"], .stApp {{
    font-family: {current_font_family} !important;
    color: #f1f1f4;
}}

/* ── Luxury Charcoal Background Canvas ── */
.stApp {{
    background-color: #131316 !important;
}}

/* ── Centered Main Viewport ── */
.block-container {{
    max-width: 820px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 7rem !important;
}}

/* ── Top Header ── */
.top-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 0.9rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}}
.top-brand {{
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.35rem;
    font-weight: 700;
    color: #fbfbfa;
    letter-spacing: -0.01em;
}}
.top-icon {{
    color: #da7756;
    font-size: 1.35rem;
}}
.top-user-pill {{
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 9999px;
    padding: 0.3rem 0.85rem;
}}
.user-badge-name {{
    color: #fbfbfa;
    font-weight: 600;
    font-size: 0.88rem;
}}
.top-badge {{
    background: rgba(218, 119, 86, 0.16);
    border: 1px solid rgba(218, 119, 86, 0.35);
    color: #e5987d;
    font-size: 0.8rem;
    font-weight: 600;
    padding: 0.15rem 0.65rem;
    border-radius: 9999px;
}}

/* ── Focus Mode Banner ── */
.focus-banner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(218, 119, 86, 0.12);
    border: 1px solid rgba(218, 119, 86, 0.3);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
    color: #fbfbfa;
    margin-bottom: 1.2rem;
}}

/* ── Welcome Screen ── */
.welcome-hero {{
    text-align: center;
    padding: 2.8rem 1rem 1.6rem 1rem;
}}
.welcome-icon {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 58px;
    height: 58px;
    border-radius: 50%;
    background: rgba(218, 119, 86, 0.14);
    border: 1.5px solid rgba(218, 119, 86, 0.35);
    color: #da7756;
    font-size: 1.85rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 4px 20px rgba(218, 119, 86, 0.2);
}}
.welcome-title {{
    font-family: 'Newsreader', serif;
    font-size: 2.3rem;
    font-weight: 500;
    color: #fbfbfa;
    margin-bottom: 0.5rem;
    letter-spacing: -0.01em;
}}
.welcome-sub {{
    font-size: 1rem;
    color: #a1a1aa;
    max-width: 560px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
}}

/* ── Buttons ── */
.stButton > button {{
    background: #1c1c22 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f4f4f5 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background: #272730 !important;
    border-color: #da7756 !important;
    color: #ffffff !important;
    transform: translateY(-1px);
}}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 0 !important;
    margin-bottom: 0.4rem !important;
}}

/* User Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    display: flex;
    justify-content: flex-end;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div {{
    background: #23232c !important;
    border-radius: 18px !important;
    padding: 0.9rem 1.35rem !important;
    max-width: 85%;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}}

/* Assistant (AI Tutor) Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div {{
    background: #191920 !important;
    border-radius: 18px !important;
    padding: 1.3rem 1.6rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
}}

/* Typography inside chat */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{
    color: #f4f4f5 !important;
    font-size: 1.02rem !important;
    line-height: 1.75 !important;
}}
[data-testid="stChatMessage"] strong {{
    color: #e5987d !important;
    font-weight: 700;
}}
[data-testid="stChatMessage"] code {{
    background: #121216 !important;
    color: #f59e0b !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── KaTeX Math Formula Highlight ── */
.katex, .katex * {{
    color: #fbfbfa !important;
    font-size: 1.08em !important;
}}
.katex-display {{
    background: rgba(218, 119, 86, 0.08) !important;
    border-left: 3px solid #da7756 !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin: 0.85rem 0 !important;
}}

/* ── Artifact & Card Container ── */
.artifact-box {{
    background: #191920;
    border: 1.5px solid rgba(218, 119, 86, 0.35);
    border-radius: 14px;
    padding: 1.25rem 1.45rem;
    margin: 1rem 0;
}}
.artifact-box-title {{
    font-size: 1.08rem;
    font-weight: 700;
    color: #fbfbfa;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.35rem;
}}
.artifact-box-desc {{
    font-size: 0.88rem;
    color: #a1a1aa;
    margin-bottom: 0.9rem;
    line-height: 1.6;
}}

/* ── About Section Cards ── */
.about-hero {{
    background: linear-gradient(135deg, #231f20 0%, #17171c 100%);
    border: 1px solid rgba(218, 119, 86, 0.35);
    border-radius: 18px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
}}
.about-badge {{
    display: inline-block;
    background: rgba(218, 119, 86, 0.18);
    color: #e5987d;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    margin-bottom: 0.6rem;
}}
.about-title {{
    font-size: 1.8rem;
    font-weight: 700;
    color: #fbfbfa;
    margin-bottom: 0.4rem;
}}
.about-sub {{
    font-size: 0.98rem;
    color: #d4d4d8;
    line-height: 1.65;
}}
.profile-card {{
    background: #191920;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
}}

/* ── Attached File Chip ── */
.file-chip {{
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(218, 119, 86, 0.14);
    border: 1px solid rgba(218, 119, 86, 0.35);
    border-radius: 10px;
    padding: 0.4rem 0.85rem;
    color: #fbfbfa;
    font-size: 0.88rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
}}

/* ── Floating Prompt Bar ── */
[data-testid="stChatInput"] {{
    background: #1c1c24 !important;
    border: 1.5px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45) !important;
    transition: all 0.25s ease;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: #da7756 !important;
    box-shadow: 0 0 0 3px rgba(218, 119, 86, 0.3) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: #ffffff !important;
    font-size: 1.02rem !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: #71717a !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background-color: #0e0e11 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}}
[data-testid="stSidebar"] * {{
    color: #d4d4d8 !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #fbfbfa !important;
}}

/* ── Download Button Styling ── */
.stDownloadButton > button {{
    background: linear-gradient(135deg, #da7756 0%, #c86544 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# LOAD API KEY (once per session)
# ─────────────────────────────────────────────

@st.cache_resource
def get_api_key():
    """Load API key from .env (locally) or st.secrets (Streamlit Cloud)."""
    try:
        return load_api_key(), None
    except ValueError as e:
        return None, str(e)


api_key, key_error = get_api_key()


# ─────────────────────────────────────────────
# HELPER: Message and Session Sync
# ─────────────────────────────────────────────

def add_message(role: str, content: str, image=None, file_meta=None):
    """Save message for display and Gemini context."""
    author = st.session_state.user_name if role == "user" else "AI Tutor"
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "image": image,
        "file_meta": file_meta,
        "author": author,
    })
    gemini_role = "model" if role == "assistant" else "user"
    st.session_state.gemini_history.append({
        "role": gemini_role,
        "parts": [content],
    })
    # Sync with active chat session
    sid = st.session_state.active_session_id
    if sid in st.session_state.chat_sessions:
        st.session_state.chat_sessions[sid]["messages"] = st.session_state.messages
        st.session_state.chat_sessions[sid]["gemini_history"] = st.session_state.gemini_history


def send_to_tutor(user_text: str, image=None, file_meta=None):
    """Send user query to Gemini, receives worked solution + similar practice."""
    add_message("user", user_text, image=image, file_meta=file_meta)

    system_prompt = get_system_prompt(st.session_state.class_level)

    with st.spinner("AI Tutor is analyzing & drafting solution... 📐"):
        reply = get_gemini_response(
            api_key=api_key,
            system_prompt=system_prompt,
            chat_history=st.session_state.gemini_history[:-1],
            user_message=user_text,
        )

    add_message("assistant", reply)

    # Auto-rename active chat session title if default
    sid = st.session_state.active_session_id
    if sid in st.session_state.chat_sessions:
        if st.session_state.chat_sessions[sid]["title"].startswith("Chat "):
            st.session_state.chat_sessions[sid]["title"] = user_text[:24] + ("..." if len(user_text) > 24 else "")

    if st.session_state.notify_solved:
        st.toast("🎯 Solution & practice problem prepared!", icon="⭐")


# ─────────────────────────────────────────────
# AUTHENTICATION GATEWAY (LOGIN / SIGN UP SCREEN)
# ─────────────────────────────────────────────

if not st.session_state.is_logged_in:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 68px; height: 68px; border-radius: 20px; background: rgba(217, 119, 87, 0.15); border: 1px solid rgba(217, 119, 87, 0.4); font-size: 34px; margin-bottom: 1.1rem; box-shadow: 0 10px 30px rgba(217, 119, 87, 0.25);">📐</div>
            <h1 style="font-size: 2.3rem; font-weight: 800; color: #f5f5f7; margin: 0; letter-spacing: -0.03em;">AI Math Tutor</h1>
            <p style="color: #9c9ca4; font-size: 1.05rem; margin-top: 0.6rem; max-width: 480px; margin-left: auto; margin-right: auto; line-height: 1.5;">
                Master mathematics with step-by-step conceptual explanations, personalized practice problems, and your private workspace.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    auth_col1, auth_col2, auth_col3 = st.columns([1, 2.6, 1])
    with auth_col2:
        tab_login, tab_signup = st.tabs(["🔑 Log In", "✨ Create Account"])

        with tab_login:
            st.markdown("<p style='color: #8c8c96; font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 1rem;'>Enter your email and password to access your tutoring sessions.</p>", unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                login_email = st.text_input("Email Address", placeholder="name@example.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Sign In →", use_container_width=True, type="primary")

                if submit_login:
                    if not login_email.strip() or not login_password.strip():
                        st.error("⚠️ Please enter both your email and password.")
                    else:
                        success, user_data, msg = authenticate_user(login_email, login_password)
                        if success and user_data:
                            st.session_state.is_logged_in = True
                            st.session_state.user_name = user_data["name"]
                            st.session_state.user_email = user_data["email"]
                            st.session_state.class_level = user_data.get("class_level", 8)
                            st.session_state.user_id = user_data["id"]
                            st.success(f"✅ Welcome back, {user_data['name']}! Loading workspace...")
                            time.sleep(0.3)
                            st.rerun()
                        else:
                            st.error(f"❌ {msg}")

            st.markdown(
                """
                <div style="background: rgba(217, 119, 87, 0.08); border: 1px dashed rgba(217, 119, 87, 0.35); border-radius: 12px; padding: 0.85rem 1rem; margin-top: 1.2rem; font-size: 0.85rem; color: #e0947c;">
                    <b>💡 Demo Account:</b><br/>
                    Email: <code>ramanshukla2005@gmail.com</code> &nbsp;•&nbsp; Password: <code>naman123</code>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🚀 Fast Login as Naman Shukla", use_container_width=True, key="fast_demo_login"):
                success, user_data, msg = authenticate_user("ramanshukla2005@gmail.com", "naman123")
                if success and user_data:
                    st.session_state.is_logged_in = True
                    st.session_state.user_name = user_data["name"]
                    st.session_state.user_email = user_data["email"]
                    st.session_state.class_level = user_data.get("class_level", 10)
                    st.session_state.user_id = user_data["id"]
                    st.rerun()

        with tab_signup:
            st.markdown("<p style='color: #8c8c96; font-size: 0.9rem; margin-top: 0.5rem; margin-bottom: 1rem;'>Create a free account to track your math progress and worksheets.</p>", unsafe_allow_html=True)
            with st.form("signup_form", clear_on_submit=False):
                reg_name = st.text_input("Full Name", placeholder="e.g. Naman Shukla")
                reg_email = st.text_input("Email Address", placeholder="name@example.com")
                reg_class = st.selectbox("Select Your School Class:", options=list(range(1, 13)), index=7, help="Adjusts math difficulty and curriculum")
                reg_password = st.text_input("Create Password", type="password", placeholder="At least 6 characters")
                reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submit_signup = st.form_submit_button("Create Account ✨", use_container_width=True, type="primary")

                if submit_signup:
                    if not reg_name.strip():
                        st.error("⚠️ Please enter your full name.")
                    elif not reg_email.strip() or "@" not in reg_email or "." not in reg_email:
                        st.error("⚠️ Please enter a valid email address.")
                    elif len(reg_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters long.")
                    elif reg_password != reg_confirm:
                        st.error("⚠️ Passwords do not match. Please verify and try again.")
                    else:
                        created, reg_msg = register_user(reg_name, reg_email, reg_password, reg_class)
                        if created:
                            ok, udata, _ = authenticate_user(reg_email, reg_password)
                            if ok and udata:
                                st.session_state.is_logged_in = True
                                st.session_state.user_name = udata["name"]
                                st.session_state.user_email = udata["email"]
                                st.session_state.class_level = udata.get("class_level", reg_class)
                                st.session_state.user_id = udata["id"]
                                st.success("🎉 Account created successfully! Launching AI Tutor...")
                                time.sleep(0.4)
                                st.rerun()
                            else:
                                st.success(reg_msg)
                        else:
                            st.error(f"❌ {reg_msg}")

    # Stop execution: Ensure NO chat, projects, or tutor features are accessible while logged out!
    st.stop()


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION & PROFILE SETTINGS
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📐 AI Tutor")

    # 1. Start New Chat Button
    if st.button("➕ Start new chat", use_container_width=True, key="new_chat_btn"):
        new_sid = f"Chat {len(st.session_state.chat_sessions) + 1}"
        st.session_state.chat_sessions[new_sid] = {
            "title": new_sid,
            "messages": [],
            "gemini_history": [],
        }
        st.session_state.active_session_id = new_sid
        st.session_state.messages = st.session_state.chat_sessions[new_sid]["messages"]
        st.session_state.gemini_history = st.session_state.chat_sessions[new_sid]["gemini_history"]
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.session_state.active_nav = "💬 Chat"
        st.rerun()

    # 2. Recent Chats List (Multi-Session History)
    st.markdown("**📜 Recent Chats**")
    for sid, sdata in list(st.session_state.chat_sessions.items()):
        is_active = (sid == st.session_state.active_session_id)
        display_title = sdata.get("title", sid)
        col_c, col_d = st.columns([5, 1])
        with col_c:
            btn_text = f"👉 **{display_title}**" if is_active else f"💬 {display_title}"
            if st.button(btn_text, key=f"sbtn_{sid}", use_container_width=True):
                st.session_state.active_session_id = sid
                st.session_state.messages = sdata["messages"]
                st.session_state.gemini_history = sdata["gemini_history"]
                st.session_state.active_nav = "💬 Chat"
                st.rerun()
        with col_d:
            if len(st.session_state.chat_sessions) > 1:
                if st.button("✕", key=f"del_{sid}", help="Delete chat"):
                    del st.session_state.chat_sessions[sid]
                    if sid == st.session_state.active_session_id:
                        rem_id = list(st.session_state.chat_sessions.keys())[0]
                        st.session_state.active_session_id = rem_id
                        st.session_state.messages = st.session_state.chat_sessions[rem_id]["messages"]
                        st.session_state.gemini_history = st.session_state.chat_sessions[rem_id]["gemini_history"]
                    st.rerun()

    st.markdown("---")

    # 3. Main Navigation Tabs
    nav_options = ["💬 Chat", "📁 Projects", "💻 Code", "📄 Artifacts", "ℹ️ About"]
    cur_idx = nav_options.index(st.session_state.active_nav) if st.session_state.active_nav in nav_options else 0
    st.session_state.active_nav = st.radio(
        label="Navigation",
        options=nav_options,
        index=cur_idx,
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 4. Class Level Selector
    st.markdown("**🎓 Class Level**")
    new_class = st.selectbox(
        label="Select Class",
        options=list(range(1, 13)),
        index=st.session_state.class_level - 1,
        format_func=lambda x: f"Class {x}",
        label_visibility="collapsed",
    )
    if new_class != st.session_state.class_level:
        st.session_state.class_level = new_class
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.chat_sessions[st.session_state.active_session_id]["messages"] = []
        st.session_state.chat_sessions[st.session_state.active_session_id]["gemini_history"] = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.rerun()

    # 5. Quick Session Summary
    if st.button("📋 Session Summary", use_container_width=True):
        if key_error:
            st.error(key_error)
        elif not st.session_state.messages:
            st.warning("Chat first to generate a summary.")
        else:
            system_prompt = get_system_prompt(st.session_state.class_level)
            with st.spinner("Generating summary..."):
                summary = generate_parent_summary(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    chat_history=st.session_state.gemini_history,
                )
            st.session_state.summary_text = summary
            st.session_state.show_summary = True
            st.rerun()

    st.markdown("---")

    # 6. USER PROFILE MENU (Tap to edit username, ID, font, notifications, focus)
    user_status_label = f"👤 {st.session_state.user_name}" if st.session_state.is_logged_in else "👤 Guest (Click to Log In)"

    with st.popover(user_status_label, use_container_width=True):
        st.markdown("#### ⚙️ Profile & Settings")
        
        # User details inputs
        edit_name = st.text_input("Username:", value=st.session_state.user_name)
        edit_email = st.text_input("User Email / ID:", value=st.session_state.user_email)
        if edit_name != st.session_state.user_name or edit_email != st.session_state.user_email:
            st.session_state.user_name = edit_name.strip() if edit_name.strip() else "Student"
            st.session_state.user_email = edit_email.strip() if edit_email.strip() else "user@math.edu"
            st.rerun()

        st.divider()

        # A. Font Style Selector
        st.markdown("**🔤 Font Style**")
        selected_font = st.selectbox(
            "Change Reading Font:",
            options=["Modern Sans", "Classic Editorial", "Clean Mono"],
            index=["Modern Sans", "Classic Editorial", "Clean Mono"].index(st.session_state.font_style),
            label_visibility="collapsed",
        )
        if selected_font != st.session_state.font_style:
            st.session_state.font_style = selected_font
            st.rerun()

        st.divider()

        # B. Notification When Problem Solved
        st.markdown("**🔔 Notifications**")
        notif_val = st.toggle("Notify when problem solved", value=st.session_state.notify_solved)
        if notif_val != st.session_state.notify_solved:
            st.session_state.notify_solved = notif_val
            st.rerun()

        st.divider()

        # C. Time & Focus Mode
        st.markdown("**⏱️ Time & Focus**")
        elapsed_mins = int((time.time() - st.session_state.session_start_time) / 60)
        st.caption(f"Study Session Time: **{elapsed_mins} minutes**")

        focus_val = st.toggle("Focus Mode (Distraction-Free)", value=st.session_state.focus_mode)
        if focus_val != st.session_state.focus_mode:
            st.session_state.focus_mode = focus_val
            st.rerun()

        st.divider()

        # D. Logout Option
        if st.button("🚪 Log Out", use_container_width=True, key="popover_logout_btn"):
            st.session_state.is_logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.session_state.user_id = None
            st.session_state.messages = []
            st.session_state.gemini_history = []
            st.rerun()

    # Direct Sidebar Logout Button
    if st.button("🚪 Log Out", key="sidebar_logout_direct", use_container_width=True):
        st.session_state.is_logged_in = False
        st.session_state.user_name = ""
        st.session_state.user_email = ""
        st.session_state.user_id = None
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.rerun()


# ─────────────────────────────────────────────
# MAIN TOP HEADER WITH DYNAMIC USER IDENTITY
# ─────────────────────────────────────────────

st.markdown(
    f"""
    <div class="top-header">
        <div class="top-brand">
            <span class="top-icon">📐</span>
            <span>AI Tutor</span>
        </div>
        <div class="top-user-pill">
            <span class="user-badge-name">👤 {st.session_state.user_name}</span>
            <span class="top-badge">Class {st.session_state.class_level}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Focus Mode Banner
if st.session_state.focus_mode:
    elapsed_mins = int((time.time() - st.session_state.session_start_time) / 60)
    st.markdown(
        f"""
        <div class="focus-banner">
            <span>⏱️ <b>Focus Mode Active</b> • {st.session_state.user_name} is in deep study flow</span>
            <span>Study Time: <b>{elapsed_mins}m</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# SDK Availability Check
if not GENAI_AVAILABLE:
    st.warning(
        "⚠️ **Google GenAI SDK Setup Notice (Streamlit Cloud)**\n\n"
        f"*{GENAI_ERROR}*\n\n"
        "**To resolve this:**\n"
        "1. Click **Manage app** (bottom-right corner) → **⋮ (three dots)** → **Reboot app**.\n"
        "2. (If prompted in App Settings) set Python version to **3.11**."
    )

# API Key Error Check
if key_error:
    st.error(f"🔑 **API Key Missing:** {key_error}")
    st.info("Add `GEMINI_API_KEY` to your `.env` file locally or in Cloud Secrets.")
    st.stop()


# ─────────────────────────────────────────────
# VIEW 1: 💬 CHAT (Main Conversational Tutor with Streaming)
# ─────────────────────────────────────────────

if st.session_state.active_nav == "💬 Chat":

    # Welcome Screen
    if not st.session_state.messages:
        st.markdown(
            f"""
            <div class="welcome-hero">
                <div class="welcome-icon">📐</div>
                <div class="welcome-title">Welcome back, {st.session_state.user_name}!</div>
                <div class="welcome-sub">
                    What math problem would you like to master today?
                    Attach <b>photos, PDFs, or worksheets</b> below. I will explain the complete
                    detailed solution, and create a <b>similar practice problem</b> for you!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🍕 Explain Fractions with real-life examples", use_container_width=True):
                send_to_tutor(f"Explain fractions with simple real-life examples for Class {st.session_state.class_level}.")
                st.rerun()

            if st.button("📐 Solve 3x + 12 = 45 with detailed steps", use_container_width=True):
                send_to_tutor("Solve 3x + 12 = 45 with complete step-by-step working and a similar practice problem.")
                st.rerun()

        with col2:
            if st.button("📄 Generate a Practice Worksheet file for me", use_container_width=True):
                with st.spinner("Generating Practice Worksheet artifact..."):
                    fname, fcontent = create_math_artifact(
                        api_key=api_key,
                        topic="Fractions and Decimals" if st.session_state.class_level <= 6 else "Linear Equations",
                        class_level=st.session_state.class_level,
                        artifact_type="worksheet",
                    )
                st.session_state.artifacts.append({"name": fname, "content": fcontent, "type": "worksheet"})
                send_to_tutor(
                    f"I generated a practice worksheet file for you: **{fname}**! "
                    "Download it from the Artifacts section or click download below. Let's solve the first question together!"
                )
                st.rerun()

            if st.button("📎 What file formats can I attach?", use_container_width=True):
                send_to_tutor(
                    "What file formats can I upload here? Explain how you can read photos, PDFs, textbooks, and homework notes."
                )
                st.rerun()

    # Render Chat History
    for msg in st.session_state.messages:
        author_display = msg.get("author", st.session_state.user_name if msg["role"] == "user" else "AI Tutor")
        with st.chat_message(
            name=msg["role"],
            avatar="🧑‍🎓" if msg["role"] == "user" else "📐",
        ):
            st.caption(f"**{author_display}**")
            if msg.get("file_meta"):
                f_meta = msg["file_meta"]
                st.markdown(
                    f'<div class="file-chip">📎 Attached File: <b>{f_meta["name"]}</b> ({f_meta["type"]})</div>',
                    unsafe_allow_html=True,
                )
            if msg.get("image"):
                st.image(msg["image"], caption="📷 Attached Problem Image", width=340)

            st.markdown(msg["content"])

    # Parent Summary Display
    if st.session_state.show_summary and st.session_state.summary_text:
        st.markdown("---")
        st.markdown("### 📋 Parent Session Summary")
        st.markdown(
            f'<div class="artifact-box" style="border-color: #10b981;">{st.session_state.summary_text}</div>',
            unsafe_allow_html=True,
        )

    # Floating Prompt Bar with Multi-File Upload & Real-time Streaming
    chat_val = st.chat_input(
        placeholder=f"Ask any math doubt or attach photos, PDFs, worksheets...",
        accept_file=True,
        file_type=["png", "jpg", "jpeg", "webp", "pdf", "txt", "md", "csv", "py"],
    )

    if chat_val:
        user_text = ""
        uploaded_files = []

        if hasattr(chat_val, "text"):
            user_text = chat_val.text.strip()
        elif isinstance(chat_val, str):
            user_text = chat_val.strip()

        if hasattr(chat_val, "files") and chat_val.files:
            uploaded_files = chat_val.files

        file_meta = None
        img_payload = None
        full_query = user_text

        if uploaded_files:
            attached_file = uploaded_files[0]
            file_bytes = attached_file.read()
            file_name = attached_file.name
            mime_type = attached_file.type or ""
            ext = file_name.lower().split(".")[-1] if "." in file_name else ""

            with st.spinner(f"Reading and scanning {file_name}... 📄"):
                extracted_text = extract_content_from_file(
                    api_key=api_key,
                    file_bytes=file_bytes,
                    file_name=file_name,
                    mime_type=mime_type,
                )

            is_image = ext in ["png", "jpg", "jpeg", "webp", "bmp"]
            img_payload = file_bytes if is_image else None
            file_meta = {"name": file_name, "type": ext.upper() or "Document"}

            if user_text:
                full_query = (
                    f"{user_text}\n\n"
                    f"**Extracted Content from '{file_name}':**\n{extracted_text}\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )
            else:
                full_query = (
                    f"I attached a file: **{file_name}**\n\n"
                    f"**Extracted Math Problem(s):**\n{extracted_text}\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )

        if full_query:
            # 1. Display User Message Immediately
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.caption(f"**{st.session_state.user_name}**")
                if file_meta:
                    st.markdown(
                        f'<div class="file-chip">📎 Attached File: <b>{file_meta["name"]}</b> ({file_meta["type"]})</div>',
                        unsafe_allow_html=True,
                    )
                if img_payload:
                    st.image(img_payload, caption="📷 Attached Problem Image", width=340)
                st.markdown(user_text if user_text else f"Attached: {file_meta['name']}")

            add_message("user", full_query, image=img_payload, file_meta=file_meta)

            # 2. Stream Assistant Response in Real-Time
            with st.chat_message("assistant", avatar="📐"):
                st.caption("**AI Tutor**")
                system_prompt = get_system_prompt(st.session_state.class_level)
                stream_gen = get_gemini_stream(
                    api_key=api_key,
                    system_prompt=system_prompt,
                    chat_history=st.session_state.gemini_history[:-1],
                    user_message=full_query,
                )
                full_reply = st.write_stream(stream_gen)

            add_message("assistant", full_reply)

            # Auto-title chat session
            sid = st.session_state.active_session_id
            if sid in st.session_state.chat_sessions:
                if st.session_state.chat_sessions[sid]["title"].startswith("Chat "):
                    display_title = user_text if user_text else (file_meta["name"] if file_meta else "Math Problem")
                    st.session_state.chat_sessions[sid]["title"] = display_title[:24] + ("..." if len(display_title) > 24 else "")

            if st.session_state.notify_solved:
                st.toast("🎯 Solution & practice problem prepared!", icon="⭐")

            st.rerun()


# ─────────────────────────────────────────────
# VIEW 2: 📁 PROJECTS (Math Workspaces)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "📁 Projects":
    st.markdown("### 📁 Math Projects & Workspaces")
    st.caption("Organized study workspaces tailored for " + st.session_state.user_name + " (Class " + str(st.session_state.class_level) + ")")

    p1, p2 = st.columns(2)
    with p1:
        st.markdown(
            """
            <div class="artifact-box">
                <div class="artifact-box-title">📘 NCERT Curriculum Mastery</div>
                <div class="artifact-box-desc">Step-by-step solutions and exercise-by-exercise guided practice.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open NCERT Workspace", key="open_proj_1", use_container_width=True):
            send_to_tutor(f"Let's start the NCERT Curriculum Workspace for Class {st.session_state.class_level}. Give me the first key chapter concept and problem.")
            st.session_state.active_nav = "💬 Chat"
            st.rerun()

    with p2:
        st.markdown(
            """
            <div class="artifact-box">
                <div class="artifact-box-title">🏆 Exam & Olympiad Challenge</div>
                <div class="artifact-box-desc">Higher-order thinking questions (HOTS) and past exam problems.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Open Exam Challenge", key="open_proj_2", use_container_width=True):
            send_to_tutor(f"Give me a challenging exam/olympiad-level problem for Class {st.session_state.class_level}, solve it with detailed steps, and test me on a similar problem!")
            st.session_state.active_nav = "💬 Chat"
            st.rerun()


# ─────────────────────────────────────────────
# VIEW 3: 💻 CODE (Python Math Calculator & Solver)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "💻 Code":
    st.markdown("### 💻 Math Code & Formula Sandbox")
    st.caption("Verify math formulas and run Python calculations")

    code_input = st.text_area(
        "Enter math expression or Python code:",
        value="""# Calculate quadratic roots or evaluate formulas
import math

a, b, c = 1, -5, 6
discriminant = b**2 - 4*a*c
root1 = (-b + math.sqrt(discriminant)) / (2*a)
root2 = (-b - math.sqrt(discriminant)) / (2*a)
print(f"Roots of x^2 - 5x + 6 = 0 are: {root1}, {root2}")
""",
        height=180,
    )

    if st.button("▶️ Run & Verify Code", key="run_math_code"):
        try:
            import io
            import sys
            buffer = io.StringIO()
            sys_stdout = sys.stdout
            sys.stdout = buffer
            exec(code_input, {"math": __import__("math")})
            sys.stdout = sys_stdout
            out = buffer.getvalue()
            st.success("✅ Output:")
            st.code(out if out else "(Executed successfully with no printed output)")
        except Exception as e:
            st.error(f"Execution Error: {e}")


# ─────────────────────────────────────────────
# VIEW 4: 📄 ARTIFACTS (File Creation & Download)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "📄 Artifacts":
    st.markdown("### 📄 Created Files & Artifacts")
    st.caption("Generate printable practice worksheets, formula cheat sheets, and study sets.")

    with st.expander("✨ Create New Math File (Worksheet / Cheat Sheet)", expanded=True):
        topic_input = st.text_input("Math Topic:", placeholder="e.g. Linear Equations, Fractions, Trigonometry")
        art_type = st.selectbox(
            "File Type:",
            options=["worksheet", "cheat_sheet", "solution_set"],
            format_func=lambda x: {
                "worksheet": "📝 Printable Practice Worksheet (.md)",
                "cheat_sheet": "⚡ Formula Cheat Sheet (.md)",
                "solution_set": "📘 Master Solved Set (.md)",
            }[x],
        )
        if st.button("Generate File Now", key="gen_art_page_btn", use_container_width=True):
            if not topic_input.strip():
                st.warning("Please enter a topic.")
            elif key_error:
                st.error(key_error)
            else:
                with st.spinner("Generating file... 📄"):
                    fname, fcontent = create_math_artifact(
                        api_key=api_key,
                        topic=topic_input.strip(),
                        class_level=st.session_state.class_level,
                        artifact_type=art_type,
                    )
                st.session_state.artifacts.append({"name": fname, "content": fcontent, "type": art_type})
                st.success(f"Generated {fname}!")
                st.rerun()

    if st.session_state.artifacts:
        st.markdown("#### 📥 Your Downloadable Files:")
        for idx, art in enumerate(reversed(st.session_state.artifacts)):
            st.markdown(
                f"""
                <div class="artifact-box">
                    <div class="artifact-box-title">📄 {art['name']}</div>
                    <div class="artifact-box-desc">Class {st.session_state.class_level} • Markdown Document</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.download_button(
                label=f"⬇️ Download {art['name']}",
                data=art["content"],
                file_name=art["name"],
                mime="text/markdown",
                key=f"dl_page_art_{idx}",
                use_container_width=True,
            )
    else:
        st.info("No files generated yet. Use the creator above to generate your first worksheet or cheat sheet!")


# ─────────────────────────────────────────────
# VIEW 5: ℹ️ ABOUT (Creator & Product Specification)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "ℹ️ About":
    st.markdown(
        """
        <div class="about-hero">
            <span class="about-badge">PRODUCT SPECIFICATION & ARCHITECTURE</span>
            <div class="about-title">📐 AI Math Tutor</div>
            <div class="about-sub">
                A state-of-the-art educational AI companion engineered to empower school students (Class 1–12) 
                with conceptual clarity, step-by-step problem walkthroughs, and proactive practice testing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 1. Creator Profile Card
    st.markdown(
        """
        <div class="profile-card">
            <h3 style="color:#fbfbfa; margin-top:0;">👨‍💻 About the Creator</h3>
            <p style="color:#d4d4d8; font-size:1rem; line-height:1.7;">
                <b>Creator & Developer:</b> Naman Shukla<br>
                <b>Email:</b> <a href="mailto:ramanshukla2005@gmail.com" style="color:#e5987d; text-decoration:none;">ramanshukla2005@gmail.com</a><br>
                <b>GitHub:</b> <a href="https://github.com/namanshukla93" target="_blank" style="color:#e5987d; text-decoration:none;">github.com/namanshukla93</a><br>
                <b>Project Repository:</b> <a href="https://github.com/namanshukla93/ai-math-tutor" target="_blank" style="color:#e5987d; text-decoration:none;">github.com/namanshukla93/ai-math-tutor</a>
            </p>
            <p style="color:#a1a1aa; font-size:0.92rem; line-height:1.6;">
                Naman Shukla is an AI & Python software developer passionate about crafting high-impact, human-centric educational technologies. 
                AI Math Tutor was developed to eliminate math anxiety, making top-tier personalized tutoring accessible to every school student regardless of background.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. Product Architecture & Core Features
    st.markdown(
        """
        <div class="profile-card">
            <h3 style="color:#fbfbfa; margin-top:0;">⚡ Product Architecture & Highlights</h3>
            <ul style="color:#d4d4d8; font-size:0.95rem; line-height:1.8;">
                <li><b>Two-Step Pedagogical Engine:</b> Walk students through each calculation step conceptually, and then automatically synthesize a similar problem for active self-testing.</li>
                <li><b>Real-time Streaming Engine:</b> Token-by-token response streaming with <code>generate_content_stream</code> and <code>st.write_stream</code>.</li>
                <li><b>Multi-Session Chat History:</b> Manage multiple chat conversations with auto-titles, switching, and deletion directly from the sidebar.</li>
                <li><b>Universal Multimodal Perception:</b> Process images, PDF worksheets, and raw text files via Google Gemini Vision.</li>
                <li><b>Claude-Style Artifacts System:</b> On-demand creation of printable practice worksheets, formula cheat sheets, and solved problem sets downloadable as standard Markdown documents.</li>
                <li><b>Dynamic Grade Adaptation:</b> Adjust vocabulary, tone, and CBSE/NCERT curriculum benchmarks across 4 age bands (Class 1–3, 4–6, 7–10, 11–12).</li>
                <li><b>Bespoke Dark Aesthetic:</b> Distraction-free, responsive dark canvas with dynamic typography switching and zero platform watermarks.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
