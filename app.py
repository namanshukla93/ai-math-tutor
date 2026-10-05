# app.py — AI Math Tutor with Claude-Style Interface, Multi-File Scanning & File Creation (Artifacts)
#
# Highlights:
#   - Claude's iconic warm terracotta & charcoal aesthetic
#   - Multi-File Scanning: Images (PNG/JPG), PDFs, Text files, Worksheets, Code
#   - Claude-Style Artifacts: Create & download Worksheets, Formula Cheat Sheets & Study Guides
#   - Teach-First (Detailed Solution) -> Auto-generated Similar Practice Question
#   - Clean, distraction-free conversational experience

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
    page_title="Claude Math Tutor",
    page_icon="✳️",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# CLAUDE-STYLE ICONIC WARM THEME CSS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #ececec;
}

/* ── Claude Warm Dark Canvas ── */
.stApp {
    background-color: #18181b !important;
}

/* ── Centered Claude Reading Column ── */
.block-container {
    max-width: 820px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 7rem !important;
}

/* ── Claude Top Navigation Bar ── */
.claude-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}
.claude-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.35rem;
    font-weight: 700;
    color: #fbfbfa;
    font-family: 'Plus Jakarta Sans', sans-serif;
}
.claude-sparkle {
    color: #da7756;
    font-size: 1.4rem;
}
.claude-badge {
    background: rgba(218, 119, 86, 0.15);
    border: 1px solid rgba(218, 119, 86, 0.35);
    color: #e5987d;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.25rem 0.8rem;
    border-radius: 9999px;
}

/* ── Claude Welcome Screen ── */
.claude-welcome {
    text-align: center;
    padding: 3rem 1rem 1.8rem 1rem;
}
.claude-avatar-hero {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: rgba(218, 119, 86, 0.12);
    border: 1.5px solid rgba(218, 119, 86, 0.3);
    color: #da7756;
    font-size: 2rem;
    margin-bottom: 1rem;
}
.claude-greeting {
    font-family: 'Newsreader', serif;
    font-size: 2.3rem;
    font-weight: 500;
    color: #fbfbfa;
    margin-bottom: 0.6rem;
    letter-spacing: -0.01em;
}
.claude-subtext {
    font-size: 1.02rem;
    color: #a1a1aa;
    max-width: 560px;
    margin: 0 auto 2.2rem auto;
    line-height: 1.6;
}

/* ── Claude Suggestion Cards ── */
.claude-card {
    background: #232328;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 1.1rem;
    transition: all 0.2s ease;
}
.claude-card:hover {
    background: #2a2a32;
    border-color: #da7756;
    transform: translateY(-2px);
}

/* ── Chat Messages ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.75rem 0 !important;
    margin-bottom: 0.5rem !important;
}

/* User Message Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    display: flex;
    justify-content: flex-end;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) > div {
    background: #27272f !important;
    border-radius: 18px !important;
    padding: 0.9rem 1.3rem !important;
    max-width: 85%;
    border: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

/* Assistant (Claude) Bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) > div {
    background: #1f1f25 !important;
    border-radius: 18px !important;
    padding: 1.3rem 1.6rem !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.25);
}

/* Text Visibility */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div {
    color: #f4f4f5 !important;
    font-size: 1.03rem !important;
    line-height: 1.75 !important;
}
[data-testid="stChatMessage"] strong {
    color: #e5987d !important;
    font-weight: 700;
}
[data-testid="stChatMessage"] code {
    background: #141416 !important;
    color: #f59e0b !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    padding: 0.15rem 0.4rem !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── KaTeX Math Formula Highlight ── */
.katex, .katex * {
    color: #fbfbfa !important;
    font-size: 1.1em !important;
}
.katex-display {
    background: rgba(218, 119, 86, 0.08) !important;
    border-left: 3px solid #da7756 !important;
    border-radius: 8px !important;
    padding: 0.75rem 1rem !important;
    margin: 0.85rem 0 !important;
}

/* ── Claude-Style Artifact Card (Created Files) ── */
.artifact-card {
    background: #1b1b22;
    border: 1.5px solid rgba(218, 119, 86, 0.4);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(218, 119, 86, 0.15);
}
.artifact-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 1.1rem;
    font-weight: 700;
    color: #fbfbfa;
    margin-bottom: 0.35rem;
}
.artifact-desc {
    font-size: 0.88rem;
    color: #a1a1aa;
    margin-bottom: 0.9rem;
}

