# app.py — AI Tutor (Claude-Style Clean Interface with Projects, Code, Artifacts & Profile Settings)
#
# Highlights:
#   - Name: "AI Tutor" (Replaced Claude branding)
#   - Clean interface: Removed clutter, focused on Chat, Projects, Code, Artifacts
#   - Sidebar Navigation: Start new chat, Chats, Projects, Code, Artifacts
#   - Profile Menu (Click to open):
#       * Font Style selector (Modern Sans, Classic Editorial, Clean Mono)
#       * Notification on Problem Solved (celebration toast & chime)
#       * Time & Focus Mode (Study stopwatch & distraction-free mode)
#       * Logout / Login option
#   - Multi-File Scanning: Images (PNG/JPG), PDFs, Text, Worksheets, Code
#   - File Creation (Artifacts): Create & download printable worksheets, cheat sheets & solution files
#   - Teach-First (Detailed Solution) -> Auto-generated Similar Practice Question

import time
import streamlit as st
from tutor_prompt import get_system_prompt
from utils import (
    load_api_key,
    get_gemini_response,
    generate_parent_summary,
    extract_content_from_file,
    create_math_artifact,
)


# ─────────────────────────────────────────────
# PAGE CONFIGURATION
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Tutor",
    page_icon="📐",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

if "class_level" not in st.session_state:
    st.session_state.class_level = 5

if "artifacts" not in st.session_state:
    st.session_state.artifacts = []  # List of {name, content, type}

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "💬 Chat"

# Profile & Preferences Settings
if "font_style" not in st.session_state:
    st.session_state.font_style = "Modern Sans"  # "Modern Sans", "Classic Editorial", "Clean Mono"

if "notify_solved" not in st.session_state:
    st.session_state.notify_solved = True

if "focus_mode" not in st.session_state:
    st.session_state.focus_mode = False

if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = True

if "user_name" not in st.session_state:
    st.session_state.user_name = "Naman Shukla"

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""


# ─────────────────────────────────────────────
# DYNAMIC FONT & CLAUDE-STYLE WARM CSS
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

html, body, [class*="css"], .stApp {{
    font-family: {current_font_family} !important;
    color: #ececec;
}}

/* ── Claude Warm Dark Canvas ── */
.stApp {{
    background-color: #18181b !important;
}}

