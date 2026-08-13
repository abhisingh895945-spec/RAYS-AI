import io
import os
import shutil
import subprocess
import tempfile
import streamlit as st
from PIL import Image
from rembg import remove

# Try importing pdf2docx for better PDF to Word handling
try:
  from pdf2docx import Converter

  HAS_PDF2DOCX = True
except ImportError:
  HAS_PDF2DOCX = False


# ---------- Helper: find LibreOffice on any OS ----------
def find_soffice():
  """Return a runnable soffice command, checking PATH then common install locations."""
  if shutil.which('soffice'):
    return 'soffice'
  common_paths = [
      r'C:\Program Files\LibreOffice\program\soffice.exe',
      r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
      '/usr/bin/soffice',
      '/opt/libreoffice/program/soffice',
      '/Applications/LibreOffice.app/Contents/MacOS/soffice',
  ]
  for path in common_paths:
    if os.path.exists(path):
      return path
  return None


# ---------- Page setup ----------
st.set_page_config(
    page_title='Rays AI - Suite',
    page_icon='⚡',
    layout='centered',
    initial_sidebar_state='expanded',
)


# ---------- Simple password gate ----------
def check_password():
  """Show a branded welcome + password box; only let the rest of the app render if correct."""

  def password_entered():
    if st.session_state.get('password_input') == st.secrets.get(
        'APP_PASSWORD', ''
    ):
      st.session_state['password_correct'] = True
      del st.session_state['password_input']
    else:
      st.session_state['password_correct'] = False

  if st.session_state.get('password_correct', False):
    return True

  st.markdown(
      """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f172a 0%, #020617 100%);
        }
        .welcome-wrap {
            text-align: center;
            padding-top: 5rem;
        }
        .welcome-logo {
            font-size: 3.5rem;
            margin-bottom: 0.3rem;
            filter: drop-shadow(0 0 15px rgba(127, 90, 240, 0.6));
        }
        .welcome-title {
            font-size: 2.4rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.2rem;
        }
        .welcome-title span {
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .welcome-sub {
            color: #94a3b8;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        </style>
        <div class="welcome-wrap">
            <div class="welcome-logo">⚡</div>
            <div class="welcome-title">Welcome to <span>Rays AI</span></div>
            <div class="welcome-sub">Enter password to continue</div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    st.text_input(
        'Password',
        type='password',
        key='password_input',
        on_change=password_entered,
        label_visibility='collapsed',
        placeholder='Enter password',
    )
    if (
        'password_correct' in st.session_state
        and not st.session_state['password_correct']
    ):
      st.error('Incorrect password.')
  return False


if not check_password():
  st.stop()


# ---------- Custom Premium Glassmorphism Theme & Wallpaper CSS ----------
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Background Wallpaper & Glow FX */
    .stApp {
        background-color: #0b0f19;
        background-image: 
            radial-gradient(at 0% 0%, rgba(56, 189, 248, 0.12) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(129, 140, 248, 0.12) 0px, transparent 50%),
            radial-gradient(at 50% 50%, rgba(15, 23, 42, 0.8) 0px, transparent 100%);
        background-attachment: fixed;
    }

    /* ---- Navbar ---- */
    .navbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 1.2rem;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        margin-bottom: 2rem;
    }
    .navbar-logo {
        font-size: 1.4rem;
        font-weight: 800;
        color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .navbar-logo span {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .streamfiles-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #38bdf8;
        background: rgba(56, 189, 248, 0.1);
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 999px;
        padding: 0.3rem 0.8rem;
        text-decoration: none !important;
        transition: all 0.3s ease;
    }
    .streamfiles-badge:hover {
        background: rgba(56, 189, 248, 0.25);
        border-color: #38bdf8;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(56, 189, 248, 0.2);
    }

    /* ---- Hero ---- */
    .hero {
        text-align: center;
        padding: 1rem 0 2rem 0;
    }
    .hero h1 {
        font-size: 2.6rem;
        font-weight: 800;
        color: #FFFFFF;
        margin-bottom: 0.4rem;
        letter-spacing: -0.5px;
    }
    .hero h1 span {
        background: linear-gradient(90deg, #38bdf8, #818cf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero p {
        color: #94a3b8;
        font-size: 1.05rem;
        max-width: 500px;
        margin: 0 auto;
    }

    /* ---- Tool Card Wrapper ---- */
    .tool-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
    }
    .trust-row {
        display: flex;
        justify-content: center;
        gap: 1.5rem;
        color: #64748b;
        font-size: 0.85rem;
        padding-bottom: 1.8rem;
        flex-wrap: wrap;
    }

    /* ---- Buttons ---- */
    div.stButton > button, div.stDownloadButton > button {
        background: linear-gradient(90deg, #0284c7, #6366f1);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.6rem;
        font-weight: 600;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3);
        transition: all 0.25s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        opacity: 0.95;
        transform: translateY(-1px);
        box-shadow: 0 6px 20px rgba(2, 132, 199, 0.45);
        color: white;
    }

    /* ---- File Uploader ---- */
    [data-testid="stFileUploaderDropzone"] {
        border-radius: 14px;
        border: 2px dashed rgba(56, 189, 248, 0.35);
        background: rgba(15, 23, 42, 0.6);
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: #38bdf8;
        background: rgba(56, 189, 248, 0.05);
    }

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }

    /* ---- Footer ---- */
    .footer-note {
        text-align: center;
        color: #64748b;
        font-size: 0.85rem;
        padding: 2rem 0;
    }
    .footer-note a {
        color: #38bdf8;
        text-decoration: none;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------- Navbar with Streamfiles logo badge ----------
st.markdown(
    """
    <div class="navbar">
        <div class="navbar-logo">⚡ <span>Rays AI</span></div>
        <a href="https://streamfiles.eu.org/" target="_blank" class="streamfiles-badge">
            🚀 StreamFiles
        </a>
    </div>
""",
    unsafe_allow_html=True,
)

# ---------- Hero Section ----------
st.markdown(
    """
    <div class="hero">
        <h1>Smart AI Tools <span>Fast & Free</span></h1>
        <p>Remove backgrounds, convert documents instantly without signups or limits.</p>
    </div>
    <div class="trust-row">
        <span>⚡ Lightning Fast</span>
        <span>🔒 Secure & Private</span>
        <span>🌐 100% Free Tools</span>
    </div>
""",
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
st.sidebar.markdown("### 🛠️ Navigation")
tool = st.sidebar.radio(
    "Choose a tool",
    [
        "🖼️ Background Remover",
        "📄 Word to PDF",
        "📝 PDF to Word",
        "📢 Job Notifications",
    ],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")

# Sidebar Direct Link Badge
st.sidebar.markdown(
    """
    <a href="https://streamfiles.eu.org/" target="_blank" style="text-decoration:none;">
        <div style="
            padding: 10px; 
            border-radius: 10px; 
            background: rgba(56, 189, 248, 0.1); 
            border: 1px solid rgba(56, 189, 248, 0.3);
            text-align: center;
            color: #38bdf8;
            font-weight: 600;
            font-size: 0.85rem;
        ">
            🌐 Visit StreamFiles Web
        </div>
    </a>
""",
    unsafe_allow_html=True,
)

# =========================================================
# TOOL 1: BACKGROUND REMOVER
# =========================================================
if tool == "🖼️ Background Remover":
  st.markdown('<div class="tool-card">', unsafe_allow_html=True)
  st.markdown("### 🖼️ Background Remover")
  st.markdown("Upload any photo to instantly isolate the subject.")

  bg_color = st.sidebar.color_picker("Background color (optional)", "#FFFFFF")
  use_bg_color = st.sidebar.checkbox("Apply background color", value=False)

  uploaded_file = st.file_uploader(
      "Upload an image", type=["png", "jpg", "jpeg", "webp"]
  )

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
    st.info("👆 Upload an image to start processing.")
  st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TOOL 2: WORD TO PDF
# =========================================================
elif tool == "📄 Word to PDF":
  st.markdown('<div class="tool-card">', unsafe_allow_html=True)
  st.markdown("### 📄 Word to PDF Converter")
  st.markdown("Convert DOCX, DOC, ODT or TXT documents to PDF.")

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

          soffice_cmd = find_soffice()
          if soffice_cmd:
            try:
              profile_dir = os.path.join(tmpdir, "lo_profile")
              subprocess.run(
                  [
                      soffice_cmd,
                      f"-env:UserInstallation=file:///{profile_dir.replace(os.sep, '/')}",
                      "--headless",
                      "--norestore",
                      "--convert-to",
                      "pdf",
                      "--outdir",
                      tmpdir,
                      input_path,
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
            except Exception as e:
              st.error(f"Conversion failed: {e}")
          else:
            st.error(
                "LibreOffice is not installed on the server environment."
            )
  else:
    st.info("👆 Upload a document to get started.")
  st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TOOL 3: PDF TO WORD
# =========================================================
elif tool == "📝 PDF to Word":
  st.markdown('<div class="tool-card">', unsafe_allow_html=True)
  st.markdown("### 📝 PDF to Word Converter")
  st.markdown("Convert PDF documents to editable DOCX format.")

  pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

  if pdf_file is not None:
    if st.button("Convert to Word"):
      with st.spinner("Converting... please wait ⏳"):
        with tempfile.TemporaryDirectory() as tmpdir:
          input_path = os.path.join(tmpdir, pdf_file.name)
          docx_name = os.path.splitext(pdf_file.name)[0] + ".docx"
          docx_path = os.path.join(tmpdir, docx_name)

          with open(input_path, "wb") as f:
            f.write(pdf_file.getbuffer())

          converted_success = False

          # Strategy 1: Use pdf2docx (Highly reliable Python engine)
          if HAS_PDF2DOCX:
            try:
              cv = Converter(input_path)
              cv.convert(docx_path, start=0, end=None)
              cv.close()
              converted_success = True
            except Exception:
              converted_success = False

          # Strategy 2: Fallback to LibreOffice if pdf2docx fails or is missing
          if not converted_success:
            soffice_cmd = find_soffice()
            if soffice_cmd:
              try:
                profile_dir = os.path.join(tmpdir, "lo_profile")
                subprocess.run(
                    [
                        soffice_cmd,
                        f"-env:UserInstallation=file:///{profile_dir.replace(os.sep, '/')}",
                        "--headless",
                        "--norestore",
                        "--convert-to",
                        "docx",
                        "--outdir",
                        tmpdir,
                        input_path,
                    ],
                    check=True,
                    timeout=120,
                    capture_output=True,
                    text=True,
                )
                converted_success = True
              except Exception:
                converted_success = False

          if converted_success and os.path.exists(docx_path):
            with open(docx_path, "rb") as f:
              docx_bytes = f.read()

            st.success("Done! Your Word document is ready.")
            st.download_button(
                "⬇️ Download Word File",
                data=docx_bytes,
                file_name=docx_name,
                mime=(
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ),
            )
          else:
            st.error(
                "Conversion failed. Please ensure the PDF is text-based or try"
                " installing `pdf2docx` in your requirements.txt."
            )
  else:
    st.info("👆 Upload a PDF to get started.")
  st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# TOOL 4: JOB NOTIFICATIONS
# =========================================================
elif tool == "📢 Job Notifications":
  st.markdown('<div class="tool-card">', unsafe_allow_html=True)
  st.markdown("### 📢 Govt Job Notifications")
  st.markdown(
      "Quick access to top government recruitment portals and updates."
  )

  job_sources = [
      (
          "🏛️",
          "Sarkari Result",
          "Latest results, admit cards & job alerts",
          "https://www.sarkariresult.com",
      ),
      (
          "📋",
          "Employment News",
          "Official Govt of India employment paper",
          "https://www.employmentnews.gov.in",
      ),
      (
          "🎯",
          "SSC Board",
          "Staff Selection Commission portal",
          "https://ssc.nic.in",
      ),
      ("🏦", "IBPS", "Bank recruitment & results portal", "https://www.ibps.in"),
      (
          "🚂",
          "RRB Board",
          "Railway Recruitment Board",
          "https://www.rrbcdg.gov.in",
      ),
      (
          "📝",
          "UPSC",
          "Civil Services & Defence exam alerts",
          "https://upsc.gov.in",
      ),
  ]

  for icon, name, desc, url in job_sources:
    st.markdown(
        f"""
            <a href="{url}" target="_blank" style="text-decoration:none;">
                <div style="
                    display:flex; align-items:center; gap:1rem;
                    background: rgba(15, 23, 42, 0.6);
                    border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 12px;
                    padding: 0.9rem 1.1rem;
                    margin-bottom: 0.7rem;
                    transition: border-color 0.3s ease;
                ">
                    <div style="font-size:1.6rem;">{icon}</div>
                    <div>
                        <div style="color:#FFFFFF; font-weight:600;">{name}</div>
                        <div style="color:#94a3b8; font-size:0.85rem;">{desc}</div>
                    </div>
                </div>
            </a>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer-note">
        Powered by <a href="https://streamfiles.eu.org/" target="_blank">StreamFiles</a> &nbsp;•&nbsp; Rays AI © 2026
    </div>
""",
    unsafe_allow_html=True,
)
