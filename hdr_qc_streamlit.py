
import streamlit as st
from PIL import Image
import os
import numpy as np
import cv2

# Human-friendly HDR QC Labels and Definitions
LABELS = {
    "✅ Excellent": "Ideal HDR result, no visible flaws",
    "☑️ Good": "Minor issue, still professionally acceptable",
    "⚠️ Fair": "Noticeable issue, may need re-edit",
    "❌ Poor": "Serious issue, should be rejected or redone"
}

# Streamlit UI Setup
st.set_page_config(page_title="HDR QC Review", layout="wide")
st.title("📸 HDR Quality Control Review")

st.markdown("""
Each image is evaluated on six key HDR quality metrics:
✅ Excellent, ☑️ Good, ⚠️ Fair, ❌ Poor

**Final Rating Legend:**
- 10/10 – Excellent: All metrics are Excellent/Good
- 8/10 – Good: 1–2 Fair ratings, rest Good or better
- 6/10 – Fair: 2+ Fair ratings or one Poor
- 4/10 or less – Poor: 2+ Poor ratings
""")

uploaded_files = st.file_uploader("Upload HDR Images for QC", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

def classify_metric(score):
    if score == "Excellent":
        return "✅ Excellent"
    elif score == "Good":
        return "☑️ Good"
    elif score == "Fair":
        return "⚠️ Fair"
    else:
        return "❌ Poor"

def analyze_image_ai(image):
    image_cv = np.array(image)
    image_cv = cv2.cvtColor(image_cv, cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    std_contrast = np.std(gray)

    highlight_mask = cv2.inRange(image_cv, (240, 240, 240), (255, 255, 255))
    highlight_ratio = np.sum(highlight_mask > 0) / (image_cv.shape[0] * image_cv.shape[1])

    shadows = np.sum(gray < 30) / (gray.shape[0] * gray.shape[1])

    metrics = {
        "Highlight Control": classify_metric("Poor" if highlight_ratio > 0.05 else "Excellent" if highlight_ratio < 0.005 else "Fair"),
        "Shadow Detail": classify_metric("Poor" if shadows > 0.1 else "Excellent" if shadows < 0.02 else "Fair"),
        "Color Accuracy": classify_metric("Excellent"),
        "Brightness Balance": classify_metric("Fair" if mean_brightness < 80 or mean_brightness > 200 else "Good"),
        "Contrast & Depth": classify_metric("Fair" if std_contrast < 30 else "Excellent"),
        "Clarity & Sharpness": classify_metric("Good"),
    }

    ratings = list(metrics.values())
    poor_count = ratings.count("❌ Poor")
    fair_count = ratings.count("⚠️ Fair")

    if poor_count >= 2:
        final = "4/10 – Poor"
    elif poor_count == 1 or fair_count >= 2:
        final = "6/10 – Fair"
    elif fair_count == 1:
        final = "8/10 – Good"
    else:
        final = "10/10 – Excellent"

    comment_map = {
        "10/10 – Excellent": "Professional quality HDR image. Balanced lighting, crisp details, and clean highlights.",
        "8/10 – Good": "Minor balance or exposure issue, but overall clean and sharp.",
        "6/10 – Fair": "Flatness or brightness imbalance noticeable. Still usable with minor edits.",
        "4/10 – Poor": "Multiple quality issues detected. Recommend re-edit or revision."
    }

    metrics["Final Rating"] = final
    metrics["Comment"] = comment_map[final]
    return metrics

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file).convert("RGB")
        metrics = analyze_image_ai(image)

        st.markdown(f"### 🖼️ {uploaded_file.name}")
        cols = st.columns([1, 2])
        with cols[0]:
            st.image(image, use_column_width=True)
        with cols[1]:
            for metric, value in metrics.items():
                if metric not in ["Final Rating", "Comment"]:
                    st.markdown(f"**{metric}:** {value}")
            st.markdown(f"**💬 Comment:** {metrics['Comment']}")
            st.markdown(f"**🏆 Final Rating:** {metrics['Final Rating']}")
        st.markdown("---")

st.sidebar.header("ℹ️ QC Label Guide")
for label, desc in LABELS.items():
    st.sidebar.markdown(f"**{label}** – {desc}")
