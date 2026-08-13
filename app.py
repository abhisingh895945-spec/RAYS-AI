import streamlit as st
from rembg import remove
from PIL import Image
import io
import subprocess
import os
import tempfile
import shutil

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
    page_title="Rays AI - Suite & Portals",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Password Protection ----------
def check_password():
    """Show a branded welcome + password box; only let the rest of the app render if correct."""

    def password_entered():
        if st.session_state.get("password_input") == st.secrets.get("APP_PASSWORD", "raysai123"):
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]
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

    /* Big Front Hero Banner */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(255,255,255,0.02);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 20px;
        margin-bottom: 2rem;
    }
    .hero-logo-big {
        font-size: 5rem;
        line-height: 1;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0px 0px 15px rgba(127, 90, 240, 0.8));
    }
    .hero-title {
        font-size: 3rem;
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
        font-size: 1.1rem;
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

    /* Circle Logobox Design Theme */
    .circle-card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1.5rem;
        justify-content: center;
        padding: 1rem 0;
    }
    .circle-logobox {
        width: 130px;
        height: 130px;
        border-radius: 50%;
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
    .circle-logobox:hover {
        transform: scale(1.08);
        border-color: #2CB67D;
        box-shadow: 0 0 25px rgba(44,182,125,0.4);
    }
    .circle-icon {
        font-size: 2.2rem;
        margin-bottom: 0.2rem;
    }
    .circle-label {
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
        <div class="navbar-badge">v2.0 PRO</div>
    </div>
""", unsafe_allow_html=True)

# ---------- BIG RAYS AI FRONT LOGO HEADER ----------
st.markdown("""
    <div class="hero-container">
        <div class="hero-logo-big">⚡</div>
        <div class="hero-title">RAYS <span>AI</span></div>
        <div class="hero-desc">All-in-One Powerful Utilities & Learning Portals</div>
    </div>
""", unsafe_allow_html=True)

# ---------- Sidebar Menu ----------
st.sidebar.markdown("### 🛠️ Navigation Menu")
tool = st.sidebar.radio(
    "Choose a tool",
    [
        "⭕ Circle Logo Hub",
        "🔗 Study & Resource Portals",
        "🖼️ Background Remover",
        "📄 Word to PDF",
        "📝 PDF to Word",
        "📢 Job Notifications"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("⚡ Powered by Rays AI Engine")

# =========================================================
# TOOL 1: CIRCLE LOGOBOX HUB
# =========================================================
if tool == "⭕ Circle Logo Hub":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### ⭕ Circle Logobox Dashboard")
    st.markdown("Quick access circular icons for major portals.")

    st.markdown("""
        <div class="circle-card-container">
            <a href="https://studypanda.live/" target="_blank" class="circle-logobox">
                <div class="circle-icon">📚</div>
                <div class="circle-label">StudyPanda</div>
            </a>
            <a href="https://pwthor.live/" target="_blank" class="circle-logobox">
                <div class="circle-icon">⚡</div>
                <div class="circle-label">PW Thor</div>
            </a>
            <a href="https://rarestudy.in/" target="_blank" class="circle-logobox">
                <div class="circle-icon">📖</div>
                <div class="circle-label">RareStudy</div>
            </a>
            <a href="https://studybeepro.site/" target="_blank" class="circle-logobox">
                <div class="circle-icon">🐝</div>
                <div class="circle-label">StudyBee</div>
            </a>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 2: CUSTOM WEBSITES PORTAL SLIDE
# =========================================================
elif tool == "🔗 Study & Resource Portals":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Quick Access Links & Portals")
    st.markdown("Direct portal shortcuts added for quick redirection.")

    links = [
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
# TOOL 3: BACKGROUND REMOVER
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
# TOOL 4: WORD TO PDF
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

                        st.success("Done!")
                        st.download_button("⬇️ Download PDF", data=pdf_bytes, file_name=pdf_name, mime="application/pdf")
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a document to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 5: PDF TO WORD
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

                        st.success("Done!")
                        st.download_button("⬇️ Download Word Document", data=docx_bytes, file_name=docx_name, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a PDF to start.")
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# TOOL 6: JOB NOTIFICATIONS
# =========================================================
elif tool == "📢 Job Notifications":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📢 Govt Job Notifications")
    
    job_sources = [
        ("🏛️", "Sarkari Result", "https://www.sarkariresult.com"),
        ("📋", "Employment News", "https://www.employmentnews.gov.in"),
        ("🎯", "SSC Official Portal", "https://ssc.nic.in"),
        ("🏦", "IBPS Portal", "https://www.ibps.in"),
    ]

    for icon, name, url in job_sources:
        st.markdown(f"""
            <a href="{url}" target="_blank" class="portal-card">
                <div>
                    <div class="portal-title">{icon} {name}</div>
                </div>
                <div style="color:#2CB67D;">Visit ↗</div>
            </a>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Footer ----------
st.markdown('<div class="footer-note">Powered by ⚡ Rays AI Suite • 2026</div>', unsafe_allow_html=True)
