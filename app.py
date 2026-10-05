"""
app.py - ApexSolve: AI Math & Logical Reasoning Master
A student-centric web application for rigorous mathematical solutions,
logical reasoning deductions, and adaptive practice problems.
Creator: Naman Shukla (namanshukla9889@gmail.com)
"""

import streamlit as st
from PIL import Image
import json
import database
import solver
import formula_book

# 1. Page Configuration
st.set_page_config(
    page_title="ApexSolve | AI Math & Reasoning Master",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Custom CSS for modern student-centric aesthetics & high-impact animations
st.markdown("""
<style>
    /* Global styles & Modern Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Sleek Deep Space Radial Gradient Background */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #1e1b4b 0%, #0f172a 45%, #050814 100%) !important;
        background-attachment: fixed !important;
    }

    /* Ambient Background Glow Orbs */
    .stApp::before {
        content: '';
        position: fixed;
        top: -150px;
        left: 20%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 0;
        pointer-events: none;
        animation: floatOrb 12s ease-in-out infinite alternate;
    }

    .stApp::after {
        content: '';
        position: fixed;
        bottom: -100px;
        right: 15%;
        width: 450px;
        height: 450px;
        background: radial-gradient(circle, rgba(236, 72, 153, 0.12) 0%, transparent 70%);
        border-radius: 50%;
        z-index: 0;
        pointer-events: none;
        animation: floatOrb 15s ease-in-out infinite alternate-reverse;
    }

    /* Keyframe Animations */
    @keyframes floatOrb {
        0% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(40px) scale(1.08); }
        100% { transform: translateY(0px) scale(1); }
    }

    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(22px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseGlow {
        0%, 100% {
            box-shadow: 0 0 15px rgba(99, 102, 241, 0.35);
        }
        50% {
            box-shadow: 0 0 28px rgba(99, 102, 241, 0.7), 0 0 45px rgba(168, 85, 247, 0.4);
        }
    }

    @keyframes floatSymbol {
        0% { transform: translateY(0) rotate(0deg); opacity: 0.15; }
        50% { transform: translateY(-15px) rotate(8deg); opacity: 0.35; }
        100% { transform: translateY(0) rotate(0deg); opacity: 0.15; }
    }

    @keyframes buttonShimmer {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }

    /* Top Floating Glassmorphic Nav Bar */
    .top-glass-nav {
        background: rgba(15, 23, 42, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .brand-logo-wrap {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .brand-logo-icon {
        background: linear-gradient(135deg, #6366f1, #a855f7);
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
    }

    .brand-name-text {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 60%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .status-badge-pill {
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.35);
        color: #34d399;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 5px 14px;
        border-radius: 9999px;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .status-dot-pulse {
        width: 8px;
        height: 8px;
        background-color: #10b981;
        border-radius: 50%;
        display: inline-block;
        box-shadow: 0 0 10px #10b981;
        animation: pulseGlow 2s infinite ease-in-out;
    }

    /* Hero Header & Shimmering Title */
    .hero-badge {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.35);
        color: #c7d2fe;
        padding: 6px 18px;
        border-radius: 9999px;
        font-size: 0.82rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        box-shadow: 0 0 12px rgba(99, 102, 241, 0.25);
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 25%, #a855f7 60%, #6366f1 100%);
        background-size: 250% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 6s ease-in-out infinite;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }

    .sub-title {
        color: #94a3b8;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-bottom: 24px;
    }

    /* Interactive Feature Grid Cards on Landing */
    .landing-features-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 16px;
        margin-top: 28px;
        animation: fadeInUp 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .feature-card-item {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        padding: 18px 20px;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }

    .feature-card-item:hover {
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.5);
        box-shadow: 0 12px 28px -6px rgba(99, 102, 241, 0.25);
        background: rgba(30, 41, 59, 0.8);
    }

    .feature-card-icon {
        font-size: 1.6rem;
        margin-bottom: 8px;
    }

    .feature-card-title {
        color: #f1f5f9;
        font-weight: 700;
        font-size: 0.98rem;
        margin-bottom: 6px;
    }

    .feature-card-desc {
        color: #94a3b8;
        font-size: 0.83rem;
        line-height: 1.45;
    }

    /* Cards with Modern Glassmorphism */
    .card-box {
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(148, 163, 184, 0.16);
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
        transition: transform 0.25s ease, border-color 0.25s ease;
    }

    .card-box:hover {
        border-color: rgba(99, 102, 241, 0.35);
    }

    .step-card {
        background: rgba(15, 23, 42, 0.85);
        backdrop-filter: blur(10px);
        border-left: 4px solid #6366f1;
        border-top: 1px solid rgba(148, 163, 184, 0.1);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
        border-bottom: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 0 10px 10px 0;
        padding: 16px 20px;
        margin: 14px 0;
        transition: transform 0.2s ease, border-left-color 0.2s ease;
    }

    .step-card:hover {
        transform: translateX(4px);
        border-left-color: #a855f7;
    }

    .concept-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.06));
        border: 1px solid rgba(99, 102, 241, 0.35);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 18px;
        box-shadow: 0 0 18px rgba(99, 102, 241, 0.12);
    }

    .final-answer-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.18), rgba(5, 150, 105, 0.08));
        border: 1px solid rgba(16, 185, 129, 0.5);
        border-radius: 14px;
        padding: 20px 24px;
        margin: 20px 0;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.2);
        animation: pulseGlow 3s infinite ease-in-out;
    }

    .practice-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 12px;
        padding: 20px;
        margin: 14px 0;
        transition: all 0.25s ease;
    }

    .practice-card:hover {
        border-color: rgba(99, 102, 241, 0.45);
        box-shadow: 0 8px 25px -5px rgba(99, 102, 241, 0.2);
    }

    .tip-card {
        background: rgba(245, 158, 11, 0.12);
        border: 1px solid rgba(245, 158, 11, 0.35);
        border-radius: 10px;
        padding: 14px 18px;
        margin: 16px 0;
    }

    /* Enhanced Streamlit Buttons with Shimmer & 3D Hover */
    .stButton>button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 8px 20px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px -4px rgba(99, 102, 241, 0.4) !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 50%, #4338ca 100%) !important;
        box-shadow: 0 0 16px rgba(99, 102, 241, 0.35) !important;
    }

    .stButton>button[kind="primary"]:hover {
        background: linear-gradient(135deg, #818cf8 0%, #6366f1 50%, #4f46e5 100%) !important;
        box-shadow: 0 0 26px rgba(99, 102, 241, 0.6) !important;
    }

    /* Form Inputs & Focus Rings */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(15, 23, 42, 0.75) !important;
        border: 1px solid rgba(148, 163, 184, 0.25) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        transition: all 0.2s ease !important;
    }

    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #818cf8 !important;
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.45) !important;
    }

    /* Custom Sleek Scrollbar */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }
    ::-webkit-scrollbar-track {
        background: #090d16;
    }
    ::-webkit-scrollbar-thumb {
        background: #312e81;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #6366f1;
    }
</style>
""", unsafe_allow_html=True)


# 3. Session State Initialization
if "user" not in st.session_state:
    st.session_state["user"] = None

if "current_solution" not in st.session_state:
    st.session_state["current_solution"] = None

if "current_question_text" not in st.session_state:
    st.session_state["current_question_text"] = ""

if "saved_question_id" not in st.session_state:
    st.session_state["saved_question_id"] = None


# 4. Authentication Views
# 4. Top Navigation Bar (Common for all views)
def render_top_navbar():
    user = st.session_state.get("user")
    user_badge = f"""
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="status-badge-pill"><span class="status-dot-pulse"></span> AI Engine: Active</span>
            <span style="color: #cbd5e1; font-size: 0.85rem; font-weight: 600; background: rgba(99,102,241,0.18); border: 1px solid rgba(99,102,241,0.3); padding: 5px 14px; border-radius: 9999px;">
                👤 {user['name']} ({user.get('target_exam', 'General')})
            </span>
        </div>
    """ if user else """
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="status-badge-pill"><span class="status-dot-pulse"></span> Google Gemini AI: Online</span>
            <span style="color: #94a3b8; font-size: 0.82rem; font-weight: 500;">v2.4 Production</span>
        </div>
    """

    st.markdown(f"""
    <div class="top-glass-nav">
        <div class="brand-logo-wrap">
            <div class="brand-logo-icon">📐</div>
            <div>
                <div class="brand-name-text">ApexSolve</div>
                <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;">AI Math & Logical Reasoning Master</div>
            </div>
        </div>
        {user_badge}
    </div>
    """, unsafe_allow_html=True)


# 5. Authentication & Landing Views
def render_auth_page():
    render_top_navbar()

    # Hero Banner
    st.markdown("""
    <div style="text-align: center; margin-top: 15px; margin-bottom: 25px; animation: fadeInUp 0.7s cubic-bezier(0.16, 1, 0.3, 1);">
        <div class="hero-badge">✨ Next-Generation Student Intelligence Platform</div>
        <h1 class="main-title">Master Mathematics & Logical Reasoning</h1>
        <p class="sub-title" style="max-width: 680px; margin: 0 auto 20px auto;">
            Experience textbook-grade KaTeX proofs with zero skipped steps, intelligent deductive reasoning, 
            and adaptive practice problem challenges tailored to your exam.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Centered Auth Card
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown('<div class="card-box" style="border: 1px solid rgba(99, 102, 241, 0.3); box-shadow: 0 16px 40px -10px rgba(0,0,0,0.5);">', unsafe_allow_html=True)
        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In to Portal", "📝 New Student Registration"])

        with auth_tab1:
            st.markdown("<div style='font-weight:700; color:#f8fafc; font-size:1.1rem; margin-bottom:6px;'>Welcome Back, Scholar</div>", unsafe_allow_html=True)
            st.markdown("<div style='color:#94a3b8; font-size:0.85rem; margin-bottom:16px;'>Enter your registered email and password to access your workspace.</div>", unsafe_allow_html=True)

            login_email = st.text_input("Student Email", key="login_email_input", placeholder="student@example.com")
            login_pass = st.text_input("Password", type="password", key="login_pass_input")

            col_sub, col_demo = st.columns([1.1, 1.1])
            with col_sub:
                if st.button("🚀 Sign In to Account", use_container_width=True, type="primary"):
                    if not login_email or not login_pass:
                        st.error("Please fill in both email and password.")
                    else:
                        success, msg, user_data = database.authenticate_user(login_email, login_pass)
                        if success:
                            st.session_state["user"] = user_data
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

            with col_demo:
                if st.button("⚡ 1-Click Instant Demo Login", use_container_width=True, help="Instant 1-click test login for examiners/evaluators"):
                    success, msg, user_data = database.authenticate_user("namanshukla9889@gmail.com", "naman123")
                    if success:
                        st.session_state["user"] = user_data
                        st.success("Welcome, Naman Shukla!")
                        st.rerun()
                    else:
                        st.error(msg)

            st.markdown("""
            <div style="background: rgba(99, 102, 241, 0.08); border: 1px dashed rgba(99, 102, 241, 0.25); border-radius: 8px; padding: 8px 12px; margin-top: 14px; text-align: center;">
                <span style="color: #94a3b8; font-size: 0.8rem;">💡 Quick Demo Account: <code style="color:#c7d2fe;">namanshukla9889@gmail.com</code> | <code style="color:#c7d2fe;">naman123</code></span>
            </div>
            """, unsafe_allow_html=True)

        with auth_tab2:
            st.markdown("<div style='font-weight:700; color:#f8fafc; font-size:1.1rem; margin-bottom:6px;'>Create Your Student Profile</div>", unsafe_allow_html=True)
            new_name = st.text_input("Full Name", placeholder="e.g. Naman Shukla", key="reg_name")
            new_email = st.text_input("Email Address", placeholder="e.g. namanshukla9889@gmail.com", key="reg_email")
            new_pass = st.text_input("Create Password (min 6 characters)", type="password", key="reg_pass")
            target_exam = st.selectbox(
                "Target Examination / Academic Level",
                ["JEE Mains & Advanced", "SSC CGL / Banking / Railways", "CAT / Management Aptitude", "Olympiad / High School", "University / College Degree", "General Aptitude"],
                key="reg_exam"
            )

            if st.button("✨ Register & Launch Workspace", use_container_width=True, type="primary"):
                success, msg, user_data = database.register_user(new_name, new_email, new_pass, target_exam)
                if success:
                    st.session_state["user"] = user_data
                    st.success(f"Welcome aboard, {new_name}! Redirecting...")
                    st.rerun()
                else:
                    st.error(msg)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # 4 Highlights Feature Cards Grid
    st.markdown("""
    <div class="landing-features-grid">
        <div class="feature-card-item">
            <div class="feature-card-icon">📐</div>
            <div class="feature-card-title">Rigorous Math Proofs</div>
            <div class="feature-card-desc">Zero intermediate steps skipped. Every algebraic substitution and theorem clearly justified in textbook KaTeX.</div>
        </div>
        <div class="feature-card-item">
            <div class="feature-card-icon">🧠</div>
            <div class="feature-card-title">Deductive Logic Engine</div>
            <div class="feature-card-desc">Formal syllogisms, Euler-Venn diagrams, complex bloodline relations, and number series sequence analysis.</div>
        </div>
        <div class="feature-card-item">
            <div class="feature-card-icon">🎯</div>
            <div class="feature-card-title">Adaptive Practice Arena</div>
            <div class="feature-card-desc">Generate instant multi-tiered practice problems with live answer checking, step hints, and full solutions.</div>
        </div>
        <div class="feature-card-item">
            <div class="feature-card-icon">📚</div>
            <div class="feature-card-title">Concept & Formula Book</div>
            <div class="feature-card-desc">High-yield mathematical handbook and reasoning cheat codes (EJOTY, reverse pairs) built directly inside.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# 5. Main Application Header & Sidebar
def render_sidebar():
    user = st.session_state["user"]
    with st.sidebar:
        st.markdown(f"""
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.25); border-radius: 10px; padding: 12px; margin-bottom: 16px;">
            <div style="font-weight: 700; color: #f8fafc; font-size: 1.05rem;">👤 {user['name']}</div>
            <div style="color: #94a3b8; font-size: 0.82rem; overflow: hidden; text-overflow: ellipsis;">{user['email']}</div>
            <div style="margin-top: 6px; font-size: 0.75rem; background: rgba(99,102,241,0.25); color: #c7d2fe; display: inline-block; padding: 2px 8px; border-radius: 4px;">
                🎯 {user.get('target_exam', 'General')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        menu = st.radio(
            "Navigation",
            ["🚀 AI Solver", "🎯 Practice Arena", "📚 Concept Handbook", "🕒 Saved History", "📊 My Analytics", "⚙️ Profile Settings"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        
        # Scratchpad widget in sidebar
        with st.expander("📝 Student Scratchpad / Rough Work"):
            scratch_text = st.text_area("Jot quick steps or numbers here:", height=140, key="sidebar_scratchpad")
            if scratch_text:
                st.caption(f"Chars: {len(scratch_text)}")

        # Gemini API Key configuration
        api_ok = solver.is_api_key_configured()
        with st.expander("🔑 Gemini API Settings", expanded=not api_ok):
            if api_ok:
                st.markdown("<span style='color:#10b981; font-weight:600; font-size:0.85rem;'>🟢 AI Engine: Active</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='color:#f59e0b; font-weight:600; font-size:0.85rem;'>⚠️ API Key Required</span>", unsafe_allow_html=True)

            cur_k = solver.get_configured_api_key() or ""
            mask_text = f"...{cur_k[-6:]}" if len(cur_k) > 6 else ""

            sidebar_key_val = st.text_input(
                "Gemini API Key:",
                type="password",
                placeholder=f"Active ({mask_text})" if mask_text else "Paste Gemini API Key...",
                key="sidebar_api_key_input",
                help="Enter your free API key from Google AI Studio (aistudio.google.com)"
            )
            if st.button("💾 Save Key", use_container_width=True, key="save_sidebar_key_btn"):
                if sidebar_key_val.strip():
                    st.session_state["gemini_api_key"] = sidebar_key_val.strip()
                    import os
                    os.environ["GEMINI_API_KEY"] = sidebar_key_val.strip()
                    st.success("API Key saved!")
                    st.rerun()

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["user"] = None
            st.session_state["current_solution"] = None
            st.rerun()

        st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 0.75rem; margin-top: 20px;">
            ApexSolve v2.0 • Designed for Students<br>
            Maths & Reasoning Engine
        </div>
        """, unsafe_allow_html=True)

        return menu


# 6. View: AI Solver
def render_solver_view():
    user = st.session_state["user"]
    st.markdown("""
    <div>
        <div class="hero-badge">📐 Instant Math & Reasoning Solver</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Solve Any Mathematics or Logical Problem</h2>
        <p class="sub-title">Type a question, pick an example, or upload an image to receive a rigorous step-by-step proof and similar practice problems.</p>
    </div>
    """, unsafe_allow_html=True)

    # Category selector and presets
    col_mode, col_presets = st.columns([1, 2])
    with col_mode:
        preferred_cat = st.selectbox(
            "Select Problem Domain",
            ["Auto-Detect", "Mathematics", "Reasoning"],
            help="Choose the problem domain or let AI auto-detect"
        )

    with col_presets:
        st.markdown("<div style='font-size:0.85rem; color:#94a3b8; margin-bottom:4px;'>💡 Quick Test Examples:</div>", unsafe_allow_html=True)
        ex_col1, ex_col2, ex_col3, ex_col4 = st.columns(4)
        preset_question = None
        if ex_col1.button("Algebra", use_container_width=True):
            preset_question = "Find the roots of 3x^2 - 10x + 3 = 0 using factorization and quadratic formula."
        if ex_col2.button("Calculus", use_container_width=True):
            preset_question = "Evaluate the definite integral of (3x^2 + 2x - 5) dx from x = 1 to x = 3."
        if ex_col3.button("Series", use_container_width=True):
            preset_question = "Find the missing number in the sequence: 4, 9, 19, 39, 79, ?"
        if ex_col4.button("Relations", use_container_width=True):
            preset_question = "A is the brother of B. B is the daughter of C. D is the father of C. How is A related to D?"

    if not solver.is_api_key_configured():
        st.warning("⚠️ **Gemini API Key is needed for live solution generation.**")
        st.caption("💡 Enter your free Gemini API key below to unlock instant solving for this session:")
        c_sk1, c_sk2 = st.columns([3, 1])
        with c_sk1:
            solver_k = st.text_input("Gemini API Key:", type="password", placeholder="Paste API Key here...", key="solver_key_input")
        with c_sk2:
            st.write("")
            if st.button("🚀 Activate Key", use_container_width=True, key="solver_activate_btn"):
                if solver_k.strip():
                    st.session_state["gemini_api_key"] = solver_k.strip()
                    import os
                    os.environ["GEMINI_API_KEY"] = solver_k.strip()
                    st.success("API Key successfully activated!")
                    st.rerun()

    # Question Input
    default_text = preset_question if preset_question else st.session_state["current_question_text"]
    q_input = st.text_area(
        "Enter your Math or Reasoning Question:",
        value=default_text,
        height=110,
        placeholder="e.g. Solve: If 6 men can complete a work in 12 days, how many men are needed to complete the work in 8 days? Or paste a reasoning series..."
    )

    # Optional image upload
    uploaded_image = st.file_uploader("📷 Upload Problem Image (Optional)", type=["png", "jpg", "jpeg"])
    pil_image = None
    if uploaded_image:
        pil_image = Image.open(uploaded_image)
        st.image(pil_image, caption="Uploaded Problem Image", width=320)

    # Action Buttons
    col_solve, col_clear = st.columns([1, 4])
    with col_solve:
        solve_pressed = st.button("⚡ Solve with Detail", type="primary", use_container_width=True)

    if solve_pressed:
        if not q_input.strip() and not pil_image:
            st.warning("Please type a question or upload an image.")
        else:
            with st.spinner("🧠 Analyzing problem, verifying theorems, and generating step-by-step breakdown..."):
                success, data, msg = solver.solve_question(
                    question_text=q_input,
                    image_file=pil_image,
                    preferred_category=preferred_cat
                )

                if success:
                    st.session_state["current_solution"] = data
                    st.session_state["current_question_text"] = q_input
                    # Save to database
                    qid = database.save_solved_question(
                        user_id=user["id"],
                        category=data.get("category", "Mathematics"),
                        topic=data.get("topic", "General"),
                        question_text=q_input if q_input.strip() else "[Image Problem]",
                        solution_markdown=json.dumps(data),
                        practice_problems=data.get("practice_problems", [])
                    )
                    st.session_state["saved_question_id"] = qid
                    st.success("✅ Solution formulated and stored in your Learning Archive!")
                else:
                    st.error(f"❌ Error: {msg}")

    # Display Current Solution
    solution_data = st.session_state.get("current_solution")
    if solution_data:
        st.markdown("---")
        render_solution_card(solution_data, user["id"])


def render_solution_card(sol: dict, user_id: int):
    """Renders a fully detailed, structured solution card."""
    category = sol.get("category", "Mathematics")
    topic = sol.get("topic", "General")
    difficulty = sol.get("difficulty", "Standard")
    cat_icon = "📐" if category == "Mathematics" else "🧠"

    # Meta header
    st.markdown(f"""
    <div style="display: flex; gap: 8px; align-items: center; margin-bottom: 12px;">
        <span style="background: rgba(99, 102, 241, 0.2); color: #a5b4fc; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">
            {cat_icon} {category}
        </span>
        <span style="background: rgba(16, 185, 129, 0.15); color: #6ee7b7; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">
            🏷️ Topic: {topic}
        </span>
        <span style="background: rgba(245, 158, 11, 0.15); color: #fcd34d; padding: 4px 12px; border-radius: 6px; font-weight: 600; font-size: 0.85rem;">
            ⚡ Level: {difficulty}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Core Concept Box
    core_concept = sol.get("core_concept")
    if core_concept:
        st.markdown(f"""
        <div class="concept-card">
            <b style="color: #818cf8;">🎯 Core Concept / Governing Principle:</b><br>
            <span style="color: #cbd5e1;">{core_concept}</span>
        </div>
        """, unsafe_allow_html=True)

    # Key formulas if any
    formulas = sol.get("key_formulas", [])
    if formulas:
        st.markdown("**Key Mathematical Laws / Formulas Applied:**")
        for f in formulas:
            st.latex(f)

    # Step-by-Step Breakdown
    st.markdown("### 🪜 Step-by-Step Rigorous Explanation")
    steps = sol.get("step_by_step_solution", [])
    for idx, s in enumerate(steps, 1):
        step_title = s.get("step_title", f"Step {idx}")
        explanation = s.get("explanation", "")
        math_expr = s.get("math_expression", "")

        st.markdown(f"""
        <div class="step-card">
            <b style="color: #818cf8; font-size: 1rem;">Step {idx}: {step_title}</b>
            <div style="color: #e2e8f0; margin-top: 6px; line-height: 1.6;">{explanation}</div>
        </div>
        """, unsafe_allow_html=True)

        if math_expr and math_expr.strip():
            # If standard latex format
            if "$$" in math_expr:
                st.markdown(math_expr)
            else:
                st.latex(math_expr)

    # Final Answer Card
    final_ans = sol.get("final_answer", "")
    st.markdown(f"""
    <div class="final-answer-card">
        <div style="color: #34d399; font-weight: 700; font-size: 1.1rem; margin-bottom: 4px;">
            ✅ Final Answer:
        </div>
        <div style="font-size: 1.25rem; font-weight: 700; color: #ffffff;">
            {final_ans}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Pro Tip Card
    pro_tip = sol.get("pro_tip")
    if pro_tip:
        st.markdown(f"""
        <div class="tip-card">
            <b style="color: #fbbf24;">💡 Student Pro Tip / Speed Shortcut:</b><br>
            <span style="color: #e2e8f0;">{pro_tip}</span>
        </div>
        """, unsafe_allow_html=True)

    # Practice Problems Section
    practice_problems = sol.get("practice_problems", [])
    if practice_problems:
        st.markdown("---")
        st.markdown("""
        <div>
            <span class="hero-badge">🎯 Reinforce Your Learning</span>
            <h3 style="margin-top: 4px;">Similar Practice Problems</h3>
            <p style="color: #94a3b8; font-size: 0.9rem;">Test your understanding immediately on these similar questions carefully crafted to test this exact concept.</p>
        </div>
        """, unsafe_allow_html=True)

        for p_idx, prob in enumerate(practice_problems, 1):
            with st.container():
                st.markdown(f"""
                <div class="practice-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="color: #a5b4fc; font-size: 1rem;">Exercise #{p_idx}: {prob.get('level', 'Practice')}</b>
                    </div>
                    <div style="color: #f1f5f9; font-size: 1.05rem; margin: 10px 0; font-weight: 500;">
                        {prob.get('question', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Student Interactive Attempt
                col_ans, col_btn = st.columns([3, 1])
                user_ans_key = f"attempt_ans_{p_idx}_{prob.get('id', p_idx)}"
                with col_ans:
                    student_guess = st.text_input("Your Answer:", placeholder="Enter your calculated answer...", key=user_ans_key)
                with col_btn:
                    st.write("") # spacing
                    verify_clicked = st.button("Check Answer", key=f"btn_check_{p_idx}")

                if verify_clicked:
                    expected = str(prob.get("correct_answer", "")).strip().lower()
                    attempt = str(student_guess).strip().lower()
                    if not attempt:
                        st.warning("Please type an answer to check.")
                    else:
                        # Simple match check
                        is_match = (attempt == expected) or (expected in attempt) or (attempt in expected)
                        database.log_practice_attempt(
                            user_id=user_id,
                            question_id=st.session_state.get("saved_question_id"),
                            problem_text=prob.get("question", ""),
                            student_answer=student_guess,
                            correct_answer=prob.get("correct_answer", ""),
                            is_correct=is_match
                        )
                        if is_match:
                            st.success(f"🎉 Excellent! Correct answer: {prob.get('correct_answer')}")
                        else:
                            st.error(f"❌ Not quite. Expected: {prob.get('correct_answer')}")

                # Hint and Full solution expanders
                h_col, s_col = st.columns(2)
                with h_col:
                    with st.expander("💡 Need a Hint?"):
                        st.info(prob.get("hint", "Break down the problem using the step-by-step logic shown above."))
                with s_col:
                    with st.expander("📖 View Full Solution"):
                        st.markdown(prob.get("step_by_step_solution", "Solution not available."))


# 7. View: Practice Arena
def render_practice_arena_view():
    user = st.session_state["user"]
    st.markdown("""
    <div>
        <div class="hero-badge">🎯 Interactive Arena</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Practice & Mastery Arena</h2>
        <p class="sub-title">Generate unlimited customized practice problems in specific topics to sharpen your problem-solving speed.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        arena_domain = st.selectbox("Topic Category", ["Mathematics", "Reasoning"])
    with col2:
        if arena_domain == "Mathematics":
            arena_topic = st.selectbox("Math Topic", ["Algebra & Quadratics", "Calculus & Derivatives", "Integration", "Trigonometry", "Probability & Statistics", "Arithmetic & Percentages", "Coordinate Geometry"])
        else:
            arena_topic = st.selectbox("Reasoning Topic", ["Number & Letter Series", "Syllogisms & Venn Logic", "Blood Relations", "Direction Sense", "Coding-Decoding", "Seating Arrangement", "Mathematical Puzzles"])
    with col3:
        arena_level = st.selectbox("Difficulty", ["Foundation / Beginner", "Standard / Intermediate", "Advanced / Challenge"])

    if not solver.is_api_key_configured():
        st.warning("⚠️ **Gemini API Key is needed for live problem generation.**")
        st.caption("💡 Enter your free Gemini API key below to unlock instant generation for this session:")
        c_k1, c_k2 = st.columns([3, 1])
        with c_k1:
            arena_k = st.text_input("Gemini API Key:", type="password", placeholder="Paste API Key here...", key="arena_key_input")
        with c_k2:
            st.write("")
            if st.button("🚀 Activate Key", use_container_width=True, key="arena_activate_btn"):
                if arena_k.strip():
                    st.session_state["gemini_api_key"] = arena_k.strip()
                    import os
                    os.environ["GEMINI_API_KEY"] = arena_k.strip()
                    st.success("API Key successfully activated!")
                    st.rerun()

    if st.button("✨ Generate New Practice Challenge", type="primary", use_container_width=True):
        # Build a full, canonical practice question per topic so AI returns proper structured JSON
        ARENA_TOPIC_QUESTIONS = {
            # Mathematics
            "Algebra & Quadratics": "Solve the quadratic equation 2x² - 5x - 3 = 0 using the quadratic formula. Find both roots and verify by substitution.",
            "Calculus & Derivatives": "Differentiate f(x) = 3x³ - 5x² + 7x - 2 with respect to x. Also find the value of f'(2).",
            "Integration": "Evaluate the definite integral of (4x³ - 6x + 2) dx from x = 0 to x = 2.",
            "Trigonometry": "Prove that sin²θ + cos²θ = 1 and use it to find sin θ if cos θ = 3/5 (θ in first quadrant).",
            "Probability & Statistics": "A bag contains 4 red, 3 blue, and 5 green balls. Two balls are drawn at random without replacement. Find the probability that both balls are red.",
            "Arithmetic & Percentages": "A shopkeeper marks his goods 40% above cost price and allows a discount of 20%. What is the percentage profit or loss?",
            "Coordinate Geometry": "Find the equation of the straight line passing through (3, -2) and (7, 4). Also find its slope and y-intercept.",
            # Reasoning
            "Number & Letter Series": "Find the next term in the series: 2, 6, 12, 20, 30, ?",
            "Syllogisms & Venn Logic": "All dogs are animals. Some animals are cats. Conclusion I: Some dogs are cats. Conclusion II: All animals are dogs. Which conclusions logically follow?",
            "Blood Relations": "Pointing to a man in a photograph, a woman said 'His mother is the only daughter of my mother.' How is the woman related to the man?",
            "Direction Sense": "Ravi walks 10 km north, turns right and walks 5 km, then turns right again and walks 10 km. How far is he from the starting point and in which direction?",
            "Coding-Decoding": "In a certain code language, COMPUTER is written as RFUVQNPC. Using the same logic, decode the word RPTUFE.",
            "Seating Arrangement": "Six people A, B, C, D, E, F sit in a row. A is at one end. B sits immediately to the right of C. D is not next to A. E is between F and D. Find the seating arrangement.",
            "Mathematical Puzzles": "A farmer has chickens and cows. He counts 50 heads and 140 legs in total. How many chickens and cows does he have?"
        }
        # Choose a canonical question that fits the selected topic and difficulty level
        base_q = ARENA_TOPIC_QUESTIONS.get(
            arena_topic,
            f"Create and solve a {arena_level} level {arena_domain} problem from the topic: {arena_topic}."
        )
        # Embed the difficulty level context in the prompt
        difficulty_hint = {
            "Foundation / Beginner": "Treat this as a Foundation level question. Keep explanations extremely simple and beginner-friendly.",
            "Standard / Intermediate": "Treat this as a Standard/Intermediate level question. Include moderate complexity.",
            "Advanced / Challenge": "Treat this as an Advanced/Competitive level question (JEE/SSC/CAT style). Maximize rigor and complexity."
        }.get(arena_level, "")
        prompt_q = f"{base_q}\n\n{difficulty_hint}"

        with st.spinner("🧠 Generating challenge with step-by-step solution and practice problems..."):
            ok, data, msg = solver.solve_question(prompt_q, preferred_category=arena_domain)
            if ok:
                st.session_state["arena_challenge"] = data
                st.session_state["arena_last_error"] = None
            else:
                st.session_state["arena_last_error"] = msg
                st.error(f"❌ Generation error: {msg}")

    challenge = st.session_state.get("arena_challenge")
    if challenge:
        st.markdown("---")
        render_solution_card(challenge, user["id"])


# 8. View: Concept Handbook
def render_handbook_view():
    st.markdown("""
    <div>
        <div class="hero-badge">📚 Instant Revision</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Student Concept & Formula Pocketbook</h2>
        <p class="sub-title">High-yield mathematical formulas and reasoning shortcuts at your fingertips.</p>
    </div>
    """, unsafe_allow_html=True)

    hb_tab1, hb_tab2 = st.tabs(["📐 Pure Mathematics Formulas", "🧠 Logical Reasoning Rules"])

    with hb_tab1:
        for section_title, formula_list in formula_book.MATH_FORMULAS.items():
            with st.expander(f"📌 {section_title}", expanded=True):
                for item in formula_list:
                    st.markdown(f"**{item['name']}**")
                    st.latex(item["formula"].replace("$$", ""))
                    st.caption(f"📝 {item['desc']}")
                    st.markdown("---")

    with hb_tab2:
        for section_title, rules_list in formula_book.REASONING_CONCEPTS.items():
            with st.expander(f"🧩 {section_title}", expanded=True):
                for item in rules_list:
                    st.markdown(f"**{item['name']}**")
                    st.code(item["rule"], language="text")
                    st.caption(f"📝 {item['desc']}")
                    st.markdown("---")


# 9. View: Saved History & Bookmarks
def render_history_view():
    user = st.session_state["user"]
    st.markdown("""
    <div>
        <div class="hero-badge">🕒 Learning Archive</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Saved Questions & Revision Hub</h2>
        <p class="sub-title">Review previously solved questions, bookmark challenging problems, and export notes.</p>
    </div>
    """, unsafe_allow_html=True)

    # Filters
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    with col_f1:
        cat_filter = st.selectbox("Filter Category", ["All", "Mathematics", "Reasoning"])
    with col_f2:
        bookmarked_filter = st.checkbox("⭐ Bookmarked Only", value=False)
    with col_f3:
        search_kw = st.text_input("🔍 Search question or topic...", placeholder="Type keywords...")

    history = database.get_user_history(
        user_id=user["id"],
        category_filter=cat_filter,
        search_query=search_kw,
        bookmarked_only=bookmarked_filter
    )

    if not history:
        st.info("No saved questions found matching your filter criteria. Go to 'AI Solver' to solve your first question!")
        return

    st.caption(f"Showing {len(history)} saved questions")

    for q in history:
        qid = q["id"]
        is_bookmarked = (q["is_bookmarked"] == 1)
        star_icon = "⭐" if is_bookmarked else "☆"

        with st.expander(f"{star_icon} [{q['category']}] {q['topic']} — {q['question_text'][:80]}...", expanded=False):
            st.markdown(f"**Full Question:** {q['question_text']}")
            st.caption(f"Saved on: {q['created_at']}")

            col_actions = st.columns([1, 1, 1, 3])
            with col_actions[0]:
                btn_bm_label = "Unstar" if is_bookmarked else "⭐ Bookmark"
                if st.button(btn_bm_label, key=f"hist_bm_{qid}"):
                    database.toggle_bookmark(qid, user["id"])
                    st.rerun()
            with col_actions[1]:
                if st.button("🗑️ Delete", key=f"hist_del_{qid}"):
                    database.delete_question(qid, user["id"])
                    st.success("Deleted from history.")
                    st.rerun()
            with col_actions[2]:
                if st.button("🚀 Load into Solver", key=f"hist_load_{qid}"):
                    st.session_state["current_question_text"] = q["question_text"]
                    try:
                        st.session_state["current_solution"] = json.loads(q["solution_markdown"])
                    except Exception:
                        pass
                    st.success("Loaded! Switch to 'AI Solver' tab.")

            st.markdown("---")
            # Parse solution data
            try:
                sol_obj = json.loads(q["solution_markdown"])
                render_solution_card(sol_obj, user["id"])
            except Exception:
                st.markdown(q["solution_markdown"])


# 10. View: Student Analytics
def render_analytics_view():
    user = st.session_state["user"]
    st.markdown("""
    <div>
        <div class="hero-badge">📊 Personal Dashboard</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Student Performance Analytics</h2>
        <p class="sub-title">Track your problem-solving momentum and practice accuracy over time.</p>
    </div>
    """, unsafe_allow_html=True)

    stats = database.get_student_dashboard_stats(user["id"])

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Solved", stats["total_questions"], delta="Saved in Archive")
    m2.metric("Math Questions", stats["math_questions"], delta="📐 Pure Math")
    m3.metric("Reasoning Questions", stats["reasoning_questions"], delta="🧠 Logic & Series")
    m4.metric("Practice Accuracy", f"{stats['practice_accuracy']}%", delta=f"{stats['practice_correct']}/{stats['practice_attempts']} Correct")

    st.markdown("---")

    col_chart, col_study = st.columns(2)
    with col_chart:
        st.markdown("### 📈 Practice Engagement")
        st.write(f"- **Total Practice Exercises Attempted:** {stats['practice_attempts']}")
        st.write(f"- **Correct Answers on First Try:** {stats['practice_correct']}")
        st.write(f"- **Bookmarked for Revision:** {stats['bookmarked_questions']}")

        progress_val = min(1.0, stats["practice_accuracy"] / 100.0) if stats["practice_attempts"] > 0 else 0.0
        st.progress(progress_val)
        st.caption(f"Mastery Score: {stats['practice_accuracy']}%")

    with col_study:
        st.markdown("### 🎯 Recommended Daily Routine")
        st.info("""
        1. **Solve 3 Math Concept Questions** (Algebra / Calculus / Geometry) daily.
        2. **Complete all generated Practice Problems** immediately after reading the solution.
        3. **Review Bookmarked Questions** every Sunday before exam day.
        4. **Consult Concept Pocketbook** for high-frequency formulas and alphabet shortcut rules.
        """)


# 11. View: Profile Settings
def render_profile_view():
    user = st.session_state["user"]
    st.markdown("""
    <div>
        <div class="hero-badge">⚙️ Account Settings</div>
        <h2 class="main-title" style="font-size: 1.8rem;">Student Profile & Preferences</h2>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Update Profile")
        edit_name = st.text_input("Full Name", value=user["name"])
        edit_exam = st.selectbox(
            "Target Examination",
            ["JEE Mains & Advanced", "SSC CGL / Banking / Railways", "CAT / Management Aptitude", "Olympiad / High School", "University / College Degree", "General Aptitude"],
            index=0
        )

        if st.button("💾 Save Profile Changes", type="primary"):
            ok, msg = database.update_user_profile(user["id"], edit_name, edit_exam)
            if ok:
                user["name"] = edit_name
                user["target_exam"] = edit_exam
                st.session_state["user"] = user
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with col2:
        st.markdown("### 🎓 About ApexSolve")
        st.markdown("""
        **ApexSolve** is an advanced AI Math & Logical Reasoning system engineered specifically for students, competitive exam aspirants, and academic self-learners.

        - **Lead Developer:** Naman Shukla
        - **Contact / Feedback:** `namanshukla9889@gmail.com`
        - **Core AI Engine:** Google Gemini (High Precision Flash Models)
        - **Security:** Bcrypt Password Hashing + SQLite Local Database
        - **Formula Rendering:** Standard LaTeX & KaTeX
        """)


# 12. Main Controller
def main():
    if not st.session_state["user"]:
        render_auth_page()
    else:
        render_top_navbar()
        selected_menu = render_sidebar()

        if selected_menu == "🚀 AI Solver":
            render_solver_view()
        elif selected_menu == "🎯 Practice Arena":
            render_practice_arena_view()
        elif selected_menu == "📚 Concept Handbook":
            render_handbook_view()
        elif selected_menu == "🕒 Saved History":
            render_history_view()
        elif selected_menu == "📊 My Analytics":
            render_analytics_view()
        elif selected_menu == "⚙️ Profile Settings":
            render_profile_view()


if __name__ == "__main__":
    main()
