# app.py — Main Streamlit web application
#
# This file controls everything the student SEES and INTERACTS WITH.
# It does NOT contain any AI logic — that lives in utils.py and tutor_prompt.py.
#
# HOW STREAMLIT WORKS (important for interviews):
#   Every time the user clicks a button or types something, Streamlit re-runs
#   this entire script from top to bottom. So we use st.session_state (a
#   dictionary that persists between reruns) to remember the chat history,
#   the selected class, etc.

import streamlit as st
from tutor_prompt import get_system_prompt
from utils import load_api_key, get_gemini_response, generate_parent_summary, extract_math_from_image


# ─────────────────────────────────────────────
# PAGE CONFIGURATION (must be the very first Streamlit call)
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="AI Math Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CUSTOM CSS — High-contrast typography & premium modern aesthetics
# ─────────────────────────────────────────────

st.markdown("""
<style>
/* ── Fonts ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #f8fafc !important;
}

/* ── App background ─────────────────────────────── */
.stApp {
    background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0f172a 45%, #090d16 100%) !important;
    min-height: 100vh;
}

/* ── Typography & Global Text Visibility ─────────── */
p, span, li, label, div {
    color: #f1f5f9;
}
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em;
}

/* ── Main Title & Subtitle ───────────────────────── */
.main-title {
    font-size: 2.5rem;
    font-weight: 800;
    color: #ffffff;
    background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 40%, #60a5fa 70%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.2rem;
    line-height: 1.2;
}
.main-subtitle {
    font-size: 1.1rem;
    color: #cbd5e1 !important;
    margin-top: 0.2rem;
    margin-bottom: 1.2rem;
    font-weight: 500;
}
.badge-class {
    display: inline-block;
    background: rgba(99, 102, 241, 0.25);
    border: 1px solid rgba(129, 140, 248, 0.5);
    color: #c7d2fe !important;
    padding: 0.2rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-right: 0.5rem;
}

/* ── Quick Scan Problem Card (Main Page) ─────────── */
.scan-card {
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1.5px solid #4f46e5;
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.2);
}
.scan-card-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.15rem;
    font-weight: 700;
    color: #ffffff !important;
    margin-bottom: 0.35rem;
}
.scan-card-sub {
    font-size: 0.92rem;
    color: #94a3b8 !important;
    margin-bottom: 0.75rem;
}

/* ── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #0b0f19 !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #cbd5e1 !important;
    font-size: 0.95rem;
}

/* ── Sidebar Selectbox ───────────────────────────── */
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: #1e293b !important;
    border: 1.5px solid #4338ca !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 600;
}
div[data-baseweb="select"] * {
    color: #ffffff !important;
}
ul[role="listbox"] {
    background-color: #1e293b !important;
    border: 1px solid #4f46e5 !important;
}
ul[role="listbox"] li {
    color: #f8fafc !important;
}
ul[role="listbox"] li:hover {
    background-color: #312e81 !important;
}

/* ── Buttons ─────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
    border: 1px solid #818cf8 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #6366f1 0%, #7c3aed 100%) !important;
    border-color: #a5b4fc !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5) !important;
}

/* ── Chat Messages (High Contrast & Distinct Roles) ── */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    margin-bottom: 1rem !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25) !important;
}

/* Assistant (Tutor) message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]),
[data-testid="stChatMessage"]:nth-child(even) {
    background: #131b2e !important;
    border: 1.5px solid #334155 !important;
}

/* User (Student) message */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]),
[data-testid="stChatMessage"]:nth-child(odd) {
    background: linear-gradient(135deg, #1e1b4b 0%, #2e1065 100%) !important;
    border: 1.5px solid #6366f1 !important;
}

/* Text inside chat messages - ultra clear */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] div {
    color: #f8fafc !important;
    font-size: 1.05rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] strong {
    color: #fbbf24 !important; /* Gold highlight for keywords */
    font-weight: 700 !important;
}
[data-testid="stChatMessage"] code {
    background: #0f172a !important;
    color: #67e8f9 !important;
    border: 1px solid #334155 !important;
    padding: 0.15rem 0.45rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.95em !important;
}

/* ── KaTeX Math Formula Clarity ──────────────────── */
.katex, .katex * {
    color: #f8fafc !important;
    font-size: 1.1em !important;
}
.katex-display {
    background: rgba(99, 102, 241, 0.12) !important;
    border-left: 3px solid #818cf8 !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin: 0.75rem 0 !important;
}

/* ── Chat Input ──────────────────────────────────── */
[data-testid="stChatInput"] {
    border-radius: 14px !important;
    background: #1e293b !important;
    border: 2px solid #4f46e5 !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 3px rgba(129, 140, 248, 0.35) !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1.05rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
}

/* ── File Uploader (Scan Problem Widget) ─────────── */
[data-testid="stFileUploader"] {
    background: #131b2e !important;
    border: 2px dashed #6366f1 !important;
    border-radius: 14px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"] * {
    color: #e2e8f0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background: #312e81 !important;
    color: #ffffff !important;
    border: 1px solid #6366f1 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
[data-testid="stFileUploaderDropzone"] button:hover {
    background: #4338ca !important;
}

/* ── Welcome Box / Alerts ────────────────────────── */
[data-testid="stAlert"] {
    background: #1e293b !important;
    border: 1.5px solid #6366f1 !important;
    border-radius: 14px !important;
    padding: 1.2rem !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] li, [data-testid="stAlert"] span {
    color: #f1f5f9 !important;
    font-size: 1.02rem !important;
    line-height: 1.7 !important;
}

/* ── Expander ────────────────────────────────────── */
[data-testid="stExpander"] {
    background: #111827 !important;
    border: 1.5px solid #374151 !important;
    border-radius: 14px !important;
}
[data-testid="stExpander"] summary {
    color: #c7d2fe !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
}
[data-testid="stExpander"] summary:hover {
    color: #ffffff !important;
}

/* ── Text Input ──────────────────────────────────── */
.stTextInput > div > div > input {
    background: #1e293b !important;
    border: 1.5px solid #4f46e5 !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-size: 1.02rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.3) !important;
}

/* ── Disclaimer Box ──────────────────────────────── */
.disclaimer {
    background: rgba(245, 158, 11, 0.12);
    border-left: 4px solid #f59e0b;
    padding: 0.8rem 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #fef08a !important;
    margin-top: 1rem;
    line-height: 1.5;
}
.disclaimer b {
    color: #fbbf24 !important;
}

/* ── Summary Box ─────────────────────────────────── */
.summary-box {
    background: rgba(16, 185, 129, 0.12);
    border-left: 4px solid #10b981;
    padding: 1.2rem 1.4rem;
    border-radius: 12px;
    font-size: 1.02rem;
    color: #a7f3d0 !important;
    margin-top: 1rem;
    line-height: 1.8;
}

/* ── Scrollbars ──────────────────────────────────── */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #0f172a; }
::-webkit-scrollbar-thumb {
    background: #4f46e5;
    border-radius: 10px;
}
::-webkit-scrollbar-thumb:hover { background: #6366f1; }
</style>
""", unsafe_allow_html=True)



