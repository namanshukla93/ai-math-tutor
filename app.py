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
    get_user_details,
    update_user_profile,
    change_user_password,
    get_user_chats,
    create_db_chat,
    update_db_chat_title,
    delete_db_chat,
    save_db_message,
    get_db_messages,
)

# Initialize SQLite database for users & persistent chat history
init_db()


# ─────────────────────────────────────────────
# PAGE CONFIGURATION & LOGO SYSTEM
# ─────────────────────────────────────────────

def get_starburst_logo(size=26, color="#D97757"):
    """Returns Claude-style warm coral starburst asterism SVG."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style="vertical-align: middle; display: inline-block; flex-shrink: 0;">
      <line x1="16" y1="3" x2="16" y2="8" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="16" y1="24" x2="16" y2="29" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="3" y1="16" x2="8" y2="16" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="24" y1="16" x2="29" y2="16" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="6.8" y1="6.8" x2="10.3" y2="10.3" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="21.7" y1="21.7" x2="25.2" y2="25.2" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="6.8" y1="25.2" x2="10.3" y2="21.7" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <line x1="21.7" y1="10.3" x2="25.2" y2="6.8" stroke="{color}" stroke-width="2.8" stroke-linecap="round"/>
      <circle cx="16" cy="16" r="3.2" fill="{color}"/>
    </svg>"""

st.set_page_config(
    page_title="AI Tutor",
    page_icon="✴️",
    layout="wide",
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

/* ── Hide Streamlit Branding & Chrome while PRESERVING Sidebar Collapsing ── */
#MainMenu {{visibility: hidden !important; display: none !important;}}
footer {{visibility: hidden !important; display: none !important;}}
[data-testid="stToolbar"] {{display: none !important; visibility: hidden !important;}}
[data-testid="stDecoration"] {{display: none !important;}}
[data-testid="stStatusWidget"] {{display: none !important;}}
.viewerBadge_container__1QSob, [class*="viewerBadge"] {{display: none !important;}}
[data-testid="manage-app-button"] {{display: none !important;}}
button[title="View app in Streamlit Community Cloud"] {{display: none !important;}}
a[href*="streamlit.io"] {{display: none !important;}}

/* Keep header zero-height and transparent so it never covers content */
header[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0px !important;
    min-height: 0px !important;
    pointer-events: none !important;
    border: none !important;
}}

/* ── Collapsible Left Sidebar Controls (Screen se kinare / bring back) ── */
/* When sidebar is collapsed, show the toggle button in the top-left margin */
[data-testid="stSidebarCollapsedControl"] {{
    pointer-events: auto !important;
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 14px !important;
    left: 14px !important;
    z-index: 100000 !important;
    background: #22201D !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    padding: 3px 6px !important;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.45) !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stSidebarCollapsedControl"]:hover {{
    background: #2E2C28 !important;
    border-color: #D97757 !important;
}}
[data-testid="stSidebarCollapsedControl"] button {{
    color: #ECE6DD !important;
}}

/* Sidebar Collapse button inside the open sidebar */
[data-testid="stSidebarCollapseButton"] {{
    visibility: visible !important;
}}
[data-testid="stSidebarCollapseButton"] button {{
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: #9C978D !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stSidebarCollapseButton"] button:hover {{
    background: #22201D !important;
    color: #ECE6DD !important;
    border-color: rgba(255, 255, 255, 0.1) !important;
}}

/* ── Global Canvas & Typography ── */
html, body, [class*="css"], .stApp {{
    font-family: {current_font_family} !important;
    color: #ECE6DD !important;
}}
.stApp {{
    background-color: #18181A !important;
}}

/* Centered Main Viewport */
.block-container {{
    max-width: 840px !important;
    padding-top: 0.8rem !important;
    padding-bottom: 6rem !important;
}}

/* ── Top Bar in Main Canvas ── */
.claude-top-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.2rem 0 1rem 0;
    margin-bottom: 1.2rem;
}}
.claude-top-right {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-left: auto;
}}
.claude-plan-text {{
    font-size: 0.84rem;
    color: #8E8B85;
    font-weight: 500;
}}
.claude-upgrade-link {{
    color: #D97757;
    text-decoration: none;
    font-weight: 600;
    margin-left: 4px;
}}
.claude-upgrade-link:hover {{
    text-decoration: underline;
}}
.claude-ghost-avatar {{
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    color: #C5C2BB;
}}