/* ── Attached File Chip (Multi-File Access) ── */
.file-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(218, 119, 86, 0.14);
    border: 1px solid rgba(218, 119, 86, 0.35);
    border-radius: 10px;
    padding: 0.4rem 0.85rem;
    color: #fbfbfa;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.6rem;
}

/* ── Claude Floating Prompt Bar ── */
[data-testid="stChatInput"] {
    background: #23232a !important;
    border: 1.5px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 20px !important;
    box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45) !important;
    transition: all 0.25s ease;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #da7756 !important;
    box-shadow: 0 0 0 3px rgba(218, 119, 86, 0.3) !important;
}
[data-testid="stChatInput"] textarea {
    color: #ffffff !important;
    font-size: 1.02rem !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #71717a !important;
}

/* ── Sidebar (Claude Warm Dark) ── */
[data-testid="stSidebar"] {
    background-color: #131316 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}
[data-testid="stSidebar"] * {
    color: #d4d4d8 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #fbfbfa !important;
}

/* ── Claude Terracotta Buttons ── */
.stButton > button {
    background: #da7756 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(218, 119, 86, 0.3) !important;
}
.stButton > button:hover {
    background: #c86544 !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(218, 119, 86, 0.45) !important;
}

/* Secondary Button in Sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: #23232a !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    color: #fbfbfa !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #2e2e38 !important;
    border-color: #da7756 !important;
}

/* ── Download Button (Artifacts) ── */
.stDownloadButton > button {
    background: linear-gradient(135deg, #da7756 0%, #c86544 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #ffffff !important;
    font-weight: 700 !important;
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

if "artifacts" not in st.session_state:
    st.session_state.artifacts = []  # List of {name, content, type}

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

if "summary_text" not in st.session_state:
    st.session_state.summary_text = ""


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

    with st.spinner("Claude Tutor is thinking & drafting response... ✳️"):
        reply = get_gemini_response(
            api_key=api_key,
            system_prompt=system_prompt,
            chat_history=st.session_state.gemini_history[:-1],
            user_message=user_text,
        )

    add_message("assistant", reply)


# ─────────────────────────────────────────────
# SIDEBAR (Claude Minimalist Theme)
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ✳️ Claude Math Tutor")

    # + New Chat button
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.gemini_history = []
        st.session_state.show_summary = False
        st.session_state.summary_text = ""
        st.rerun()

    st.markdown("---")

    # Class Selector
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

    st.markdown("---")

    # Claude Artifact Creator (File Creation Feature)
    st.markdown("**📄 Create File (Artifacts)**")
    st.caption("Generate printable worksheets, cheat sheets & study files.")
    
    with st.expander("✨ Create New File", expanded=False):
        topic_input = st.text_input("Math Topic:", placeholder="e.g. Linear Equations, Fractions, Trigonometry")
        art_type = st.selectbox(
            "File Type:",
            options=["worksheet", "cheat_sheet", "solution_set"],
            format_func=lambda x: {
                "worksheet": "📝 Practice Worksheet (.md)",
                "cheat_sheet": "⚡ Formula Cheat Sheet (.md)",
                "solution_set": "📘 Master Solved Set (.md)",
            }[x],
        )
        if st.button("Generate & Download File", use_container_width=True):
            if not topic_input.strip():
                st.warning("Please enter a topic.")
            elif key_error:
                st.error(key_error)
            else:
                with st.spinner("Creating your file... 📄"):
                    fname, fcontent = create_math_artifact(
                        api_key=api_key,
                        topic=topic_input.strip(),
                        class_level=st.session_state.class_level,
                        artifact_type=art_type,
                    )
                st.session_state.artifacts.append({"name": fname, "content": fcontent, "type": art_type})
                send_to_tutor(
                    f"I have created a new file for you: **{fname}** on topic '{topic_input}'. "
                    "I am ready to guide you through any questions from it!"
                )
                st.rerun()

    # Saved Artifacts List
    if st.session_state.artifacts:
        st.markdown("**📥 Generated Files:**")
        for i, art in enumerate(st.session_state.artifacts):
            st.download_button(
                label=f"⬇️ {art['name']}",
                data=art["content"],
                file_name=art["name"],
                mime="text/markdown",
                key=f"dl_sidebar_art_{i}",
                use_container_width=True,
            )

    st.markdown("---")

    # Parent Summary Button
    st.markdown("**📋 Parent Summary**")
    if st.button("Generate Session Summary", use_container_width=True):
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
    st.caption("✳️ *Supports all file formats (Images, PDFs, Text). Creates downloadable study files.*")


# ─────────────────────────────────────────────
# MAIN CHAT AREA (Claude Theme)
# ─────────────────────────────────────────────

# Header
st.markdown(
    f"""
    <div class="claude-header">
        <div class="claude-brand">
            <span class="claude-sparkle">✳️</span>
            <span>Claude Math Tutor</span>
        </div>
        <div class="claude-badge">Class {st.session_state.class_level}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# API Key Error Check
if key_error:
    st.error(f"🔑 **API Key Missing:** {key_error}")
    st.info("Add `GEMINI_API_KEY` to your `.env` file locally or in Streamlit Cloud Secrets.")
    st.stop()

# ── Claude Welcome Screen (shown when conversation is empty) ──
if not st.session_state.messages:
    st.markdown(
        f"""
        <div class="claude-welcome">
            <div class="claude-avatar-hero">✳️</div>
            <div class="claude-greeting">How can I help you with math today?</div>
            <div class="claude-subtext">
                Ask any question, or attach <b>images, PDFs, or worksheets</b> below.
                I will explain the complete step-by-step solution, and create a
                <b>similar practice problem</b> for you to solve!
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 4 Claude Suggestion Cards
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🍕 Explain Fractions with real-world examples", use_container_width=True):
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
                "Download it from the sidebar or click the download button. Let's solve the first question together!"
            )
            st.rerun()

        if st.button("📎 What file formats can I attach?", use_container_width=True):
            send_to_tutor(
                "What file formats can I upload here? Explain how you can read photos, PDFs, textbooks, and homework notes."
            )
            st.rerun()

# ── Render Chat History ──
for msg in st.session_state.messages:
    with st.chat_message(
        name=msg["role"],
        avatar="🧑‍🎓" if msg["role"] == "user" else "✳️",
    ):
        # If a file was attached in this message, display attachment card
        if msg.get("file_meta"):
            f_meta = msg["file_meta"]
            st.markdown(
                f'<div class="file-chip">📎 Attached File: <b>{f_meta["name"]}</b> ({f_meta["type"]})</div>',
                unsafe_allow_html=True,
            )
        if msg.get("image"):
            st.image(msg["image"], caption="📷 Attached Problem Image", width=340)

        st.markdown(msg["content"])

# ── Display Generated Artifacts (Downloadable Files like Claude) ──
if st.session_state.artifacts:
    latest_art = st.session_state.artifacts[-1]
    st.markdown(
        f"""
        <div class="artifact-card">
            <div class="artifact-header">
                <span>📄 Created File (Artifact):</span>
                <span>{latest_art['name']}</span>
            </div>
            <div class="artifact-desc">
                Generated custom math file for Class {st.session_state.class_level}. Click below to save it to your device.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        label=f"⬇️ Download {latest_art['name']}",
        data=latest_art["content"],
        file_name=latest_art["name"],
        mime="text/markdown",
        key="main_artifact_dl_btn",
        use_container_width=True,
    )

# ── Parent Summary Display ──
if st.session_state.show_summary and st.session_state.summary_text:
    st.markdown("---")
    st.markdown("### 📋 Parent Session Summary")
    st.markdown(
        f'<div class="artifact-card" style="border-color: #10b981;">{st.session_state.summary_text}</div>',
        unsafe_allow_html=True,
    )

# ── Claude Floating Chat Bar with Multi-File Upload ──
# Accepts Images (PNG, JPG, WEBP), PDFs, Text files, Worksheets, Code
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

    # Multi-file processing: Images, PDFs, Text files
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