# ─────────────────────────────────────────────
# LOAD API KEY (once per session)
# ─────────────────────────────────────────────

# We use st.cache_resource so the key is loaded only once,
# not on every Streamlit rerun. This is a small performance win.
@st.cache_resource
def get_api_key():
    """Load the API key — cached so it only runs once per app session."""
    try:
        return load_api_key(), None  # (key, error)
    except ValueError as e:
        return None, str(e)


api_key, key_error = get_api_key()


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────
# st.session_state is like a dictionary that survives page reruns.
# We check "if key not in session_state" to initialize only once.

if "messages" not in st.session_state:
    st.session_state.messages = []       # List of {role, content} dicts for display

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = [] # List of {role, parts} dicts for Gemini API

if "class_level" not in st.session_state:
    st.session_state.class_level = 5     # Default to Class 5

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""

if "check_answer_mode" not in st.session_state:
    st.session_state.check_answer_mode = False

if "scanned_question" not in st.session_state:
    st.session_state.scanned_question = ""


# ─────────────────────────────────────────────
# HELPER: Add a message to both display history and Gemini history
# ─────────────────────────────────────────────

def add_message(role: str, content: str, image=None):
    """
    Saves a message to:
      1. st.session_state.messages       → used to DISPLAY the chat on screen
      2. st.session_state.gemini_history → sent to Gemini so it remembers context

    'role' must be "user" or "assistant" for display.
    Gemini expects "user" or "model" in its history format.
    'image' optionally holds the image bytes for scanned problems.
    """
    # For display
    st.session_state.messages.append({"role": role, "content": content, "image": image})

    # For Gemini API (it uses "model" instead of "assistant")
    gemini_role = "model" if role == "assistant" else "user"
    st.session_state.gemini_history.append({
        "role": gemini_role,
        "parts": [content],
    })


