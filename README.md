diff --git a/README.md b/README.md
index 3c2cfb8c76e6dc06bfe1bac8ee1d773bea8ec833..9515ed1e876ff7dec028f3006999242199598600 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,209 @@
-# Interpretable-CNN-Disease-Prediction-XAI
\ No newline at end of file
+# Interpretable-CNN-Disease-Prediction-XAI
+
+A full-stack medical AI web application with:
+- **React + Tailwind** frontend (dashboard, X-ray, eye camera check, history, XAI info)
+- **Flask + TensorFlow/Keras** backend (prediction, Grad-CAM, SQLite history, PDF reports)
+
+---
+
+## Backend files
+
+### `backend/app.py`
+- Loads models from:
+  - `backend/cnn_model/medxai_model.h5`
+  - `backend/cnn_model/eye_model.h5`
+- Routes:
+  - `POST /predict-xray`
+  - `POST /predict-eye`
+  - `GET /history`
+  - `GET /download-report?id=<id>`
+  - Static image helpers:
+    - `GET /files/upload/<filename>`
+    - `GET /files/heatmap/<filename>`
+- Includes:
+  - image preprocessing (224x224 + normalization)
+  - Grad-CAM generation
+  - SQLite history insert/list
+  - ReportLab PDF report generation
+  - CORS enabled for frontend API calls
+
+### `backend/train_xray_model.py`
+Training utility for **Kaggle Chest X-ray Pneumonia** dataset:
+- Default dataset path: `/kaggle/input/chest-xray-pneumonia`
+- Saves model to: `backend/cnn_model/medxai_model.h5`
+
+### `backend/init_db.py`
+Initializes SQLite database (`medical_ai.db`) and creates `history` table.
+
+### `backend/schema.sql`
+Standalone SQL schema for `history` table.
+
+### `backend/requirements.txt`
+Python dependencies for backend runtime.
+
+---
+
+## Frontend files
+
+### App structure (`frontend/src`)
+- **Router entry**: `App.js`
+- **Pages**:
+  - `pages/DashboardPage.jsx`
+  - `pages/XrayAnalysisPage.jsx`
+  - `pages/EyeCheckPage.jsx`
+  - `pages/HistoryPage.jsx`
+  - `pages/AboutXAIPage.jsx`
+- **Reusable components**:
+  - `components/Header.jsx`
+  - `components/Footer.jsx`
+  - `components/UploadForm.jsx`
+  - `components/CameraCapture.jsx`
+  - `components/HeatmapDisplay.jsx`
+  - `components/HistoryTable.jsx`
+- **API + hooks**:
+  - `services/api.js` (Axios calls)
+  - `hooks/useApiState.js`
+- **Interactive UI improvements**:
+  - glassmorphism cards
+  - animated confidence bar
+  - fade-in transitions
+  - camera capture/retake workflow
+  - square eye-alignment guide so only boxed eye region is analyzed
+
+---
+
+## VS Code run guide (local machine)
+
+> Recommended versions:
+- Python **3.10+**
+- Node **18 LTS** (for CRA compatibility)
+
+### 1) Open in VS Code
+If you already have this project folder on your PC, **do not clone again**:
+
+```powershell
+cd C:\path\to\Interpretable-CNN-Disease-Prediction-XAI
+code .
+```
+
+If you need to clone, copy the exact repo URL from GitHub's **Code → HTTPS** button:
+
+```powershell
+git clone https://github.com/OWNER/REPO.git
+cd REPO
+code .
+```
+
+PowerShell note: writing `git clone <your-repo-url>` causes
+`The '<' operator is reserved for future use` because angle brackets are parsed as operators.
+
+If you get `Repository not found`, the URL is wrong, the repo is private, or you are not authenticated to that account.
+
+### How to create your repository link (GitHub)
+1. Open your repository page on GitHub.
+2. Click the green **Code** button.
+3. Select **HTTPS**.
+4. Copy the URL shown there (it looks like `https://github.com/<your-user>/<your-repo>.git`).
+5. Use that copied URL in `git clone`.
+
+PowerShell example:
+```powershell
+git clone https://github.com/jashe/Interpretable-CNN-Disease-Prediction-XAI.git
+```
+
+If the repo is private, make sure you are signed into the GitHub account that owns or has access to it.
+
+### 2) Backend setup
+```bash
+cd backend
+python -m venv .venv
+source .venv/bin/activate   # Windows: .venv\Scripts\activate
+pip install -r requirements.txt
+python init_db.py
+python app.py
+```
+Backend: `http://localhost:5000`
+
+### 3) Frontend setup
+```bash
+cd frontend
+npm install
+npm start
+```
+Frontend: `http://localhost:3000`
+
+### PowerShell quick-start (copy/paste)
+```powershell
+# 1) If already downloaded, open it directly
+cd C:\path\to\Interpretable-CNN-Disease-Prediction-XAI
+
+# (OR) clone from your own actual URL
+# git clone https://github.com/OWNER/REPO.git
+# cd REPO
+
+# 2) Backend
+cd backend
+python -m venv .venv
+.\.venv\Scripts\Activate.ps1
+pip install -r requirements.txt
+python init_db.py
+python app.py
+```
+
+Open a second PowerShell terminal:
+```powershell
+cd C:\path\to\Interpretable-CNN-Disease-Prediction-XAI\frontend
+npm install
+npm start
+```
+
+If backend URL is different:
+```bash
+export REACT_APP_API_URL=http://localhost:5000
+```
+
+---
+
+## Train X-ray model from Kaggle dataset
+
+If you have dataset at `/kaggle/input/chest-xray-pneumonia`:
+
+```bash
+cd backend
+python train_xray_model.py \
+  --dataset /kaggle/input/chest-xray-pneumonia \
+  --output cnn_model/medxai_model.h5 \
+  --epochs 12 \
+  --fine-tune-epochs 10 \
+  --unfreeze-layers 40
+```
+
+For local (non-Kaggle) use, download the same dataset and pass your local dataset path to `--dataset`.
+
+---
+
+## API quick reference
+
+### `POST /predict-xray`
+`multipart/form-data`
+- `image` (file)
+- optional fields: `name`, `age`, `gender`, `symptoms`, `doctor`
+
+### `POST /predict-eye`
+Accepts either:
+- `multipart/form-data` with `image` file, or
+- JSON `{ "image": "data:image/png;base64,..." }`
+
+### `GET /history`
+Returns all history rows ordered by latest first.
+
+### `GET /download-report?id=<id>`
+Returns a generated PDF report for the selected record, including a short "Why this can happen" explanation for the predicted condition.
+
+---
+
+## Notes
+
+- Place trained models in `backend/cnn_model/` before production use.
+- If model files are missing, backend uses a fallback prediction path so API can still be smoke-tested.
+- This project is educational/assistive and not a replacement for clinical diagnosis.
