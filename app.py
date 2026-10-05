# app.py — AI Math Tutor (ChatGPT / Gemini style minimalist interface)
#
# Features:
#   - Minimalist, distraction-free conversational UI (like ChatGPT & Gemini)
#   - Worked detailed solution first -> Auto-generated similar practice question
#   - Direct photo/image attachment in the chat bar (using Gemini Vision)
#   - Class 1–12 selector & NCERT/CBSE level adaptation
#   - Clean collapsible sidebar with "+ New Chat" and "Parent Summary"

import streamlit as st
from tutor_prompt import get_system_prompt
from utils import load_api_key, get_gemini_response, generate_parent_summary, extract_math_from_image


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
# CHATGPT / GEMINI STYLE MINIMALIST CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #ececf1;
}

/* ── App background (Clean dark tone like ChatGPT / Gemini) ── */
.stApp {
    background-color: #0e1117 !important;
}

/* ── Centered Main Container ── */
.block-container {
    max-width: 820px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 7rem !important;
}

/* ── Clean Header ── */
.chat-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.chat-header-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.chat-header-badge {
    background: rgba(99, 102, 241, 0.18);
    border: 1px solid rgba(129, 140, 248, 0.4);
    color: #a5b4fc;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
}

/* ── Welcome Screen (ChatGPT / Gemini style) ── */
.welcome-container {
    text-align: center;
    padding: 3.5rem 1rem 2rem 1rem;
}
.welcome-hero-icon {
    font-size: 3rem;
    margin-bottom: 0.8rem;
}
.welcome-title {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}
.welcome-sub {
    font-size: 1rem;
    color: #94a3b8;
    max-width: 540px;
    margin: 0 auto 2rem auto;
    line-height: 1.6;
}

/* ── Suggestion Cards ── */
.suggestion-card {
    background: #1e222d;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1rem 1.1rem;
    text-align: left;
    transition: all 0.2s ease;
    cursor: pointer;
    min-height: 85px;
}
.suggestion-card:hover {
    background: #262c3b;
    border-color: #6366f1;
    transform: translateY(-2px);
}
.suggestion-title {
    font-size: 0.95rem;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 0.25rem;
}
.suggestion-desc {
    font-size: 0.8rem;
    color: #94a3b8;
}

/* ── Chat Messages (Sleek ChatGPT bubbles) ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 0 !important;
    margin-bottom: 0.5rem !important;
}

/* User Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    display: flex;
    justify-content: flex-end;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div {
    background: #2a2e3d !important;
    border-radius: 18px !important;
    padding: 0.85rem 1.25rem !important;
    max-width: 85%;
    border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Assistant (Tutor) Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div {
    background: #171b24 !important;
    border-radius: 18px !important;
    padding: 1.2rem 1.5rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* Chat text visibility */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #f1f5f9 !important;
    font-size: 1.02rem !important;
    line-height: 1.7 !important;
}
[data-testid="stChatMessage"] strong {
    color: #fbbf24 !important;
    font-weight: 700 !important;
}
[data-testid="stChatMessage"] code {
    background: #0f131a !important;
    color: #38bdf8 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── KaTeX Math Formula Highlight ── */
.katex, .katex * {
    color: #f8fafc !important;
    font-size: 1.08em !important;
}
.katex-display {
    background: rgba(99, 102, 241, 0.08) !important;
    border-left: 3px solid #6366f1 !important;
    border-radius: 8px !important;
    padding: 0.6rem 0.9rem !important;
    margin: 0.8rem 0 !important;
}

/* ── Floating Chat Input Bar (Gemini / ChatGPT style) ── */
[data-testid="stChatInput"] {
    background: #1e222d !important;
    border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 20px !important;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.2s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25) !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #94a3b8 !important;
}

/* ── Sidebar (ChatGPT style) ── */
[data-testid="stSidebar"] {
    background-color: #12151c !important;
    border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
}
[data-testid="stSidebar"] * {
    color: #cbd5e1 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
}

/* ── New Chat & Action Buttons ── */
.stButton > button {
    background: #1e222d !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: #2a2e3d !important;
    border-color: #6366f1 !important;
    color: #ffffff !important;
}

/* ── Summary card ── */
.summary-card {
    background: #172520;
    border-left: 4px solid #10b981;
    border-radius: 12px;
    padding: 1.2rem;
    margin-top: 1rem;
    color: #d1fae5 !important;
    font-size: 0.98rem;
    line-height: 1.7;
}