# ─────────────────────────────────────────────
# HELPER: Send a message to Gemini and get reply
# ─────────────────────────────────────────────

def send_to_tutor(user_text: str, image=None):
    """
    Takes the student's message, adds it to history, calls Gemini,
    and saves the tutor's reply. Shows a spinner while waiting.
    """
    add_message("user", user_text, image=image)

    system_prompt = get_system_prompt(st.session_state.class_level)

    with st.spinner("Tutor is thinking... 🤔"):
        reply = get_gemini_response(
            api_key=api_key,
            system_prompt=system_prompt,
            chat_history=st.session_state.gemini_history[:-1],  # exclude the message we just added
            user_message=user_text,
        )

    add_message("assistant", reply)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🧮 AI Math Tutor")
    st.markdown("*Your step-by-step math guide*")
    st.divider()

    # ── Class Selector ──────────────────────
    st.markdown("### 🎓 Select Your Class")
    new_class = st.selectbox(
        label="Class",
        options=list(range(1, 13)),
        index=st.session_state.class_level - 1,  # default to current class
        format_func=lambda x: f"Class {x}",
        label_visibility="collapsed",
    )

    # If the student changes their class, reset the conversation
    if new_class != st.session_state.class_level:
        st.session_state.class_level = new_class
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.session_state.check_answer_mode = False
        st.rerun()

    st.divider()

    # ── Practice Question Button ─────────────
    st.markdown("### 🎲 Practice")
    if st.button("Give me a practice question", use_container_width=True):
        if key_error:
            st.error(key_error)
        else:
            send_to_tutor(
                f"Give me one practice question for Class {st.session_state.class_level}."
            )
            st.session_state.check_answer_mode = True
            st.rerun()

    st.divider()

    # ── Parent Summary Button ────────────────
    st.markdown("### 📋 Parent Summary")
    if st.button("Generate session summary", use_container_width=True):
        if key_error:
            st.error(key_error)
        elif not st.session_state.messages:
            st.warning("No conversation yet! Start chatting first.")
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

    st.divider()

    # ── Scan Problem (Image Upload) ──────────
    st.markdown("### 📷 Scan a Problem")
    st.markdown(
        "<small style='color:#cbd5e1'>Upload a photo of your textbook or notebook question</small>",
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        label="Upload image",
        type=["jpg", "jpeg", "png", "webp", "bmp"],
        label_visibility="collapsed",
        key="image_uploader",
    )
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded problem", use_container_width=True)
        if st.button("Read & Ask Tutor 🔍", use_container_width=True, key="scan_btn"):
            if key_error:
                st.error(key_error)
            else:
                image_bytes = uploaded_file.read()
                mime_type = uploaded_file.type or "image/jpeg"
                with st.spinner("Reading your problem... 👀"):
                    extracted = extract_math_from_image(
                        api_key=api_key,
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                    )
                if extracted.startswith(("API limit", "Could not", "Image reading")):
                    st.error(extracted)
                elif "No math problem found" in extracted:
                    st.warning("No math problem detected in the image. Try a clearer photo.")
                else:
                    st.session_state.scanned_question = extracted
                    send_to_tutor(
                        f"I uploaded a photo of this problem: **{extracted}**\nPlease help me solve it step-by-step!",
                        image=image_bytes
                    )
                    st.rerun()

    st.divider()

    # ── Clear Chat Button ────────────────────
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.session_state.check_answer_mode = False
        st.rerun()

    # ── Disclaimer ───────────────────────────
    st.markdown("""
    <div class="disclaimer">
    ⚠️ <b>Note:</b> AI can make mistakes.
    Always verify important answers with
    your teacher or textbook.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN CONTENT AREA
# ─────────────────────────────────────────────

# Title
st.markdown('<p class="main-title">🧮 AI Math Tutor</p>', unsafe_allow_html=True)
st.markdown(
    f'<p class="main-subtitle"><span class="badge-class">Class {st.session_state.class_level}</span> '
    'Ask your doubt or snap a photo — I\'ll guide you step-by-step! ✨</p>',
    unsafe_allow_html=True,
)

# Show API key error prominently if missing
if key_error:
    st.error(f"🔑 **API Key Missing:** {key_error}")
    st.info(
        "**How to fix:** Create a `.env` file in the project folder and add:\n"
        "```\nGEMINI_API_KEY=your_key_here\n```\n"
        "Get a free key at [aistudio.google.com](https://aistudio.google.com)"
    )
    st.stop()  # Don't show the rest of the app if there's no key

# ── Scan / Upload Math Problem (Main Area - for users facing problem typing) ───
with st.expander("📷 **Facing problem typing? Click here to Scan / Upload a Photo of your question**", expanded=False):
    st.markdown(
        "<p style='color: #cbd5e1; font-size: 0.95rem; margin-bottom: 0.8rem;'>"
        "Take a photo of your notebook or textbook, upload it below, and the tutor will read it and guide you step-by-step!</p>",
        unsafe_allow_html=True,
    )
    col_up, col_info = st.columns([3, 2])
    with col_up:
        main_uploaded_file = st.file_uploader(
            label="Upload photo of your math question",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            key="main_problem_uploader",
        )
    with col_info:
        st.markdown("""
        **💡 Quick Tips:**
        - Ensure good lighting 💡
        - Crop or frame only the problem you want help with ✂️
        - Works with handwritten notes & printed textbooks 📖
        """)

    if main_uploaded_file is not None:
        st.image(main_uploaded_file, caption="Selected Question Preview", width=320)
        if st.button("✨ Scan & Solve with Tutor", key="main_scan_btn", use_container_width=True):
            if key_error:
                st.error(key_error)
            else:
                image_bytes = main_uploaded_file.read()
                mime_type = main_uploaded_file.type or "image/jpeg"
                with st.spinner("🔍 Reading math problem from image using Gemini Vision..."):
                    extracted = extract_math_from_image(
                        api_key=api_key,
                        image_bytes=image_bytes,
                        mime_type=mime_type,
                    )
                if extracted.startswith(("API limit", "Could not", "Image reading")):
                    st.error(extracted)
                elif "No math problem found" in extracted:
                    st.warning("⚠️ No math problem detected in the image. Please try a clearer photo.")
                else:
                    st.session_state.scanned_question = extracted
                    send_to_tutor(
                        f"I uploaded a photo of this problem: **{extracted}**\nPlease help me solve it step-by-step!",
                        image=image_bytes,
                    )
                    st.rerun()

# ── Welcome message (shown only when chat is empty) ──────────────────
if not st.session_state.messages:
    st.info(
        f"👋 **Welcome, Class {st.session_state.class_level} student!**\n\n"
        "Ask your math doubt below, or try these quick options:\n"
        "- 📷 **Can't type?** Open the **Scan / Upload** box above to upload a photo of your question!\n"
        "- 🎲 Click **Give me a practice question** in the sidebar to test yourself.\n"
        "- ✅ Click **Check your answer** when you're ready to submit your solution.\n"
        "- 📋 Click **Parent Summary** at any time to review what was learned.\n\n"
        "*Remember: I won't just dump the final answer — I will guide you so you truly understand! 🧠*"
    )

# ── Render chat history ───────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(
        name=msg["role"],
        avatar="🧑‍🎓" if msg["role"] == "user" else "🤖",
    ):
        if msg.get("image"):
            st.image(msg["image"], caption="📷 Scanned Question Photo", width=340)
        st.markdown(msg["content"])

# ── Parent summary display ────────────────────────────────────────────
if st.session_state.show_summary and st.session_state.summary_text:
    st.markdown("---")
    st.markdown("### 📋 Parent Summary")
    st.markdown(
        f'<div class="summary-box">{st.session_state.summary_text}</div>',
        unsafe_allow_html=True,
    )

# ── Check my answer section ───────────────────────────────────────────
if st.session_state.check_answer_mode:
    st.markdown("---")
    with st.expander("✅ Check my answer", expanded=True):
        answer_input = st.text_input(
            label="Type your answer here:",
            placeholder="e.g. 3/4 or x = 5 ...",
            key="answer_input_box",
        )
        if st.button("Submit answer", key="submit_answer_btn"):
            if answer_input.strip():
                send_to_tutor(f"I think the answer is: {answer_input.strip()}")
                st.session_state.check_answer_mode = False
                st.rerun()
            else:
                st.warning("Please type your answer before submitting.")

# ── Main chat input ───────────────────────────────────────────────────
# st.chat_input stays pinned at the bottom of the page — very user-friendly
user_input = st.chat_input(
    placeholder="Type your math doubt here... (e.g. 'I don't understand fractions')",
)

if user_input:
    send_to_tutor(user_input)
    st.rerun()  # Refresh the page to show the new messages