/* ── Claude Center Hero Greeting ── */
.claude-hero-container {{
    text-align: center;
    padding: 2.2rem 0.5rem 1.2rem 0.5rem;
}}
.claude-hero-title {{
    font-family: 'Newsreader', Georgia, serif;
    font-size: 2.85rem;
    font-weight: 400;
    color: #ECE6DD;
    letter-spacing: -0.015em;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin-bottom: 2rem;
}}

/* ── Claude Prompt Mockup Card ── */
.claude-prompt-card {{
    background: #22201D;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 1.15rem 1.4rem 1rem 1.4rem;
    text-align: left;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    margin-bottom: 1.2rem;
}}
.claude-prompt-placeholder {{
    color: #8E8B85;
    font-size: 1.05rem;
    padding-bottom: 2rem;
    user-select: none;
}}
.claude-prompt-footer {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding-top: 0.75rem;
}}
.claude-prompt-left {{
    display: flex;
    align-items: center;
    gap: 8px;
}}
.claude-tool-btn {{
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.08);
    color: #ECE6DD;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 600;
}}
.claude-pill-active {{
    background: #2E2C28;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 9999px;
    padding: 0.2rem 0.75rem;
    font-size: 0.82rem;
    font-weight: 600;
    color: #ECE6DD;
}}
.claude-pill-subtle {{
    color: #8E8B85;
    font-size: 0.82rem;
    padding: 0.2rem 0.4rem;
}}
.claude-prompt-right {{
    display: flex;
    align-items: center;
    gap: 12px;
}}
.claude-model-badge {{
    color: #8E8B85;
    font-size: 0.82rem;
}}
.claude-tool-icon {{
    font-size: 0.95rem;
    color: #8E8B85;
}}

/* ── Claude Quick Action Pills (Buttons) ── */
div[data-testid="column"] .stButton > button {{
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    border-radius: 9999px !important;
    color: #C5C2BB !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.35rem 0.8rem !important;
    transition: all 0.2s ease !important;
}}
div[data-testid="column"] .stButton > button:hover {{
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: rgba(255, 255, 255, 0.18) !important;
    color: #FFFFFF !important;
    transform: translateY(-1px);
}}

