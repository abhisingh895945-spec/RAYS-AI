import streamlit as st
from rembg import remove
from PIL import Image
import io
import subprocess
import os
import tempfile
import shutil
import requests
import json
import urllib.parse

# Optional heavy library imports with error handling
try:
    import cv2
    import numpy as np
    HAS_OPENCV = True
except ImportError:
    HAS_OPENCV = False

try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


# ---------- Helper: Universal AI Call via OpenRouter (100% FREE & FAST) ----------
def call_claude(prompt, system=None, max_tokens=1500):
    """Send a prompt to OpenRouter API using free open-source models."""
    api_key = st.secrets.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        return None, "AI features setup nahi hain (secrets.toml mein OPENROUTER_API_KEY missing hai)."

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Rays AI Suite"
    }

    # OpenRouter Free Models to try in fallback order
    free_models = [
        "meta-llama/llama-3.1-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-2-9b-it:free"
    ]

    messages = []
    if system and system.strip():
        messages.append({"role": "system", "content": system.strip()})
    messages.append({"role": "user", "content": prompt})

    last_error = ""
    for model_name in free_models:
        body = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens
        }

        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    text = choices[0].get("message", {}).get("content", "")
                    if text:
                        return text, None
            else:
                last_error = resp.json().get("error", {}).get("message", resp.text)
        except Exception as e:
            last_error = str(e)

    return None, f"OpenRouter API Error: {last_error if last_error else 'Unable to connect to OpenRouter models.'}"


# ---------- Helper: Extract Text from PDF ----------
def extract_text_from_pdf(pdf_file):
    if not HAS_PYPDF:
        return None, "pypdf library missing. Please add 'pypdf' to requirements.txt"
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text, None
    except Exception as e:
        return None, str(e)


# ---------- Helper: find LibreOffice on any OS ----------
def find_soffice():
    """Return a runnable soffice command, checking PATH then common install locations."""
    if shutil.which("soffice"):
        return "soffice"
    common_paths = [
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        "/usr/bin/soffice",
        "/opt/libreoffice/program/soffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("soffice not found")


# ---------- Page setup ----------
st.set_page_config(
    page_title="Rays AI - Ultimate Suite & Tools",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)


# ---------- Password Protection ----------
def check_password():
    """Show a branded welcome + password box; only let the rest of the app render if correct."""

    def password_entered():
        correct_pwd = st.secrets.get("APP_PASSWORD", "raysai123")
        if st.session_state.get("password_input") == correct_pwd:
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at top, #1a1a2e 0%, #0F0F13 65%);
        }
        .welcome-wrap {
            text-align: center;
            padding-top: 3rem;
        }
        .welcome-logo {
            font-size: 4.5rem;
            margin-bottom: 0.1rem;
            text-shadow: 0 0 20px rgba(127,90,240,0.6);
        }
        .welcome-title {
            font-size: 2.8rem;
            font-weight: 800;
            color: #FFFFFE;
            margin-bottom: 0.2rem;
        }
        .welcome-title span {
            background: linear-gradient(90deg, #7F5AF0, #2CB67D);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .welcome-sub {
            color: #9CA3AF;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        </style>
        <div class="welcome-wrap">
            <div class="welcome-logo">⚡</div>
            <div class="welcome-title">Welcome to <span>RAYS AI</span></div>
            <div class="welcome-sub">Enter password to unlock dashboard</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input(
            "Password",
            type="password",
            key="password_input",
            on_change=password_entered,
            label_visibility="collapsed",
            placeholder="Enter access key...",
        )
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Incorrect password.")
    return False


if not check_password():
    st.stop()


# ---------- Styling (CSS) ----------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e 0%, #0F0F13 60%);
    }

    /* Navbar */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.5rem;
    }
    .navbar-logo {
        font-size: 1.6rem;
        font-weight: 900;
        color: #FFFFFE;
        letter-spacing: 1px;
    }
    .navbar-logo span {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .navbar-badge {
        font-size: 0.8rem;
        color: #2CB67D;
        border: 1px solid #2CB67D;
        border-radius: 999px;
        padding: 0.2rem 0.8rem;
        font-weight: 600;
    }

    /* Front Hero Banner */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .hero-logo-big {
        font-size: 4rem;
        line-height: 1;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0px 0px 15px rgba(127, 90, 240, 0.8));
    }
    .hero-title {
        font-size: 2.8rem;
        font-weight: 900;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -1px;
    }
    .hero-title span {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-desc {
        color: #9CA3AF;
        font-size: 1.05rem;
        margin-top: 0.5rem;
    }

    /* Cards */
    .tool-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    }

    /* Square Logobox Design Theme */
    .square-card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
        padding: 1rem 0;
    }
    .square-logobox {
        width: 120px;
        height: 120px;
        border-radius: 16px;
        background: linear-gradient(135deg, rgba(127,90,240,0.15), rgba(44,182,125,0.15));
        border: 2px solid #7F5AF0;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        text-decoration: none !important;
        box-shadow: 0 0 15px rgba(127,90,240,0.2);
    }
    .square-logobox:hover {
        transform: scale(1.08);
        border-color: #2CB67D;
        box-shadow: 0 0 25px rgba(44,182,125,0.4);
    }
    .square-icon {
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .square-label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #FFFFFF;
        text-align: center;
    }

    /* Custom Link Buttons */
    .portal-card {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        transition: all 0.3s ease;
        text-decoration: none !important;
    }
    .portal-card:hover {
        background: rgba(127,90,240,0.15);
        border-color: #7F5AF0;
        transform: translateY(-2px);
    }
    .portal-title {
        color: #FFFFFF;
        font-size: 1.05rem;
        font-weight: 700;
    }
    .portal-sub {
        color: #9CA3AF;
        font-size: 0.85rem;
    }

    /* Buttons */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.4rem;
        font-weight: 600;
        width: 100%;
        transition: opacity 0.2s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        opacity: 0.88;
        color: white;
    }

    /* File Uploader */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
        border: 1.5px dashed rgba(127,90,240,0.5);
        background: rgba(127,90,240,0.05);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #16161A;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    .footer-note {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Top Navbar ----------