/* ── File uploader dropzone inside chat bar ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
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
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "gemini_history" not in st.session_state:
    st.session_state.gemini_history = []

if "class_level" not in st.session_state:
    st.session_state.class_level = 5

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""


# ─────────────────────────────────────────────
# HELPER: Send to Tutor
# ─────────────────────────────────────────────

def add_message(role: str, content: str, image=None):
    """Save message for display and Gemini context."""
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "image": image,
    })
    gemini_role = "model" if role == "assistant" else "user"
    st.session_state.gemini_history.append({
        "role": gemini_role,
        "parts": [content],
    })


def send_to_tutor(user_text: str, image=None):
    """Send question to Gemini, receive worked solution + practice challenge."""
    add_message("user", user_text, image=image)

    system_prompt = get_system_prompt(st.session_state.class_level)

    with st.spinner("Solving step-by-step & preparing practice challenge... 🧠"):
        reply = get_gemini_response(
            api_key=api_key,
            system_prompt=system_prompt,
            chat_history=st.session_state.gemini_history[:-1],
            user_message=user_text,
        )

    add_message("assistant", reply)


# ─────────────────────────────────────────────
# SIDEBAR (ChatGPT / Gemini style)
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 📐 AI Math Tutor")

    # + New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.rerun()

    st.markdown("---")

    # Class Selector
    st.markdown("**🎓 Student Class**")
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

    st.markdown("---")

    # Parent Summary Button
    st.markdown("**📋 Parent / Session Summary**")
    if st.button("Generate Summary", use_container_width=True):
        if key_error:
            st.error(key_error)
        elif not st.session_state.messages:
            st.warning("Chat with the tutor first to generate a summary.")
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
    st.caption("✨ *Gives full step-by-step solutions first, then generates similar practice questions.*")


# ─────────────────────────────────────────────
# MAIN CHAT AREA
# ─────────────────────────────────────────────

# Header
st.markdown(
    f"""
    <div class="chat-header">
        <div class="chat-header-title">
            <span>📐 AI Math Tutor</span>
        </div>
        <div class="chat-header-badge">Class {st.session_state.class_level}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Key Error Check
if key_error:
    st.error(f"🔑 **API Key Missing:** {key_error}")
    st.info(
        "Add `GEMINI_API_KEY` to your `.env` file locally or in Streamlit Cloud Secrets."
    )
    st.stop()

# ── Welcome Screen (shown when conversation is empty) ──
if not st.session_state.messages:
    st.markdown(
        f"""
        <div class="welcome-container">
            <div class="welcome-hero-icon">✨</div>
            <div class="welcome-title">What math problem are you working on?</div>
            <div class="welcome-sub">
                Type any math doubt or attach a photo from your textbook.
                I will give you a <b>detailed step-by-step solution</b>, and then
                give you a <b>similar practice problem</b> to test yourself!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Quick Suggestion Chips (like ChatGPT)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍕 Explain Fractions with simple examples", use_container_width=True):
            send_to_tutor(f"Explain fractions with simple real-life examples for Class {st.session_state.class_level}.")
            st.rerun()

        if st.button("📐 Solve 2x + 7 = 19 step-by-step", use_container_width=True):
            send_to_tutor("Solve 2x + 7 = 19 step-by-step and show the complete solution.")
            st.rerun()

    with col2:
        if st.button(f"🎲 Give me a Class {st.session_state.class_level} challenge", use_container_width=True):
            send_to_tutor(f"Give me an interesting math problem suitable for Class {st.session_state.class_level}, solve it with full steps, and give me a similar practice problem.")
            st.rerun()

        if st.button("📷 How do I scan / upload my textbook problem?", use_container_width=True):
            send_to_tutor("How can I upload a photo of my math problem? Explain how you will solve it and help me practice.")
            st.rerun()

# ── Render Chat History ──
for msg in st.session_state.messages:
    with st.chat_message(
        name=msg["role"],
        avatar="🧑‍🎓" if msg["role"] == "user" else "✨",
    ):
        if msg.get("image"):
            st.image(msg["image"], caption="📷 Scanned Question Photo", width=340)
        st.markdown(msg["content"])

# ── Parent Summary Display ──
if st.session_state.show_summary and st.session_state.summary_text:
    st.markdown("---")
    st.markdown("### 📋 Parent Session Summary")
    st.markdown(
        f'<div class="summary-card">{st.session_state.summary_text}</div>',
        unsafe_allow_html=True,
    )

# ── Chat Input Bar (with native file/camera upload like ChatGPT) ──
chat_val = st.chat_input(
    placeholder=f"Ask any Class {st.session_state.class_level} math doubt or attach a photo...",
    accept_file=True,
    file_type=["png", "jpg", "jpeg", "webp"],
)

if chat_val:
    # Extract text and files from ChatInputValue
    user_text = ""
    uploaded_files = []

    if hasattr(chat_val, "text"):
        user_text = chat_val.text.strip()
    elif isinstance(chat_val, str):
        user_text = chat_val.strip()

    if hasattr(chat_val, "files") and chat_val.files:
        uploaded_files = chat_val.files

    # Process image if attached
    if uploaded_files:
        img_file = uploaded_files[0]
        image_bytes = img_file.read()
        mime_type = img_file.type or "image/jpeg"

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
            if user_text:
                full_prompt = (
                    f"{user_text}\n\n"
                    f"**Problem from uploaded photo:**\n{extracted}\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )
            else:
                full_prompt = (
                    f"I uploaded a photo of this math problem:\n**{extracted}**\n\n"
                    f"Please provide the detailed step-by-step solution first, "
                    f"and then create a similar practice problem for me!"
                )

            send_to_tutor(full_prompt, image=image_bytes)
            st.rerun()

    elif user_text:
        send_to_tutor(user_text)
        st.rerun()
