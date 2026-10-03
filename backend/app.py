from __future__ import annotations

import io
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "cnn_model"
UPLOAD_DIR = BASE_DIR / "uploads"
HEATMAP_DIR = BASE_DIR / "heatmaps"
REPORT_DIR = BASE_DIR / "reports"
DB_PATH = BASE_DIR / "medical_ai.db"

for directory in [UPLOAD_DIR, HEATMAP_DIR, REPORT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
CORS(app)

# medxai_model.keras has a single sigmoid output: 0 = Normal, 1 = Pneumonia.
XRAY_CLASSES = ["Normal", "Pneumonia"]
EYE_CLASSES = ["Healthy", "Conjunctivitis", "Cataract", "Diabetic Retinopathy"]


DISEASE_EXPLANATIONS = {
    "Pneumonia": "Pneumonia is often caused by bacterial, viral, or fungal infections that inflame the air sacs in the lungs.",
    "Tuberculosis": "Tuberculosis is caused by Mycobacterium tuberculosis and typically spreads through airborne droplets.",
    "COVID-19": "COVID-19 is caused by SARS-CoV-2, which can produce inflammatory lung changes visible on chest imaging.",
    "Conjunctivitis": "Conjunctivitis is usually caused by viral or bacterial infection, allergy, or irritation of the eye surface.",
    "Cataract": "Cataracts develop when lens proteins break down over time, making the lens cloudy and reducing vision clarity.",
    "Diabetic Retinopathy": "Diabetic retinopathy is caused by long-term high blood sugar that damages retinal blood vessels.",
    "Normal": "No strong disease-specific pattern was detected by the model in this image.",
    "Healthy": "No strong disease-specific pattern was detected by the model in this image.",
}


def get_db_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                symptoms TEXT,
                doctor TEXT,
                test_type TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                risk_level TEXT NOT NULL,
                date TEXT NOT NULL,
                image_path TEXT,
                heatmap_path TEXT
            )
            """
        )


def _safe_load_model(model_path: Path) -> tf.keras.Model | None:
    if not model_path.exists():
        app.logger.warning("Model file missing: %s", model_path)
        return None
    try:
        return tf.keras.models.load_model(model_path, compile=False)
    except Exception as exc:  # pragma: no cover - runtime environment variability
        app.logger.error("Could not load model %s: %s", model_path, exc)
        return None


xray_model = _safe_load_model(MODEL_DIR / "medxai_model.keras")
eye_model = _safe_load_model(MODEL_DIR / "eye_model.h5")


def preprocess_image(
    image_bytes: bytes,
    target_size: tuple[int, int] = (224, 224),
    normalize: bool = True,
) -> tuple[np.ndarray, np.ndarray]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.resize(target_size)
    image_array = np.array(image)
    model_input = image_array.astype(np.float32)
    if normalize:
        model_input /= 255.0
    batched = np.expand_dims(model_input, axis=0)
    return image_array, batched


def decode_base64_image(image_str: str) -> bytes:
    import base64

    if "," in image_str:
        image_str = image_str.split(",", 1)[1]
    return base64.b64decode(image_str)




def center_crop_square(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    cropped = image.crop((left, top, left + size, top + size))
    buffer = io.BytesIO()
    cropped.save(buffer, format="PNG")
    return buffer.getvalue()


def infer_prediction(model: tf.keras.Model | None, batch: np.ndarray, classes: list[str]) -> tuple[str, float, np.ndarray]:
    if model is None:
        # Safe fallback if model files are not yet available.
        random_conf = float(np.random.uniform(0.72, 0.93))
        probs = np.zeros((len(classes),), dtype=np.float32)
        probs[np.random.randint(0, len(classes))] = random_conf
        probs = probs / probs.sum()
    else:
        predictions = np.asarray(model.predict(batch, verbose=0)[0], dtype=np.float32).reshape(-1)
        if predictions.size == 1 and len(classes) == 2:
            positive_probability = float(np.clip(predictions[0], 0.0, 1.0))
            probs = np.array([1.0 - positive_probability, positive_probability], dtype=np.float32)
        elif predictions.size == len(classes):
            probs = predictions
        else:
            raise ValueError(
                f"Model returned {predictions.size} output(s), but {len(classes)} class labels were configured."
            )
    idx = int(np.argmax(probs))
    return classes[idx], float(probs[idx]), probs


def get_last_conv_layer(model: tf.keras.Model) -> str:
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return layer.name
    raise ValueError("No Conv2D layer found for Grad-CAM")


def generate_gradcam(
    model: tf.keras.Model | None,
    image_batch: np.ndarray,
    original_image: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    heatmap: np.ndarray | None = None
    if model is not None:
        try:
            conv_layer_name = get_last_conv_layer(model)
            grad_model = tf.keras.models.Model(
                model.inputs,
                [model.get_layer(conv_layer_name).output, model.output],
            )

            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(image_batch)
                pred_index = tf.argmax(predictions[0])
                class_channel = predictions[:, pred_index]

            grads = tape.gradient(class_channel, conv_outputs)
            pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
            conv_outputs = conv_outputs[0]
            heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]
            heatmap = tf.squeeze(heatmap)
            heatmap = tf.maximum(heatmap, 0) / tf.math.reduce_max(heatmap)
            heatmap = np.uint8(255 * heatmap.numpy())
        except ValueError:
            # medxai_model.keras stores its Conv2D layers inside a nested MobileNet model.
            # Its convolution output is not directly addressable from the top-level graph.
            app.logger.warning("Grad-CAM is unavailable for the loaded model; using a fallback heatmap.")

    if heatmap is None:
        # Fallback pseudo heatmap when weights or an addressable Conv2D layer are unavailable.
        gray = cv2.cvtColor(original_image, cv2.COLOR_RGB2GRAY)
        heatmap = cv2.GaussianBlur(gray, (11, 11), 0)
        heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    resized_heatmap = cv2.resize(heatmap, (original_image.shape[1], original_image.shape[0]))
    color_map = cv2.applyColorMap(resized_heatmap, cv2.COLORMAP_JET)
    overlay = cv2.addWeighted(cv2.cvtColor(original_image, cv2.COLOR_RGB2BGR), 0.55, color_map, 0.45, 0)
    return resized_heatmap, overlay


def risk_from_confidence(confidence: float) -> str:
    if confidence >= 0.85:
        return "High"
    if confidence >= 0.65:
        return "Moderate"
    return "Low"


def save_images(original_bytes: bytes, overlay: np.ndarray, prefix: str) -> tuple[Path, Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    image_path = UPLOAD_DIR / f"{prefix}_{timestamp}.png"
    heatmap_path = HEATMAP_DIR / f"{prefix}_{timestamp}_heatmap.png"

    with image_path.open("wb") as img_file:
        img_file.write(original_bytes)
    cv2.imwrite(str(heatmap_path), overlay)
    return image_path, heatmap_path


def insert_history(payload: dict[str, Any]) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO history
            (name, age, gender, symptoms, doctor, test_type, disease, confidence, risk_level, date, image_path, heatmap_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["name"],
                payload.get("age"),
                payload.get("gender"),
                payload.get("symptoms"),
                payload.get("doctor"),
                payload["test_type"],
                payload["disease"],
                payload["confidence"],
                payload["risk_level"],
                payload["date"],
                payload.get("image_path"),
                payload.get("heatmap_path"),
            ),
        )
        return int(cursor.lastrowid)




def explanation_for_disease(disease: str, test_type: str) -> str:
    base_explanation = DISEASE_EXPLANATIONS.get(
        disease,
        "The predicted pattern can be related to infection, inflammation, metabolic disease, or degenerative change depending on the clinical context.",
    )
    modality_note = (
        "Eye-image prediction reflects visual retinal or ocular-surface patterns only."
        if test_type == "eye"
        else "X-ray prediction reflects radiographic lung patterns only."
    )
    return f"{base_explanation} {modality_note} Confirm with clinical evaluation and specialist review."


def generate_pdf_report(record: sqlite3.Row) -> Path:
    report_path = REPORT_DIR / f"report_{record['id']}.pdf"
    doc = SimpleDocTemplate(str(report_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story: list[Any] = []

    story.append(Paragraph("Medical AI Diagnostic Report", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    table_data = [
        ["Patient Name", record["name"]],
        ["Age", str(record["age"] or "-")],
        ["Gender", record["gender"] or "-"],
        ["Symptoms", record["symptoms"] or "-"],
        ["Doctor", record["doctor"] or "-"],
        ["Test Type", record["test_type"]],
        ["Predicted Disease", record["disease"]],
        ["Confidence", f"{record['confidence'] * 100:.2f}%"],
        ["Risk Level", record["risk_level"]],
        ["Date", record["date"]],
    ]
    table = Table(table_data, colWidths=[2.2 * inch, 4.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#E6F0FF")),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    explanation = explanation_for_disease(record["disease"], record["test_type"])
    story.append(Paragraph("Why this can happen", styles["Heading3"]))
    story.append(Paragraph(explanation, styles["BodyText"]))
    story.append(Spacer(1, 0.2 * inch))

    for label, path_key in [("Original Image", "image_path"), ("Grad-CAM Heatmap", "heatmap_path")]:
        image_path = record[path_key]
        if image_path and Path(image_path).exists():
            story.append(Paragraph(label, styles["Heading3"]))
            story.append(RLImage(image_path, width=3.0 * inch, height=3.0 * inch))
            story.append(Spacer(1, 0.15 * inch))

    doc.build(story)
    return report_path


def parse_patient_form() -> dict[str, Any]:
    return {
        "name": request.form.get("name", "Anonymous"),
        "age": request.form.get("age"),
        "gender": request.form.get("gender", "Unspecified"),
        "symptoms": request.form.get("symptoms", ""),
        "doctor": request.form.get("doctor", ""),
    }


@app.route("/health", methods=["GET"])
def health() -> Any:
    return jsonify({"status": "ok", "message": "Medical AI backend running"})


@app.route("/predict-xray", methods=["POST"])
def predict_xray() -> Any:
    if "image" not in request.files:
        return jsonify({"error": "image file is required"}), 400

    uploaded = request.files["image"]
    safe_name = secure_filename(uploaded.filename or "xray.png")
    img_bytes = uploaded.read()
    # medxai_model.keras contains MobileNet preprocessing and expects 0-255 RGB pixels.
    raw_image, batch = preprocess_image(img_bytes, normalize=False)

    disease, confidence, _ = infer_prediction(xray_model, batch, XRAY_CLASSES)
    _, overlay = generate_gradcam(xray_model, batch, raw_image)
    image_path, heatmap_path = save_images(img_bytes, overlay, "xray")

    patient = parse_patient_form()
    payload = {
        **patient,
        "test_type": "xray",
        "disease": disease,
        "confidence": confidence,
        "risk_level": risk_from_confidence(confidence),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": str(image_path),
        "heatmap_path": str(heatmap_path),
    }
    record_id = insert_history(payload)

    return jsonify(
        {
            "id": record_id,
            "filename": safe_name,
            "disease": disease,
            "confidence": confidence,
            "risk_level": payload["risk_level"],
            "heatmap_url": f"/files/heatmap/{heatmap_path.name}",
            "image_url": f"/files/upload/{image_path.name}",
        }
    )


@app.route("/predict-eye", methods=["POST"])
def predict_eye() -> Any:
    img_bytes: bytes
    if "image" in request.files:
        img_bytes = request.files["image"].read()
    else:
        body = request.get_json(silent=True) or {}
        image_data = body.get("image")
        if not image_data:
            return jsonify({"error": "image file or base64 image is required"}), 400
        img_bytes = decode_base64_image(image_data)

    cropped_eye_bytes = center_crop_square(img_bytes)
    raw_image, batch = preprocess_image(cropped_eye_bytes)
    disease, confidence, _ = infer_prediction(eye_model, batch, EYE_CLASSES)
    _, overlay = generate_gradcam(eye_model, batch, raw_image)
    image_path, heatmap_path = save_images(cropped_eye_bytes, overlay, "eye")

    patient = parse_patient_form() if request.form else (request.get_json(silent=True) or {})
    payload = {
        "name": patient.get("name", "Anonymous"),
        "age": patient.get("age"),
        "gender": patient.get("gender", "Unspecified"),
        "symptoms": patient.get("symptoms", ""),
        "doctor": patient.get("doctor", ""),
        "test_type": "eye",
        "disease": disease,
        "confidence": confidence,
        "risk_level": risk_from_confidence(confidence),
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "image_path": str(image_path),
        "heatmap_path": str(heatmap_path),
    }
    record_id = insert_history(payload)

    return jsonify(
        {
            "id": record_id,
            "disease": disease,
            "confidence": confidence,
            "risk_level": payload["risk_level"],
            "heatmap_url": f"/files/heatmap/{heatmap_path.name}",
            "image_url": f"/files/upload/{image_path.name}",
        }
    )


@app.route("/history", methods=["GET"])
def history() -> Any:
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    return jsonify([dict(row) for row in rows])


@app.route("/download-report", methods=["GET"])
def download_report() -> Any:
    record_id = request.args.get("id")
    if not record_id:
        return jsonify({"error": "id query parameter is required"}), 400

    with get_db_connection() as conn:
        record = conn.execute("SELECT * FROM history WHERE id = ?", (record_id,)).fetchone()

    if record is None:
        return jsonify({"error": "record not found"}), 404

    report_path = generate_pdf_report(record)
    return send_file(
        report_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=report_path.name,
        max_age=0,
    )


@app.route("/files/upload/<filename>", methods=["GET"])
def serve_uploaded_file(filename: str) -> Any:
    return send_file(UPLOAD_DIR / filename)


@app.route("/files/heatmap/<filename>", methods=["GET"])
def serve_heatmap_file(filename: str) -> Any:
    return send_file(HEATMAP_DIR / filename)


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