/* ── Sidebar Styling ── */
[data-testid="stSidebar"] {{
    background-color: #131315 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}}
[data-testid="stSidebar"] * {{
    color: #C5C2BB !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: #ECE6DD !important;
}}

/* Sidebar New Button */
[data-testid="stSidebar"] .stButton > button {{
    background: #22201D !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #ECE6DD !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: #2D2B27 !important;
    border-color: #D97757 !important;
    color: #FFFFFF !important;
}}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {{
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 0 !important;
    margin-bottom: 0.4rem !important;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {{
    display: flex;
    justify-content: flex-end;
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div {{
    background: #242220 !important;
    border-radius: 18px !important;
    padding: 0.9rem 1.35rem !important;
    max-width: 85%;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div {{
    background: #1C1B19 !important;
    border-radius: 18px !important;
    padding: 1.3rem 1.6rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.3);
}}
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {{
    color: #ECE6DD !important;
    font-size: 1.02rem !important;
    line-height: 1.75 !important;
}}
[data-testid="stChatMessage"] strong {{
    color: #E29278 !important;
    font-weight: 700;
}}
[data-testid="stChatMessage"] code {{
    background: #121214 !important;
    color: #F59E0B !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}}

/* ── KaTeX Formulas ── */
.katex, .katex * {{
    color: #ECE6DD !important;
    font-size: 1.08em !important;
}}
.katex-display {{
    background: rgba(217, 119, 87, 0.08) !important;
    border-left: 3px solid #D97757 !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin: 0.85rem 0 !important;
}}

/* ── Floating Prompt Input ── */
[data-testid="stChatInput"] {{
    background: #22201D !important;
    border: 1.5px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45) !important;
    transition: all 0.25s ease;
}}
[data-testid="stChatInput"]:focus-within {{
    border-color: #D97757 !important;
    box-shadow: 0 0 0 3px rgba(217, 119, 87, 0.3) !important;
}}
[data-testid="stChatInput"] textarea {{
    color: #ECE6DD !important;
    font-size: 1.02rem !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{
    color: #8E8B85 !important;
}}

/* ── Artifact & Card Container ── */
.artifact-box {{
    background: #1E1D1B;
    border: 1.5px solid rgba(217, 119, 87, 0.35);
    border-radius: 14px;
    padding: 1.25rem 1.45rem;
    margin: 1rem 0;
}}
.artifact-box-title {{
    font-size: 1.08rem;
    font-weight: 700;
    color: #ECE6DD;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.35rem;
}}
.artifact-box-desc {{
    font-size: 0.88rem;
    color: #9C978D;
    margin-bottom: 0.9rem;
    line-height: 1.6;
}}

/* ── Focus Banner ── */
.focus-banner {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: rgba(217, 119, 87, 0.12);
    border: 1px solid rgba(217, 119, 87, 0.3);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
    color: #ECE6DD;
    margin-bottom: 1.2rem;
}}

/* ── Download Button Styling ── */
.stDownloadButton > button {{
    background: linear-gradient(135deg, #D97757 0%, #C86544 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
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
# HELPER: Message and Session Sync (SQLite Persistent)
# ─────────────────────────────────────────────

def load_user_sessions(user_id: int):
    """Loads all saved chat sessions from SQLite database for the user."""
    db_chats = get_user_chats(user_id)
    st.session_state.chat_sessions = {}
    if db_chats:
        for c in db_chats:
            st.session_state.chat_sessions[c["id"]] = {
                "title": c["title"],
                "created_at": c.get("created_at", ""),
                "updated_at": c.get("updated_at", ""),
                "messages": [],
                "gemini_history": [],
                "loaded": False,
            }
        first_cid = db_chats[0]["id"]
    else:
        first_cid = f"chat_{user_id}_{int(time.time())}"
        create_db_chat(user_id, first_cid, "New Chat")
        st.session_state.chat_sessions[first_cid] = {
            "title": "New Chat",
            "created_at": "Just now",
            "updated_at": "Just now",
            "messages": [],
            "gemini_history": [],
            "loaded": True,
        }

    st.session_state.active_session_id = first_cid
    # Load messages for the active session
    msgs = get_db_messages(first_cid, user_id)
    st.session_state.messages = msgs
    st.session_state.gemini_history = [
        {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
        for m in msgs
    ]
    st.session_state.chat_sessions[first_cid]["messages"] = st.session_state.messages
    st.session_state.chat_sessions[first_cid]["gemini_history"] = st.session_state.gemini_history
    st.session_state.chat_sessions[first_cid]["loaded"] = True


def add_message(role: str, content: str, image=None, file_meta=None):
    """Save message for display, Gemini context, and SQLite persistent history."""
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
    # Sync with active chat session in session state
    sid = st.session_state.active_session_id
    if sid in st.session_state.chat_sessions:
        st.session_state.chat_sessions[sid]["messages"] = st.session_state.messages
        st.session_state.chat_sessions[sid]["gemini_history"] = st.session_state.gemini_history

    # Persist message to SQLite users.db
    uid = st.session_state.get("user_id")
    if uid and sid:
        save_db_message(sid, uid, role, content, author)


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

    # Auto-rename active chat session title in session state & SQLite
    sid = st.session_state.active_session_id
    uid = st.session_state.get("user_id")
    if sid in st.session_state.chat_sessions:
        curr_t = st.session_state.chat_sessions[sid]["title"]
        if curr_t.startswith("Chat ") or curr_t == "New Chat":
            new_title = user_text[:28].strip() + ("..." if len(user_text) > 28 else "")
            st.session_state.chat_sessions[sid]["title"] = new_title
            if uid:
                update_db_chat_title(sid, uid, new_title)

    if st.session_state.notify_solved:
        st.toast("🎯 Solution & practice problem prepared!", icon="⭐")


# ─────────────────────────────────────────────
# AUTHENTICATION GATEWAY (LOGIN / SIGN UP SCREEN)
# ─────────────────────────────────────────────

if not st.session_state.is_logged_in:
    st.markdown(
        f"""
        <div style="text-align: center; margin-top: 1.5rem; margin-bottom: 2rem;">
            <div style="display: inline-flex; align-items: center; justify-content: center; width: 68px; height: 68px; border-radius: 20px; background: rgba(217, 119, 87, 0.12); border: 1px solid rgba(217, 119, 87, 0.35); margin-bottom: 1.1rem; box-shadow: 0 10px 30px rgba(217, 119, 87, 0.2);">
                {get_starburst_logo(size=38)}
            </div>
            <h1 style="font-family: 'Newsreader', Georgia, serif; font-size: 2.5rem; font-weight: 400; color: #ECE6DD; margin: 0; letter-spacing: -0.02em;">AI Tutor</h1>
            <p style="color: #9C978D; font-size: 1.05rem; margin-top: 0.6rem; max-width: 480px; margin-left: auto; margin-right: auto; line-height: 1.5;">
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
                            load_user_sessions(user_data["id"])
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
                    load_user_sessions(user_data["id"])
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
                                load_user_sessions(udata["id"])
                                st.success("🎉 Account created successfully! Launching AI Tutor...")
                                time.sleep(0.4)
                                st.rerun()
                            else:
                                st.success(reg_msg)
                        else:
                            st.error(f"❌ {reg_msg}")

    # Stop execution: Ensure NO chat, projects, or tutor features are accessible while logged out!
    st.stop()

# Ensure sessions are loaded if logged in
if st.session_state.is_logged_in and (not st.session_state.chat_sessions or not any(st.session_state.chat_sessions.values())):
    load_user_sessions(st.session_state.user_id)


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION & PROFILE SETTINGS
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION & CLAUDE LEFT PANEL
# ─────────────────────────────────────────────

with st.sidebar:
    # 1. Header with Asterism Starburst Logo
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.2rem 0 0.8rem 0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                {get_starburst_logo(size=22)}
                <span style="font-size: 1.15rem; font-weight: 700; color: #ECE6DD; letter-spacing: -0.01em;">AI Tutor</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    uid = st.session_state.get("user_id", 1)

    # 2. + New Button (Full-width rounded pill button)
    if st.button("➕ New", use_container_width=True, key="new_chat_btn"):
        new_sid = f"chat_{uid}_{int(time.time())}"
        create_db_chat(uid, new_sid, "New Chat")
        st.session_state.chat_sessions[new_sid] = {
            "title": "New Chat",
            "messages": [],
            "gemini_history": [],
            "loaded": True,
        }
        st.session_state.active_session_id = new_sid
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.session_state.active_nav = "💬 Chat"
        st.rerun()

    # 3. Primary Navigation Items (Matching Claude Sidebar)
    if st.button("📁 Projects", key="side_nav_projects", use_container_width=True):
        st.session_state.active_nav = "📁 Projects"
        st.rerun()

    if st.button("🗂️ Artifacts", key="side_nav_artifacts", use_container_width=True):
        st.session_state.active_nav = "📄 Artifacts"
        st.rerun()

    col_nav_code, col_nav_upg = st.columns([3.8, 1.4])
    with col_nav_code:
        if st.button("💻 Code", key="side_nav_code", use_container_width=True):
            st.session_state.active_nav = "💻 Code"
            st.rerun()
    with col_nav_upg:
        st.markdown(
            "<div style='padding-top: 7px;'><span style='background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: #8E8B85; font-size: 0.72rem; padding: 2px 7px; border-radius: 9999px; font-weight: 600;'>Upgrade</span></div>",
            unsafe_allow_html=True,
        )

    if st.button("🎛️ Customize", key="side_nav_customize", use_container_width=True):
        st.session_state.active_nav = "ℹ️ About"
        st.rerun()

    # 4. Chats and Tasks Section
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 1.2rem; margin-bottom: 0.45rem; padding: 0 4px;">
            <span style="font-size: 0.76rem; font-weight: 600; color: #787570; text-transform: uppercase; letter-spacing: 0.05em;">Chats and tasks</span>
            <span style="font-size: 0.85rem; color: #787570; cursor: pointer;" title="Filter">⫶⫶</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for sid, sdata in list(st.session_state.chat_sessions.items()):
        is_active = (sid == st.session_state.active_session_id)
        display_title = sdata.get("title", "Chat")
        col_c, col_d = st.columns([5, 1])
        with col_c:
            btn_text = f"◦ **{display_title}**" if is_active else f"◦ {display_title}"
            if st.button(btn_text, key=f"sbtn_{sid}", use_container_width=True):
                if not sdata.get("loaded", False):
                    msgs = get_db_messages(sid, uid)
                    sdata["messages"] = msgs
                    sdata["gemini_history"] = [
                        {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                        for m in msgs
                    ]
                    sdata["loaded"] = True
                st.session_state.active_session_id = sid
                st.session_state.messages = sdata["messages"]
                st.session_state.gemini_history = sdata["gemini_history"]
                st.session_state.active_nav = "💬 Chat"
                st.rerun()
        with col_d:
            if len(st.session_state.chat_sessions) > 1:
                if st.button("✕", key=f"del_{sid}", help="Delete chat"):
                    delete_db_chat(sid, uid)
                    del st.session_state.chat_sessions[sid]
                    if sid == st.session_state.active_session_id:
                        rem_id = list(st.session_state.chat_sessions.keys())[0]
                        st.session_state.active_session_id = rem_id
                        if not st.session_state.chat_sessions[rem_id].get("loaded", False):
                            msgs = get_db_messages(rem_id, uid)
                            st.session_state.chat_sessions[rem_id]["messages"] = msgs
                            st.session_state.chat_sessions[rem_id]["gemini_history"] = [
                                {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                                for m in msgs
                            ]
                            st.session_state.chat_sessions[rem_id]["loaded"] = True
                        st.session_state.messages = st.session_state.chat_sessions[rem_id]["messages"]
                        st.session_state.gemini_history = st.session_state.chat_sessions[rem_id]["gemini_history"]
                    st.rerun()

    # 5. User Account Profile Popover (Bottom of Sidebar matching screenshot)
    initial = st.session_state.user_name[:1].upper() if st.session_state.user_name else "N"
    first_name = st.session_state.user_name.split()[0] if st.session_state.user_name else "Naman"
    st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
    with st.popover(f"👤 {initial}   {first_name} · Free  ▾", use_container_width=True):
        st.markdown(
            f"<div style='font-size: 0.82rem; color: #8E8B85; padding-bottom: 0.4rem; border-bottom: 1px solid rgba(255,255,255,0.08);'>{st.session_state.user_email}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="padding: 0.5rem 0; font-size: 0.88rem; line-height: 2.1; color: #ECE6DD;">
                <div>⚙️ <b>Settings</b> &nbsp; <span style='color: #787570; font-size: 0.78rem;'>Ctrl+Shift+,</span></div>
                <div>🌐 <b>Language:</b> English</div>
                <div>❓ <b>Get help</b></div>
                <div>⬆️ <b>Upgrade plan</b></div>
                <div>📱 <b>Get apps and extensions</b></div>
                <div>ℹ️ <b>Learn more &gt;</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        # Preferences Controls Inside Popover
        st.markdown("<b style='color: #ECE6DD; font-size: 0.85rem;'>Reading & Study Preferences</b>", unsafe_allow_html=True)
        selected_font = st.selectbox(
            "Reading Font:",
            options=["Modern Sans", "Classic Editorial", "Clean Mono"],
            index=["Modern Sans", "Classic Editorial", "Clean Mono"].index(st.session_state.font_style),
            key="pop_font_sel",
        )
        if selected_font != st.session_state.font_style:
            st.session_state.font_style = selected_font
            st.rerun()

        new_class = st.selectbox(
            "Academic Grade:",
            options=list(range(1, 13)),
            index=st.session_state.class_level - 1,
            format_func=lambda x: f"Class {x}",
            key="pop_class_sel",
        )
        if new_class != st.session_state.class_level:
            st.session_state.class_level = new_class
            update_user_profile(uid, st.session_state.user_name, new_class)
            st.rerun()

        notif_val = st.toggle("Notify when problem solved", value=st.session_state.notify_solved, key="pop_notif_tog")
        if notif_val != st.session_state.notify_solved:
            st.session_state.notify_solved = notif_val
            st.rerun()

        focus_val = st.toggle("Focus Mode (Distraction-Free)", value=st.session_state.focus_mode, key="pop_focus_tog")
        if focus_val != st.session_state.focus_mode:
            st.session_state.focus_mode = focus_val
            st.rerun()

        st.divider()

        col_pa, col_pl = st.columns(2)
        with col_pa:
            if st.button("👤 Account", key="pop_acc_btn", use_container_width=True):
                st.session_state.active_nav = "👤 Account Details"
                st.rerun()
        with col_pl:
            if st.button("🚪 Log out", key="pop_logout_btn", use_container_width=True):
                st.session_state.is_logged_in = False
                st.session_state.user_name = ""
                st.session_state.user_email = ""
                st.session_state.user_id = None
                st.session_state.messages = []
                st.session_state.gemini_history = []
                st.session_state.chat_sessions = {}
                st.rerun()


# ─────────────────────────────────────────────
# MAIN TOP BAR (Free plan · Upgrade & Ghost Avatar)
# ─────────────────────────────────────────────

st.markdown(
    """
    <div class="claude-top-bar">
        <div></div>
        <div class="claude-top-right">
            <span class="claude-plan-text">Free plan · <a href="#upgrade" class="claude-upgrade-link">Upgrade</a></span>
            <div class="claude-ghost-avatar">👻</div>
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

    # Welcome Screen / Center Hero Greeting (Matching Claude Reference Screenshot)
    if not st.session_state.messages:
        first_name = st.session_state.user_name.split()[0] if st.session_state.user_name else "there"
        st.markdown(
            f"""
            <div class="claude-hero-container">
                <div class="claude-hero-title">
                    {get_starburst_logo(size=36)}
                    <span>Let's solve, {first_name}</span>
                </div>
                <div class="claude-prompt-card">
                    <div class="claude-prompt-placeholder">How can I help you today?</div>
                    <div class="claude-prompt-footer">
                        <div class="claude-prompt-left">
                            <span class="claude-tool-btn">+</span>
                            <span class="claude-pill-active">Chat</span>
                            <span class="claude-pill-subtle">Step-by-Step</span>
                        </div>
                        <div class="claude-prompt-right">
                            <span class="claude-model-badge">AI Tutor 2.5 Flash</span>
                            <span class="claude-tool-icon">🎙️</span>
                            <span class="claude-tool-icon">〰️</span>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Quick Action Pill Chips (5 Buttons Underneath Prompt Box)
        col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
        with col_p1:
            if st.button("✏️ Step-by-Step", use_container_width=True, key="hero_step"):
                send_to_tutor(f"Solve this math problem with complete step-by-step reasoning and a similar practice problem for Class {st.session_state.class_level}.")
                st.rerun()
        with col_p2:
            if st.button("🎓 Learn", use_container_width=True, key="hero_learn"):
                send_to_tutor(f"Teach me a core math concept from Class {st.session_state.class_level} using simple intuition and real-world examples.")
                st.rerun()
        with col_p3:
            if st.button("</> Code", use_container_width=True, key="hero_code"):
                send_to_tutor("Write a clean Python script to visualize and solve a math algorithm with step-by-step comments.")
                st.rerun()
        with col_p4:
            if st.button("☕ Practice", use_container_width=True, key="hero_practice"):
                send_to_tutor(f"Give me 3 engaging math practice puzzles suited for Class {st.session_state.class_level} with progressive hints.")
                st.rerun()
        with col_p5:
            if st.button("💡 Tutor's choice", use_container_width=True, key="hero_choice"):
                send_to_tutor("Surprise me with a fascinating, real-world application of mathematics that connects to everyday life!")
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
# VIEW: 📜 CHAT HISTORY (Persistent SQLite Archive)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "📜 Chat History":
    uid = st.session_state.get("user_id")
    all_chats = get_user_chats(uid) if uid else []

    st.markdown("### 📜 Chat History & Past Tutoring Sessions")
    st.caption("Review, search, and resume your past math problems, step-by-step solutions, and practice sets.")

    top_c1, top_c2 = st.columns([3, 1])
    with top_c1:
        search_query = st.text_input("🔍 Search past topics & questions:", placeholder="e.g. Fractions, Trigonometry, Linear equations...", label_visibility="collapsed")
    with top_c2:
        if st.button("➕ Start New Chat", type="primary", use_container_width=True, key="hist_start_new_btn"):
            new_cid = f"chat_{uid}_{int(time.time())}"
            create_db_chat(uid, new_cid, "New Chat")
            st.session_state.chat_sessions[new_cid] = {
                "title": "New Chat",
                "created_at": "Just now",
                "updated_at": "Just now",
                "messages": [],
                "gemini_history": [],
                "loaded": True,
            }
            st.session_state.active_session_id = new_cid
            st.session_state.messages = []
            st.session_state.gemini_history = []
            st.session_state.active_nav = "💬 Chat"
            st.rerun()

    filtered_chats = [c for c in all_chats if not search_query.strip() or search_query.strip().lower() in c["title"].lower()]

    if not filtered_chats:
        st.info("No saved chat sessions found. Start a new chat to begin practicing!")
    else:
        for c in filtered_chats:
            cid = c["id"]
            ctitle = c["title"]
            c_msgs = get_db_messages(cid, uid)
            msg_count = len(c_msgs)
            last_active = c.get("updated_at", c.get("created_at", "Recently"))

            with st.container():
                st.markdown(
                    f"""
                    <div class="artifact-box" style="margin-bottom: 0.6rem;">
                        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                            <div>
                                <div class="artifact-box-title" style="font-size: 1.05rem;">💬 {ctitle}</div>
                                <div class="artifact-box-desc" style="margin-top: 0.3rem;">
                                    <span>⏱️ <b>{last_active}</b></span> &nbsp;•&nbsp; 
                                    <span>💬 <b>{msg_count}</b> messages</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                col_res, col_del = st.columns([4, 1])
                with col_res:
                    if st.button(f"Resume Chat: {ctitle[:30]} →", key=f"hist_resume_{cid}", use_container_width=True):
                        st.session_state.active_session_id = cid
                        st.session_state.messages = c_msgs
                        st.session_state.gemini_history = [
                            {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                            for m in c_msgs
                        ]
                        if cid in st.session_state.chat_sessions:
                            st.session_state.chat_sessions[cid]["messages"] = st.session_state.messages
                            st.session_state.chat_sessions[cid]["gemini_history"] = st.session_state.gemini_history
                            st.session_state.chat_sessions[cid]["loaded"] = True
                        st.session_state.active_nav = "💬 Chat"
                        st.rerun()
                with col_del:
                    if st.button("🗑️ Delete", key=f"hist_del_{cid}", use_container_width=True):
                        delete_db_chat(cid, uid)
                        if cid in st.session_state.chat_sessions:
                            del st.session_state.chat_sessions[cid]
                        if cid == st.session_state.active_session_id:
                            load_user_sessions(uid)
                        st.toast("Chat deleted permanently.")
                        st.rerun()


# ─────────────────────────────────────────────
# VIEW: 👤 ACCOUNT DETAILS (Profile, Grade & Security)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "👤 Account Details":
    uid = st.session_state.get("user_id")
    user_info = get_user_details(uid) if uid else None

    st.markdown("### 👤 Account Details & Preferences")
    st.caption("Manage your student profile, academic grade level, security password, and tutor preferences.")

    col_l, col_r = st.columns([1.1, 1.4])

    with col_l:
        # Profile Summary Card
        initials = (st.session_state.user_name[:2].upper() if st.session_state.user_name else "NS")
        member_since = user_info.get("created_at", "October 2026") if user_info else "October 2026"
        total_chats = user_info.get("total_chats", len(st.session_state.chat_sessions)) if user_info else 0
        total_questions = user_info.get("total_questions", 0) if user_info else 0

        st.markdown(
            f"""
            <div class="profile-card" style="text-align: center; padding: 2rem 1.2rem;">
                <div style="width: 72px; height: 72px; border-radius: 50%; background: linear-gradient(135deg, #da7756, #c86544); display: flex; align-items: center; justify-content: center; font-weight: 800; color: white; font-size: 1.8rem; margin: 0 auto 1rem auto; box-shadow: 0 8px 24px rgba(218, 119, 86, 0.3);">
                    {initials}
                </div>
                <h3 style="color: #fbfbfa; margin: 0 0 0.2rem 0; font-size: 1.4rem;">{st.session_state.user_name}</h3>
                <div style="color: #9c9ca4; font-size: 0.9rem; margin-bottom: 0.8rem;">{st.session_state.user_email}</div>
                <div style="display: inline-block; background: rgba(218, 119, 86, 0.15); border: 1px solid rgba(218, 119, 86, 0.4); border-radius: 20px; padding: 0.3rem 0.9rem; font-size: 0.82rem; font-weight: 600; color: #e5987d; margin-bottom: 1.5rem;">
                    🎓 Student Scholar • Class {st.session_state.class_level}
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; text-align: left; margin-top: 0.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08); padding-top: 1.2rem;">
                    <div style="background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 0.7rem;">
                        <div style="color: #8c8c96; font-size: 0.78rem;">Total Chats</div>
                        <div style="color: #fbfbfa; font-size: 1.2rem; font-weight: 700;">{total_chats}</div>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 0.7rem;">
                        <div style="color: #8c8c96; font-size: 0.78rem;">Questions Asked</div>
                        <div style="color: #fbfbfa; font-size: 1.2rem; font-weight: 700;">{total_questions}</div>
                    </div>
                </div>
                <div style="color: #8c8c96; font-size: 0.8rem; margin-top: 1rem;">
                    Member Since: <b>{member_since}</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_r:
        # Card 1: Edit Profile Details
        st.markdown("#### ✏️ Edit Profile Details")
        with st.form("edit_profile_form"):
            new_name = st.text_input("Full Name:", value=st.session_state.user_name)
            new_class_choice = st.selectbox(
                "School Class / Grade Level:",
                options=list(range(1, 13)),
                index=st.session_state.class_level - 1,
                format_func=lambda x: f"Class {x} (CBSE/NCERT)",
            )
            save_profile_btn = st.form_submit_button("💾 Save Profile Changes", type="primary", use_container_width=True)

            if save_profile_btn:
                if not new_name.strip():
                    st.error("Name cannot be empty.")
                else:
                    ok_p, msg_p = update_user_profile(uid, new_name, new_class_choice)
                    if ok_p:
                        st.session_state.user_name = new_name.strip()
                        st.session_state.class_level = new_class_choice
                        st.success("✅ Profile updated successfully!")
                        time.sleep(0.3)
                        st.rerun()
                    else:
                        st.error(f"❌ {msg_p}")

        st.markdown("---")

        # Card 2: Security & Password Update
        st.markdown("#### 🔒 Security & Password")
        with st.form("change_pwd_form"):
            current_pwd = st.text_input("Current Password:", type="password", placeholder="••••••••")
            new_pwd = st.text_input("New Password:", type="password", placeholder="Min 6 characters")
            confirm_new_pwd = st.text_input("Confirm New Password:", type="password", placeholder="Re-enter new password")
            save_pwd_btn = st.form_submit_button("🔑 Update Password", use_container_width=True)

            if save_pwd_btn:
                if not current_pwd or not new_pwd:
                    st.error("Please enter both current and new password.")
                elif len(new_pwd) < 6:
                    st.error("New password must be at least 6 characters.")
                elif new_pwd != confirm_new_pwd:
                    st.error("New passwords do not match.")
                else:
                    ok_w, msg_w = change_user_password(uid, current_pwd, new_pwd)
                    if ok_w:
                        st.success("✅ Password changed successfully! Plain text was never stored.")
                    else:
                        st.error(f"❌ {msg_w}")

        st.markdown("---")

        # Card 3: Account Sign Out
        if st.button("🚪 Log Out of AI Tutor", type="secondary", use_container_width=True, key="acc_details_logout"):
            st.session_state.is_logged_in = False
            st.session_state.user_name = ""
            st.session_state.user_email = ""
            st.session_state.user_id = None
            st.session_state.messages = []
            st.session_state.gemini_history = []
            st.session_state.chat_sessions = {}
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