st.markdown("""
    <div class="navbar">
        <div class="navbar-logo">⚡ <span>RAYS AI</span></div>
        <div class="navbar-badge">v3.0 PRO</div>
    </div>
""", unsafe_allow_html=True)

# ---------- BIG RAYS AI FRONT LOGO HEADER ----------
st.markdown("""
    <div class="hero-container">
        <div class="hero-logo-big">⚡</div>
        <div class="hero-title">RAYS <span>AI</span></div>
        <div class="hero-desc">All-in-One AI Tools, Converters & Learning Portals</div>
    </div>
""", unsafe_allow_html=True)

# ---------- Sidebar Menu ----------
st.sidebar.markdown("### 🛠️ Navigation Menu")
tool = st.sidebar.radio(
    "Choose a tool",
    [
        "🔳 Square Logo Hub",
        "🔗 Study & Resource Portals",
        "🧮 Math Calculator",
        "🖊️ Digital Whiteboard",
        "🗂️ Flashcard Generator",
        "💬 Doubt Solver",
        "🎨 Text-to-Image Generator",
        "📝 Text & PDF Summarizer",
        "🌐 Language Translator",
        "🔊 Text-to-Voice (TTS)",
        "📄 Resume / CV Analyzer",
        "👤 Face Detection",
        "🖼️ Background Remover",
        "📄 Word to PDF",
        "📝 PDF to Word",
        "📢 Job Notifications",
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Rays AI Engine • 2026")

# =========================================================
# TOOL 1: SQUARE LOGOBOX HUB
# =========================================================
if tool == "🔳 Square Logo Hub":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🔳 Square Logobox Dashboard")
    st.markdown("Quick access square icons for major portals.")

    st.markdown("""
        <div class="square-card-container">
            <a href="https://www.youtube.com/@ArcRays" target="_blank" class="square-logobox">
                <div class="square-icon">📺</div>
                <div class="square-label">ArcRays YT</div>
            </a>
            <a href="https://studypanda.live/" target="_blank" class="square-logobox">
                <div class="square-icon">📚</div>
                <div class="square-label">StudyPanda</div>
            </a>
            <a href="https://pwthor.live/" target="_blank" class="square-logobox">
                <div class="square-icon">⚡</div>
                <div class="square-label">PW Thor</div>
            </a>
            <a href="https://rarestudy.in/" target="_blank" class="square-logobox">
                <div class="square-icon">📖</div>
                <div class="square-label">RareStudy</div>
            </a>
            <a href="https://studybeepro.site/" target="_blank" class="square-logobox">
                <div class="square-icon">🐝</div>
                <div class="square-label">StudyBee</div>
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 2: CUSTOM WEBSITES PORTAL
# =========================================================
elif tool == "🔗 Study & Resource Portals":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Quick Access Links & Portals")
    st.markdown("Direct portal shortcuts added for quick redirection.")

    links = [
        ("📺 ArcRays YouTube", "https://www.youtube.com/@ArcRays", "Official YouTube Channel"),
        ("📚 StudyPanda", "https://studypanda.live/", "Live Study Platform"),
        ("⚡ PW Thor Live", "https://pwthor.live/", "Streaming & Learning Portal"),
        ("📖 RareStudy Portal", "https://rarestudy.in/", "Educational Resources"),
        ("⚡ Lite PW4Free", "https://lite.pw4free.in/", "Free Learning Materials"),
        ("🐝 StudyBee Pro", "https://studybeepro.site/", "Pro Learning Site"),
        ("📺 Stream TestUK", "https://stream.testuk.org/", "Streaming Test Server"),
    ]

    for title, url, desc in links:
        st.markdown(f"""
            <a href="{url}" target="_blank" class="portal-card">
                <div>
                    <div class="portal-title">{title}</div>
                    <div class="portal-sub">{desc}</div>
                </div>
                <div style="color:#7F5AF0; font-weight:bold;">Visit ↗</div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 3: MATH CALCULATOR
# =========================================================
elif tool == "🧮 Math Calculator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🧮 Math Calculator (Step-by-Step)")
    st.markdown("Type any math problem to receive complete step-by-step working.")

    problem = st.text_area(
        "Enter your math problem",
        placeholder="e.g. Solve for x: 2x + 5 = 17\nor: Find derivative of x^3 + 2x",
        height=100,
    )

    if st.button("Solve step-by-step"):
        if not problem.strip():
            st.warning("Please enter a math problem first.")
        else:
            with st.spinner("Solving... 🧠"):
                answer, error = call_claude(
                    prompt=problem,
                    system=(
                        "You are a patient math tutor. Always solve the problem showing "
                        "every step clearly, explaining the reasoning in simple language, "
                        "and give the final answer clearly marked at the end."
                    ),
                )
            if error:
                st.error(f"Couldn't solve problem: {error}")
            else:
                st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 4: DIGITAL WHITEBOARD
# =========================================================
elif tool == "🖊️ Digital Whiteboard":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🖊️ Digital Whiteboard Notes")
    st.markdown("Generates structured whiteboard diagrams and revision notes on any topic.")

    topic = st.text_input("Enter a topic", placeholder="e.g. Photosynthesis, Newton's Laws, Organic Chemistry")

    if st.button("Generate whiteboard notes"):
        if not topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Generating whiteboard layout... ✏️"):
                answer, error = call_claude(
                    prompt=f"Explain the topic: {topic}",
                    system=(
                        "You are a teacher creating whiteboard-style notes. Structure your "
                        "response like a visual diagram using markdown: a short definition, "
                        "then a tree/branch structure (using headings, bullet points, and "
                        "indentation) showing key concepts, sub-points, and how they connect."
                    ),
                )
            if error:
                st.error(f"Couldn't generate whiteboard notes: {error}")
            else:
                st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 5: FLASHCARD GENERATOR
# =========================================================
elif tool == "🗂️ Flashcard Generator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🗂️ Flashcard Generator")
    st.markdown("Create custom Q&A flashcards for quick revision.")

    fc_topic = st.text_input("Topic", placeholder="e.g. Physics Formulas, Indian History, Python Functions")
    num_cards = st.slider("Number of flashcards", 3, 15, 6)

    if st.button("Generate Flashcards"):
        if not fc_topic.strip():
            st.warning("Please enter a topic first.")
        else:
            with st.spinner("Creating flashcards... 🗂️"):
                answer, error = call_claude(
                    prompt=f"Create {num_cards} flashcards on the topic: {fc_topic}",
                    system=(
                        "Generate flashcards for studying. Reply with ONLY valid JSON, "
                        "no other text, no markdown code fences. Format: "
                        '[{"question": "...", "answer": "..."}, ...]'
                    ),
                )
            if error:
                st.error(f"Couldn't generate flashcards: {error}")
            else:
                try:
                    clean = answer.strip().strip("`").replace("json\n", "", 1)
                    cards = json.loads(clean)
                    for i, card in enumerate(cards, 1):
                        with st.expander(f"Card {i}: {card.get('question', '')}"):
                            st.write(card.get("answer", ""))
                except Exception:
                    st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 6: DOUBT SOLVER CHATBOT
# =========================================================
elif tool == "💬 Doubt Solver":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 💬 Doubt Solver Chatbot")
    st.markdown("Ask any study or homework doubt for instant, clear explanation.")

    if "doubt_chat" not in st.session_state:
        st.session_state.doubt_chat = []

    for msg in st.session_state.doubt_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_msg = st.chat_input("Ask your doubt here...")
    if user_msg:
        st.session_state.doubt_chat.append({"role": "user", "content": user_msg})
        with st.chat_message("user"):
            st.markdown(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                convo = "\n\n".join(
                    f"{m['role'].upper()}: {m['content']}" for m in st.session_state.doubt_chat
                )
                answer, error = call_claude(
                    prompt=convo,
                    system=(
                        "You are a friendly, patient homework helper for students. "
                        "Explain concepts clearly and simply, use examples, and guide "
                        "the student step-by-step."
                    ),
                )
            if error:
                st.error(f"Error: {error}")
            else:
                st.markdown(answer)
                st.session_state.doubt_chat.append({"role": "assistant", "content": answer})

    if st.session_state.doubt_chat:
        if st.button("Clear Chat"):
            st.session_state.doubt_chat = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 7: TEXT-TO-IMAGE GENERATOR
# =========================================================
elif tool == "🎨 Text-to-Image Generator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🎨 AI Text-to-Image Generator")
    st.markdown("Generate high-quality AI artwork instantly from text prompt.")

    img_prompt = st.text_area("Describe the image you want to generate", placeholder="e.g. A futuristic cybernetic tiger in neon cyberpunk city, 8k wallpaper")
    col_a, col_b = st.columns(2)
    with col_a:
        img_width = st.selectbox("Width", [1024, 768, 512], index=0)
    with col_b:
        img_height = st.selectbox("Height", [1024, 768, 512], index=0)

    if st.button("🚀 Generate Image"):
        if not img_prompt.strip():
            st.warning("Please enter an image prompt first.")
        else:
            with st.spinner("Rendering your AI image... 🎨"):
                encoded_prompt = urllib.parse.quote(img_prompt.strip())
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={img_width}&height={img_height}&nologo=true"
                
                try:
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        img_bytes = response.content
                        st.image(img_bytes, caption=img_prompt, use_container_width=True)
                        st.download_button(
                            "⬇️ Download Image",
                            data=img_bytes,
                            file_name="rays_ai_generated.png",
                            mime="image/png"
                        )
                        st.success("Image generated successfully!")
                    else:
                        st.error("Failed to generate image. Please try again.")
                except Exception as e:
                    st.error(f"Error generating image: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 8: TEXT & PDF SUMMARIZER
# =========================================================
elif tool == "📝 Text & PDF Summarizer":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📝 Text & PDF Summarizer")
    st.markdown("Summarize long articles, notes, or uploaded PDF documents into structured key points.")

    sum_option = st.radio("Choose Input Method:", ["Paste Text", "Upload PDF"], horizontal=True)
    raw_text = ""

    if sum_option == "Paste Text":
        raw_text = st.text_area("Paste long text here", height=200, placeholder="Paste your article or notes...")
    else:
        uploaded_pdf = st.file_uploader("Upload PDF Document", type=["pdf"])
        if uploaded_pdf:
            extracted, err = extract_text_from_pdf(uploaded_pdf)
            if err:
                st.error(f"Error reading PDF: {err}")
            else:
                raw_text = extracted
                st.success(f"PDF Loaded Successfully ({len(raw_text)} characters extracted)")

    summary_type = st.selectbox("Summary Format", ["Bullet Points & Key Takeaways", "Short Executive Summary", "Detailed Section-by-Section"])

    if st.button("✨ Summarize Document"):
        if not raw_text.strip():
            st.warning("Please provide text or upload a PDF first.")
        else:
            with st.spinner("Analyzing document and summarizing... ⚡"):
                prompt = f"Summarize the following text in {summary_type} format:\n\n{raw_text[:12000]}"
                answer, error = call_claude(
                    prompt=prompt,
                    system="You are an expert document summarizer. Highlight core concepts clearly with emojis and key bullet points."
                )
                if error:
                    st.error(f"Summarization error: {error}")
                else:
                    st.markdown("### 📌 Summary Result")
                    st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 9: LANGUAGE TRANSLATOR
# =========================================================
elif tool == "🌐 Language Translator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Multi-Language AI Translator")
    st.markdown("Accurately translate sentences while maintaining natural context.")

    col1, col2 = st.columns(2)
    with col1:
        target_lang = st.selectbox("Translate to:", ["Hindi", "English", "Sanskrit", "Spanish", "French", "German", "Japanese", "Bengali", "Marathi", "Tamil"])
    
    text_to_translate = st.text_area("Enter text to translate", height=120, placeholder="Type text here...")

    if st.button("🌐 Translate Now"):
        if not text_to_translate.strip():
            st.warning("Please enter text to translate.")
        else:
            with st.spinner("Translating... 🌐"):
                prompt = f"Translate the following text into {target_lang}. Provide only the accurate translation followed by a brief pronunciation/cultural note if helpful:\n\n{text_to_translate}"
                answer, error = call_claude(
                    prompt=prompt,
                    system="You are a professional translator fluent in global and regional languages."
                )
                if error:
                    st.error(f"Translation Error: {error}")
                else:
                    st.markdown("### 🎯 Translation")
                    st.success(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 10: TEXT-TO-VOICE (TTS)
# =========================================================
elif tool == "🔊 Text-to-Voice (TTS)":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🔊 Text-to-Voice (TTS) Audio Generator")
    st.markdown("Convert any text into natural speech audio.")

    tts_text = st.text_area("Enter text to generate audio", height=120, placeholder="e.g. Welcome to Rays AI Suite. How can I assist you today?")
    tts_lang = st.selectbox("Voice Language", ["English (en)", "Hindi (hi)", "Spanish (es)", "French (fr)"])

    if st.button("🔊 Generate Audio"):
        if not tts_text.strip():
            st.warning("Please enter text first.")
        else:
            if not HAS_GTTS:
                st.error("gTTS package is missing. Please add 'gTTS' to requirements.txt")
            else:
                with st.spinner("Generating Voice Audio... 🔊"):
                    try:
                        lang_code = tts_lang.split("(")[1].replace(")", "").strip()
                        tts = gTTS(text=tts_text, lang=lang_code, slow=False)
                        fp = io.BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        
                        st.audio(fp, format="audio/mp3")
                        st.download_button(
                            "⬇️ Download Audio MP3",
                            data=fp.getvalue(),
                            file_name="rays_ai_speech.mp3",
                            mime="audio/mp3"
                        )
                        st.success("Audio Generated!")
                    except Exception as e:
                        st.error(f"TTS Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 11: RESUME / CV ANALYZER
# =========================================================
elif tool == "📄 Resume / CV Analyzer":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📄 AI Resume / CV Evaluator")
    st.markdown("Evaluates resumes, calculates match scores, lists missing skills, and gives improvements.")

    resume_pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_uploader")
    job_desc = st.text_area("Target Job Role / Description (Optional)", placeholder="e.g. Python Developer / Data Analyst role requirements...")

    if st.button("📊 Analyze Resume"):
        if not resume_pdf:
            st.warning("Please upload a PDF resume.")
        else:
            with st.spinner("Analyzing Resume Structure & ATS Optimization... 📈"):
                resume_text, err = extract_text_from_pdf(resume_pdf)
                if err:
                    st.error(f"Error reading Resume PDF: {err}")
                else:
                    prompt = f"""
Analyze this resume text and evaluate it.
Target Job Description: {job_desc if job_desc else 'General Professional Evaluation'}

Resume Content:
{resume_text[:10000]}

Provide analysis in the following exact format:
1. **Overall Resume Score (out of 100)**
2. **Key Strengths**
3. **Missing Critical Skills & Keywords**
4. **Formatting & ATS Optimization Tips**
5. **Actionable Step-by-Step Improvement Plan**
                    """
                    answer, error = call_claude(
                        prompt=prompt,
                        system="You are an expert HR recruiter and ATS Resume Auditor."
                    )
                    if error:
                        st.error(f"Analysis Error: {error}")
                    else:
                        st.markdown(answer)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 12: FACE DETECTION
# =========================================================
elif tool == "👤 Face Detection":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 👤 OpenCV Face Detection")
    st.markdown("Detect human faces in uploaded photos using computer vision.")

    if not HAS_OPENCV:
        st.error("OpenCV library is not available. Please install `opencv-python-headless`.")
    else:
        face_file = st.file_uploader("Upload photo for face detection", type=["jpg", "png", "jpeg", "webp"])

        if face_file:
            input_image = Image.open(face_file).convert("RGB")
            img_np = np.array(input_image)
            
            col1, col2 = st.columns(2)
            with col1:
                st.caption("Original Image")
                st.image(input_image, use_container_width=True)

            with st.spinner("Detecting faces... 👁️"):
                gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                for (x, y, w, h) in faces:
                    cv2.rectangle(img_np, (x, y), (x+w, y+h), (0, 255, 125), 3)

                processed_img = Image.fromarray(img_np)

            with col2:
                st.caption(f"Detected: {len(faces)} Face(s)")
                st.image(processed_img, use_container_width=True)

            st.success(f"Successfully detected {len(faces)} face(s) in image!")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 13: BACKGROUND REMOVER
# =========================================================
elif tool == "🖼️ Background Remover":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🖼️ AI Background Remover")
    st.markdown("Upload any photo and get an instant transparent cutout.")

    bg_color = st.sidebar.color_picker("Background color (optional)", "#FFFFFF")
    use_bg_color = st.sidebar.checkbox("Apply background color", value=False)

    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg", "webp"])

    if uploaded_file is not None:
        input_image = Image.open(uploaded_file).convert("RGBA")

        col1, col2 = st.columns(2)
        with col1:
            st.caption("Original")
            st.image(input_image, use_container_width=True)

        with st.spinner("Removing background... please wait ⏳"):
            output_image = remove(input_image)
            if use_bg_color:
                bg = Image.new("RGBA", output_image.size, bg_color)
                bg.paste(output_image, (0, 0), output_image)
                output_image = bg.convert("RGB")

        with col2:
            st.caption("Result")
            st.image(output_image, use_container_width=True)

        buf = io.BytesIO()
        fmt = "PNG" if output_image.mode == "RGBA" else "JPEG"
        output_image.save(buf, format=fmt)
        st.download_button(
            "⬇️ Download Result",
            data=buf.getvalue(),
            file_name=f"rays_ai_cutout.{fmt.lower()}",
            mime=f"image/{fmt.lower()}",
        )
        st.success("Done! Background removed.")
    else:
        st.info("👆 Upload an image to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 14: WORD TO PDF
# =========================================================
elif tool == "📄 Word to PDF":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Word to PDF Converter")
    st.markdown("Convert Word, ODT, RTF, or TXT documents to PDF.")

    word_file = st.file_uploader("Upload a document", type=["docx", "doc", "odt", "rtf", "txt"])

    if word_file is not None:
        if st.button("Convert to PDF"):
            with st.spinner("Converting... ⏳"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, word_file.name)
                    with open(input_path, "wb") as f:
                        f.write(word_file.getbuffer())

                    try:
                        soffice_cmd = find_soffice()
                        profile_dir = os.path.join(tmpdir, "lo_profile")
                        subprocess.run(
                            [
                                soffice_cmd,
                                f"-env:UserInstallation=file:///{profile_dir.replace(os.sep, '/')}",
                                "--headless", "--norestore",
                                "--convert-to", "pdf",
                                "--outdir", tmpdir, input_path,
                            ],
                            check=True,
                            timeout=120,
                            capture_output=True,
                            text=True,
                        )
                        pdf_name = os.path.splitext(word_file.name)[0] + ".pdf"
                        pdf_path = os.path.join(tmpdir, pdf_name)

                        with open(pdf_path, "rb") as f:
                            pdf_bytes = f.read()

                        st.success("Done! Your PDF is ready.")
                        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=pdf_name, mime="application/pdf")
                    except FileNotFoundError:
                        st.error("LibreOffice is not installed or not found on the system.")
                    except subprocess.CalledProcessError as e:
                        st.error("Conversion failed.")
                        with st.expander("Show technical details"):
                            st.code(e.stderr or e.stdout or str(e))
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a document to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 15: PDF TO WORD
# =========================================================
elif tool == "📝 PDF to Word":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📝 PDF to Word Converter")
    st.markdown("Convert text-based PDFs to DOCX files.")

    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf_file is not None:
        if st.button("Convert to Word"):
            with st.spinner("Converting... ⏳"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, pdf_file.name)
                    with open(input_path, "wb") as f:
                        f.write(pdf_file.getbuffer())

                    try:
                        soffice_cmd = find_soffice()
                        profile_dir = os.path.join(tmpdir, "lo_profile")
                        subprocess.run(
                            [
                                soffice_cmd,
                                f"-env:UserInstallation=file:///{profile_dir.replace(os.sep, '/')}",
                                "--headless", "--norestore",
                                "--convert-to", "docx",
                                "--outdir", tmpdir, input_path,
                            ],
                            check=True,
                            timeout=120,
                            capture_output=True,
                            text=True,
                        )
                        docx_name = os.path.splitext(pdf_file.name)[0] + ".docx"
                        docx_path = os.path.join(tmpdir, docx_name)

                        with open(docx_path, "rb") as f:
                            docx_bytes = f.read()

                        st.success("Done! Your Word file is ready.")
                        st.download_button(
                            "⬇️ Download Word Document",
                            data=docx_bytes,
                            file_name=docx_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                        st.caption("Note: Scanned PDFs or image-heavy layouts may not convert perfectly.")
                    except FileNotFoundError:
                        st.error("LibreOffice is not installed or not found on the system.")
                    except subprocess.CalledProcessError as e:
                        st.error("Conversion failed. PDF might be scanned or protected.")
                        with st.expander("Show technical details"):
                            st.code(e.stderr or e.stdout or str(e))
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a PDF to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 16: JOB NOTIFICATIONS
# =========================================================
elif tool == "📢 Job Notifications":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📢 Govt Job Notifications & Alerts")
    st.markdown("Quick links to official government job portals, admit cards, and exam results.")
    
    job_sources = [
        ("🏛️", "Sarkari Result", "Latest results, admit cards & job alerts", "https://www.sarkariresult.com"),
        ("📋", "Employment News", "Official Govt of India employment newspaper", "https://www.employmentnews.gov.in"),
        ("🎯", "SSC Portal", "Staff Selection Commission official site", "https://ssc.nic.in"),
        ("🏦", "IBPS Portal", "Banking recruitment portal", "https://www.ibps.in"),
        ("🚂", "RRB Portal", "Railway Recruitment Board portal", "https://www.rrbcdg.gov.in"),
        ("📝", "UPSC Portal", "Civil Services & national examinations", "https://upsc.gov.in"),
        ("🏢", "National Career Service", "Govt of India job portal", "https://www.ncs.gov.in"),
    ]

    for icon, name, desc, url in job_sources:
        st.markdown(f"""
            <a href="{url}" target="_blank" class="portal-card">
                <div>
                    <div class="portal-title">{icon} {name}</div>
                    <div class="portal-sub">{desc}</div>
                </div>
                <div style="color:#2CB67D; font-weight:bold;">Visit ↗</div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div class="footer-note">Powered by ⚡ Rays AI Suite • 2026</div>', unsafe_allow_html=True)