/* ── Centered Claude Reading Column ── */
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
}}
.top-icon {{
    color: #da7756;
    font-size: 1.35rem;
}}
.top-badge {{
    background: rgba(218, 119, 86, 0.15);
    border: 1px solid rgba(218, 119, 86, 0.35);
    color: #e5987d;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.25rem 0.8rem;
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
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: rgba(218, 119, 86, 0.14);
    border: 1.5px solid rgba(218, 119, 86, 0.3);
    color: #da7756;
    font-size: 1.8rem;
    margin-bottom: 0.9rem;
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

/* ── Suggestion Cards ── */
.stButton > button {{
    background: #232328 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #f4f4f5 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: all 0.2s ease !important;
}}
.stButton > button:hover {{
    background: #2e2e36 !important;
    border-color: #da7756 !important;
    color: #ffffff !important;
}}

/* ── Primary Terracotta Action Button ── */
.primary-btn button {{
    background: #da7756 !important;
    border: none !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(218, 119, 86, 0.3) !important;
}}
.primary-btn button:hover {{
    background: #c86544 !important;
    box-shadow: 0 6px 20px rgba(218, 119, 86, 0.45) !important;
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
    background: #27272f !important;
    border-radius: 18px !important;
    padding: 0.9rem 1.3rem !important;
    max-width: 85%;
    border: 1px solid rgba(255, 255, 255, 0.08);
}}

/* Assistant (AI Tutor) Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div {{
    background: #1f1f25 !important;
    border-radius: 18px !important;
    padding: 1.3rem 1.6rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
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
    background: #141416 !important;
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

/* ── Artifact Card (Downloadable File) ── */
.artifact-box {{
    background: #1c1c22;
    border: 1.5px solid rgba(218, 119, 86, 0.35);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
}}
.artifact-box-title {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #fbfbfa;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.3rem;
}}
.artifact-box-desc {{
    font-size: 0.88rem;
    color: #a1a1aa;
    margin-bottom: 0.9rem;
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

/* ── Claude Floating Prompt Bar ── */
[data-testid="stChatInput"] {{
    background: #23232a !important;
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
    background-color: #121215 !important;
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
# HELPER: Send to Tutor
# ─────────────────────────────────────────────

def add_message(role: str, content: str, image=None, file_meta=None):
    """Save message for display and Gemini context."""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "image": image,
        "file_meta": file_meta,
    })
    gemini_role = "model" if role == "assistant" else "user"
    st.session_state.gemini_history.append({
        "role": gemini_role,
        "parts": [content],
    })


def send_to_tutor(user_text: str, image=None, file_meta=None):
    """Send user query to Gemini, receives worked solution + similar practice."""
    add_message("user", user_text, image=image, file_meta=file_meta)

    system_prompt = get_system_prompt(st.session_state.class_level)

    with st.spinner("AI Tutor is thinking & drafting solution... 📐"):
        reply = get_gemini_response(
            api_key=api_key,
            system_prompt=system_prompt,
            chat_history=st.session_state.gemini_history[:-1],
            user_message=user_text,
        )

    add_message("assistant", reply)

    # Trigger celebration notification if enabled
    if st.session_state.notify_solved:
        st.toast("🎯 Detailed solution & practice problem prepared!", icon="⭐")


# ─────────────────────────────────────────────
# SIDEBAR (Claude-Style Clean Navigation + Profile Menu)
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📐 AI Tutor")

    # 1. Start New Chat Button (Prominent)
    col_new, _ = st.columns([1, 0.01])
    with col_new:
        if st.button("➕ Start new chat", use_container_width=True, key="new_chat_btn"):
            st.session_state.messages = []
            st.session_state.gemini_history = []
            st.session_state.show_summary = False
            st.session_state.summary_text = ""
            st.session_state.active_nav = "💬 Chat"
            st.rerun()

    st.markdown("")

    # 2. Main Navigation Tabs (Chat, Projects, Code, Artifacts)
    st.session_state.active_nav = st.radio(
        label="Navigation",
        options=["💬 Chat", "📁 Projects", "💻 Code", "📄 Artifacts"],
        index=["💬 Chat", "📁 Projects", "💻 Code", "📄 Artifacts"].index(st.session_state.active_nav),
        label_visibility="collapsed",
    )

    st.markdown("---")

    # 3. Class Level Selector
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
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.rerun()

    # 4. Quick Session Parent Summary
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

    # 5. USER PROFILE MENU (Tap to open Settings, Font, Notification, Time & Focus, Logout)
    user_status_label = f"👤 {st.session_state.user_name}" if st.session_state.is_logged_in else "👤 Guest (Click to Log In)"

    with st.popover(user_status_label, use_container_width=True):
        st.markdown(f"#### ⚙️ Settings & Profile")
        if st.session_state.is_logged_in:
            st.caption(f"Signed in as **{st.session_state.user_name}**")
        else:
            st.caption("You are currently logged out.")

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

        # D. Logout / Login Option
        if st.session_state.is_logged_in:
            if st.button("🚪 Log Out", use_container_width=True):
                st.session_state.is_logged_in = False
                st.session_state.user_name = "Guest"
                st.rerun()
        else:
            login_name = st.text_input("Enter Student Name:", value="Naman Shukla")
            if st.button("🔑 Log In", use_container_width=True):
                st.session_state.is_logged_in = True
                st.session_state.user_name = login_name.strip() if login_name.strip() else "Student"
                st.rerun()


# ─────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────

# Clean Top Header
st.markdown(
    f"""
    <div class="top-header">
        <div class="top-brand">
            <span class="top-icon">📐</span>
            <span>AI Tutor</span>
        </div>
        <div class="top-badge">Class {st.session_state.class_level} • {st.session_state.active_nav}</div>
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
            <span>⏱️ <b>Focus Mode Active</b> • Stay in the flow</span>
            <span>Study Time: <b>{elapsed_mins}m</b></span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# API Key Error Check
if key_error:
    st.error(f"🔑 **API Key Missing:** {key_error}")
    st.info("Add `GEMINI_API_KEY` to your `.env` file locally or in Streamlit Cloud Secrets.")
    st.stop()


# ─────────────────────────────────────────────
# VIEW 1: 💬 CHAT (Main Conversational Tutor)
# ─────────────────────────────────────────────

if st.session_state.active_nav == "💬 Chat":

    # Welcome Screen (Shown when chat is empty)
    if not st.session_state.messages:
        st.markdown(
            f"""
            <div class="welcome-hero">
                <div class="welcome-icon">📐</div>
                <div class="welcome-title">How can I help you with math today?</div>
                <div class="welcome-sub">
                    Ask any question, or attach <b>images, PDFs, or worksheets</b> below.
                    I will explain the complete step-by-step solution, and create a
                    <b>similar practice problem</b> for you to solve!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # 4 Clean Suggestion Cards
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
        with st.chat_message(
            name=msg["role"],
            avatar="🧑‍🎓" if msg["role"] == "user" else "📐",
        ):
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

    # Floating Prompt Bar with Multi-File Upload
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
                full_prompt = (
                    f"{user_text}\n\n"
                    f"**Extracted Content from '{file_name}':**\n{extracted_text}\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )
            else:
                full_prompt = (
                    f"I attached a file: **{file_name}**\n\n"
                    f"**Extracted Math Problem(s):**\n{extracted_text}\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )

            send_to_tutor(full_prompt, image=img_payload, file_meta=file_meta)
            st.rerun()

        elif user_text:
            send_to_tutor(user_text)
            st.rerun()


# ─────────────────────────────────────────────
# VIEW 2: 📁 PROJECTS (Math Workspaces)
# ─────────────────────────────────────────────

elif st.session_state.active_nav == "📁 Projects":
    st.markdown("### 📁 Math Projects & Workspaces")
    st.caption("Organized study workspaces tailored for Class " + str(st.session_state.class_level))

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
    st.caption("Generate printable practice worksheets, formula cheat sheets, and study sets like Claude.")

    # Generator Card
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

    # List of all generated files with download buttons
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
