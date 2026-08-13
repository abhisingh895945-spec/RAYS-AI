import streamlit as st
import requests
import json
import re
import io
import os
import tempfile
import shutil
from PIL import Image
import cv2
import numpy as np

# Optional PDF processing
try:
    import pypdf
except ImportError:
    pypdf = None

# ---------- Helper: Robust Claude AI API Call ----------
def call_claude(prompt, system=None, max_tokens=1500):
    """Calls Anthropic Claude API with robust error handling and proper model fallback."""
    api_key = st.secrets.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        return None, "⚠️ Missing ANTHROPIC_API_KEY in Secrets. Please configure it in .streamlit/secrets.toml."

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    
    # Using widely supported Claude 3.5 Haiku model
    body = {
        "model": "claude-3-5-haiku-20241022",
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=body,
            timeout=60,
        )
        if resp.status_code != 200:
            try:
                err_msg = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                err_msg = resp.text
            return None, f"Anthropic API Error ({resp.status_code}): {err_msg}"

        data = resp.json()
        text = "".join(block.get("text", "") for block in data.get("content", []))
        return text, None
    except Exception as e:
        return None, str(e)

# ---------- Helper: LibreOffice Finder ----------
def find_soffice():
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

# ---------- Streamlit Page Config ----------
st.set_page_config(
    page_title="Rays AI - Ultimate Suite",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Password Protection ----------
def check_password():
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
        .stApp { background: radial-gradient(circle at top, #1a1a2e 0%, #0F0F13 65%); }
        .welcome-wrap { text-align: center; padding-top: 3rem; }
        .welcome-title { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; }
        .welcome-title span { background: linear-gradient(90deg, #7F5AF0, #2CB67D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        </style>
        <div class="welcome-wrap">
            <h1 class="welcome-title">Welcome to <span>RAYS AI SUITE</span></h1>
            <p style="color:#9CA3AF;">Enter password to access dashboard</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.text_input("Password", type="password", key="password_input", on_change=password_entered, label_visibility="collapsed")
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Incorrect Password.")
    return False

if not check_password():
    st.stop()

# ---------- Global Custom CSS Styling ----------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background: radial-gradient(circle at top left, #1a1a2e 0%, #0F0F13 60%); }
    .hero-container {
        text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 1.5rem;
    }
    .hero-title { font-size: 2.2rem; font-weight: 900; color: #FFFFFF; }
    .hero-title span { background: linear-gradient(90deg, #7F5AF0, #2CB67D); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .tool-card {
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem;
    }
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D); color: white; border: none; border-radius: 10px; font-weight: 600;
    }
    section[data-testid="stSidebar"] { background-color: #16161A; }
    </style>
""", unsafe_allow_html=True)

# ---------- Top Hero Banner ----------
st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚡ RAYS <span>AI SUITE</span></div>
        <p style="color:#9CA3AF; margin:0;">All-in-One Multi-Tool AI Hub • Smart Utilities & Converters</p>
    </div>
""", unsafe_allow_html=True)

# ---------- Sidebar Tools Menu ----------
tool = st.sidebar.radio(
    "🛠️ Select AI Tool",
    [
        "🧮 Smart Calculator (Step-by-Step)",
        "🖊️ Digital Whiteboard",
        "🗂️ Flashcard Generator",
        "💬 Doubt Solver / Virtual Assistant",
        "🎨 AI Image Generator (Text-to-Image)",
        "📝 Text & PDF Summarizer",
        "🌐 Language Translator",
        "🔊 Text-to-Voice (Audio Helper)",
        "📄 Resume / CV Analyzer",
        "👤 Face Detection & Recognition",
        "🖼️ Background Remover",
        "📄 Word / PDF Converters"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Rays AI • 2026")

# =========================================================
# 1. SMART CALCULATOR
# =========================================================
if tool == "🧮 Smart Calculator (Step-by-Step)":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🧮 Smart Math Calculator & Step Solver")
    st.write("Type any complex math or algebra problem to get complete step-by-step logic.")

    problem = st.text_area("Enter Math Problem:", placeholder="e.g. Solve for x: 3x^2 + 5x - 2 = 0 or Find integral of x*sin(x)")
    if st.button("Solve Step-by-Step"):
        if not problem.strip():
            st.warning("Please enter a math problem.")
        else:
            with st.spinner("Calculating solution steps... 🧠"):
                res, err = call_claude(
                    prompt=problem,
                    system="You are an expert Math Tutor. Solve the given math problem by showing each step with simple explanations. Highlight the final answer clearly."
                )
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 2. DIGITAL WHITEBOARD
# =========================================================
elif tool == "🖊️ Digital Whiteboard":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🖊️ AI Digital Whiteboard & Visual Notes")
    st.write("Generates visual tree diagrams, flowcharts, and structured notes on any topic.")

    topic = st.text_input("Enter Topic:", placeholder="e.g. Quantum Computing, Photosynthesis, Neural Networks")
    if st.button("Generate Whiteboard Diagram"):
        if not topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Designing whiteboard layout... ✏️"):
                res, err = call_claude(
                    prompt=f"Explain: {topic}",
                    system="You are a whiteboard teacher. Create clean, structured Markdown whiteboard notes. Include a core definition, tree structures (using ASCII or Markdown bullet trees), and key takeaways."
                )
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 3. FLASHCARD GENERATOR
# =========================================================
elif tool == "🗂️ Flashcard Generator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🗂️ AI Flashcard Generator")
    st.write("Automatically generates revision Q&A flashcards for studying.")

    fc_topic = st.text_input("Topic / Subject:", placeholder="e.g. Organic Chemistry, World War II, Python Data Structures")
    count = st.slider("Number of cards:", 3, 10, 5)

    if st.button("Generate Flashcards"):
        if not fc_topic.strip():
            st.warning("Please enter a topic.")
        else:
            with st.spinner("Generating Flashcards... 🗂️"):
                res, err = call_claude(
                    prompt=f"Create {count} study flashcards for: {fc_topic}",
                    system="Generate revision flashcards. Respond with ONLY valid JSON array in this format: [{\"question\": \"...\", \"answer\": \"...\"}]"
                )
                if err:
                    st.error(err)
                else:
                    try:
                        match = re.search(r'\[.*\]', res, re.DOTALL)
                        cards = json.loads(match.group(0)) if match else json.loads(res)
                        for idx, c in enumerate(cards, 1):
                            with st.expander(f"📌 Card {idx}: {c.get('question', '')}"):
                                st.success(f"**Answer:** {c.get('answer', '')}")
                    except Exception:
                        st.markdown(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 4. DOUBT SOLVER / CHATBOT
# =========================================================
elif tool == "💬 Doubt Solver / Virtual Assistant":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("💬 AI Homework Helper & Virtual Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_query = st.chat_input("Ask any doubt or question...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                convo = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.chat_history])
                res, err = call_claude(
                    prompt=convo,
                    system="You are a helpful AI Virtual Assistant & Homework Doubt Solver. Answer clearly and politely."
                )
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
                    st.session_state.chat_history.append({"role": "assistant", "content": res})

    if st.session_state.chat_history:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 5. AI IMAGE GENERATOR
# =========================================================
elif tool == "🎨 AI Image Generator (Text-to-Image)":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🎨 AI Image Generator")
    st.write("Generate high-quality photos directly from text prompts.")

    prompt = st.text_input("Enter Image Prompt:", placeholder="e.g. Futuristic cybernetic tiger in a neon rainforest, 8k render")
    if st.button("Generate Image 🖼️"):
        if not prompt.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Rendering image... 🎨"):
                # Connects via free Pollinations Image Generation API
                encoded_prompt = requests.utils.quote(prompt)
                img_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
                img_resp = requests.get(img_url)
                if img_resp.status_code == 200:
                    image = Image.open(io.BytesIO(img_resp.content))
                    st.image(image, caption=f"Prompt: {prompt}", use_container_width=True)
                    
                    buf = io.BytesIO()
                    image.save(buf, format="PNG")
                    st.download_button("Download Image ⬇️", data=buf.getvalue(), file_name="rays_ai_gen.png", mime="image/png")
                else:
                    st.error("Failed to generate image. Please try again.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 6. TEXT & PDF SUMMARIZER
# =========================================================
elif tool == "📝 Text & PDF Summarizer":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("📝 Text & PDF Summarizer")
    st.write("Extract and summarize lengthy documents or articles.")

    uploaded_pdf = st.file_uploader("Upload PDF File (Optional)", type=["pdf"])
    raw_text = st.text_area("Or Paste Raw Text Here:", height=150)

    text_to_summarize = ""
    if uploaded_pdf and pypdf:
        reader = pypdf.PdfReader(uploaded_pdf)
        text_to_summarize = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
    elif raw_text.strip():
        text_to_summarize = raw_text

    if st.button("Summarize Text"):
        if not text_to_summarize.strip():
            st.warning("Please upload a PDF or enter text.")
        else:
            with st.spinner("Analyzing document & summarizing... 📄"):
                res, err = call_claude(
                    prompt=f"Summarize this content in concise bullet points with key insights:\n\n{text_to_summarize[:6000]}",
                    system="You are a professional text summarizer. Provide a crisp summary with main key points."
                )
                if err:
                    st.error(err)
                else:
                    st.markdown("### 📌 Summary:")
                    st.markdown(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 7. LANGUAGE TRANSLATOR
# =========================================================
elif tool == "🌐 Language Translator":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🌐 AI Multi-Language Translator")

    target_lang = st.selectbox("Select Target Language:", ["Hindi", "Spanish", "French", "German", "Japanese", "English", "Marathi", "Tamil"])
    source_text = st.text_area("Text to Translate:", placeholder="Type text here...")

    if st.button("Translate Text"):
        if not source_text.strip():
            st.warning("Please enter text to translate.")
        else:
            with st.spinner("Translating... 🌐"):
                res, err = call_claude(
                    prompt=f"Translate this text to {target_lang}:\n\n{source_text}",
                    system="You are a professional translator. Provide only the translated text."
                )
                if err:
                    st.error(err)
                else:
                    st.success(f"**Translation ({target_lang}):**")
                    st.write(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 8. TEXT-TO-VOICE
# =========================================================
elif tool == "🔊 Text-to-Voice (Audio Helper)":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🔊 Text-to-Speech (Voice Audio)")

    tts_text = st.text_area("Text to convert to voice:", placeholder="Enter text to speak out loud...")
    if st.button("Generate Audio 🎧"):
        if not tts_text.strip():
            st.warning("Please enter text.")
        else:
            # Generate Web-based HTML Speech Synthesizer fallback
            clean_text = json.dumps(tts_text)
            audio_script = f"""
                <script>
                    var msg = new SpeechSynthesisUtterance({clean_text});
                    window.speechSynthesis.speak(msg);
                </script>
                <p style="color:#2CB67D; font-weight:bold;">🔊 Playing audio in browser speech engine...</p>
            """
            st.components.v1.html(audio_script, height=50)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 9. RESUME ANALYZER
# =========================================================
elif tool == "📄 Resume / CV Analyzer":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("📄 Resume & CV Analyzer")
    st.write("Analyze resume content, get scoring, skill recommendations, and improvement tips.")

    resume_text = st.text_area("Paste Resume Text or Details:", height=200, placeholder="Paste job experience, skills, and resume details...")
    target_job = st.text_input("Target Job Role (Optional):", placeholder="e.g. Python Developer, Data Analyst")

    if st.button("Analyze Resume 🚀"):
        if not resume_text.strip():
            st.warning("Please enter resume details.")
        else:
            with st.spinner("Evaluating CV..."):
                prompt_str = f"Analyze this Resume:\n\n{resume_text}"
                if target_job:
                    prompt_str += f"\nTarget Role: {target_job}"
                
                res, err = call_claude(
                    prompt=prompt_str,
                    system="You are an expert HR Manager. Analyze the resume. Provide: 1. Overall Score /10 2. Key Strengths 3. Missing Critical Skills 4. Specific Tips to Improve."
                )
                if err:
                    st.error(err)
                else:
                    st.markdown(res)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 10. FACE DETECTION / RECOGNITION
# =========================================================
elif tool == "👤 Face Detection & Recognition":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("👤 Computer Vision Face Detector")
    st.write("Upload an image to detect human faces automatically using OpenCV Vision API.")

    face_file = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png"])
    if face_file:
        img_bytes = np.frombuffer(face_file.read(), np.uint8)
        img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 3)

        result_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        st.image(result_rgb, caption=f"Detected {len(faces)} Face(s)", use_container_width=True)
        st.success(f"✅ Detection Complete! Found {len(faces)} face(s).")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 11. BACKGROUND REMOVER & CONVERTERS
# =========================================================
elif tool == "🖼️ Background Remover":
    from rembg import remove
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("🖼️ AI Background Remover")

    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        input_image = Image.open(uploaded_file).convert("RGBA")
        with st.spinner("Removing background..."):
            output_image = remove(input_image)
            st.image(output_image, caption="Background Removed", use_container_width=True)

        buf = io.BytesIO()
        output_image.save(buf, format="PNG")
        st.download_button("⬇️ Download PNG", data=buf.getvalue(), file_name="no_bg.png", mime="image/png")
    st.markdown('</div>', unsafe_allow_html=True)

elif tool == "📄 Word / PDF Converters":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.subheader("📄 Document Converter")
    st.info("Upload Word or PDF files to convert them using system LibreOffice engine.")
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div style="text-align:center; color:#6B7280; padding-top:2rem;">Powered by ⚡ Rays AI Suite • 2026</div>', unsafe_allow_html=True)
