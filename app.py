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
    page_title="Rays AI - Online Tools",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------- Custom professional theme (CSS) ----------
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e 0%, #0F0F13 60%);
    }

    /* ---- Navbar ---- */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1.5rem;
    }
    .navbar-logo {
        font-size: 1.4rem;
        font-weight: 800;
        color: #FFFFFE;
    }
    .navbar-logo span {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .navbar-badge {
        font-size: 0.75rem;
        color: #2CB67D;
        border: 1px solid #2CB67D;
        border-radius: 999px;
        padding: 0.15rem 0.7rem;
    }

    /* ---- Hero ---- */
    .hero {
        text-align: center;
        padding: 1.5rem 0 2.2rem 0;
    }
    .hero h1 {
        font-size: 2.4rem;
        font-weight: 800;
        color: #FFFFFE;
        margin-bottom: 0.3rem;
        letter-spacing: -0.5px;
    }
    .hero h1 span {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        color: #9CA3AF;
        font-size: 1.05rem;
        max-width: 480px;
        margin: 0 auto;
    }

    /* ---- Feature/tool card wrapper ---- */
    .tool-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 1.6rem 1.6rem 1.2rem 1.6rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
    }
    .trust-row {
        display: flex;
        justify-content: center;
        gap: 1.8rem;
        color: #6B7280;
        font-size: 0.82rem;
        padding-bottom: 1.6rem;
        flex-wrap: wrap;
    }
    .tool-card h3 {
        margin-top: 0;
        color: #FFFFFE;
    }
    .tool-card p {
        color: #9CA3AF;
        margin-top: -0.4rem;
    }

    /* ---- Buttons ---- */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #7F5AF0, #2CB67D);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.65rem 1.4rem;
        font-weight: 600;
        transition: opacity 0.2s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        opacity: 0.88;
        color: white;
    }

    /* ---- File uploader ---- */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 12px;
        border: 1.5px dashed rgba(127,90,240,0.5);
        background: rgba(127,90,240,0.05);
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background-color: #16161A;
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* ---- Footer ---- */
    .footer-note {
        text-align: center;
        color: #6B7280;
        font-size: 0.85rem;
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- Navbar ----------
st.markdown("""
    <div class="navbar">
        <div class="navbar-logo">⚡ <span>Rays AI</span></div>
        <div class="navbar-badge">100% Free</div>
    </div>
""", unsafe_allow_html=True)

# ---------- Hero ----------
st.markdown("""
    <div class="hero">
        <h1>AI tools that just <span>work</span></h1>
        <p>Remove backgrounds, convert files, and more — free, fast, no signup required.</p>
    </div>
    <div class="trust-row">
        <span>⚡ Instant results</span>
        <span>🔒 Files processed privately</span>
        <span>🆓 No signup needed</span>
    </div>
""", unsafe_allow_html=True)

# ---------- Sidebar: tool selector ----------
st.sidebar.markdown("### 🛠️ Tools")
tool = st.sidebar.radio(
    "Choose a tool",
    ["🖼️ Background Remover", "📄 Word to PDF", "📝 PDF to Word", "📢 Job Notifications"],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.caption("More tools coming soon: Image Compressor, Resize Image...")


# =========================================================
# TOOL 1: BACKGROUND REMOVER
# =========================================================
if tool == "🖼️ Background Remover":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 🖼️ Background Remover")
    st.markdown("Upload any photo and get an instant background-free cutout.")

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
        st.success("Done! Your background has been removed.")
    else:
        st.info("👆 Upload a JPG or PNG to get started.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TOOL 2: WORD TO PDF
# =========================================================
elif tool == "📄 Word to PDF":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📄 Word to PDF Converter")
    st.markdown("Upload a Word, ODT, RTF, or TXT file and convert it to PDF instantly.")

    word_file = st.file_uploader(
        "Upload a document",
        type=["docx", "doc", "odt", "rtf", "txt"],
    )

    if word_file is not None:
        if st.button("Convert to PDF"):
            with st.spinner("Converting... please wait ⏳"):
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
                        st.download_button(
                            "⬇️ Download PDF",
                            data=pdf_bytes,
                            file_name=pdf_name,
                            mime="application/pdf",
                        )
                    except FileNotFoundError:
                        st.error(
                            "LibreOffice is not installed or not found. "
                            "Please install it first — see README.md for steps."
                        )
                    except subprocess.CalledProcessError as e:
                        st.error("Conversion failed.")
                        with st.expander("Show technical details"):
                            st.code(e.stderr or e.stdout or str(e))
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a document to get started.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TOOL 3: PDF TO WORD
# =========================================================
elif tool == "📝 PDF to Word":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📝 PDF to Word Converter")
    st.markdown("Upload a PDF file and convert it to an editable Word (.docx) file.")

    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf_file is not None:
        if st.button("Convert to Word"):
            with st.spinner("Converting... please wait ⏳"):
                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, pdf_file.name)
                    with open(input_path, "wb") as f:
                        f.write(pdf_file.getbuffer())

                    try:
                        soffice_cmd = find_soffice()
                        profile_dir = os.path.join(tmpdir, "lo_profile")
                        result = subprocess.run(
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
                            "⬇️ Download Word File",
                            data=docx_bytes,
                            file_name=docx_name,
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        )
                        st.caption(
                            "Note: complex layouts, scanned PDFs, or heavy formatting "
                            "may not convert perfectly — this works best on text-based PDFs."
                        )
                    except FileNotFoundError:
                        st.error(
                            "LibreOffice is not installed or not found. "
                            "Please install it first — see README.md for steps."
                        )
                    except subprocess.CalledProcessError as e:
                        st.error(
                            "Conversion failed. This PDF might be scanned/image-based "
                            "(LibreOffice can only convert text-based PDFs to Word)."
                        )
                        with st.expander("Show technical details"):
                            st.code(e.stderr or e.stdout or str(e))
                    except Exception as e:
                        st.error(f"Conversion failed: {e}")
    else:
        st.info("👆 Upload a PDF to get started.")
    st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# TOOL 4: JOB NOTIFICATIONS
# =========================================================
elif tool == "📢 Job Notifications":
    st.markdown('<div class="tool-card">', unsafe_allow_html=True)
    st.markdown("### 📢 Govt Job Notifications")
    st.markdown(
        "Quick links to trusted official sources for the latest government "
        "job notifications, results, and admit cards."
    )

    job_sources = [
        ("🏛️", "Sarkari Result", "Latest results, admit cards & job alerts", "https://www.sarkariresult.com"),
        ("📋", "Employment News", "Official Govt of India employment newspaper", "https://www.employmentnews.gov.in"),
        ("🎯", "SSC (Staff Selection Commission)", "SSC exam notifications & results", "https://ssc.nic.in"),
        ("🏦", "IBPS", "Bank recruitment notifications", "https://www.ibps.in"),
        ("🚂", "RRB (Railway Recruitment Board)", "Railway job notifications", "https://www.rrbcdg.gov.in"),
        ("📝", "UPSC", "Civil services & other UPSC exams", "https://upsc.gov.in"),
        ("🏢", "National Career Service", "Govt of India's official job portal", "https://www.ncs.gov.in"),
    ]

    for icon, name, desc, url in job_sources:
        st.markdown(f"""
            <a href="{url}" target="_blank" style="text-decoration:none;">
                <div style="
                    display:flex; align-items:center; gap:0.9rem;
                    background: rgba(255,255,255,0.03);
                    border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 12px;
                    padding: 0.8rem 1rem;
                    margin-bottom: 0.6rem;
                ">
                    <div style="font-size:1.6rem;">{icon}</div>
                    <div>
                        <div style="color:#FFFFFE; font-weight:600;">{name}</div>
                        <div style="color:#9CA3AF; font-size:0.85rem;">{desc}</div>
                    </div>
                </div>
            </a>
        """, unsafe_allow_html=True)

    st.caption("These links go directly to the official websites of each organization.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="footer-note">Built with ❤️ using Streamlit &nbsp;•&nbsp; Rays AI © 2026</div>', unsafe_allow_html=True)
