# Rays AI — Multi-tool Website (Background Remover + Word to PDF)

## What's new in this version
- New theme (purple-green gradient, dark mode) — looks like a real product now
- ⚡ icon and "Rays AI" branding
- Sidebar to switch between tools
- New tool: **Word to PDF converter**

---

## Files in this folder
- `app.py` — the app (both tools)
- `requirements.txt` — Python packages
- `.streamlit/config.toml` — the theme colors
- `packages.txt` — tells Streamlit Cloud to install LibreOffice (needed for Word to PDF)

---

## PART 1 — Update your existing setup (you already have Python + venv)

### Step 1: Replace your old files
In your `cutout-app` folder (or wherever your project is):
1. Delete/replace the old `app.py` and `requirements.txt` with the new ones from this folder
2. Copy the new `.streamlit` folder (with `config.toml` inside) into your project folder too
3. Copy `packages.txt` into your project folder as well

Your folder should now look like:
```
your-project-folder/
  app.py
  requirements.txt
  packages.txt
  .streamlit/
    config.toml
```

### Step 2: Install LibreOffice (needed for Word to PDF tool only)
Download the free installer from: https://www.libreoffice.org/download/download/
Install it normally (Next, Next, Finish) — this is what actually converts
Word files to PDF behind the scenes.

### Step 3: Re-install Python packages (in case anything changed)
Open your project folder → open terminal there (Shift + Right-click →
"Open PowerShell window here") → activate venv:
```
venv\Scripts\activate
```
Then:
```
pip install -r requirements.txt
```

### Step 4: Run the app
```
streamlit run app.py
```
Browser will open with the new purple-green theme, ⚡ Rays AI branding, and
a sidebar to switch between "Background Remover" and "Word to PDF".

---

## PART 2 — Deploying live (updated)

Same as before (GitHub → share.streamlit.io), but this time upload **all 5
items**: `app.py`, `requirements.txt`, `packages.txt`, and the `.streamlit`
folder (with `config.toml` inside).

The `packages.txt` file tells Streamlit's cloud servers to install
LibreOffice automatically, so the Word-to-PDF tool works online too — no
extra steps needed once it's uploaded.

---

## Notes
- Want a custom logo instead of the ⚡ emoji? Add a `logo.png` file to your
  folder and change `page_icon="⚡"` in `app.py` to `page_icon="logo.png"`.
- To add more tools later (Image Compressor, PDF to Word, Resize Image),
  just add a new option to the sidebar `st.sidebar.radio(...)` list and a
  new `elif tool == "...":` block in `app.py`.
